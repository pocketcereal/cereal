"""Object detector port."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence

    import numpy as np

    from cereal.detection.types import DetectionCandidate

__all__ = ["ObjectDetector"]


class ObjectDetector(Protocol):
    """Replaceable object detector boundary."""

    @property
    def model_name(self) -> str:
        """Return side-effect-free model identity."""

    def detect(self, frame: np.ndarray) -> Sequence[DetectionCandidate]:
        """Detect object candidates in one frame."""
