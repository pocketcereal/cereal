"""Tests for Detection detector boundaries."""

from __future__ import annotations

import importlib
import os
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
import pytest

from cereal.detection.types import BoundingBox, DetectionCandidate
from cereal.detection.yolo_adapter import (
    UltralyticsObjectDetector,
    yolo_results_to_detection_candidates,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


def test_core_detection_contracts_do_not_import_ultralytics() -> None:
    sys.modules.pop("ultralytics", None)

    importlib.import_module("cereal.detection")
    importlib.import_module("cereal.detection.detector")

    assert "ultralytics" not in sys.modules


def test_yolo_result_mapping_converts_boxes_to_detection_candidates() -> None:
    result = FakeYoloResult(
        names={0: "person", 2: "car"},
        boxes=FakeBoxes(
            cls=FakeArray([0, 2]),
            conf=FakeArray([0.91, 0.42]),
            xyxy=FakeArray([[1.0, 2.0, 30.0, 40.0], [5.0, 6.0, 70.0, 80.0]]),
            ids=None,
        ),
    )

    candidates = yolo_results_to_detection_candidates([result])

    assert candidates == [
        DetectionCandidate(
            class_id=0,
            class_name="person",
            confidence=0.91,
            bounding_box=BoundingBox(x1=1.0, y1=2.0, x2=30.0, y2=40.0),
            track_id=None,
        ),
        DetectionCandidate(
            class_id=2,
            class_name="car",
            confidence=0.42,
            bounding_box=BoundingBox(x1=5.0, y1=6.0, x2=70.0, y2=80.0),
            track_id=None,
        ),
    ]


def test_yolo_result_mapping_normalizes_numeric_track_ids() -> None:
    result = FakeYoloResult(
        names={0: "person"},
        boxes=FakeBoxes(
            cls=FakeArray([0]),
            conf=FakeArray([0.91]),
            xyxy=FakeArray([[1.0, 2.0, 30.0, 40.0]]),
            ids=FakeArray([12.0]),
        ),
    )

    candidates = yolo_results_to_detection_candidates([result])

    assert candidates[0].track_id == "12"


def test_ultralytics_object_detector_uses_injected_model() -> None:
    frame = np.zeros((10, 10, 3), dtype=np.uint8)
    fake_model = FakeModel(
        results=[
            FakeYoloResult(
                names={0: "person"},
                boxes=FakeBoxes(
                    cls=FakeArray([0]),
                    conf=FakeArray([0.91]),
                    xyxy=FakeArray([[1.0, 2.0, 3.0, 4.0]]),
                    ids=None,
                ),
            ),
        ],
    )
    detector = UltralyticsObjectDetector(model=fake_model, model_name_or_path="fake-model")

    candidates = detector.detect(frame)

    assert detector.model_name == "fake-model"
    assert fake_model.predicted_frames == [frame]
    assert len(candidates) == 1
    assert candidates[0].class_name == "person"


@pytest.mark.slow
@pytest.mark.skipif(
    os.environ.get("CEREAL_RUN_SLOW_DETECTION") != "1",
    reason="real model loading is opt-in for local checks",
)
def test_ultralytics_object_detector_loads_real_model() -> None:
    detector = UltralyticsObjectDetector()
    frame = np.zeros((32, 32, 3), dtype=np.uint8)

    assert isinstance(detector.detect(frame), list)


@dataclass(frozen=True)
class FakeArray:
    values: object

    def tolist(self) -> object:
        return self.values


@dataclass(frozen=True)
class FakeBoxes:
    cls: FakeArray
    conf: FakeArray
    xyxy: FakeArray
    ids: FakeArray | None

    @property
    def id(self) -> FakeArray | None:
        return self.ids


@dataclass(frozen=True)
class FakeYoloResult:
    names: dict[int, str]
    boxes: FakeBoxes


@dataclass
class FakeModel:
    results: list[FakeYoloResult]
    predicted_frames: list[np.ndarray]

    def __init__(self, results: Sequence[FakeYoloResult]) -> None:
        self.results = list(results)
        self.predicted_frames = []

    def predict(self, frame: np.ndarray, *, verbose: bool) -> list[FakeYoloResult]:
        assert verbose is False
        self.predicted_frames.append(frame)
        return self.results
