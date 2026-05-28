"""Detection domain value types and pure conversions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

__all__ = [
    "BoundingBox",
    "DetectionCandidate",
    "DetectionEvent",
    "DetectionStreamDefaults",
    "FrameTime",
    "to_detection_events",
]


@dataclass(frozen=True)
class BoundingBox:
    """Pixel-space xyxy bounding box."""

    x1: float
    y1: float
    x2: float
    y2: float

    def __post_init__(self) -> None:
        """Validate box coordinate ordering without clamping to a frame."""
        if self.x1 > self.x2:
            msg = "x1 must be less than or equal to x2"
            raise ValueError(msg)
        if self.y1 > self.y2:
            msg = "y1 must be less than or equal to y2"
            raise ValueError(msg)


@dataclass(frozen=True)
class DetectionCandidate:
    """Raw object detector output before persistence context is attached."""

    class_id: int
    class_name: str
    confidence: float
    bounding_box: BoundingBox
    track_id: str | None


@dataclass(frozen=True)
class DetectionEvent:
    """One model observation for one object candidate in one frame."""

    source_name: str
    observed_time: datetime | None
    media_time_ms: int | None
    frame_index: int
    frame_width: int
    frame_height: int
    evidence_uri: str
    model_name: str
    class_id: int
    class_name: str
    confidence: float
    bounding_box: BoundingBox
    track_id: str | None

    def __post_init__(self) -> None:
        """Validate the minimum context needed to recover the source frame."""
        if self.observed_time is None and self.media_time_ms is None:
            msg = "DetectionEvent requires at least one observed or media time"
            raise ValueError(msg)
        if self.frame_width <= 0:
            msg = "frame_width must be positive"
            raise ValueError(msg)
        if self.frame_height <= 0:
            msg = "frame_height must be positive"
            raise ValueError(msg)


@dataclass(frozen=True)
class FrameTime:
    """Observed time or media offset assigned to a frame."""

    observed: datetime | None
    media_ms: int | None

    def __post_init__(self) -> None:
        """Require at least one timestamp flavor."""
        if self.observed is None and self.media_ms is None:
            msg = "FrameTime requires at least one observed or media time"
            raise ValueError(msg)


@dataclass(frozen=True)
class DetectionStreamDefaults:
    """Prototype-owned detection stream defaults."""

    sample_interval_s: float = 3.0
    confidence_threshold: float = 0.5


def to_detection_events(  # noqa: PLR0913 - conversion receives explicit runtime context.
    *,
    candidates: Sequence[DetectionCandidate],
    source_name: str,
    frame_index: int,
    frame_width: int,
    frame_height: int,
    frame_time: FrameTime,
    evidence_uri: str,
    model_name: str,
) -> list[DetectionEvent]:
    """Attach frame and evidence context to detector candidates."""
    return [
        DetectionEvent(
            source_name=source_name,
            observed_time=frame_time.observed,
            media_time_ms=frame_time.media_ms,
            frame_index=frame_index,
            frame_width=frame_width,
            frame_height=frame_height,
            evidence_uri=evidence_uri,
            model_name=model_name,
            class_id=candidate.class_id,
            class_name=candidate.class_name,
            confidence=candidate.confidence,
            bounding_box=candidate.bounding_box,
            track_id=candidate.track_id,
        )
        for candidate in candidates
    ]
