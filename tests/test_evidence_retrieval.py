"""Tests for Evidence window retrieval."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import numpy as np
import pytest

from cereal.detection.types import BoundingBox, DetectionEvent
from cereal.evidence.retrieval import EvidenceFrameUnavailableError, retrieve_evidence_window
from cereal.evidence.types import EvidenceFrame, EvidenceWindowRequest

if TYPE_CHECKING:
    from collections.abc import Mapping

FRAME_HEIGHT = 24
FRAME_WIDTH = 32
TARGET_CONFIDENCE = 0.875
TARGET_FRAME_INDEX = 5


def test_retrieve_evidence_window_returns_full_frames_with_target_context() -> None:
    event = make_event(frame_index=TARGET_FRAME_INDEX)
    reader = FakeEvidenceFrameReader(
        {
            3: make_evidence_frame(3),
            4: make_evidence_frame(4),
            5: make_evidence_frame(5),
            6: make_evidence_frame(6),
            7: make_evidence_frame(7),
        },
    )

    window = retrieve_evidence_window(EvidenceWindowRequest(event=event), reader)

    assert window.evidence_uri == event.evidence_uri
    assert window.center_frame_index == TARGET_FRAME_INDEX
    assert [frame.frame_index for frame in window.frames] == [3, 4, 5, 6, 7]
    assert window.target.class_name == "person"
    assert window.target.confidence == TARGET_CONFIDENCE
    assert window.target.bounding_box == event.bounding_box


def test_retrieve_evidence_window_skips_missing_neighbor_frames() -> None:
    event = make_event(frame_index=0)
    reader = FakeEvidenceFrameReader(
        {
            0: make_evidence_frame(0),
            1: make_evidence_frame(1),
        },
    )

    window = retrieve_evidence_window(
        EvidenceWindowRequest(event=event, radius_frames=2),
        reader,
    )

    assert [frame.frame_index for frame in window.frames] == [0, 1]


def test_retrieve_evidence_window_requires_center_frame() -> None:
    event = make_event(frame_index=4)
    reader = FakeEvidenceFrameReader({3: make_evidence_frame(3), 5: make_evidence_frame(5)})

    with pytest.raises(EvidenceFrameUnavailableError, match="center frame"):
        retrieve_evidence_window(EvidenceWindowRequest(event=event), reader)


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
