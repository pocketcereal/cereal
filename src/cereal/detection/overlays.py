"""Preview overlay rendering for Detection candidates and events."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, cast

if TYPE_CHECKING:
    from collections.abc import Sequence

    import numpy as np

    from cereal.detection.types import BoundingBox

__all__ = ["render_detection_overlays"]

BOX_COLOR = (0, 255, 0)
LABEL_BACKGROUND = (0, 0, 0)
LABEL_TEXT_COLOR = (255, 255, 255)
BOX_THICKNESS = 2
FONT_SCALE = 0.5
TEXT_THICKNESS = 1


class OverlayDetection(Protocol):
    """Detection shape needed for preview overlay rendering."""

    class_name: str
    confidence: float
    bounding_box: BoundingBox


class OpenCvOverlayModule(Protocol):
    """OpenCV drawing surface used by the overlay helper."""

    FONT_HERSHEY_SIMPLEX: int
    LINE_AA: int

    def rectangle(
        self,
        image: np.ndarray,
        start: tuple[int, int],
        end: tuple[int, int],
        color: tuple[int, int, int],
        thickness: int,
    ) -> object:
        """Draw a rectangle."""

    def getTextSize(  # noqa: N802 - mirrors OpenCV API shape.
        self,
        text: str,
        font_face: int,
        font_scale: float,
        thickness: int,
    ) -> tuple[tuple[int, int], int]:
        """Measure text size."""

    def putText(  # noqa: N802, PLR0913 - mirrors OpenCV API shape.
        self,
        image: np.ndarray,
        text: str,
        origin: tuple[int, int],
        font_face: int,
        font_scale: float,
        color: tuple[int, int, int],
        thickness: int,
        line_type: int,
    ) -> object:
        """Draw text."""


def render_detection_overlays(
    frame: np.ndarray,
    detections: Sequence[OverlayDetection],
) -> np.ndarray:
    """Return a copy of the frame with Detection boxes and labels drawn."""
    rendered = frame.copy()
    if not detections:
        return rendered

    opencv = _load_opencv()
    for detection in detections:
        box = detection.bounding_box
        start = (round(box.x1), round(box.y1))
        end = (round(box.x2), round(box.y2))
        opencv.rectangle(rendered, start, end, BOX_COLOR, BOX_THICKNESS)

        label = f"{detection.class_name} {detection.confidence:.2f}"
        text_origin = (start[0], max(0, start[1] - 4))
        (text_width, text_height), baseline = opencv.getTextSize(
            label,
            opencv.FONT_HERSHEY_SIMPLEX,
            FONT_SCALE,
            TEXT_THICKNESS,
        )
        background_start = (text_origin[0], max(0, text_origin[1] - text_height - baseline))
        background_end = (text_origin[0] + text_width, text_origin[1] + baseline)
        opencv.rectangle(rendered, background_start, background_end, LABEL_BACKGROUND, -1)
        opencv.putText(
            rendered,
            label,
            text_origin,
            opencv.FONT_HERSHEY_SIMPLEX,
            FONT_SCALE,
            LABEL_TEXT_COLOR,
            TEXT_THICKNESS,
            opencv.LINE_AA,
        )

    return rendered


def _load_opencv() -> OpenCvOverlayModule:
    import cv2  # noqa: PLC0415

    return cast("OpenCvOverlayModule", cv2)
