"""Tests for agent-facing Evidence data tools."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest
from langchain_core.tools.convert import tool as convert_to_langchain_tool

from cereal.agents.evidence import make_retrieve_evidence_window_tool
from cereal.evidence.types import EvidenceFrame, EvidenceWindow

if TYPE_CHECKING:
    from collections.abc import Mapping

CENTER_FRAME_INDEX = 2
EXPECTED_EVIDENCE_FRAME_COUNT = 3


def test_retrieve_evidence_window_tool_returns_serializable_reference() -> None:
    stored_windows: dict[str, EvidenceWindow] = {}
    tool = make_retrieve_evidence_window_tool(
        reader=FakeEvidenceFrameReader(
            {
                1: make_frame(1),
                2: make_frame(2),
                3: make_frame(3),
            },
        ),
        evidence_windows=stored_windows,
    )

    result = tool(
        detection_event_ref={
            "source_name": "smoke_fixture",
            "frame_index": 2,
            "media_time_ms": 200,
            "observed_time": "2026-05-29T12:00:00+00:00",
            "class_name": "car",
            "confidence": 0.91,
            "evidence_uri": "file:///tmp/cereal-smoke.avi",
            "bounding_box": [10, 20, 80, 90],
        },
        frame_radius=1,
    )

    assert result == {
        "evidence_window_ref": "run-local:smoke_fixture:2:car",
        "source_name": "smoke_fixture",
        "center_frame_index": 2,
        "frame_count": 3,
        "target": {
            "class_name": "car",
            "confidence": 0.91,
            "bounding_box": [10.0, 20.0, 80.0, 90.0],
        },
        "evidence_uri": "file:///tmp/cereal-smoke.avi",
    }
    assert tuple(stored_windows) == ("run-local:smoke_fixture:2:car",)
    assert stored_windows["run-local:smoke_fixture:2:car"].center_frame_index == CENTER_FRAME_INDEX


def test_retrieve_evidence_window_tool_accepts_single_lookup_result_event() -> None:
    stored_windows: dict[str, EvidenceWindow] = {}
    tool = make_retrieve_evidence_window_tool(
        reader=FakeEvidenceFrameReader(
            {
                1: make_frame(1),
                2: make_frame(2),
                3: make_frame(3),
            },
        ),
        evidence_windows=stored_windows,
    )

    result = tool(
        detection_event_ref={
            "label": "car",
            "event_count": 1,
            "events": [
                {
                    "source_name": "smoke_fixture",
                    "frame_index": 2,
                    "media_time_ms": 200,
                    "observed_time": "2026-05-29T12:00:00+00:00",
                    "class_name": "car",
                    "confidence": 0.91,
                    "evidence_uri": "file:///tmp/cereal-smoke.avi",
                    "bounding_box": [10, 20, 80, 90],
                },
            ],
        },
        frame_radius=1,
    )

    assert result["evidence_window_ref"] == "run-local:smoke_fixture:2:car"
    assert result["frame_count"] == EXPECTED_EVIDENCE_FRAME_COUNT


def test_retrieve_evidence_window_tool_tolerates_missing_target_details() -> None:
    stored_windows: dict[str, EvidenceWindow] = {}
    tool = make_retrieve_evidence_window_tool(
        reader=FakeEvidenceFrameReader(
            {
                1: make_frame(1),
                2: make_frame(2),
                3: make_frame(3),
            },
        ),
        evidence_windows=stored_windows,
    )

    result = tool(
        detection_event_ref={
            "source_name": "smoke_fixture",
            "frame_index": 2,
            "class_name": "car",
            "evidence_uri": "file:///tmp/cereal-smoke.avi",
        },
        frame_radius=1,
    )

    assert result["evidence_window_ref"] == "run-local:smoke_fixture:2:car"
    assert result["target"] == {
        "class_name": "car",
        "confidence": 0.0,
        "bounding_box": [0.0, 0.0, 1.0, 1.0],
    }


def test_retrieve_evidence_window_tool_rejects_empty_lookup_result() -> None:
    tool = make_retrieve_evidence_window_tool(
        reader=FakeEvidenceFrameReader({}),
        evidence_windows={},
    )

    with pytest.raises(ValueError, match="at least one event"):
        tool(detection_event_ref={"label": "car", "event_count": 0, "events": []})


def test_retrieve_evidence_window_tool_coalesces_null_time_fields() -> None:
    stored_windows: dict[str, EvidenceWindow] = {}
    tool = make_retrieve_evidence_window_tool(
        reader=FakeEvidenceFrameReader(
            {
                1: make_frame(1),
                2: make_frame(2),
                3: make_frame(3),
            },
        ),
        evidence_windows=stored_windows,
    )

    result = tool(
        detection_event_ref={
            "source_name": "smoke_fixture",
            "frame_index": 2,
            "media_time_ms": None,
            "observed_time": None,
            "class_name": "car",
            "evidence_uri": "file:///tmp/cereal-smoke.avi",
        },
    )

    assert result["evidence_window_ref"] == "run-local:smoke_fixture:2:car"


def test_retrieve_evidence_window_tool_requires_class_name_or_label() -> None:
    tool = make_retrieve_evidence_window_tool(
        reader=FakeEvidenceFrameReader({}),
        evidence_windows={},
    )

    with pytest.raises(ValueError, match="class_name or label"):
        tool(
            detection_event_ref={
                "source_name": "smoke_fixture",
                "frame_index": 2,
                "evidence_uri": "file:///tmp/cereal-smoke.avi",
            },
        )


def test_retrieve_evidence_window_tool_can_convert_to_langchain_tool() -> None:
    stored_windows: dict[str, EvidenceWindow] = {}
    retrieve_window = make_retrieve_evidence_window_tool(
        reader=FakeEvidenceFrameReader({}),
        evidence_windows=stored_windows,
    )

    converted = convert_to_langchain_tool(retrieve_window)

    assert converted.name == "retrieve_evidence_window"
    assert converted.description


class FakeEvidenceFrameReader:
    def __init__(self, frames: Mapping[int, EvidenceFrame]) -> None:
        self._frames = dict(frames)

    def read_frame(self, evidence_uri: str, frame_index: int) -> EvidenceFrame | None:
        del evidence_uri
        return self._frames.get(frame_index)


def make_frame(frame_index: int) -> EvidenceFrame:
    return EvidenceFrame(
        frame_index=frame_index,
        media_time_ms=frame_index * 100,
        image=np.zeros((24, 32, 3), dtype=np.uint8),
    )
