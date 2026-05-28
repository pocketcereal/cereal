"""Evidence retrieval value types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

    from cereal.detection.types import BoundingBox, DetectionEvent

__all__ = [
    "DEFAULT_EVIDENCE_RADIUS_FRAMES",
    "EvidenceFrame",
    "EvidenceTarget",
    "EvidenceWindow",
    "EvidenceWindowRequest",
]

DEFAULT_EVIDENCE_RADIUS_FRAMES = 2


@dataclass(frozen=True)
class EvidenceFrame:
    """One full recovered frame from durable evidence."""

    frame_index: int
    media_time_ms: int | None
    image: np.ndarray


@dataclass(frozen=True)
class EvidenceTarget:
    """Detection context that identifies the target inside an Evidence window."""

    class_name: str
    confidence: float
    bounding_box: BoundingBox
    frame_index: int


@dataclass(frozen=True)
class EvidenceWindowRequest:
    """Request to recover Frames around one Detection event."""

    event: DetectionEvent
    radius_frames: int = DEFAULT_EVIDENCE_RADIUS_FRAMES

    def __post_init__(self) -> None:
        """Reject nonsensical Evidence window sizes."""
        if self.radius_frames < 0:
            msg = "radius_frames must be non-negative"
            raise ValueError(msg)


@dataclass(frozen=True)
class EvidenceWindow:
    """Full Frames around a Detection event with target metadata."""

    evidence_uri: str
    center_frame_index: int
    target: EvidenceTarget
    frames: tuple[EvidenceFrame, ...]
