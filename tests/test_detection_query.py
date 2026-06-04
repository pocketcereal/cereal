"""Tests for developer-facing Detection query helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest

from cereal.detection.query import (
    DetectionQueryOptions,
    render_detection_events_tsv,
    run_detection_query,
    run_object_track_query,
    to_detection_event_query,
)
from cereal.detection.store import SqliteDetectionStore
from cereal.detection.types import BoundingBox, DetectionEvent
from cereal.settings import load_settings
from tests.helpers import write_config

if TYPE_CHECKING:
    from pathlib import Path

FRAME_HEIGHT = 1080
FRAME_WIDTH = 1920
MEDIA_TIME_START_MS = 1_000
MIN_CONFIDENCE = 0.8
QUERY_LIMIT = 5


def test_detection_query_options_map_to_store_query() -> None:
    observed_start = datetime(2026, 5, 24, 12, tzinfo=UTC)
    options = DetectionQueryOptions(
        source_name="camera",
        class_name="person",
        observed_time_start=observed_start,
        media_time_start=MEDIA_TIME_START_MS,
        min_confidence=MIN_CONFIDENCE,
        limit=QUERY_LIMIT,
    )

    query = to_detection_event_query(options)

    assert query.source_name == "camera"
    assert query.class_name == "person"
    assert query.observed_time_start == observed_start
    assert query.media_time_start == MEDIA_TIME_START_MS
    assert query.min_confidence == MIN_CONFIDENCE
    assert query.limit == QUERY_LIMIT


def test_detection_query_options_reject_negative_limit() -> None:
    with pytest.raises(ValueError, match="limit must be non-negative"):
        DetectionQueryOptions(limit=-1)


def test_render_detection_events_tsv_includes_stable_detection_fields() -> None:
    rendered = render_detection_events_tsv([make_event()])

    assert rendered.splitlines()[0].split("\t") == [
        "source",
        "class",
        "confidence",
        "observed_time",
        "media_time_ms",
        "frame_index",
        "box_xyxy",
        "evidence_uri",
    ]
    assert "camera\tperson\t0.875" in rendered
    assert "1.0,2.0,30.0,40.0" in rendered


def test_run_detection_query_reads_configured_store_and_writes_tsv(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yaml"
    storage_path = tmp_path / "storage"
    database_path = storage_path / "cereal.sqlite3"
    write_config(config_path, storage=storage_path)
    store = SqliteDetectionStore(database_path)
    try:
        store.insert_many([make_event(class_name="person"), make_event(class_name="car")])
    finally:
        store.close()
    output: list[str] = []

    assert (
        run_detection_query(
            settings=load_settings(config_path),
            options=DetectionQueryOptions(class_name="person"),
            write=output.append,
        )
        == 0
    )

    assert len(output) == 1
    assert "camera\tperson\t0.875" in output[0]
    assert "camera\tcar\t0.875" not in output[0]


def test_run_object_track_query_counts_fewer_tracks_than_events(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yaml"
    storage_path = tmp_path / "storage"
    database_path = storage_path / "cereal.sqlite3"
    write_config(config_path, storage=storage_path)
    store = SqliteDetectionStore(database_path)
    try:
        store.insert_many(
            [
                make_event(class_name="car", frame_index=1, track_id="1"),
                make_event(class_name="car", frame_index=2, track_id="1"),
                make_event(class_name="car", frame_index=3, track_id="1"),
            ],
        )
    finally:
        store.close()
    output: list[str] = []

    assert (
        run_object_track_query(
            settings=load_settings(config_path),
            options=DetectionQueryOptions(class_name="car"),
            write=output.append,
        )
        == 0
    )

    assert len(output) == 1
    assert "car\t1\t3" in output[0]


def make_event(
    *,
    class_name: str = "person",
    frame_index: int = 7,
    track_id: str | None = None,
) -> DetectionEvent:
    return DetectionEvent(
        source_name="camera",
        observed_time=datetime(2026, 5, 24, 12, 30, tzinfo=UTC),
        media_time_ms=None,
        frame_index=frame_index,
        frame_width=FRAME_WIDTH,
        frame_height=FRAME_HEIGHT,
        evidence_uri="file:///tmp/cereal.mp4",
        model_name="test-model",
        class_id=1,
        class_name=class_name,
        confidence=0.875,
        bounding_box=BoundingBox(x1=1.0, y1=2.0, x2=30.0, y2=40.0),
        track_id=track_id,
    )
