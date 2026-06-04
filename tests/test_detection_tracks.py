"""Tests for the pure Object track builder."""

from __future__ import annotations

from cereal.detection.tracks import build_object_tracks
from cereal.detection.types import BoundingBox, DetectionEvent

SEPARATE_TRACK_COUNT = 2
FIRST_EVENT_MEDIA_MS = 1000
LAST_EVENT_MEDIA_MS = 4000


def _event(
    *,
    frame_index: int,
    track_id: str | None,
    confidence: float = 0.5,
    source_name: str = "camera",
    class_name: str = "car",
) -> DetectionEvent:
    """Build a Detection event with media-time ordering tied to the frame index."""
    return DetectionEvent(
        source_name=source_name,
        observed_time=None,
        media_time_ms=frame_index * 1000,
        frame_index=frame_index,
        frame_width=1920,
        frame_height=1080,
        evidence_uri="file:///tmp/cereal.mp4",
        model_name="test-model",
        class_id=2,
        class_name=class_name,
        confidence=confidence,
        bounding_box=BoundingBox(x1=1.0, y1=2.0, x2=30.0, y2=40.0),
        track_id=track_id,
    )


def test_events_with_same_track_id_group_into_one_track() -> None:
    first = _event(frame_index=1, track_id="7", confidence=0.6)
    second = _event(frame_index=2, track_id="7", confidence=0.9)

    tracks = build_object_tracks([first, second])

    assert len(tracks) == 1
    track = tracks[0]
    assert track.track_id == "7"
    assert track.source_name == "camera"
    assert track.class_name == "car"
    assert track.events == (first, second)


def test_track_list_order_is_independent_of_input_order() -> None:
    first = _event(frame_index=1, track_id="1")
    second = _event(frame_index=2, track_id="2")

    forward = build_object_tracks([first, second])
    reversed_input = build_object_tracks([second, first])

    assert [track.track_id for track in forward] == [track.track_id for track in reversed_input]


def test_track_events_are_ordered_chronologically() -> None:
    third = _event(frame_index=3, track_id="7")
    first = _event(frame_index=1, track_id="7")
    second = _event(frame_index=2, track_id="7")

    track = build_object_tracks([third, first, second])[0]

    assert track.events == (first, second, third)


def test_track_exposes_frame_and_time_ranges() -> None:
    first = _event(frame_index=1, track_id="7")
    last = _event(frame_index=4, track_id="7")

    track = build_object_tracks([last, first])[0]

    assert track.frame_range == (1, 4)
    start, end = track.time_range
    assert start.media_ms == FIRST_EVENT_MEDIA_MS
    assert end.media_ms == LAST_EVENT_MEDIA_MS


def test_representative_is_highest_confidence_event() -> None:
    low = _event(frame_index=1, track_id="7", confidence=0.4)
    high = _event(frame_index=2, track_id="7", confidence=0.95)
    mid = _event(frame_index=3, track_id="7", confidence=0.7)

    track = build_object_tracks([low, high, mid])[0]

    assert track.representative is high


def test_representative_ties_break_to_earliest_frame() -> None:
    later = _event(frame_index=5, track_id="7", confidence=0.8)
    earlier = _event(frame_index=2, track_id="7", confidence=0.8)

    track = build_object_tracks([later, earlier])[0]

    assert track.representative is earlier


def test_untracked_events_become_separate_singleton_tracks() -> None:
    first = _event(frame_index=1, track_id=None)
    second = _event(frame_index=2, track_id=None)

    tracks = build_object_tracks([first, second])

    assert len(tracks) == SEPARATE_TRACK_COUNT
    assert all(len(track.events) == 1 for track in tracks)
    assert all(track.track_id is None for track in tracks)


def test_same_track_id_in_different_sources_is_not_merged() -> None:
    first = _event(frame_index=1, track_id="7", source_name="camera-a")
    second = _event(frame_index=1, track_id="7", source_name="camera-b")

    tracks = build_object_tracks([first, second])

    assert len(tracks) == SEPARATE_TRACK_COUNT


def test_same_track_id_in_different_classes_is_not_merged() -> None:
    first = _event(frame_index=1, track_id="7", class_name="car")
    second = _event(frame_index=1, track_id="7", class_name="truck")

    tracks = build_object_tracks([first, second])

    assert len(tracks) == SEPARATE_TRACK_COUNT
