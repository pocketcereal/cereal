"""Agent-facing Evidence data tools."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import TYPE_CHECKING, cast

from cereal.detection.types import BoundingBox, DetectionEvent
from cereal.evidence.retrieval import retrieve_evidence_window
from cereal.evidence.types import EvidenceWindow, EvidenceWindowRequest

if TYPE_CHECKING:
    from collections.abc import Callable, MutableMapping

    from cereal.evidence.retrieval import EvidenceFrameReader

__all__ = ["make_retrieve_evidence_window_tool"]

DEFAULT_REFERENCE_MEDIA_TIME_MS = 0


def make_retrieve_evidence_window_tool(
    *,
    reader: EvidenceFrameReader,
    evidence_windows: MutableMapping[str, EvidenceWindow],
) -> Callable[..., dict[str, object]]:
    """Create an Evidence window retrieval tool for agent harnesses."""

    def retrieve_evidence_window_tool(
        detection_event_ref: dict[str, object],
        frame_radius: int = 1,
    ) -> dict[str, object]:
        """Retrieve Evidence frames for one event from find_detection_events."""
        event = _event_from_ref(detection_event_ref)
        window = retrieve_evidence_window(
            EvidenceWindowRequest(event=event, radius_frames=frame_radius),
            reader,
        )
        evidence_window_ref = _evidence_window_ref(event)
        evidence_windows[evidence_window_ref] = window
        return {
            "evidence_window_ref": evidence_window_ref,
            "source_name": event.source_name,
            "center_frame_index": window.center_frame_index,
            "frame_count": len(window.frames),
            "target": {
                "class_name": window.target.class_name,
                "confidence": window.target.confidence,
                "bounding_box": [
                    window.target.bounding_box.x1,
                    window.target.bounding_box.y1,
                    window.target.bounding_box.x2,
                    window.target.bounding_box.y2,
                ],
            },
            "evidence_uri": window.evidence_uri,
        }

    retrieve_evidence_window_tool.__name__ = "retrieve_evidence_window"
    return retrieve_evidence_window_tool


def _event_from_ref(reference: dict[str, object]) -> DetectionEvent:
    event_reference = _unwrap_event_reference(reference)
    bounding_box = _bounding_box(event_reference.get("bounding_box", [0, 0, 1, 1]))
    observed_time = _optional_datetime(event_reference.get("observed_time"))
    media_time_ms = _optional_int(event_reference.get("media_time_ms"))
    if observed_time is None and media_time_ms is None:
        media_time_ms = DEFAULT_REFERENCE_MEDIA_TIME_MS
    return DetectionEvent(
        source_name=str(event_reference["source_name"]),
        observed_time=observed_time,
        media_time_ms=media_time_ms,
        frame_index=_required_int(event_reference["frame_index"]),
        frame_width=max(1, round(bounding_box.x2)),
        frame_height=max(1, round(bounding_box.y2)),
        evidence_uri=str(event_reference["evidence_uri"]),
        model_name="agent-facing-reference",
        class_id=0,
        class_name=_class_name(event_reference),
        confidence=_required_float(event_reference.get("confidence", 0.0)),
        bounding_box=bounding_box,
        track_id=None,
    )


def _unwrap_event_reference(reference: Mapping[str, object]) -> Mapping[str, object]:
    events = reference.get("events")
    if isinstance(events, Sequence) and not isinstance(events, str | bytes):
        if not events:
            msg = "detection_event_ref events must include at least one event"
            raise ValueError(msg)
        first_event = events[0]
        if isinstance(first_event, Mapping):
            return cast("Mapping[str, object]", first_event)
    event = reference.get("event")
    if isinstance(event, Mapping):
        return cast("Mapping[str, object]", event)
    return reference


def _class_name(reference: Mapping[str, object]) -> str:
    value = reference.get("class_name", reference.get("label"))
    if value is None or str(value).strip() == "":
        msg = "detection_event_ref requires class_name or label"
        raise ValueError(msg)
    return str(value).strip()


def _bounding_box(value: object) -> BoundingBox:
    coordinates = cast("Sequence[object]", value)
    return BoundingBox(
        x1=_required_float(coordinates[0]),
        y1=_required_float(coordinates[1]),
        x2=_required_float(coordinates[2]),
        y2=_required_float(coordinates[3]),
    )


def _optional_datetime(value: object | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(str(value))


def _optional_int(value: object | None) -> int | None:
    if value is None:
        return None
    return _required_int(value)


def _required_int(value: object) -> int:
    return int(str(value))


def _required_float(value: object) -> float:
    return float(str(value))


def _evidence_window_ref(event: DetectionEvent) -> str:
    return f"run-local:{event.source_name}:{event.frame_index}:{event.class_name}"
