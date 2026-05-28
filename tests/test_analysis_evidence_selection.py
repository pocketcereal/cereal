"""Tests for Analysis evidence selection."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import numpy as np
import pytest

from cereal.analysis.evidence_selection import select_evidence_windows
from cereal.detection.store import DetectionEventQuery
from cereal.detection.types import BoundingBox, DetectionEvent
from cereal.evidence.retrieval import EvidenceFrameUnavailableError
from cereal.evidence.types import EvidenceFrame

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

FRAME_HEIGHT = 24
FRAME_WIDTH = 32
TARGET_CONFIDENCE = 0.875
TARGET_FRAME_INDEX = 5
CUSTOM_RADIUS_FRAMES = 1


def test_select_evidence_windows_queries_store_and_retrieves_windows() -> None:
    event = make_event(frame_index=TARGET_FRAME_INDEX)
    query = DetectionEventQuery(source_name="camera", class_name="person")
    store = FakeDetectionStore(events=[event])
    reader = FakeEvidenceFrameReader(
        {
            3: make_evidence_frame(3),
            4: make_evidence_frame(4),
            5: make_evidence_frame(5),
            6: make_evidence_frame(6),
            7: make_evidence_frame(7),
        },
    )

    windows = select_evidence_windows(query=query, store=store, reader=reader)

    assert store.queries == [query]
    assert len(windows) == 1
    assert windows[0].target.class_name == "person"
    assert [frame.frame_index for frame in windows[0].frames] == [3, 4, 5, 6, 7]


def test_select_evidence_windows_returns_empty_tuple_when_store_has_no_events() -> None:
    query = DetectionEventQuery(class_name="person")

    windows = select_evidence_windows(
        query=query,
        store=FakeDetectionStore(events=[]),
        reader=FakeEvidenceFrameReader({}),
    )

    assert windows == ()


def test_select_evidence_windows_accepts_custom_radius() -> None:
    event = make_event(frame_index=TARGET_FRAME_INDEX)
    reader = FakeEvidenceFrameReader(
        {
            4: make_evidence_frame(4),
            5: make_evidence_frame(5),
            6: make_evidence_frame(6),
        },
    )

    windows = select_evidence_windows(
        query=DetectionEventQuery(class_name="person"),
        store=FakeDetectionStore(events=[event]),
        reader=reader,
        radius_frames=CUSTOM_RADIUS_FRAMES,
    )

    assert [frame.frame_index for frame in windows[0].frames] == [4, 5, 6]


def test_select_evidence_windows_fails_when_center_frame_is_unavailable() -> None:
    event = make_event(frame_index=TARGET_FRAME_INDEX)

    with pytest.raises(EvidenceFrameUnavailableError, match="center frame"):
        select_evidence_windows(
            query=DetectionEventQuery(class_name="person"),
            store=FakeDetectionStore(events=[event]),
            reader=FakeEvidenceFrameReader({4: make_evidence_frame(4)}),
        )


@dataclass
class FakeDetectionStore:
    events: Sequence[DetectionEvent]
    queries: list[DetectionEventQuery] = field(default_factory=list)

    def insert_many(self, events: Sequence[DetectionEvent]) -> list[DetectionEvent]:
        return list(events)

    def query(self, query: DetectionEventQuery) -> list[DetectionEvent]:
        self.queries.append(query)
        return list(self.events)

    def close(self) -> None:
        pass


@dataclass(frozen=True)
class FakeEvidenceFrameReader:
    frames: Mapping[int, EvidenceFrame]

    def read_frame(self, evidence_uri: str, frame_index: int) -> EvidenceFrame | None:
        del evidence_uri
        return self.frames.get(frame_index)


def make_event(*, frame_index: int) -> DetectionEvent:
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
        class_name="person",
        confidence=TARGET_CONFIDENCE,
        bounding_box=BoundingBox(x1=1.0, y1=2.0, x2=30.0, y2=20.0),
        track_id=None,
    )


def make_evidence_frame(frame_index: int) -> EvidenceFrame:
    return EvidenceFrame(
        frame_index=frame_index,
        media_time_ms=frame_index * 1_000,
        image=np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8),
    )
