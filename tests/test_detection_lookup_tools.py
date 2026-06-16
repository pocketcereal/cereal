"""Tests for Detection lookup agent tools."""

from __future__ import annotations

from datetime import UTC, datetime
from types import FunctionType
from typing import TYPE_CHECKING, cast

import pytest

from cereal.agents import AgentDefinition, AgentDefinitionKind
from cereal.agents.detection_lookup import (
    DetectionLabelListResult,
    DetectionLabelSummary,
    DetectionLookupEvent,
    DetectionLookupResult,
    make_detection_lookup_tool_catalog,
    make_find_detection_events_tool,
    make_list_detection_labels_tool,
    make_lookup_object_tracks_tool,
)
from cereal.detection.store import DetectionEventQuery, DetectionLabelCount, DetectionLabelQuery
from cereal.detection.types import BoundingBox, DetectionEvent

if TYPE_CHECKING:
    from collections.abc import Sequence

TWO_TRACKS = 2
THREE_EVENTS = 3


def test_find_detection_events_tool_queries_store_by_label_and_filters() -> None:
    event = make_event(class_name="car")
    store = FakeDetectionStore(events=[event])
    find_detection_events = make_find_detection_events_tool(store)

    result = find_detection_events(
        label="car",
        source_name="camera",
        observed_start="2026-05-24T12:00:00Z",
        observed_end="2026-05-24T13:00:00Z",
        min_confidence=0.5,
        limit=5,
    )

    assert store.event_queries == [
        DetectionEventQuery(
            source_name="camera",
            class_name="car",
            observed_time_start=datetime(2026, 5, 24, 12, tzinfo=UTC),
            observed_time_end=datetime(2026, 5, 24, 13, tzinfo=UTC),
            min_confidence=0.5,
            limit=5,
        ),
    ]
    assert (
        result
        == DetectionLookupResult(
            label="car",
            event_count=1,
            events=(
                DetectionLookupEvent(
                    source_name="camera",
                    class_name="car",
                    confidence=0.875,
                    observed_time="2026-05-24T12:30:00+00:00",
                    media_time_ms=None,
                    frame_index=7,
                    evidence_uri="file:///tmp/cereal.mp4",
                    bounding_box=(1.0, 2.0, 30.0, 40.0),
                    track_id=None,
                ),
            ),
        ).to_dict()
    )


def test_find_detection_events_tool_rejects_blank_label() -> None:
    find_detection_events = make_find_detection_events_tool(FakeDetectionStore())

    with pytest.raises(ValueError, match="label"):
        find_detection_events(label=" ")


def test_find_detection_events_tool_rejects_invalid_observed_time() -> None:
    find_detection_events = make_find_detection_events_tool(FakeDetectionStore())

    with pytest.raises(ValueError, match="observed_start"):
        find_detection_events(label="car", observed_start="not-a-time")


def test_list_detection_labels_tool_returns_label_counts() -> None:
    store = FakeDetectionStore(
        label_counts=[
            DetectionLabelCount(class_name="car", event_count=2),
            DetectionLabelCount(class_name="person", event_count=1),
        ],
    )
    list_detection_labels = make_list_detection_labels_tool(store)

    result = list_detection_labels(
        source_name="camera",
        observed_start="2026-05-24T12:00:00Z",
        limit=10,
    )

    assert store.label_queries == [
        DetectionLabelQuery(
            source_name="camera",
            observed_time_start=datetime(2026, 5, 24, 12, tzinfo=UTC),
            limit=10,
        ),
    ]
    assert (
        result
        == DetectionLabelListResult(
            labels=(
                DetectionLabelSummary(label="car", event_count=2),
                DetectionLabelSummary(label="person", event_count=1),
            ),
        ).to_dict()
    )


def test_lookup_object_tracks_tool_groups_events_into_candidate_tracks() -> None:
    store = FakeDetectionStore(
        events=[
            make_event(class_name="car", frame_index=1, track_id="1"),
            make_event(class_name="car", frame_index=2, track_id="1"),
            make_event(class_name="car", frame_index=5, track_id="2"),
        ],
    )
    lookup_object_tracks = make_lookup_object_tracks_tool(store)

    result = lookup_object_tracks(label="car", source_name="camera")

    assert store.event_queries == [
        DetectionEventQuery(source_name="camera", class_name="car", limit=None),
    ]
    assert result["label"] == "car"
    assert result["track_count"] == TWO_TRACKS
    assert result["event_count"] == THREE_EVENTS
    assert result["follow_up_capabilities"] == [
        "retrieve_evidence_window",
        "validate_visual_claim",
        "compare_candidates",
    ]
    candidates = cast("list[dict[str, object]]", result["candidates"])
    assert [candidate["event_count"] for candidate in candidates] == [2, 1]
    assert candidates[0]["grouping_basis"] == "detector_track_id"
    assert candidates[0]["frame_range"] == [1, 2]
    representative = cast("dict[str, object]", candidates[0]["representative"])
    assert representative["class_name"] == "car"
    assert representative["source_name"] == "camera"


def test_lookup_object_tracks_tool_reports_singleton_and_linked_basis() -> None:
    store = FakeDetectionStore(
        events=[
            make_event(class_name="car", frame_index=9, track_id=None),
        ],
    )
    lookup_object_tracks = make_lookup_object_tracks_tool(store)

    result = lookup_object_tracks(label="car")

    assert result["track_count"] == 1
    candidates = cast("list[dict[str, object]]", result["candidates"])
    assert candidates[0]["grouping_basis"] == "singleton"
    assert candidates[0]["track_id"] is None
    assert isinstance(result["uncertainty"], str)


def test_lookup_object_tracks_tool_rejects_blank_label() -> None:
    lookup_object_tracks = make_lookup_object_tracks_tool(FakeDetectionStore())

    with pytest.raises(ValueError, match="label"):
        lookup_object_tracks(label=" ")


def test_detection_lookup_tool_catalog_resolves_declared_tools() -> None:
    catalog = make_detection_lookup_tool_catalog(FakeDetectionStore())

    resolved = catalog.resolve(
        AgentDefinition(
            name="detection-lookup",
            description="Finds Detection events.",
            kind=AgentDefinitionKind.SPECIALIZED_SUBAGENT,
            instructions="Lookup detections.",
            tools=("find_detection_events", "list_detection_labels"),
        ),
    )

    assert all(isinstance(tool, FunctionType) for tool in resolved)
    assert [tool.__name__ for tool in resolved if isinstance(tool, FunctionType)] == [
        "find_detection_events",
        "list_detection_labels",
    ]


class FakeDetectionStore:
    def __init__(
        self,
        *,
        events: Sequence[DetectionEvent] = (),
        label_counts: Sequence[DetectionLabelCount] = (),
    ) -> None:
        self.events = list(events)
        self.label_counts = list(label_counts)
        self.event_queries: list[DetectionEventQuery] = []
        self.label_queries: list[DetectionLabelQuery] = []

    def insert_many(self, events: Sequence[DetectionEvent]) -> list[DetectionEvent]:
        return list(events)

    def query(self, query: DetectionEventQuery) -> list[DetectionEvent]:
        self.event_queries.append(query)
        return self.events

    def list_labels(self, query: DetectionLabelQuery) -> list[DetectionLabelCount]:
        self.label_queries.append(query)
        return self.label_counts

    def close(self) -> None:
        pass


def make_event(
    *,
    class_name: str,
    frame_index: int = 7,
    track_id: str | None = None,
) -> DetectionEvent:
    return DetectionEvent(
        source_name="camera",
        observed_time=datetime(2026, 5, 24, 12, 30, tzinfo=UTC),
        media_time_ms=None,
        frame_index=frame_index,
        frame_width=1920,
        frame_height=1080,
        evidence_uri="file:///tmp/cereal.mp4",
        model_name="test-model",
        class_id=1,
        class_name=class_name,
        confidence=0.875,
        bounding_box=BoundingBox(x1=1.0, y1=2.0, x2=30.0, y2=40.0),
        track_id=track_id,
    )
