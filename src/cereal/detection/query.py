"""Developer-facing Detection query helpers."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from cereal.detection.store import DetectionEventQuery, SqliteDetectionStore
from cereal.detection.tracks import build_object_tracks, summarize_object_tracks

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from datetime import datetime
    from pathlib import Path

    from cereal.detection.store import DetectionStore
    from cereal.detection.tracks import ObjectTrackSummary
    from cereal.detection.types import DetectionEvent
    from cereal.settings import Settings

__all__ = [
    "DEFAULT_DETECTION_QUERY_LIMIT",
    "DetectionQueryOptions",
    "render_detection_events_tsv",
    "render_object_track_summary_tsv",
    "run_detection_query",
    "run_object_track_query",
    "to_detection_event_query",
]

DEFAULT_DETECTION_QUERY_LIMIT = 20
DETECTION_QUERY_TSV_HEADER = (
    "source\tclass\tconfidence\tobserved_time\tmedia_time_ms\tframe_index\tbox_xyxy\tevidence_uri"
)
OBJECT_TRACK_SUMMARY_TSV_HEADER = "class\ttrack_count\tevent_count\tframe_start\tframe_end"


@dataclass(frozen=True)
class DetectionQueryOptions:
    """Filters for local Detection event inspection."""

    source_name: str | None = None
    class_name: str | None = None
    observed_time_start: datetime | None = None
    observed_time_end: datetime | None = None
    media_time_start: int | None = None
    media_time_end: int | None = None
    min_confidence: float | None = None
    limit: int = DEFAULT_DETECTION_QUERY_LIMIT

    def __post_init__(self) -> None:
        """Reject query values that can accidentally widen debug output."""
        if self.limit < 0:
            msg = "limit must be non-negative"
            raise ValueError(msg)


def run_detection_query(
    settings: Settings,
    options: DetectionQueryOptions,
    *,
    database_path: Path | None = None,
    store_factory: Callable[[Path], DetectionStore] = SqliteDetectionStore,
    write: Callable[[str], object] = print,
) -> int:
    """Print matching Detection events from the configured SQLite store."""
    from cereal.detection.runtime import default_detection_database_path  # noqa: PLC0415

    store = store_factory(database_path or default_detection_database_path(settings))
    try:
        events = store.query(to_detection_event_query(options))
    finally:
        store.close()

    write(render_detection_events_tsv(events))
    return 0


def run_object_track_query(
    settings: Settings,
    options: DetectionQueryOptions,
    *,
    database_path: Path | None = None,
    store_factory: Callable[[Path], DetectionStore] = SqliteDetectionStore,
    write: Callable[[str], object] = print,
) -> int:
    """Print per-class Object track counts derived from the configured store."""
    from cereal.detection.runtime import default_detection_database_path  # noqa: PLC0415

    store = store_factory(database_path or default_detection_database_path(settings))
    try:
        events = store.query(replace(to_detection_event_query(options), limit=None))
    finally:
        store.close()

    summaries = summarize_object_tracks(build_object_tracks(events))
    write(render_object_track_summary_tsv(summaries))
    return 0


def to_detection_event_query(options: DetectionQueryOptions) -> DetectionEventQuery:
    """Map CLI query options to the Detection store query contract."""
    return DetectionEventQuery(
        source_name=options.source_name,
        class_name=options.class_name,
        observed_time_start=options.observed_time_start,
        observed_time_end=options.observed_time_end,
        media_time_start=options.media_time_start,
        media_time_end=options.media_time_end,
        min_confidence=options.min_confidence,
        limit=options.limit,
    )


def render_detection_events_tsv(events: Iterable[DetectionEvent]) -> str:
    """Render Detection events as tab-separated rows for local debugging."""
    lines = [DETECTION_QUERY_TSV_HEADER]
    for event in events:
        box = event.bounding_box
        lines.append(
            "\t".join(
                [
                    event.source_name,
                    event.class_name,
                    f"{event.confidence:.3f}",
                    "" if event.observed_time is None else event.observed_time.isoformat(),
                    "" if event.media_time_ms is None else str(event.media_time_ms),
                    str(event.frame_index),
                    f"{box.x1:.1f},{box.y1:.1f},{box.x2:.1f},{box.y2:.1f}",
                    event.evidence_uri,
                ],
            ),
        )
    return "\n".join(lines)


def render_object_track_summary_tsv(summaries: Iterable[ObjectTrackSummary]) -> str:
    """Render per-class Object track counts as tab-separated rows."""
    lines = [OBJECT_TRACK_SUMMARY_TSV_HEADER]
    for summary in summaries:
        start, end = summary.frame_range
        lines.append(
            "\t".join(
                [
                    summary.class_name,
                    str(summary.track_count),
                    str(summary.event_count),
                    str(start),
                    str(end),
                ],
            ),
        )
    return "\n".join(lines)
