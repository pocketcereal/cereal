"""Tests for Detection domain value types."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from cereal.detection.types import (
    BoundingBox,
    DetectionCandidate,
    DetectionStreamDefaults,
    FrameTime,
    to_detection_events,
)

DEFAULT_CONFIDENCE_THRESHOLD = 0.5
DEFAULT_SAMPLE_INTERVAL_S = 3.0


def test_detection_stream_defaults_use_prototype_values() -> None:
    defaults = DetectionStreamDefaults()

    assert defaults.sample_interval_s == DEFAULT_SAMPLE_INTERVAL_S
    assert defaults.confidence_threshold == DEFAULT_CONFIDENCE_THRESHOLD


def test_bounding_box_rejects_inverted_coordinates() -> None:
    with pytest.raises(ValueError, match="x1 must be less than or equal to x2"):
        BoundingBox(x1=10.0, y1=1.0, x2=9.0, y2=2.0)

    with pytest.raises(ValueError, match="y1 must be less than or equal to y2"):
        BoundingBox(x1=1.0, y1=10.0, x2=2.0, y2=9.0)


def test_frame_time_requires_observed_or_media_time() -> None:
    with pytest.raises(ValueError, match="at least one"):
        FrameTime(observed=None, media_ms=None)


def test_candidates_convert_to_detection_events_with_explicit_context() -> None:
    observed = datetime(2026, 5, 24, 12, 30, tzinfo=UTC)
    frame_index = 11
    frame_width = 1920
    frame_height = 1080
    media_time_ms = 1234
    candidate = DetectionCandidate(
        class_id=2,
        class_name="car",
        confidence=0.75,
        bounding_box=BoundingBox(x1=1.0, y1=2.0, x2=30.0, y2=40.0),
        track_id="7",
    )

    events = to_detection_events(
        candidates=[candidate],
        source_name="camera",
        frame_index=frame_index,
        frame_width=frame_width,
        frame_height=frame_height,
        frame_time=FrameTime(observed=observed, media_ms=media_time_ms),
        evidence_uri="file:///tmp/cereal.mp4",
        model_name="test-model",
    )

    assert len(events) == 1
    event = events[0]
    assert event.source_name == "camera"
    assert event.observed_time == observed
    assert event.media_time_ms == media_time_ms
    assert event.frame_index == frame_index
    assert event.frame_width == frame_width
    assert event.frame_height == frame_height
    assert event.evidence_uri == "file:///tmp/cereal.mp4"
    assert event.model_name == "test-model"
    assert event.class_id == candidate.class_id
    assert event.class_name == candidate.class_name
    assert event.confidence == candidate.confidence
    assert event.bounding_box == candidate.bounding_box
    assert event.track_id == "7"


def test_detection_event_conversion_rejects_invalid_frame_size() -> None:
    candidate = DetectionCandidate(
        class_id=2,
        class_name="car",
        confidence=0.75,
        bounding_box=BoundingBox(x1=1.0, y1=2.0, x2=30.0, y2=40.0),
        track_id=None,
    )

    with pytest.raises(ValueError, match="frame_width must be positive"):
        to_detection_events(
            candidates=[candidate],
            source_name="camera",
            frame_index=11,
            frame_width=0,
            frame_height=1080,
            frame_time=FrameTime(observed=None, media_ms=1234),
            evidence_uri="file:///tmp/cereal.mp4",
            model_name="test-model",
        )
