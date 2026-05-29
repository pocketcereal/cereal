"""Tests for sampled Detection stream ingestion."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, cast

import numpy as np
import pytest

from cereal.detection.stream import (
    file_evidence_uri,
    filter_candidates,
    run_detection_preview_loop,
    run_detection_stream,
    should_sample,
)
from cereal.detection.types import (
    BoundingBox,
    DetectionCandidate,
    DetectionEvent,
    DetectionStreamDefaults,
    FrameTime,
)
from cereal.media.preview import PreviewBackend

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from cereal.detection.store import DetectionLabelCount, DetectionLabelQuery

FRAME_HEIGHT = 24
FRAME_WIDTH = 32
SAMPLE_INTERVAL_S = 3.0
THRESHOLD = 0.5


def test_should_sample_first_frame_and_interval_jumps_once() -> None:
    first_time = FrameTime(observed=None, media_ms=0)
    before_interval = FrameTime(observed=None, media_ms=1_000)
    at_interval = FrameTime(observed=None, media_ms=3_000)
    after_jump = FrameTime(observed=None, media_ms=9_000)

    assert should_sample(None, first_time, SAMPLE_INTERVAL_S) is True
    assert should_sample(first_time, before_interval, SAMPLE_INTERVAL_S) is False
    assert should_sample(first_time, at_interval, SAMPLE_INTERVAL_S) is True
    assert should_sample(at_interval, after_jump, SAMPLE_INTERVAL_S) is True


def test_filter_candidates_keeps_confidence_at_or_above_threshold() -> None:
    low = make_candidate(confidence=0.49)
    equal = make_candidate(confidence=THRESHOLD)
    high = make_candidate(confidence=0.9)

    assert filter_candidates([low, equal, high], THRESHOLD) == [equal, high]


def test_detection_stream_samples_filters_and_stores_events() -> None:
    frames = [make_frame(), make_frame(), make_frame(), make_frame()]
    expected_frames = list(frames)
    capture = FakeCapture(frames=frames)
    first_candidate = make_candidate(confidence=0.9, class_name="person")
    skipped_candidate = make_candidate(confidence=0.4, class_name="car")
    later_candidate = make_candidate(confidence=0.8, class_name="truck")
    detector = FakeDetector([[first_candidate], [skipped_candidate], [later_candidate]])
    store = FakeStore()
    frame_times = [
        FrameTime(observed=None, media_ms=0),
        FrameTime(observed=None, media_ms=1_000),
        FrameTime(observed=None, media_ms=3_000),
        FrameTime(observed=None, media_ms=7_000),
    ]

    run_detection_stream(
        capture=capture,
        detector=detector,
        store=store,
        source_name="camera",
        evidence_uri="file:///tmp/cereal.mp4",
        defaults=DetectionStreamDefaults(
            sample_interval_s=SAMPLE_INTERVAL_S,
            confidence_threshold=THRESHOLD,
        ),
        frame_time_provider=lambda frame_index: frame_times[frame_index],
    )

    assert detector.seen_frames == [expected_frames[0], expected_frames[2], expected_frames[3]]
    assert [[event.class_name for event in batch] for batch in store.inserted_batches] == [
        ["person"],
        ["truck"],
    ]
    assert [event.frame_index for batch in store.inserted_batches for event in batch] == [0, 3]
    assert capture.released is True


def test_detection_stream_skips_store_write_when_sample_has_no_detections() -> None:
    capture = FakeCapture(frames=[make_frame()])
    detector = FakeDetector([[]])
    store = FakeStore()

    run_detection_stream(
        capture=capture,
        detector=detector,
        store=store,
        source_name="camera",
        evidence_uri="file:///tmp/cereal.mp4",
        defaults=DetectionStreamDefaults(),
        frame_time_provider=lambda _frame_index: FrameTime(observed=None, media_ms=0),
    )

    assert store.inserted_batches == []


def test_detection_stream_surfaces_invalid_frame_time_and_releases_capture() -> None:
    capture = FakeCapture(frames=[make_frame()])

    def invalid_frame_time(_frame_index: int) -> FrameTime:
        return FrameTime(observed=None, media_ms=None)

    with pytest.raises(ValueError, match="at least one"):
        run_detection_stream(
            capture=capture,
            detector=FakeDetector([[]]),
            store=FakeStore(),
            source_name="camera",
            evidence_uri="file:///tmp/cereal.mp4",
            defaults=DetectionStreamDefaults(),
            frame_time_provider=invalid_frame_time,
        )

    assert capture.released is True


def test_detection_stream_honors_stop_predicate() -> None:
    frames = [make_frame(), make_frame()]
    detector = FakeDetector([[make_candidate(confidence=0.9)], [make_candidate(confidence=0.9)]])
    store = FakeStore()

    run_detection_stream(
        capture=FakeCapture(frames=frames),
        detector=detector,
        store=store,
        source_name="camera",
        evidence_uri="file:///tmp/cereal.mp4",
        defaults=DetectionStreamDefaults(sample_interval_s=0, confidence_threshold=THRESHOLD),
        frame_time_provider=lambda frame_index: FrameTime(observed=None, media_ms=frame_index),
        stop_predicate=lambda frame_index: frame_index == 0,
    )

    assert len(detector.seen_frames) == 1
    assert len(store.inserted_batches) == 1


def test_detection_stream_writes_every_frame_before_sampled_detection() -> None:
    frames = [make_frame(), make_frame()]
    capture = FakeCapture(frames=list(frames))
    detector = FakeDetector([[make_candidate(confidence=0.9)]])
    store = FakeStore()
    writer = FakeWriter()
    evidence_uri = "file:///tmp/cereal.mp4"

    run_detection_stream(
        capture=capture,
        detector=detector,
        store=store,
        source_name="camera",
        evidence_uri=evidence_uri,
        defaults=DetectionStreamDefaults(
            sample_interval_s=SAMPLE_INTERVAL_S,
            confidence_threshold=THRESHOLD,
        ),
        frame_time_provider=lambda frame_index: FrameTime(
            observed=None,
            media_ms=frame_index * 1_000,
        ),
        frame_writer=writer,
    )

    assert writer.written_frames == frames
    assert writer.released is True
    assert detector.seen_frames == [frames[0]]
    assert store.inserted_batches[0][0].evidence_uri == evidence_uri


def test_detection_preview_loop_draws_current_and_last_sampled_overlay() -> None:
    frames = [make_frame(), make_frame()]
    backend = CapturingPreviewBackend()
    store = FakeStore()
    overlay_inputs: list[list[str]] = []

    def render_overlay(frame: np.ndarray, detections: Sequence[DetectionCandidate]) -> np.ndarray:
        overlay_inputs.append([detection.class_name for detection in detections])
        rendered = frame.copy()
        rendered[0, 0] = [0, 255, 0]
        return rendered

    run_detection_preview_loop(
        capture=FakeCapture(frames=list(frames)),
        detector=FakeDetector([[make_candidate(confidence=0.9, class_name="person")]]),
        store=store,
        preview_backend=backend.as_backend(),
        source_name="camera",
        evidence_uri="file:///tmp/cereal.mp4",
        defaults=DetectionStreamDefaults(
            sample_interval_s=SAMPLE_INTERVAL_S,
            confidence_threshold=THRESHOLD,
        ),
        frame_time_provider=lambda frame_index: FrameTime(
            observed=None,
            media_ms=frame_index * 1_000,
        ),
        overlay_renderer=render_overlay,
    )

    assert int(backend.shown_frames[0].sum()) > 0
    assert int(backend.shown_frames[1].sum()) > 0
    assert overlay_inputs == [["person"], ["person"]]
    assert [[event.class_name for event in batch] for batch in store.inserted_batches] == [
        ["person"],
    ]


def test_detection_preview_loop_stores_overlay_sample_before_stop() -> None:
    backend = CapturingPreviewBackend(stop_after_show=True)
    store = FakeStore()

    def render_overlay(frame: np.ndarray, detections: Sequence[DetectionCandidate]) -> np.ndarray:
        del detections
        return frame.copy()

    run_detection_preview_loop(
        capture=FakeCapture(frames=[make_frame()]),
        detector=FakeDetector([[make_candidate(confidence=0.9, class_name="person")]]),
        store=store,
        preview_backend=backend.as_backend(),
        source_name="camera",
        evidence_uri="file:///tmp/cereal.mp4",
        defaults=DetectionStreamDefaults(
            sample_interval_s=SAMPLE_INTERVAL_S,
            confidence_threshold=THRESHOLD,
        ),
        frame_time_provider=lambda _frame_index: FrameTime(observed=None, media_ms=0),
        overlay_renderer=render_overlay,
    )

    assert [[event.class_name for event in batch] for batch in store.inserted_batches] == [
        ["person"],
    ]


def test_detection_preview_loop_keeps_raw_preview_without_overlay_renderer() -> None:
    backend = CapturingPreviewBackend()

    run_detection_preview_loop(
        capture=FakeCapture(frames=[make_frame(), make_frame()]),
        detector=FakeDetector([[make_candidate(confidence=0.9, class_name="person")]]),
        store=FakeStore(),
        preview_backend=backend.as_backend(),
        source_name="camera",
        evidence_uri="file:///tmp/cereal.mp4",
        defaults=DetectionStreamDefaults(
            sample_interval_s=SAMPLE_INTERVAL_S,
            confidence_threshold=THRESHOLD,
        ),
        frame_time_provider=lambda frame_index: FrameTime(
            observed=None,
            media_ms=frame_index * 1_000,
        ),
    )

    assert [int(frame.sum()) for frame in backend.shown_frames] == [0, 0]


def test_detection_stream_write_failure_skips_detection_and_store() -> None:
    writer = FakeWriter(write_error=RuntimeError("write failed"))
    detector = FakeDetector([[make_candidate(confidence=0.9)]])
    store = FakeStore()

    with pytest.raises(RuntimeError, match="write failed"):
        run_detection_stream(
            capture=FakeCapture(frames=[make_frame()]),
            detector=detector,
            store=store,
            source_name="camera",
            evidence_uri="file:///tmp/cereal.mp4",
            defaults=DetectionStreamDefaults(),
            frame_time_provider=lambda _frame_index: FrameTime(observed=None, media_ms=0),
            frame_writer=writer,
        )

    assert detector.seen_frames == []
    assert store.inserted_batches == []
    assert writer.released is True


def test_detection_stream_surfaces_writer_release_errors() -> None:
    writer = FakeWriter(release_error=RuntimeError("release failed"))

    with pytest.raises(RuntimeError, match="release failed"):
        run_detection_stream(
            capture=FakeCapture(frames=[make_frame()]),
            detector=FakeDetector([[]]),
            store=FakeStore(),
            source_name="camera",
            evidence_uri="file:///tmp/cereal.mp4",
            defaults=DetectionStreamDefaults(),
            frame_time_provider=lambda _frame_index: FrameTime(observed=None, media_ms=0),
            frame_writer=writer,
        )

    assert writer.released is True


def test_file_evidence_uri_uses_standard_file_uri(tmp_path: Path) -> None:
    artifact_path = tmp_path / "camera.mp4"

    assert file_evidence_uri(artifact_path) == artifact_path.resolve().as_uri()


@dataclass
class FakeCapture:
    frames: list[np.ndarray]
    released: bool = False

    def read(self) -> tuple[bool, object | None]:
        if not self.frames:
            return False, None
        return True, self.frames.pop(0)

    def release(self) -> None:
        self.released = True


@dataclass
class FakeDetector:
    detections: list[Sequence[DetectionCandidate]]
    seen_frames: list[object] = field(default_factory=list)
    model_name: str = "fake-model"

    def detect(self, frame: np.ndarray) -> Sequence[DetectionCandidate]:
        self.seen_frames.append(frame)
        return self.detections.pop(0)


@dataclass
class FakeStore:
    inserted_batches: list[list[DetectionEvent]] = field(default_factory=list)

    def insert_many(self, events: Sequence[DetectionEvent]) -> list[DetectionEvent]:
        batch = list(events)
        self.inserted_batches.append(batch)
        return batch

    def query(self, query: object) -> list[DetectionEvent]:
        del query
        return []

    def list_labels(self, query: DetectionLabelQuery) -> list[DetectionLabelCount]:
        del query
        return []

    def close(self) -> None:
        pass


@dataclass
class CapturingPreviewBackend:
    stop_after_show: bool = False
    shown_frames: list[np.ndarray] = field(default_factory=list)
    destroyed: bool = False

    def as_backend(self) -> PreviewBackend:
        return PreviewBackend(
            show_frame=lambda _window_name, frame: self.shown_frames.append(
                cast("np.ndarray", frame),
            ),
            should_stop=lambda _window_name, _delay_ms: self.stop_after_show,
            destroy_windows=self.destroy,
        )

    def destroy(self) -> None:
        self.destroyed = True


@dataclass
class FakeWriter:
    write_error: Exception | None = None
    release_error: Exception | None = None
    written_frames: list[object] = field(default_factory=list)
    released: bool = False

    def write(self, frame: object) -> None:
        if self.write_error is not None:
            raise self.write_error
        self.written_frames.append(frame)

    def release(self) -> None:
        self.released = True
        if self.release_error is not None:
            raise self.release_error


def make_candidate(*, confidence: float, class_name: str = "car") -> DetectionCandidate:
    return DetectionCandidate(
        class_id=1,
        class_name=class_name,
        confidence=confidence,
        bounding_box=BoundingBox(x1=1.0, y1=2.0, x2=3.0, y2=4.0),
        track_id=None,
    )


def make_frame() -> np.ndarray:
    return np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
