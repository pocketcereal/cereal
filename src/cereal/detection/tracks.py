"""Pure Object track construction from Detection events."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from cereal.detection.types import FrameTime

if TYPE_CHECKING:
    from collections.abc import Sequence

    from cereal.detection.types import DetectionEvent

__all__ = ["ObjectTrack", "build_object_tracks"]


@dataclass(frozen=True)
class ObjectTrack:
    """A query-local group of Detection events for one candidate physical object."""

    source_name: str
    class_name: str
    track_id: str | None
    events: tuple[DetectionEvent, ...]
    representative: DetectionEvent

    @property
    def frame_range(self) -> tuple[int, int]:
        """Return the first and last frame index spanned by the track."""
        return (self.events[0].frame_index, self.events[-1].frame_index)

    @property
    def time_range(self) -> tuple[FrameTime, FrameTime]:
        """Return the frame time of the first and last event in the track."""
        return (_frame_time(self.events[0]), _frame_time(self.events[-1]))


def _chronological_key(event: DetectionEvent) -> tuple[int, int, float]:
    """Order events within a track deterministically by frame then time."""
    media = event.media_time_ms if event.media_time_ms is not None else 0
    observed = event.observed_time.timestamp() if event.observed_time is not None else 0.0
    return (event.frame_index, media, observed)


def _frame_time(event: DetectionEvent) -> FrameTime:
    """Recover the frame time carried by one Detection event."""
    return FrameTime(observed=event.observed_time, media_ms=event.media_time_ms)


def _make_track(
    source_name: str,
    class_name: str,
    track_id: str | None,
    members: Sequence[DetectionEvent],
) -> ObjectTrack:
    """Build one Object track with the highest-confidence representative event."""
    ordered = sorted(members, key=_chronological_key)
    representative = min(
        ordered,
        key=lambda event: (-event.confidence, _chronological_key(event)),
    )
    return ObjectTrack(
        source_name=source_name,
        class_name=class_name,
        track_id=track_id,
        events=tuple(ordered),
        representative=representative,
    )


def build_object_tracks(events: Sequence[DetectionEvent]) -> list[ObjectTrack]:
    """Group Detection events into Object tracks by source, class, and track id."""
    grouped: dict[tuple[str, str, str], list[DetectionEvent]] = {}
    singletons: list[DetectionEvent] = []
    for event in events:
        if event.track_id is None:
            singletons.append(event)
            continue
        key = (event.source_name, event.class_name, event.track_id)
        grouped.setdefault(key, []).append(event)

    tracks = [
        _make_track(source_name, class_name, track_id, members)
        for (source_name, class_name, track_id), members in grouped.items()
    ]
    tracks.extend(
        _make_track(event.source_name, event.class_name, None, [event])
        for event in singletons
    )
    tracks.sort(key=_track_order_key)
    return tracks


def _track_order_key(track: ObjectTrack) -> tuple[str, str, tuple[int, int, float], str]:
    """Order tracks deterministically regardless of input event order."""
    first = track.events[0]
    return (
        track.source_name,
        track.class_name,
        _chronological_key(first),
        track.track_id or "",
    )
