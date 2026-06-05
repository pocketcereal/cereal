"""Tests for the pure Object track builder."""

from __future__ import annotations

from cereal.detection.tracks import build_object_tracks, summarize_object_tracks
from cereal.detection.types import BoundingBox, DetectionEvent

SEPARATE_TRACK_COUNT = 2
LINKED_EVENT_COUNT = 2
NEAR_TIE_TRACK_COUNT = 3
CAR_EVENT_COUNT = 5
FIRST_EVENT_MEDIA_MS = 1000
LAST_EVENT_MEDIA_MS = 4000


def _event(  # noqa: PLR0913 - test factory exposes each Detection event field explicitly.
    *,
    frame_index: int,
    track_id: str | None,
    confidence: float = 0.5,
    source_name: str = "camera",
    class_name: str = "car",
    bounding_box: BoundingBox | None = None,
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
        bounding_box=bounding_box or BoundingBox(x1=1.0, y1=2.0, x2=30.0, y2=40.0),
        track_id=track_id,
    )


def _box(x1: float) -> BoundingBox:
    """Return a 10x10 box at a given x offset for overlap-control in tests."""
    return BoundingBox(x1=x1, y1=0.0, x2=x1 + 10.0, y2=10.0)


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


def test_summarize_counts_tracks_and_events_per_class() -> None:
    tracks = build_object_tracks(
        [
            _event(frame_index=1, track_id="1"),
            _event(frame_index=2, track_id="1"),
            _event(frame_index=3, track_id="1"),
            _event(frame_index=1, track_id="2"),
            _event(frame_index=2, track_id="2"),
        ],
    )

    summaries = summarize_object_tracks(tracks)

    assert len(summaries) == 1
    summary = summaries[0]
    assert summary.class_name == "car"
    assert summary.track_count == SEPARATE_TRACK_COUNT
    assert summary.event_count == CAR_EVENT_COUNT


def test_summarize_spans_frame_range_across_class_tracks() -> None:
    tracks = build_object_tracks(
        [
            _event(frame_index=2, track_id="1"),
            _event(frame_index=9, track_id="1"),
            _event(frame_index=4, track_id="2"),
        ],
    )

    summary = summarize_object_tracks(tracks)[0]

    assert summary.frame_range == (2, 9)


def test_summarize_keeps_classes_separate_and_ordered_by_track_count() -> None:
    tracks = build_object_tracks(
        [
            _event(frame_index=1, track_id="1", class_name="car"),
            _event(frame_index=1, track_id="2", class_name="car"),
            _event(frame_index=1, track_id="3", class_name="person"),
        ],
    )

    summaries = summarize_object_tracks(tracks)

    assert [summary.class_name for summary in summaries] == ["car", "person"]
    assert summaries[0].track_count == SEPARATE_TRACK_COUNT
    assert summaries[1].track_count == 1


def test_one_moving_untracked_object_links_into_one_track() -> None:
    first = _event(frame_index=1, track_id=None, bounding_box=_box(0.0))
    second = _event(frame_index=2, track_id=None, bounding_box=_box(1.0))
    third = _event(frame_index=3, track_id=None, bounding_box=_box(2.0))

    tracks = build_object_tracks([first, second, third])

    assert len(tracks) == 1
    assert tracks[0].events == (first, second, third)
    assert tracks[0].track_id is None


def test_two_separated_moving_objects_form_two_tracks() -> None:
    first_a = _event(frame_index=1, track_id=None, bounding_box=_box(0.0))
    second_a = _event(frame_index=2, track_id=None, bounding_box=_box(1.0))
    first_b = _event(frame_index=1, track_id=None, bounding_box=_box(500.0))
    second_b = _event(frame_index=2, track_id=None, bounding_box=_box(501.0))

    tracks = build_object_tracks([first_a, second_a, first_b, second_b])

    assert len(tracks) == SEPARATE_TRACK_COUNT
    assert all(len(track.events) == LINKED_EVENT_COUNT for track in tracks)


def test_low_overlap_untracked_events_do_not_link() -> None:
    first = _event(frame_index=1, track_id=None, bounding_box=_box(0.0))
    second = _event(
        frame_index=2,
        track_id=None,
        bounding_box=BoundingBox(x1=8.0, y1=0.0, x2=18.0, y2=10.0),
    )

    tracks = build_object_tracks([first, second])

    assert len(tracks) == SEPARATE_TRACK_COUNT


def test_one_missed_sampled_frame_still_links_within_gap() -> None:
    first = _event(frame_index=1, track_id=None, bounding_box=_box(0.0))
    other_class = _event(
        frame_index=2,
        track_id=None,
        class_name="person",
        bounding_box=_box(900.0),
    )
    later = _event(frame_index=3, track_id=None, bounding_box=_box(1.0))

    tracks = build_object_tracks([first, other_class, later])

    car_tracks = [track for track in tracks if track.class_name == "car"]
    assert len(car_tracks) == 1
    assert len(car_tracks[0].events) == LINKED_EVENT_COUNT


def test_two_missed_sampled_frames_split_into_two_tracks() -> None:
    first = _event(frame_index=1, track_id=None, bounding_box=_box(0.0))
    other_2 = _event(
        frame_index=2,
        track_id=None,
        class_name="person",
        bounding_box=_box(900.0),
    )
    other_3 = _event(
        frame_index=3,
        track_id=None,
        class_name="person",
        bounding_box=_box(901.0),
    )
    later = _event(frame_index=4, track_id=None, bounding_box=_box(1.0))

    tracks = build_object_tracks([first, other_2, other_3, later])

    car_tracks = [track for track in tracks if track.class_name == "car"]
    assert len(car_tracks) == SEPARATE_TRACK_COUNT


def test_near_tied_candidates_start_a_new_track() -> None:
    left = _event(frame_index=1, track_id=None, bounding_box=_box(0.0))
    right = _event(frame_index=1, track_id=None, bounding_box=_box(10.0))
    middle = _event(frame_index=2, track_id=None, bounding_box=_box(5.0))

    tracks = build_object_tracks([left, right, middle])

    assert len(tracks) == NEAR_TIE_TRACK_COUNT


def test_non_overlapping_untracked_events_stay_separate_tracks() -> None:
    first = _event(frame_index=1, track_id=None, bounding_box=_box(0.0))
    second = _event(frame_index=2, track_id=None, bounding_box=_box(500.0))

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
