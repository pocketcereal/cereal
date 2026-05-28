"""Evidence window retrieval rules."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from cereal.evidence.types import EvidenceTarget, EvidenceWindow

if TYPE_CHECKING:
    from cereal.evidence.types import EvidenceFrame, EvidenceWindowRequest

__all__ = ["EvidenceFrameReader", "EvidenceFrameUnavailableError", "retrieve_evidence_window"]


class EvidenceFrameUnavailableError(RuntimeError):
    """Raised when the center Evidence frame cannot be recovered."""


class EvidenceFrameReader(Protocol):
    """Reads full frames from durable evidence."""

    def read_frame(self, evidence_uri: str, frame_index: int) -> EvidenceFrame | None:
        """Return one Evidence frame, or None when that frame is unavailable."""


def retrieve_evidence_window(
    request: EvidenceWindowRequest,
    reader: EvidenceFrameReader,
) -> EvidenceWindow:
    """Recover a full-frame Evidence window around one Detection event."""
    event = request.event
    frame_indexes = range(
        max(0, event.frame_index - request.radius_frames),
        event.frame_index + request.radius_frames + 1,
    )
    frames = tuple(
        frame
        for frame_index in frame_indexes
        if (frame := reader.read_frame(event.evidence_uri, frame_index)) is not None
    )
    if all(frame.frame_index != event.frame_index for frame in frames):
        msg = f"center frame unavailable: {event.evidence_uri} frame={event.frame_index}"
        raise EvidenceFrameUnavailableError(msg)

    return EvidenceWindow(
        evidence_uri=event.evidence_uri,
        center_frame_index=event.frame_index,
        target=EvidenceTarget(
            class_name=event.class_name,
            confidence=event.confidence,
            bounding_box=event.bounding_box,
            frame_index=event.frame_index,
        ),
        frames=frames,
    )
