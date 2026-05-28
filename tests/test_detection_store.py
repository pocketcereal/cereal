"""Tests for the Detection store port."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from cereal.detection.store import DetectionEventQuery, DetectionStore, SqliteDetectionStore
from cereal.detection.types import BoundingBox, DetectionEvent

if TYPE_CHECKING:
    from pathlib import Path

FRAME_HEIGHT = 1080
FRAME_WIDTH = 1920


def test_sqlite_detection_store_persists_and_queries_events(tmp_path: Path) -> None:
    store: DetectionStore = SqliteDetectionStore(tmp_path / "cereal.sqlite3")
    event = make_event(source_name="camera", class_name="car")

    try:
        inserted = store.insert_many([event])
        queried = store.query(DetectionEventQuery(source_name="camera", class_name="car"))
    finally:
        store.close()

    assert inserted == [event]
    assert queried == [event]


def test_sqlite_detection_store_allows_empty_insert(tmp_path: Path) -> None:
    store: DetectionStore = SqliteDetectionStore(tmp_path / "cereal.sqlite3")

    try:
        assert store.insert_many([]) == []
        assert store.query(DetectionEventQuery()) == []
    finally:
        store.close()


def test_sqlite_detection_store_creates_parent_directory(tmp_path: Path) -> None:
    database_path = tmp_path / "missing" / "nested" / "cereal.sqlite3"
    store: DetectionStore = SqliteDetectionStore(database_path)

    try:
        assert database_path.exists()
    finally:
        store.close()


def test_sqlite_detection_store_filters_by_time_and_confidence(tmp_path: Path) -> None:
    store: DetectionStore = SqliteDetectionStore(tmp_path / "cereal.sqlite3")
    base_time = datetime(2026, 5, 24, 12, 30, tzinfo=UTC)
    matching = make_event(
        source_name="camera",
        class_name="person",
        observed_time=base_time + timedelta(seconds=2),
        media_time_ms=2_000,
        confidence=0.9,
    )
    too_early = make_event(
        source_name="camera",
        class_name="person",
        observed_time=base_time,
        media_time_ms=0,
        confidence=0.9,
    )
    too_low_confidence = make_event(
        source_name="camera",
        class_name="person",
        observed_time=base_time + timedelta(seconds=3),
        media_time_ms=3_000,
        confidence=0.4,
    )

    try:
        store.insert_many([too_low_confidence, matching, too_early])

        queried = store.query(
            DetectionEventQuery(
                source_name="camera",
                class_name="person",
                observed_time_start=base_time + timedelta(seconds=1),
                observed_time_end=base_time + timedelta(seconds=4),
                min_confidence=0.5,
            ),
        )
    finally:
        store.close()

    assert queried == [matching]


def test_sqlite_detection_store_sorts_observed_time_queries_by_time_then_frame(
    tmp_path: Path,
) -> None:
    store: DetectionStore = SqliteDetectionStore(tmp_path / "cereal.sqlite3")
    observed_time = datetime(2026, 5, 24, 12, 30, tzinfo=UTC)
    frame_two = make_event(source_name="camera", frame_index=2, observed_time=observed_time)
    frame_one = make_event(source_name="camera", frame_index=1, observed_time=observed_time)

    try:
        store.insert_many([frame_two, frame_one])
        queried = store.query(DetectionEventQuery(observed_time_start=observed_time))
    finally:
        store.close()

    assert queried == [frame_one, frame_two]


def test_sqlite_detection_store_sorts_media_time_queries_by_time_then_frame(
    tmp_path: Path,
) -> None:
    store: DetectionStore = SqliteDetectionStore(tmp_path / "cereal.sqlite3")
    later = make_event(source_name="file", observed_time=None, media_time_ms=2_000, frame_index=1)
    earlier = make_event(source_name="file", observed_time=None, media_time_ms=1_000, frame_index=2)

    try:
        store.insert_many([later, earlier])
        queried = store.query(DetectionEventQuery(media_time_start=0))
    finally:
        store.close()

    assert queried == [earlier, later]


def test_sqlite_detection_store_respects_limit(tmp_path: Path) -> None:
    store: DetectionStore = SqliteDetectionStore(tmp_path / "cereal.sqlite3")
    first = make_event(source_name="camera", frame_index=1)
    second = make_event(source_name="camera", frame_index=2)

    try:
        store.insert_many([first, second])
        queried = store.query(DetectionEventQuery(limit=1))
    finally:
        store.close()

    assert queried == [first]


def test_sqlite_detection_store_records_schema_version(tmp_path: Path) -> None:
    store = SqliteDetectionStore(tmp_path / "cereal.sqlite3")

    try:
        version = store.connection.execute(
            "SELECT version FROM detection_schema_version"
        ).fetchone()
    finally:
        store.close()

    assert version == (1,)


def make_event(  # noqa: PLR0913 - test fixture exposes event fields under query.
    *,
    source_name: str,
    class_name: str = "car",
    observed_time: datetime | None = datetime(2026, 5, 24, 12, 30, tzinfo=UTC),
    media_time_ms: int | None = None,
    frame_index: int = 1,
    confidence: float = 0.75,
) -> DetectionEvent:
    return DetectionEvent(
        source_name=source_name,
        observed_time=observed_time,
        media_time_ms=media_time_ms,
        frame_index=frame_index,
        frame_width=FRAME_WIDTH,
        frame_height=FRAME_HEIGHT,
        evidence_uri="file:///tmp/cereal.mp4",
        model_name="test-model",
        class_id=2,
        class_name=class_name,
        confidence=confidence,
        bounding_box=BoundingBox(x1=1.0, y1=2.0, x2=30.0, y2=40.0),
        track_id=None,
    )
