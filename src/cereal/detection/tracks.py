"""Pure Object track construction from Detection events."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from cereal.detection.types import FrameTime

if TYPE_CHECKING:
    from collections.abc import Sequence

    from cereal.detection.types import BoundingBox, DetectionEvent

__all__ = [
    "ObjectTrack",
    "ObjectTrackSummary",
    "build_object_tracks",
    "summarize_object_tracks",
]

DEFAULT_FRAME_GAP = 1
DEFAULT_IOU_THRESHOLD = 0.3
LINK_MARGIN = 0.05


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


@dataclass(frozen=True)
class ObjectTrackSummary:
    """Per-class Object track counts kept distinct from raw event counts."""

    class_name: str
    track_count: int
    event_count: int
    frame_range: tuple[int, int]


def summarize_object_tracks(tracks: Sequence[ObjectTrack]) -> list[ObjectTrackSummary]:
    """Aggregate Object tracks per class into track and event counts."""
    by_class: dict[str, list[ObjectTrack]] = {}
    for track in tracks:
        by_class.setdefault(track.class_name, []).append(track)

    summaries = [
        ObjectTrackSummary(
            class_name=class_name,
            track_count=len(class_tracks),
            event_count=sum(len(track.events) for track in class_tracks),
            frame_range=(
                min(track.frame_range[0] for track in class_tracks),
                max(track.frame_range[1] for track in class_tracks),
            ),
        )
        for class_name, class_tracks in by_class.items()
    ]
    summaries.sort(key=lambda summary: (-summary.track_count, summary.class_name))
    return summaries


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


def _iou(box_a: BoundingBox, box_b: BoundingBox) -> float:
    """Return the intersection-over-union of two pixel-space boxes."""
    inter_x1 = max(box_a.x1, box_b.x1)
    inter_y1 = max(box_a.y1, box_b.y1)
    inter_x2 = min(box_a.x2, box_b.x2)
    inter_y2 = min(box_a.y2, box_b.y2)
    inter = max(0.0, inter_x2 - inter_x1) * max(0.0, inter_y2 - inter_y1)
    if inter == 0.0:
        return 0.0
    area_a = (box_a.x2 - box_a.x1) * (box_a.y2 - box_a.y1)
    area_b = (box_b.x2 - box_b.x1) * (box_b.y2 - box_b.y1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def _source_frame_ranks(events: Sequence[DetectionEvent]) -> dict[str, dict[int, int]]:
    """Rank each source's sampled frame indices so gaps mean missed sampled frames."""
    frames_by_source: dict[str, set[int]] = {}
    for event in events:
        frames_by_source.setdefault(event.source_name, set()).add(event.frame_index)
    return {
        source: {frame: rank for rank, frame in enumerate(sorted(frames))}
        for source, frames in frames_by_source.items()
    }


def _best_open_track(
    event: DetectionEvent,
    open_tracks: list[list[DetectionEvent]],
    rank: dict[int, int],
    frame_gap: int,
    iou_threshold: float,
) -> list[DetectionEvent] | None:
    """Pick the open track to extend, or None to start a new one."""
    scored: list[tuple[float, list[DetectionEvent]]] = []
    for track in open_tracks:
        last = track[-1]
        sampled_gap = rank[event.frame_index] - rank[last.frame_index]
        if sampled_gap < 1 or sampled_gap > frame_gap + 1:
            continue
        score = _iou(event.bounding_box, last.bounding_box)
        if score >= iou_threshold:
            scored.append((score, track))
    if not scored:
        return None
    scored.sort(key=lambda item: item[0], reverse=True)
    if len(scored) == 1:
        return scored[0][1]
    if scored[0][0] - scored[1][0] >= LINK_MARGIN:
        return scored[0][1]
    return None


def _link_untracked(
    untracked: Sequence[DetectionEvent],
    ranks: dict[str, dict[int, int]],
    frame_gap: int,
    iou_threshold: float,
) -> list[list[DetectionEvent]]:
    """Link untracked events into candidate tracks by adjacency and box overlap."""
    groups: dict[tuple[str, str], list[DetectionEvent]] = {}
    for event in untracked:
        groups.setdefault((event.source_name, event.class_name), []).append(event)

    member_lists: list[list[DetectionEvent]] = []
    for (source_name, _class_name), members in groups.items():
        rank = ranks[source_name]
        open_tracks: list[list[DetectionEvent]] = []
        for event in sorted(members, key=_chronological_key):
            best = _best_open_track(event, open_tracks, rank, frame_gap, iou_threshold)
            if best is None:
                new_track = [event]
                open_tracks.append(new_track)
                member_lists.append(new_track)
            else:
                best.append(event)
    return member_lists


def build_object_tracks(
    events: Sequence[DetectionEvent],
    *,
    frame_gap: int = DEFAULT_FRAME_GAP,
    iou_threshold: float = DEFAULT_IOU_THRESHOLD,
) -> list[ObjectTrack]:
    """Group Detection events into Object tracks by track id or overlap linking."""
    grouped: dict[tuple[str, str, str], list[DetectionEvent]] = {}
    untracked: list[DetectionEvent] = []
    for event in events:
        if event.track_id is None:
            untracked.append(event)
            continue
        key = (event.source_name, event.class_name, event.track_id)
        grouped.setdefault(key, []).append(event)

    tracks = [
        _make_track(source_name, class_name, track_id, members)
        for (source_name, class_name, track_id), members in grouped.items()
    ]
    ranks = _source_frame_ranks(events)
    tracks.extend(
        _make_track(members[0].source_name, members[0].class_name, None, members)
        for members in _link_untracked(untracked, ranks, frame_gap, iou_threshold)
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
