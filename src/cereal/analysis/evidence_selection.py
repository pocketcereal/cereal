"""Analysis composition for Detection events and Evidence windows."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cereal.evidence.retrieval import retrieve_evidence_window
from cereal.evidence.types import DEFAULT_EVIDENCE_RADIUS_FRAMES, EvidenceWindowRequest

if TYPE_CHECKING:
    from cereal.detection.store import DetectionEventQuery, DetectionStore
    from cereal.evidence.retrieval import EvidenceFrameReader
    from cereal.evidence.types import EvidenceWindow

__all__ = ["select_evidence_windows"]


def select_evidence_windows(
    *,
    query: DetectionEventQuery,
    store: DetectionStore,
    reader: EvidenceFrameReader,
    radius_frames: int = DEFAULT_EVIDENCE_RADIUS_FRAMES,
) -> tuple[EvidenceWindow, ...]:
    """Retrieve Evidence windows for Detection events selected from the store."""
    return tuple(
        retrieve_evidence_window(
            EvidenceWindowRequest(event=event, radius_frames=radius_frames),
            reader,
        )
        for event in store.query(query)
    )
