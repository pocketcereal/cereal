"""Tests for Visual validation domain types."""

from __future__ import annotations

import pytest

from cereal.validation.types import VisualClaim, VisualValidation


def test_visual_claim_rejects_blank_text() -> None:
    with pytest.raises(ValueError, match="must not be blank"):
        VisualClaim(" ")


def test_visual_validation_rejects_confidence_outside_unit_interval() -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        VisualValidation(
            claim=VisualClaim("the target is a person"),
            evidence_uri="file:///tmp/cereal.mp4",
            center_frame_index=1,
            passed=True,
            confidence=1.1,
            explanation="target matches claim",
        )


def test_visual_validation_rejects_blank_explanation() -> None:
    with pytest.raises(ValueError, match="must not be blank"):
        VisualValidation(
            claim=VisualClaim("the target is a person"),
            evidence_uri="file:///tmp/cereal.mp4",
            center_frame_index=1,
            passed=True,
            confidence=0.9,
            explanation=" ",
        )
