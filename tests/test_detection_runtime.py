"""Tests for prototype Detection runtime composition."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import numpy as np
import pytest

from cereal.detection.runtime import default_detection_database_path, run_detection_preview
from cereal.detection.store import (
    DetectionEventQuery,
    SqliteDetectionStore,
)
from cereal.detection.types import (
    BoundingBox,
    DetectionCandidate,
    DetectionEvent,
    DetectionStreamDefaults,
)
from cereal.media.adapters import SourceAdapterRegistry
from cereal.media.preview import PreviewBackend
from cereal.media.recording import WriterContext, recording_artifact_path
from cereal.settings import load_settings
from tests.helpers import write_config, write_static_video

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from cereal.detection.store import DetectionLabelCount, DetectionLabelQuery
    from cereal.settings import SourceSettings

FRAME_HEIGHT = 24
FRAME_WIDTH = 32
THRESHOLD = 0.5
MEDIA_TIME_MS = 1234


def test_detection_database_path_defaults_under_storage(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yaml"
    write_config(config_path, storage=tmp_path / "storage")

    assert default_detection_database_path(load_settings(config_path)) == (
        tmp_path / "storage" / "cereal.sqlite3"
    )


def test_run_detection_preview_composes_device_source_with_evidence_and_preview(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "settings.yaml"
    write_config(
        config_path,
        storage=tmp_path / "storage",
        sources=(("camera", "device:0", "true"),),
    )
    settings = load_settings(config_path)
    frames = [make_frame(), make_frame()]
    capture = FakeCapture(frames=list(frames))
    adapter = FakeAdapter(capture=capture)
    detector = FakeDetector([[make_candidate(class_name="person")]])
    store = FakeStore()
    backend = FakePreviewBackend()
    writer_paths: list[Path] = []
    writer = FakeWriter()
    recorded_at = datetime(2026, 5, 24, 12, 30, tzinfo=UTC)
    frame_zero_time = recorded_at + timedelta(seconds=1)
    frame_one_time = recorded_at + timedelta(seconds=2)
    clock_values = iter([recorded_at, frame_zero_time, frame_one_time])

    run_detection_preview(
        settings,
        registry=SourceAdapterRegistry({"device": adapter}),
        backend=backend.as_backend(),
        detector=detector,
        store=store,
        writer_factory=lambda artifact_path, _writer_context: (
            writer_paths.append(artifact_path) or writer
        ),
        clock=lambda: next(clock_values),
        defaults=DetectionStreamDefaults(sample_interval_s=3.0, confidence_threshold=THRESHOLD),
    )

    expected_artifact = recording_artifact_path(
        storage_root=settings.storage,
        source_name="camera",
        recorded_at=recorded_at,
        writer_context=WriterContext(),
    )
    assert adapter.opened_sources == ["camera"]
    assert writer_paths == [expected_artifact]
    assert writer.written_frames == frames
    assert backend.shown_frames == frames
    assert len(detector.seen_frames) == 1
    assert store.inserted_batches[0][0].source_name == "camera"
    assert store.inserted_batches[0][0].observed_time == frame_zero_time
    assert store.inserted_batches[0][0].evidence_uri == expected_artifact.resolve().as_uri()
    assert capture.released is True
    assert writer.released is True
    assert backend.destroyed is True
    assert store.closed is True


def test_run_detection_preview_rejects_device_source_without_write_enabled(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "settings.yaml"
    write_config(
        config_path,
        storage=tmp_path / "storage",
        source_name="camera",
        source_uri="device:0",
    )
    capture = FakeCapture(frames=[])
    store = FakeStore()

    with pytest.raises(RuntimeError, match="requires write: true"):
        run_detection_preview(
            load_settings(config_path),
            registry=SourceAdapterRegistry({"device": FakeAdapter(capture=capture)}),
            backend=FakePreviewBackend().as_backend(),
            detector=FakeDetector([]),
            store=store,
            writer_factory=raise_unexpected_writer,
            clock=lambda: datetime(2026, 5, 24, 12, 30, tzinfo=UTC),
        )

    assert capture.released is True
    assert store.closed is True


def test_run_detection_preview_uses_file_source_as_evidence_without_writer(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "sample.mp4"
    config_path = tmp_path / "settings.yaml"
    write_config(
        config_path,
        storage=tmp_path / "storage",
        source_uri=source_file.as_uri(),
    )
    capture = FakeCapture(frames=[make_frame()], media_times_ms=[float(MEDIA_TIME_MS)])
    adapter = FakeAdapter(capture=capture)
    store = FakeStore()

    run_detection_preview(
        load_settings(config_path),
        registry=SourceAdapterRegistry({"file": adapter}),
        backend=FakePreviewBackend().as_backend(),
        detector=FakeDetector([[make_candidate(class_name="car")]]),
        store=store,
        writer_factory=raise_unexpected_writer,
        defaults=DetectionStreamDefaults(sample_interval_s=3.0, confidence_threshold=THRESHOLD),
    )

    event = store.inserted_batches[0][0]
    assert event.evidence_uri == source_file.as_uri()
    assert event.media_time_ms == MEDIA_TIME_MS
    assert event.observed_time is None


def test_run_detection_preview_can_run_file_source_without_preview_backend(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "sample.mp4"
    config_path = tmp_path / "settings.yaml"
    write_config(
        config_path,
        storage=tmp_path / "storage",
        source_uri=source_file.as_uri(),
    )
    capture = FakeCapture(frames=[make_frame()], media_times_ms=[float(MEDIA_TIME_MS)])
    store = FakeStore()

    run_detection_preview(
        load_settings(config_path),
        registry=SourceAdapterRegistry({"file": FakeAdapter(capture=capture)}),
        backend=raise_unexpected_backend(),
        detector=FakeDetector([[make_candidate(class_name="car")]]),
        store=store,
        writer_factory=raise_unexpected_writer,
        defaults=DetectionStreamDefaults(sample_interval_s=3.0, confidence_threshold=THRESHOLD),
        preview_enabled=False,
    )

    event = store.inserted_batches[0][0]
    assert event.evidence_uri == source_file.as_uri()
    assert event.media_time_ms == MEDIA_TIME_MS
    assert capture.released is True
    assert store.closed is True


def test_run_detection_preview_headless_reads_static_file_and_writes_sqlite(
    tmp_path: Path,
) -> None:
    cv2 = pytest.importorskip("cv2")
    source_file = tmp_path / "sample.avi"
    write_static_video(source_file, width=FRAME_WIDTH, height=FRAME_HEIGHT)
    config_path = tmp_path / "settings.yaml"
    database_path = tmp_path / "detections.sqlite3"
    write_config(
        config_path,
        storage=tmp_path / "storage",
        source_uri=source_file.as_uri(),
    )

    run_detection_preview(
        load_settings(config_path),
        capture_factory=cv2.VideoCapture,
        detector=FakeDetector([[make_candidate(class_name="car")]]),
        defaults=DetectionStreamDefaults(sample_interval_s=0, confidence_threshold=THRESHOLD),
        database_path=database_path,
        preview_enabled=False,
    )

    store = SqliteDetectionStore(database_path)
    try:
        events = store.query(DetectionEventQuery(source_name="sample", class_name="car"))
    finally:
        store.close()

    assert len(events) == 1
    assert events[0].evidence_uri == source_file.as_uri()
    assert events[0].frame_width == FRAME_WIDTH
    assert events[0].frame_height == FRAME_HEIGHT


def test_run_detection_preview_creates_store_at_injected_database_path(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yaml"
    write_config(
        config_path,
        storage=tmp_path / "storage",
        sources=(("sample", "device:0", "true"),),
    )
    database_path = tmp_path / "custom.sqlite3"
    store_paths: list[Path] = []
    store = FakeStore()

    run_detection_preview(
        load_settings(config_path),
        registry=SourceAdapterRegistry({"device": FakeAdapter(capture=FakeCapture(frames=[]))}),
        backend=FakePreviewBackend().as_backend(),
        detector=FakeDetector([]),
        store_factory=lambda path: store_paths.append(path) or store,
        writer_factory=lambda _artifact_path, _writer_context: FakeWriter(),
        clock=lambda: datetime(2026, 5, 24, 12, 30, tzinfo=UTC),
        database_path=database_path,
    )

    assert store_paths == [database_path]
    assert store.closed is True


def test_run_detection_preview_stops_when_preview_requests_stop(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yaml"
    write_config(
        config_path,
        storage=tmp_path / "storage",
        sources=(("sample", "device:0", "true"),),
    )
    detector = FakeDetector([[make_candidate(class_name="person")]])

    run_detection_preview(
        load_settings(config_path),
        registry=SourceAdapterRegistry(
            {"device": FakeAdapter(capture=FakeCapture(frames=[make_frame()]))}
        ),
        backend=FakePreviewBackend(stop_after_show=True).as_backend(),
        detector=detector,
        store=FakeStore(),
        writer_factory=lambda _artifact_path, _writer_context: FakeWriter(),
        clock=lambda: datetime(2026, 5, 24, 12, 30, tzinfo=UTC),
    )

    assert detector.seen_frames == []


def test_run_detection_preview_closes_store_when_source_open_fails(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yaml"
    write_config(config_path, storage=tmp_path / "storage", source_uri="device:0")
    store = FakeStore()

    with pytest.raises(RuntimeError, match="open failed"):
        run_detection_preview(
            load_settings(config_path),
            registry=SourceAdapterRegistry(
                {"device": RaisingAdapter(error=RuntimeError("open failed"))}
            ),
            backend=FakePreviewBackend().as_backend(),
            detector=FakeDetector([]),
            store=store,
            writer_factory=lambda _artifact_path, _writer_context: FakeWriter(),
            clock=lambda: datetime(2026, 5, 24, 12, 30, tzinfo=UTC),
        )

    assert store.closed is True


def test_run_detection_preview_releases_capture_when_writer_creation_fails(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "settings.yaml"
    write_config(
        config_path,
        storage=tmp_path / "storage",
        sources=(("sample", "device:0", "true"),),
    )
    capture = FakeCapture(frames=[])
    store = FakeStore()

    def fail_writer(_artifact_path: Path, _writer_context: WriterContext) -> FakeWriter:
        msg = "writer failed"
        raise RuntimeError(msg)

    with pytest.raises(RuntimeError, match="writer failed"):
        run_detection_preview(
            load_settings(config_path),
            registry=SourceAdapterRegistry({"device": FakeAdapter(capture=capture)}),
            backend=FakePreviewBackend().as_backend(),
            detector=FakeDetector([]),
            store=store,
            writer_factory=fail_writer,
            clock=lambda: datetime(2026, 5, 24, 12, 30, tzinfo=UTC),
        )

    assert capture.released is True
    assert store.closed is True


@dataclass
class FakeCapture:
    frames: list[np.ndarray]
    media_times_ms: list[float] = field(default_factory=list)
    released: bool = False

    def read(self) -> tuple[bool, object | None]:
        if not self.frames:
            return False, None
        return True, self.frames.pop(0)

    def get(self, _property_id: int) -> float:
        return self.media_times_ms.pop(0)

    def release(self) -> None:
        self.released = True


@dataclass
class FakeAdapter:
    capture: FakeCapture
    opened_sources: list[str] = field(default_factory=list)

    def open(self, source: SourceSettings) -> FakeCapture:
        self.opened_sources.append(source.name)
        return self.capture


@dataclass(frozen=True)
class RaisingAdapter:
    error: Exception

    def open(self, source: SourceSettings) -> FakeCapture:
        del source
        raise self.error


@dataclass
class FakePreviewBackend:
    stop_after_show: bool = False
    shown_frames: list[object] = field(default_factory=list)
    destroyed: bool = False

    def as_backend(self) -> PreviewBackend:
        return PreviewBackend(
            show_frame=lambda _window_name, frame: self.shown_frames.append(frame),
            should_stop=lambda _window_name, _delay_ms: self.stop_after_show,
            destroy_windows=self.destroy,
        )

    def destroy(self) -> None:
        self.destroyed = True


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
    closed: bool = False

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
        self.closed = True


@dataclass
class FakeWriter:
    written_frames: list[object] = field(default_factory=list)
    released: bool = False

    def write(self, frame: object) -> None:
        self.written_frames.append(frame)

    def release(self) -> None:
        self.released = True


def make_candidate(*, class_name: str) -> DetectionCandidate:
    return DetectionCandidate(
        class_id=1,
        class_name=class_name,
        confidence=0.9,
        bounding_box=BoundingBox(x1=1.0, y1=2.0, x2=3.0, y2=4.0),
        track_id=None,
    )


def make_frame() -> np.ndarray:
    return np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)


def raise_unexpected_writer(
    _artifact_path: Path,
    _writer_context: WriterContext,
) -> FakeWriter:
    msg = "writer factory should not be called"
    raise AssertionError(msg)


def raise_unexpected_backend() -> PreviewBackend:
    return PreviewBackend(
        show_frame=raise_unexpected_show_frame,
        should_stop=lambda _window_name, _delay_ms: raise_unexpected_preview(),
        destroy_windows=raise_unexpected_destroy_windows,
    )


def raise_unexpected_show_frame(_window_name: str, _frame: object) -> None:
    msg = "preview backend should not be called"
    raise AssertionError(msg)


def raise_unexpected_destroy_windows() -> None:
    msg = "preview backend should not be called"
    raise AssertionError(msg)


def raise_unexpected_preview() -> bool:
    msg = "preview backend should not be called"
    raise AssertionError(msg)
