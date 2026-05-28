"""Tests for Analysis visual inspection composition."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import numpy as np
import pytest

from cereal.analysis.visual_inspection import run_visual_inspection_query
from cereal.detection.store import DetectionEventQuery, SqliteDetectionStore
from cereal.detection.types import BoundingBox, DetectionEvent
from cereal.evidence.retrieval import EvidenceFrameUnavailableError
from cereal.evidence.types import EvidenceFrame
from cereal.evidence.video import OpenCvEvidenceFrameReader
from cereal.validation.types import VisualClaim, VisualValidation, VisualValidationRequest
from tests.helpers import write_static_video

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from pathlib import Path

FRAME_HEIGHT = 24
FRAME_WIDTH = 32
TARGET_CONFIDENCE = 0.875
TARGET_FRAME_INDEX = 5
VALIDATION_CONFIDENCE = 0.9


def test_run_visual_inspection_query_returns_inspection_per_detection_event() -> None:
    event = make_event(frame_index=TARGET_FRAME_INDEX)
    query = DetectionEventQuery(source_name="camera", class_name="person")
    claim = VisualClaim("the target is a person")
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
    validator = FakeVisualValidator()

    inspections = run_visual_inspection_query(
        query=query,
        store=store,
        reader=reader,
        claim=claim,
        validator=validator,
    )

    assert store.queries == [query]
    assert len(inspections) == 1
    inspection = inspections[0]
    assert inspection.detection_event == event
    assert inspection.claim == claim
    assert inspection.evidence_window.target.class_name == "person"
    assert [frame.frame_index for frame in inspection.evidence_window.frames] == [3, 4, 5, 6, 7]
    assert inspection.validation.claim == claim
    assert inspection.validation.center_frame_index == TARGET_FRAME_INDEX
    assert [request.evidence_window for request in validator.requests] == [
        inspection.evidence_window
    ]


def test_run_visual_inspection_query_recovers_stored_event_frames_from_local_video(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "sample.avi"
    write_static_video(
        source_file,
        width=FRAME_WIDTH,
        height=FRAME_HEIGHT,
        frame_count=3,
    )
    event = make_event(frame_index=1, evidence_uri=source_file.as_uri())
    claim = VisualClaim("the target is a person")
    validator = FakeVisualValidator()
    store = SqliteDetectionStore(tmp_path / "detections.sqlite3")

    try:
        store.insert_many([event])
        inspections = run_visual_inspection_query(
            query=DetectionEventQuery(source_name="camera", class_name="person"),
            store=store,
            reader=OpenCvEvidenceFrameReader(),
            claim=claim,
            validator=validator,
        )
    finally:
        store.close()

    assert len(inspections) == 1
    inspection = inspections[0]
    assert inspection.detection_event == event
    assert [frame.frame_index for frame in inspection.evidence_window.frames] == [0, 1, 2]
    assert inspection.evidence_window.frames[1].image.shape == (
        FRAME_HEIGHT,
        FRAME_WIDTH,
        3,
    )
    assert inspection.validation.center_frame_index == 1


def test_run_visual_inspection_query_returns_empty_tuple_when_store_has_no_events() -> None:
    validator = FakeVisualValidator()

    inspections = run_visual_inspection_query(
        query=DetectionEventQuery(class_name="person"),
        store=FakeDetectionStore(events=[]),
        reader=FakeEvidenceFrameReader({}),
        claim=VisualClaim("the target is a person"),
        validator=validator,
    )

    assert inspections == ()
    assert validator.requests == []


def test_run_visual_inspection_query_fails_when_center_frame_is_unavailable() -> None:
    event = make_event(frame_index=TARGET_FRAME_INDEX)
    validator = FakeVisualValidator()

    with pytest.raises(EvidenceFrameUnavailableError, match="center frame"):
        run_visual_inspection_query(
            query=DetectionEventQuery(class_name="person"),
            store=FakeDetectionStore(events=[event]),
            reader=FakeEvidenceFrameReader({4: make_evidence_frame(4)}),
            claim=VisualClaim("the target is a person"),
            validator=validator,
        )

    assert validator.requests == []


def test_run_visual_inspection_query_fails_when_validator_fails() -> None:
    event = make_event(frame_index=TARGET_FRAME_INDEX)

    with pytest.raises(RuntimeError, match="validator failed"):
        run_visual_inspection_query(
            query=DetectionEventQuery(class_name="person"),
            store=FakeDetectionStore(events=[event]),
            reader=FakeEvidenceFrameReader({5: make_evidence_frame(5)}),
            claim=VisualClaim("the target is a person"),
            validator=FailingVisualValidator(),
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


@dataclass
class FakeVisualValidator:
    requests: list[VisualValidationRequest] = field(default_factory=list)

    def validate(self, request: VisualValidationRequest) -> VisualValidation:
        self.requests.append(request)
        return VisualValidation(
            claim=request.claim,
            evidence_uri=request.evidence_window.evidence_uri,
            center_frame_index=request.evidence_window.center_frame_index,
            passed=True,
            confidence=VALIDATION_CONFIDENCE,
            explanation="target matches claim",
            role_name=request.role_name,
        )


class FailingVisualValidator:
    def validate(self, request: VisualValidationRequest) -> VisualValidation:
        del request
        msg = "validator failed"
        raise RuntimeError(msg)


def make_event(
    *,
    frame_index: int,
    evidence_uri: str = "file:///tmp/cereal.mp4",
) -> DetectionEvent:
    return DetectionEvent(
        source_name="camera",
        observed_time=datetime(2026, 5, 24, 12, 30, tzinfo=UTC),
        media_time_ms=None,
        frame_index=frame_index,
        frame_width=FRAME_WIDTH,
        frame_height=FRAME_HEIGHT,
        evidence_uri=evidence_uri,
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
