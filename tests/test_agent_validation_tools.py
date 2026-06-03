"""Tests for agent-facing Visual validation data tools."""

from __future__ import annotations

import pytest
from langchain_core.tools.convert import tool as convert_to_langchain_tool

from cereal.agents.validation import make_validate_visual_claim_tool
from cereal.detection.types import BoundingBox
from cereal.evidence.types import EvidenceTarget, EvidenceWindow
from tests.test_agent_evidence_tools import make_frame


def test_validate_visual_claim_tool_returns_fixed_supported_result() -> None:
    evidence_windows = {
        "run-local:smoke_fixture:2:car": EvidenceWindow(
            evidence_uri="file:///tmp/cereal-smoke.avi",
            center_frame_index=2,
            target=EvidenceTarget(
                class_name="car",
                confidence=0.91,
                bounding_box=BoundingBox(10, 20, 80, 90),
                frame_index=2,
            ),
            frames=(make_frame(1), make_frame(2), make_frame(3)),
        ),
    }
    validate_visual_claim = make_validate_visual_claim_tool(evidence_windows=evidence_windows)

    result = validate_visual_claim(
        claim="the object is a car",
        evidence_window_ref="run-local:smoke_fixture:2:car",
    )

    assert result == {
        "claim": "the object is a car",
        "status": "supported",
        "class_name": "car",
        "evidence_window_ref": "run-local:smoke_fixture:2:car",
    }


def test_validate_visual_claim_tool_accepts_evidence_uri_reference() -> None:
    evidence_windows = {
        "run-local:smoke_fixture:2:car": EvidenceWindow(
            evidence_uri="file:///tmp/cereal-smoke.avi",
            center_frame_index=2,
            target=EvidenceTarget(
                class_name="car",
                confidence=0.91,
                bounding_box=BoundingBox(10, 20, 80, 90),
                frame_index=2,
            ),
            frames=(make_frame(1), make_frame(2), make_frame(3)),
        ),
    }
    validate_visual_claim = make_validate_visual_claim_tool(evidence_windows=evidence_windows)

    result = validate_visual_claim(
        claim="the object is a car",
        evidence_window_ref="file:///tmp/cereal-smoke.avi",
    )

    assert result == {
        "claim": "the object is a car",
        "status": "supported",
        "class_name": "car",
        "evidence_window_ref": "run-local:smoke_fixture:2:car",
    }


def test_validate_visual_claim_tool_rejects_ambiguous_evidence_uri_reference() -> None:
    evidence_windows = {
        "run-local:smoke_fixture:2:car": EvidenceWindow(
            evidence_uri="file:///tmp/cereal-smoke.avi",
            center_frame_index=2,
            target=EvidenceTarget(
                class_name="car",
                confidence=0.91,
                bounding_box=BoundingBox(10, 20, 80, 90),
                frame_index=2,
            ),
            frames=(make_frame(1), make_frame(2), make_frame(3)),
        ),
        "run-local:smoke_fixture:3:truck": EvidenceWindow(
            evidence_uri="file:///tmp/cereal-smoke.avi",
            center_frame_index=3,
            target=EvidenceTarget(
                class_name="truck",
                confidence=0.88,
                bounding_box=BoundingBox(11, 21, 81, 91),
                frame_index=3,
            ),
            frames=(make_frame(2), make_frame(3), make_frame(4)),
        ),
    }
    validate_visual_claim = make_validate_visual_claim_tool(evidence_windows=evidence_windows)

    with pytest.raises(KeyError):
        validate_visual_claim(
            claim="the object is a car",
            evidence_window_ref="file:///tmp/cereal-smoke.avi",
        )


def test_validate_visual_claim_tool_can_convert_to_langchain_tool() -> None:
    validate_visual_claim = make_validate_visual_claim_tool(evidence_windows={})

    converted = convert_to_langchain_tool(validate_visual_claim)

    assert converted.name == "validate_visual_claim"
    assert converted.description
