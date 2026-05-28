"""Prototype Detection runtime composition."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Protocol, cast

from cereal.detection.overlays import render_detection_overlays
from cereal.detection.store import SqliteDetectionStore
from cereal.detection.stream import (
    file_evidence_uri,
    run_detection_preview_loop,
    run_detection_stream,
)
from cereal.detection.types import DetectionStreamDefaults, FrameTime
from cereal.media.preview import PreviewBackend
from cereal.media.recording import FfmpegFrameWriter, WriterContext, recording_artifact_path
from cereal.media.registry import default_source_adapter_registry
from cereal.media.sources import first_configured_source
from cereal.media.uris import source_uri_scheme

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path
    from types import ModuleType

    from cereal.detection.detector import ObjectDetector
    from cereal.detection.store import DetectionStore
    from cereal.media.adapters import MediaCapture, OpenableMediaCapture, SourceAdapterRegistry
    from cereal.media.recording import FrameWriter
    from cereal.settings import Settings, SourceSettings

__all__ = ["default_detection_database_path", "run_detection_preview"]

OPENCV_POS_MSEC_PROPERTY = 0
logger = logging.getLogger(__name__)


class CaptureWithProperties(Protocol):
    """OpenCV-like capture that can expose frame position properties."""

    def get(self, property_id: int) -> float:
        """Return a capture property."""


def default_detection_database_path(settings: Settings) -> Path:
    """Return the prototype SQLite Detection store path."""
    return settings.storage / "cereal.sqlite3"


def run_detection_preview(  # noqa: C901, PLR0912, PLR0913 - runtime composition receives explicit ports and cleanup branches.
    settings: Settings,
    *,
    capture_factory: Callable[[str | int], OpenableMediaCapture] | None = None,
    registry: SourceAdapterRegistry | None = None,
    backend: PreviewBackend | None = None,
    detector: ObjectDetector | None = None,
    store: DetectionStore | None = None,
    store_factory: Callable[[Path], DetectionStore] = SqliteDetectionStore,
    writer_factory: Callable[[Path, WriterContext], FrameWriter] | None = None,
    clock: Callable[[], datetime] | None = None,
    defaults: DetectionStreamDefaults | None = None,
    database_path: Path | None = None,
    enable_overlays: bool = False,
    preview_enabled: bool = True,
) -> None:
    """Run the first-source Detection stream prototype with preview feedback."""
    opencv: ModuleType | None = None
    if capture_factory is None or (preview_enabled and backend is None):
        opencv = _load_opencv()
        if capture_factory is None:
            capture_factory = opencv.VideoCapture
        if preview_enabled and backend is None:
            backend = _opencv_preview_backend(opencv)

    if registry is None:
        registry = default_source_adapter_registry(capture_factory)
    if detector is None:
        detector = _default_detector()
    resolved_database_path = database_path or default_detection_database_path(settings)
    if store is None:
        store = store_factory(resolved_database_path)
    if clock is None:
        clock = _utc_now
    if defaults is None:
        defaults = DetectionStreamDefaults()

    capture: MediaCapture | None = None
    frame_writer: FrameWriter | None = None
    stream_started = False
    try:
        source = first_configured_source(settings)
        logger.info(
            "opening source name=%s uri=%s preview=%s overlays=%s database=%s",
            source.name,
            source.uri,
            "on" if preview_enabled else "off",
            "on" if enable_overlays else "off",
            resolved_database_path,
        )
        capture = registry.adapter_for(source).open(source)
        frame_writer, evidence_uri = _evidence_for_source(
            settings=settings,
            source=source,
            writer_factory=writer_factory,
            clock=clock,
        )
        frame_time_provider = _frame_time_provider(
            source=source,
            capture=capture,
            clock=clock,
        )
        logger.info(
            "detection runtime ready source=%s model=%s evidence_uri=%s",
            source.name,
            detector.model_name,
            evidence_uri,
        )

        if preview_enabled:
            if backend is None:
                msg = "preview backend is required when preview is enabled"
                raise RuntimeError(msg)
            stream_started = True
            run_detection_preview_loop(
                capture=capture,
                detector=detector,
                store=store,
                preview_backend=backend,
                source_name=source.name,
                evidence_uri=evidence_uri,
                defaults=defaults,
                frame_time_provider=frame_time_provider,
                frame_writer=frame_writer,
                overlay_renderer=render_detection_overlays if enable_overlays else None,
            )
        else:
            stream_started = True
            run_detection_stream(
                capture=capture,
                detector=detector,
                store=store,
                source_name=source.name,
                evidence_uri=evidence_uri,
                defaults=defaults,
                frame_time_provider=frame_time_provider,
                frame_writer=frame_writer,
            )
    finally:
        if not stream_started:
            if capture is not None:
                capture.release()
            if frame_writer is not None:
                frame_writer.release()
        store.close()


def _load_opencv() -> ModuleType:
    import cv2  # noqa: PLC0415

    return cv2


def _utc_now() -> datetime:
    return datetime.now(tz=UTC)


def _opencv_preview_backend(opencv: ModuleType) -> PreviewBackend:
    return PreviewBackend(
        show_frame=opencv.imshow,
        should_stop=lambda window_name, delay_ms: (
            opencv.waitKey(delay_ms) == ord("q")
            or opencv.getWindowProperty(window_name, opencv.WND_PROP_VISIBLE) < 1
        ),
        destroy_windows=opencv.destroyAllWindows,
    )


def _default_detector() -> ObjectDetector:
    from cereal.detection.yolo_adapter import UltralyticsObjectDetector  # noqa: PLC0415

    return UltralyticsObjectDetector()


def _evidence_for_source(
    *,
    settings: Settings,
    source: SourceSettings,
    writer_factory: Callable[[Path, WriterContext], FrameWriter] | None,
    clock: Callable[[], datetime],
) -> tuple[FrameWriter | None, str]:
    if source_uri_scheme(source.uri) == "file":
        return None, source.uri

    if not source.write:
        msg = (
            f"non-file detection source requires write: true to create recoverable evidence: "
            f"{source.name}"
        )
        raise RuntimeError(msg)

    writer_context = WriterContext()
    artifact_path = recording_artifact_path(
        storage_root=settings.storage,
        source_name=source.name,
        recorded_at=clock(),
        writer_context=writer_context,
    )
    if writer_factory is None:
        writer_factory = _default_writer

    return writer_factory(artifact_path, writer_context), file_evidence_uri(artifact_path)


def _default_writer(artifact_path: Path, writer_context: WriterContext) -> FrameWriter:
    return FfmpegFrameWriter(artifact_path=artifact_path, writer_context=writer_context)


def _frame_time_provider(
    *,
    source: SourceSettings,
    capture: MediaCapture,
    clock: Callable[[], datetime],
) -> Callable[[int], FrameTime]:
    if source_uri_scheme(source.uri) == "file":
        return lambda _frame_index: FrameTime(
            observed=None,
            media_ms=round(
                cast("CaptureWithProperties", capture).get(OPENCV_POS_MSEC_PROPERTY),
            ),
        )

    return lambda _frame_index: FrameTime(observed=clock(), media_ms=None)
