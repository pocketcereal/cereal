"""OpenCV-backed preview boundary for Cereal.

OpenCV is loaded lazily so importing the media boundary stays cheap.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path
    from types import ModuleType

    from cereal.media.adapters import MediaCapture, OpenableMediaCapture
    from cereal.media.recording import FrameWriter
    from cereal.settings import Settings

from cereal.media.recording import FfmpegFrameWriter, WriterContext, recording_artifact_path
from cereal.media.registry import default_source_adapter_registry
from cereal.media.sources import first_configured_source

__all__ = ["PreviewBackend", "run_preview", "run_preview_loop"]


@dataclass(frozen=True)
class PreviewBackend:
    """Window operations for the preview loop."""

    show_frame: Callable[[str, object], None]
    should_stop: Callable[[str, int], bool]
    destroy_windows: Callable[[], None]


def _load_opencv() -> ModuleType:
    import cv2  # noqa: PLC0415

    return cv2


def _opencv_preview_backend(opencv: ModuleType) -> PreviewBackend:
    return PreviewBackend(
        show_frame=opencv.imshow,
        should_stop=lambda window_name, delay_ms: (
            opencv.waitKey(delay_ms) == ord("q")
            or opencv.getWindowProperty(window_name, opencv.WND_PROP_VISIBLE) < 1
        ),
        destroy_windows=opencv.destroyAllWindows,
    )


def run_preview(
    settings: Settings,
    *,
    capture_factory: Callable[[str | int], OpenableMediaCapture] | None = None,
    backend: PreviewBackend | None = None,
    writer_factory: Callable[[Path, WriterContext], FrameWriter] | None = None,
    clock: Callable[[], datetime] | None = None,
) -> None:
    """Open the first configured source and run the preview loop."""
    opencv: ModuleType | None = None
    if capture_factory is None or backend is None:
        opencv = _load_opencv()
        if capture_factory is None:
            capture_factory = opencv.VideoCapture
        if backend is None:
            backend = _opencv_preview_backend(opencv)

    registry = default_source_adapter_registry(capture_factory)
    source = first_configured_source(settings)
    capture = registry.adapter_for(source).open(source)
    frame_writer = None

    if source.write:
        if writer_factory is None:
            if opencv is None:
                opencv = _load_opencv()

            def create_ffmpeg_frame_writer(
                artifact_path: Path,
                writer_context: WriterContext,
            ) -> FrameWriter:
                return FfmpegFrameWriter(
                    artifact_path=artifact_path,
                    writer_context=writer_context,
                )

            writer_factory = create_ffmpeg_frame_writer

        writer_context = WriterContext()
        recorded_at = datetime.now(tz=UTC) if clock is None else clock()
        artifact_path = recording_artifact_path(
            storage_root=settings.storage,
            source_name=source.name,
            recorded_at=recorded_at,
            writer_context=writer_context,
        )
        frame_writer = writer_factory(artifact_path, writer_context)

    run_preview_loop(capture, backend, frame_writer=frame_writer)


def run_preview_loop(
    capture: MediaCapture,
    backend: PreviewBackend,
    *,
    frame_writer: FrameWriter | None = None,
    window_name: str = "Cereal Preview",
    delay_ms: int = 33,
) -> None:
    """Display frames until EOF, user quit, or window close."""
    try:
        while True:
            has_frame, frame = capture.read()
            if not has_frame:
                break

            backend.show_frame(window_name, frame)
            if frame_writer is not None:
                frame_writer.write(frame)
            if backend.should_stop(window_name, delay_ms):
                break
    except KeyboardInterrupt:
        pass
    finally:
        try:
            capture.release()
            if frame_writer is not None:
                frame_writer.release()
        finally:
            backend.destroy_windows()
