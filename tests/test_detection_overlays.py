"""Tests for Detection preview overlays."""

from __future__ import annotations

import numpy as np

from cereal.detection.overlays import render_detection_overlays
from cereal.detection.types import BoundingBox, DetectionCandidate

FRAME_SIZE = 64


def test_render_detection_overlays_draws_box_and_label_without_mutating_input() -> None:
    frame = np.zeros((FRAME_SIZE, FRAME_SIZE, 3), dtype=np.uint8)
    candidate = DetectionCandidate(
        class_id=1,
        class_name="person",
        confidence=0.91,
        bounding_box=BoundingBox(x1=10.0, y1=20.0, x2=40.0, y2=50.0),
        track_id=None,
    )

    rendered = render_detection_overlays(frame, [candidate])

    assert int(frame.sum()) == 0
    assert int(rendered.sum()) > 0
    assert rendered.shape == frame.shape
