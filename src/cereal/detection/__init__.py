"""Detection domain contracts."""

from cereal.detection.types import (
    BoundingBox,
    DetectionCandidate,
    DetectionEvent,
    DetectionStreamDefaults,
    FrameTime,
    to_detection_events,
)

__all__ = [
    "BoundingBox",
    "DetectionCandidate",
    "DetectionEvent",
    "DetectionStreamDefaults",
    "FrameTime",
    "to_detection_events",
]
