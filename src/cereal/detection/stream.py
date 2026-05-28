"""Sampled Detection stream loop."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Protocol, cast

from cereal.detection.types import (
    DetectionCandidate,
    DetectionStreamDefaults,
    FrameTime,
    to_detection_events,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from pathlib import Path

    import numpy as np

    from cereal.detection.detector import ObjectDetector
    from cereal.detection.store import DetectionStore
    from cereal.detection.types import DetectionCandidate, DetectionEvent
    from cereal.media.adapters import MediaCapture
    from cereal.media.preview import PreviewBackend
    from cereal.media.recording import FrameWriter

__all__ = [
    "file_evidence_uri",
    "filter_candidates",
    "run_detection_preview_loop",
    "run_detection_stream",
    "should_sample",
    "to_detection_events",
]

logger = logging.getLogger(__name__)


class FrameWithShape(Protocol):
    """Frame shape needed to attach dimensions to Detection events."""

    shape: Sequence[int]


def should_sample(
    previous_sample_time: FrameTime | None,
    frame_time: FrameTime,
    sample_interval_s: float,
) -> bool:
    """Return whether a frame should be sampled at the configured interval."""
    if previous_sample_time is None:
        return True

    return _frame_time_seconds(frame_time) - _frame_time_seconds(previous_sample_time) >= (
        sample_interval_s
    )


def filter_candidates(
    candidates: Sequence[DetectionCandidate],
    confidence_threshold: float,
) -> list[DetectionCandidate]:
    """Keep candidates at or above the stream confidence threshold."""
    return [candidate for candidate in candidates if candidate.confidence >= confidence_threshold]


def file_evidence_uri(path: Path) -> str:
    """Return a standard file URI for local video evidence."""
    return path.resolve().as_uri()


def run_detection_stream(  # noqa: PLR0913 - stream composition receives explicit ports.
    *,
    capture: MediaCapture,
    detector: ObjectDetector,
    store: DetectionStore,
    source_name: str,
    evidence_uri: str,
    defaults: DetectionStreamDefaults,
    frame_time_provider: Callable[[int], FrameTime],
    frame_writer: FrameWriter | None = None,
    stop_predicate: Callable[[int], bool] | None = None,
) -> None:
    """Read frames, sample detections, and append events until capture ends."""
    frame_index = 0
    previous_sample_time: FrameTime | None = None

    try:
        while True:
            has_frame, frame = capture.read()
            if not has_frame:
                break
            if frame is None:
                break

            if frame_writer is not None:
                frame_writer.write(frame)

            frame_time = frame_time_provider(frame_index)
            _validate_frame_time(frame_time)

            if should_sample(previous_sample_time, frame_time, defaults.sample_interval_s):
                previous_sample_time = frame_time
                detection_frame = cast("np.ndarray", frame)
                raw_candidates = detector.detect(detection_frame)
                candidates = filter_candidates(raw_candidates, defaults.confidence_threshold)
                logger.info(
                    "sampled frame source=%s frame_index=%s raw_candidates=%s kept=%s overlays=off",
                    source_name,
                    frame_index,
                    len(raw_candidates),
                    len(candidates),
                )
                if candidates:
                    events = _store_detection_candidates(
                        candidates=candidates,
                        store=store,
                        source_name=source_name,
                        frame_index=frame_index,
                        frame=frame,
                        frame_time=frame_time,
                        evidence_uri=evidence_uri,
                        model_name=detector.model_name,
                    )
                    logger.info(
                        "stored detections source=%s frame_index=%s count=%s evidence_uri=%s",
                        source_name,
                        frame_index,
                        len(events),
                        evidence_uri,
                    )

            if stop_predicate is not None and stop_predicate(frame_index):
                break

            frame_index += 1
    finally:
        capture.release()
        if frame_writer is not None:
            frame_writer.release()


def run_detection_preview_loop(  # noqa: C901, PLR0912, PLR0913, PLR0915 - explicit composition.
    *,
    capture: MediaCapture,
    detector: ObjectDetector,
    store: DetectionStore,
    preview_backend: PreviewBackend,
    source_name: str,
    evidence_uri: str,
    defaults: DetectionStreamDefaults,
    frame_time_provider: Callable[[int], FrameTime],
    frame_writer: FrameWriter | None = None,
    overlay_renderer: Callable[[np.ndarray, Sequence[DetectionCandidate]], np.ndarray]
    | None = None,
    window_name: str = "Cereal Preview",
    delay_ms: int = 33,
) -> None:
    """Display every frame while sampling Detection events."""
    frame_index = 0
    previous_sample_time: FrameTime | None = None
    overlay_candidates: list[DetectionCandidate] = []

    try:
        while True:
            has_frame, frame = capture.read()
            if not has_frame:
                break
            if frame is None:
                break

            if frame_writer is not None:
                frame_writer.write(frame)

            frame_time = frame_time_provider(frame_index)
            _validate_frame_time(frame_time)
            should_detect = should_sample(
                previous_sample_time,
                frame_time,
                defaults.sample_interval_s,
            )
            candidates: list[DetectionCandidate] = []
            candidates_stored = False

            if should_detect and overlay_renderer is not None:
                previous_sample_time = frame_time
                detection_frame = cast("np.ndarray", frame)
                raw_candidates = detector.detect(detection_frame)
                candidates = filter_candidates(raw_candidates, defaults.confidence_threshold)
                logger.info(
                    "sampled frame source=%s frame_index=%s raw_candidates=%s kept=%s overlays=on",
                    source_name,
                    frame_index,
                    len(raw_candidates),
                    len(candidates),
                )
                overlay_candidates = candidates

            preview_frame = frame
            if overlay_renderer is not None and overlay_candidates:
                preview_frame = overlay_renderer(cast("np.ndarray", frame), overlay_candidates)

            preview_backend.show_frame(window_name, preview_frame)
            if should_detect and overlay_renderer is not None and candidates:
                events = _store_detection_candidates(
                    candidates=candidates,
                    store=store,
                    source_name=source_name,
                    frame_index=frame_index,
                    frame=frame,
                    frame_time=frame_time,
                    evidence_uri=evidence_uri,
                    model_name=detector.model_name,
                )
                logger.info(
                    "stored detections source=%s frame_index=%s count=%s evidence_uri=%s",
                    source_name,
                    frame_index,
                    len(events),
                    evidence_uri,
                )
                candidates_stored = True
            if preview_backend.should_stop(window_name, delay_ms):
                break

            if should_detect:
                previous_sample_time = frame_time
                if overlay_renderer is None:
                    detection_frame = cast("np.ndarray", frame)
                    raw_candidates = detector.detect(detection_frame)
                    candidates = filter_candidates(raw_candidates, defaults.confidence_threshold)
                    logger.info(
                        (
                            "sampled frame source=%s frame_index=%s raw_candidates=%s "
                            "kept=%s overlays=off"
                        ),
                        source_name,
                        frame_index,
                        len(raw_candidates),
                        len(candidates),
                    )
                if candidates and not candidates_stored:
                    events = _store_detection_candidates(
                        candidates=candidates,
                        store=store,
                        source_name=source_name,
                        frame_index=frame_index,
                        frame=frame,
                        frame_time=frame_time,
                        evidence_uri=evidence_uri,
                        model_name=detector.model_name,
                    )
                    logger.info(
                        "stored detections source=%s frame_index=%s count=%s evidence_uri=%s",
                        source_name,
                        frame_index,
                        len(events),
                        evidence_uri,
                    )

            frame_index += 1
    finally:
        try:
            capture.release()
            if frame_writer is not None:
                frame_writer.release()
        finally:
            preview_backend.destroy_windows()


def _validate_frame_time(frame_time: FrameTime) -> None:
    if frame_time.observed is None and frame_time.media_ms is None:
        msg = "FrameTime requires at least one observed or media time"
        raise ValueError(msg)


def _store_detection_candidates(  # noqa: PLR0913 - persistence needs explicit event context.
    *,
    candidates: Sequence[DetectionCandidate],
    store: DetectionStore,
    source_name: str,
    frame_index: int,
    frame: object,
    frame_time: FrameTime,
    evidence_uri: str,
    model_name: str,
) -> list[DetectionEvent]:
    frame_width, frame_height = _frame_dimensions(frame)
    events = to_detection_events(
        candidates=candidates,
        source_name=source_name,
        frame_index=frame_index,
        frame_width=frame_width,
        frame_height=frame_height,
        frame_time=frame_time,
        evidence_uri=evidence_uri,
        model_name=model_name,
    )
    return store.insert_many(events)


def _frame_time_seconds(frame_time: FrameTime) -> float:
    if frame_time.media_ms is not None:
        return frame_time.media_ms / 1000
    if frame_time.observed is not None:
        return frame_time.observed.timestamp()

    msg = "FrameTime requires at least one observed or media time"
    raise ValueError(msg)


def _frame_dimensions(frame: object) -> tuple[int, int]:
    shape = cast("FrameWithShape", frame).shape
    return int(shape[1]), int(shape[0])
