"""Detection lookup tools for specialized subagents."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from cereal.agents.tools import AgentToolCatalog
from cereal.detection.store import DetectionEventQuery, DetectionLabelQuery
from cereal.detection.tracks import build_object_tracks

if TYPE_CHECKING:
    from collections.abc import Callable

    from cereal.detection.store import DetectionStore
    from cereal.detection.tracks import ObjectTrack
    from cereal.detection.types import DetectionEvent

__all__ = [
    "DEFAULT_DETECTION_EVENT_LOOKUP_LIMIT",
    "DEFAULT_DETECTION_LABEL_LOOKUP_LIMIT",
    "DEFAULT_OBJECT_TRACK_LOOKUP_LIMIT",
    "DetectionLabelListResult",
    "DetectionLabelSummary",
    "DetectionLookupEvent",
    "DetectionLookupResult",
    "ObjectTrackCandidate",
    "ObjectTrackLookupResult",
    "make_detection_lookup_tool_catalog",
    "make_find_detection_events_tool",
    "make_list_detection_labels_tool",
    "make_lookup_object_tracks_tool",
]

DEFAULT_DETECTION_EVENT_LOOKUP_LIMIT = 20
DEFAULT_DETECTION_LABEL_LOOKUP_LIMIT = 50
DEFAULT_OBJECT_TRACK_LOOKUP_LIMIT = 20
FIND_DETECTION_EVENTS_TOOL = "find_detection_events"
LIST_DETECTION_LABELS_TOOL = "list_detection_labels"
LOOKUP_OBJECT_TRACKS_TOOL = "lookup_object_tracks"
OBJECT_TRACK_FOLLOW_UP_CAPABILITIES = (
    "retrieve_evidence_window",
    "validate_visual_claim",
    "compare_candidates",
)
OBJECT_TRACK_LOOKUP_UNCERTAINTY = (
    "Object tracks are query-local candidates. Untracked detections are linked by "
    "bounding-box overlap across adjacent sampled frames and may split or merge in "
    "crowded scenes; counts are not durable cross-run identities."
)


@dataclass(frozen=True)
class DetectionLookupEvent:
    """Serializable Detection event summary for agent tools."""

    source_name: str
    class_name: str
    confidence: float
    observed_time: str | None
    media_time_ms: int | None
    frame_index: int
    evidence_uri: str
    bounding_box: tuple[float, float, float, float]
    track_id: str | None

    @classmethod
    def from_event(cls, event: DetectionEvent) -> DetectionLookupEvent:
        """Create an agent-facing lookup event from a Detection event."""
        box = event.bounding_box
        return cls(
            source_name=event.source_name,
            class_name=event.class_name,
            confidence=event.confidence,
            observed_time=None if event.observed_time is None else event.observed_time.isoformat(),
            media_time_ms=event.media_time_ms,
            frame_index=event.frame_index,
            evidence_uri=event.evidence_uri,
            bounding_box=(box.x1, box.y1, box.x2, box.y2),
            track_id=event.track_id,
        )

    def to_dict(self) -> dict[str, object]:
        """Render as JSON-like data for agent tool return values."""
        return {
            "source_name": self.source_name,
            "class_name": self.class_name,
            "confidence": self.confidence,
            "observed_time": self.observed_time,
            "media_time_ms": self.media_time_ms,
            "frame_index": self.frame_index,
            "evidence_uri": self.evidence_uri,
            "bounding_box": list(self.bounding_box),
            "track_id": self.track_id,
        }


@dataclass(frozen=True)
class DetectionLookupResult:
    """Serializable Detection event lookup result for agent tools."""

    label: str
    event_count: int
    events: tuple[DetectionLookupEvent, ...]

    def to_dict(self) -> dict[str, object]:
        """Render as JSON-like data for agent tool return values."""
        return {
            "label": self.label,
            "event_count": self.event_count,
            "events": [event.to_dict() for event in self.events],
        }


@dataclass(frozen=True)
class DetectionLabelSummary:
    """Serializable detector-label count summary."""

    label: str
    event_count: int

    def to_dict(self) -> dict[str, object]:
        """Render as JSON-like data for agent tool return values."""
        return {
            "label": self.label,
            "event_count": self.event_count,
        }


@dataclass(frozen=True)
class DetectionLabelListResult:
    """Serializable detector-label discovery result."""

    labels: tuple[DetectionLabelSummary, ...]

    def to_dict(self) -> dict[str, object]:
        """Render as JSON-like data for agent tool return values."""
        return {"labels": [label.to_dict() for label in self.labels]}


@dataclass(frozen=True)
class ObjectTrackCandidate:
    """Serializable Object track candidate for agent planning."""

    track_id: str | None
    grouping_basis: str
    event_count: int
    frame_range: tuple[int, int]
    confidence_range: tuple[float, float]
    representative: DetectionLookupEvent

    @classmethod
    def from_track(cls, track: ObjectTrack) -> ObjectTrackCandidate:
        """Summarize one Object track without exposing raw Detection events."""
        confidences = [event.confidence for event in track.events]
        return cls(
            track_id=track.track_id,
            grouping_basis=_grouping_basis(track),
            event_count=len(track.events),
            frame_range=track.frame_range,
            confidence_range=(min(confidences), max(confidences)),
            representative=DetectionLookupEvent.from_event(track.representative),
        )

    def to_dict(self) -> dict[str, object]:
        """Render as JSON-like data for agent tool return values."""
        return {
            "track_id": self.track_id,
            "grouping_basis": self.grouping_basis,
            "event_count": self.event_count,
            "frame_range": list(self.frame_range),
            "confidence_range": list(self.confidence_range),
            "representative": self.representative.to_dict(),
        }


@dataclass(frozen=True)
class ObjectTrackLookupResult:
    """Serializable Object track lookup result for agent planning."""

    label: str
    track_count: int
    event_count: int
    grouping_bases: tuple[str, ...]
    candidates: tuple[ObjectTrackCandidate, ...]
    follow_up_capabilities: tuple[str, ...]
    uncertainty: str

    def to_dict(self) -> dict[str, object]:
        """Render as JSON-like data for agent tool return values."""
        return {
            "label": self.label,
            "track_count": self.track_count,
            "event_count": self.event_count,
            "grouping_bases": list(self.grouping_bases),
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "follow_up_capabilities": list(self.follow_up_capabilities),
            "uncertainty": self.uncertainty,
        }


def make_find_detection_events_tool(
    store: DetectionStore,
) -> Callable[..., dict[str, object]]:
    """Create a Detection event lookup tool bound to a Detection store."""

    def find_detection_events(  # noqa: PLR0913 - tool schema needs explicit args.
        label: str,
        source_name: str | None = None,
        observed_start: str | None = None,
        observed_end: str | None = None,
        media_start_ms: int | None = None,
        media_end_ms: int | None = None,
        min_confidence: float | None = None,
        limit: int = DEFAULT_DETECTION_EVENT_LOOKUP_LIMIT,
    ) -> dict[str, object]:
        """Find Detection events for one explicit detector label."""
        normalized_label = _require_label(label)
        events = store.query(
            DetectionEventQuery(
                source_name=source_name,
                class_name=normalized_label,
                observed_time_start=_parse_observed_time("observed_start", observed_start),
                observed_time_end=_parse_observed_time("observed_end", observed_end),
                media_time_start=media_start_ms,
                media_time_end=media_end_ms,
                min_confidence=min_confidence,
                limit=limit,
            ),
        )
        return DetectionLookupResult(
            label=normalized_label,
            event_count=len(events),
            events=tuple(DetectionLookupEvent.from_event(event) for event in events),
        ).to_dict()

    return find_detection_events


def make_lookup_object_tracks_tool(
    store: DetectionStore,
) -> Callable[..., dict[str, object]]:
    """Create an Object track lookup tool bound to a Detection store."""

    def lookup_object_tracks(  # noqa: PLR0913 - tool schema needs explicit args.
        label: str,
        source_name: str | None = None,
        observed_start: str | None = None,
        observed_end: str | None = None,
        media_start_ms: int | None = None,
        media_end_ms: int | None = None,
        min_confidence: float | None = None,
        limit: int = DEFAULT_OBJECT_TRACK_LOOKUP_LIMIT,
    ) -> dict[str, object]:
        """Group Detection events for one label into candidate Object tracks."""
        normalized_label = _require_label(label)
        events = store.query(
            DetectionEventQuery(
                source_name=source_name,
                class_name=normalized_label,
                observed_time_start=_parse_observed_time("observed_start", observed_start),
                observed_time_end=_parse_observed_time("observed_end", observed_end),
                media_time_start=media_start_ms,
                media_time_end=media_end_ms,
                min_confidence=min_confidence,
                limit=None,
            ),
        )
        tracks = build_object_tracks(events)
        candidates = sorted(
            (ObjectTrackCandidate.from_track(track) for track in tracks),
            key=lambda candidate: (
                -candidate.event_count,
                candidate.frame_range[0],
                candidate.track_id or "",
            ),
        )
        return ObjectTrackLookupResult(
            label=normalized_label,
            track_count=len(tracks),
            event_count=len(events),
            grouping_bases=tuple(sorted({candidate.grouping_basis for candidate in candidates})),
            candidates=tuple(candidates[:limit]),
            follow_up_capabilities=OBJECT_TRACK_FOLLOW_UP_CAPABILITIES,
            uncertainty=OBJECT_TRACK_LOOKUP_UNCERTAINTY,
        ).to_dict()

    return lookup_object_tracks


def make_detection_lookup_tool_catalog(store: DetectionStore) -> AgentToolCatalog:
    """Create a tool catalog for the Detection lookup subagent."""
    return AgentToolCatalog(
        {
            FIND_DETECTION_EVENTS_TOOL: make_find_detection_events_tool(store),
            LIST_DETECTION_LABELS_TOOL: make_list_detection_labels_tool(store),
            LOOKUP_OBJECT_TRACKS_TOOL: make_lookup_object_tracks_tool(store),
        },
    )


def _grouping_basis(track: ObjectTrack) -> str:
    if track.track_id is not None:
        return "detector_track_id"
    if len(track.events) > 1:
        return "linked_overlap"
    return "singleton"


def make_list_detection_labels_tool(
    store: DetectionStore,
) -> Callable[..., dict[str, object]]:
    """Create a detector-label discovery tool bound to a Detection store."""

    def list_detection_labels(  # noqa: PLR0913 - tool schema needs explicit args.
        source_name: str | None = None,
        observed_start: str | None = None,
        observed_end: str | None = None,
        media_start_ms: int | None = None,
        media_end_ms: int | None = None,
        min_confidence: float | None = None,
        limit: int = DEFAULT_DETECTION_LABEL_LOOKUP_LIMIT,
    ) -> dict[str, object]:
        """List detector labels and Detection event counts for a scope."""
        labels = store.list_labels(
            DetectionLabelQuery(
                source_name=source_name,
                observed_time_start=_parse_observed_time("observed_start", observed_start),
                observed_time_end=_parse_observed_time("observed_end", observed_end),
                media_time_start=media_start_ms,
                media_time_end=media_end_ms,
                min_confidence=min_confidence,
                limit=limit,
            ),
        )
        return DetectionLabelListResult(
            labels=tuple(
                DetectionLabelSummary(label=label.class_name, event_count=label.event_count)
                for label in labels
            ),
        ).to_dict()

    return list_detection_labels


def _require_label(label: str) -> str:
    normalized = label.strip()
    if not normalized:
        msg = "label must not be blank"
        raise ValueError(msg)
    return normalized


def _parse_observed_time(field_name: str, value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        msg = f"{field_name} must be an ISO-8601 datetime"
        raise ValueError(msg) from error
