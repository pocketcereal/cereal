"""Tests for Analysis visual validation composition."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from cereal.analysis.visual_validation import validate_evidence_windows
from cereal.detection.types import BoundingBox
from cereal.evidence.types import EvidenceFrame, EvidenceTarget, EvidenceWindow
from cereal.validation.types import VisualClaim, VisualValidation, VisualValidationRequest

FRAME_HEIGHT = 24
FRAME_WIDTH = 32
VALIDATION_CONFIDENCE = 0.9


def test_validate_evidence_windows_applies_validator_to_each_window() -> None:
    windows = (make_window(center_frame_index=5), make_window(center_frame_index=9))
    validator = FakeVisualValidator()
    claim = VisualClaim("the target is a person")

    validations = validate_evidence_windows(
        claim=claim,
        windows=windows,
        validator=validator,
    )

    assert [request.evidence_window.center_frame_index for request in validator.requests] == [5, 9]
    assert [validation.center_frame_index for validation in validations] == [5, 9]
    assert all(validation.claim == claim for validation in validations)


def test_validate_evidence_windows_returns_empty_tuple_for_no_windows() -> None:
    validations = validate_evidence_windows(
        claim=VisualClaim("the target is a person"),
        windows=(),
        validator=FakeVisualValidator(),
    )

    assert validations == ()


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


def make_window(*, center_frame_index: int) -> EvidenceWindow:
    return EvidenceWindow(
        evidence_uri="file:///tmp/cereal.mp4",
        center_frame_index=center_frame_index,
        target=EvidenceTarget(
            class_name="person",
            confidence=0.875,
            bounding_box=BoundingBox(x1=1.0, y1=2.0, x2=30.0, y2=20.0),
            frame_index=center_frame_index,
        ),
        frames=(
            EvidenceFrame(
                frame_index=center_frame_index,
                media_time_ms=center_frame_index * 1_000,
                image=np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8),
            ),
        ),
    )
