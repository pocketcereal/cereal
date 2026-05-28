"""Analysis composition for Detection events, Evidence windows, and validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from cereal.evidence.retrieval import retrieve_evidence_window
from cereal.evidence.types import EvidenceWindowRequest
from cereal.validation.types import VisualValidationRequest

if TYPE_CHECKING:
    from cereal.detection.store import DetectionEventQuery, DetectionStore
    from cereal.detection.types import DetectionEvent
    from cereal.evidence.retrieval import EvidenceFrameReader
    from cereal.evidence.types import EvidenceWindow
    from cereal.validation.types import VisualClaim, VisualValidation, VisualValidator

__all__ = ["VisualInspection", "run_visual_inspection_query"]


@dataclass(frozen=True)
class VisualInspection:
    """Transient Analysis result for one Detection event and one Visual claim."""

    detection_event: DetectionEvent
    evidence_window: EvidenceWindow
    claim: VisualClaim
    validation: VisualValidation


def run_visual_inspection_query(
    *,
    query: DetectionEventQuery,
    store: DetectionStore,
    reader: EvidenceFrameReader,
    claim: VisualClaim,
    validator: VisualValidator,
) -> tuple[VisualInspection, ...]:
    """Inspect Detection events by validating one claim against each Evidence window."""
    inspections: list[VisualInspection] = []
    for event in store.query(query):
        window = retrieve_evidence_window(
            EvidenceWindowRequest(event=event),
            reader,
        )
        validation = validator.validate(
            VisualValidationRequest(claim=claim, evidence_window=window),
        )
        inspections.append(
            VisualInspection(
                detection_event=event,
                evidence_window=window,
                claim=claim,
                validation=validation,
            ),
        )
    return tuple(inspections)
