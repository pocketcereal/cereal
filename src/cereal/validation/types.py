"""Visual validation value types and ports."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from cereal.evidence.types import EvidenceWindow

__all__ = [
    "DEFAULT_VALIDATION_ROLE_NAME",
    "VisualClaim",
    "VisualValidation",
    "VisualValidationRequest",
    "VisualValidator",
]

DEFAULT_VALIDATION_ROLE_NAME = "visual_validator"


@dataclass(frozen=True)
class VisualClaim:
    """One focused claim to validate against visual evidence."""

    text: str

    def __post_init__(self) -> None:
        """Reject empty Visual claims."""
        if not self.text.strip():
            msg = "VisualClaim text must not be blank"
            raise ValueError(msg)


@dataclass(frozen=True)
class VisualValidationRequest:
    """Request for one Visual validation against one Evidence window."""

    claim: VisualClaim
    evidence_window: EvidenceWindow
    role_name: str = DEFAULT_VALIDATION_ROLE_NAME


@dataclass(frozen=True)
class VisualValidation:
    """Result of evaluating one Visual claim against one Evidence window."""

    claim: VisualClaim
    evidence_uri: str
    center_frame_index: int
    passed: bool
    confidence: float
    explanation: str
    role_name: str = DEFAULT_VALIDATION_ROLE_NAME

    def __post_init__(self) -> None:
        """Validate portable Visual validation result fields."""
        if not 0 <= self.confidence <= 1:
            msg = "confidence must be between 0 and 1"
            raise ValueError(msg)
        if not self.explanation.strip():
            msg = "explanation must not be blank"
            raise ValueError(msg)


class VisualValidator(Protocol):
    """Port for validating claims against Evidence windows."""

    def validate(self, request: VisualValidationRequest) -> VisualValidation:
        """Return a Visual validation result."""
