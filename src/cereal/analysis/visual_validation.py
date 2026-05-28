"""Analysis composition for Evidence windows and Visual validation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cereal.validation.types import VisualValidationRequest

if TYPE_CHECKING:
    from collections.abc import Sequence

    from cereal.evidence.types import EvidenceWindow
    from cereal.validation.types import VisualClaim, VisualValidation, VisualValidator

__all__ = ["validate_evidence_windows"]


def validate_evidence_windows(
    *,
    claim: VisualClaim,
    windows: Sequence[EvidenceWindow],
    validator: VisualValidator,
) -> tuple[VisualValidation, ...]:
    """Run one Visual validation claim against each Evidence window."""
    return tuple(
        validator.validate(VisualValidationRequest(claim=claim, evidence_window=window))
        for window in windows
    )
