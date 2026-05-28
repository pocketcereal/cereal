"""Ultralytics-backed object detector adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol, cast

from cereal.detection.types import BoundingBox, DetectionCandidate

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

    import numpy as np

__all__ = [
    "DEFAULT_YOLO_MODEL",
    "UltralyticsObjectDetector",
    "yolo_results_to_detection_candidates",
]

DEFAULT_YOLO_MODEL = "yolov8n.pt"


@dataclass
class UltralyticsObjectDetector:
    """Object detector adapter for Ultralytics YOLO models."""

    model_name_or_path: str = DEFAULT_YOLO_MODEL
    model: _YoloModel | None = None

    def __post_init__(self) -> None:
        """Load Ultralytics only when this adapter is constructed without a model."""
        if self.model is None:
            from ultralytics import YOLO  # noqa: PLC0415

            self.model = cast("_YoloModel", YOLO(self.model_name_or_path))

    @property
    def model_name(self) -> str:
        """Return configured model identity without touching the model."""
        return self.model_name_or_path

    def detect(self, frame: np.ndarray) -> list[DetectionCandidate]:
        """Run YOLO prediction and map results to Detection candidates."""
        if self.model is None:
            msg = "YOLO model is not initialized"
            raise RuntimeError(msg)

        results = self.model.predict(frame, verbose=False)
        return yolo_results_to_detection_candidates(cast("Iterable[_YoloResult]", results))


def yolo_results_to_detection_candidates(results: Iterable[object]) -> list[DetectionCandidate]:
    """Map Ultralytics-like prediction results to Detection candidates."""
    candidates: list[DetectionCandidate] = []
    for raw_result in results:
        result = cast("_YoloResult", raw_result)
        boxes = result.boxes
        class_ids = _to_list(boxes.cls)
        confidences = _to_list(boxes.conf)
        coordinates = _to_list(boxes.xyxy)
        track_ids = _to_optional_list(getattr(boxes, "id", None))

        for index, class_id_value in enumerate(class_ids):
            class_id = _required_int(class_id_value)
            x1, y1, x2, y2 = cast("Sequence[object]", coordinates[index])
            candidates.append(
                DetectionCandidate(
                    class_id=class_id,
                    class_name=_class_name(result.names, class_id),
                    confidence=_required_float(confidences[index]),
                    bounding_box=BoundingBox(
                        x1=_required_float(x1),
                        y1=_required_float(y1),
                        x2=_required_float(x2),
                        y2=_required_float(y2),
                    ),
                    track_id=_track_id_at(track_ids, index),
                ),
            )
    return candidates


class _YoloModel(Protocol):
    """Model-like object with Ultralytics predict behavior."""

    def predict(self, frame: np.ndarray, *, verbose: bool) -> object:
        """Return prediction results."""


class _YoloBoxes(Protocol):
    """Boxes object returned on an Ultralytics result."""

    cls: object
    conf: object
    xyxy: object

    @property
    def id(self) -> object | None:
        """Return optional tracking IDs."""


class _YoloResult(Protocol):
    """Minimal result shape consumed by the mapper."""

    names: Mapping[int, str]
    boxes: _YoloBoxes


class _CpuConvertible(Protocol):
    """Value that can be moved to CPU before conversion."""

    def cpu(self) -> object:
        """Return CPU-backed value."""


class _NumpyConvertible(Protocol):
    """Value that can expose a numpy representation."""

    def numpy(self) -> object:
        """Return numpy-backed value."""


class _ListConvertible(Protocol):
    """Value that can expose a Python list."""

    def tolist(self) -> object:
        """Return list-like value."""


def _to_optional_list(value: object | None) -> list[object] | None:
    if value is None:
        return None
    return _to_list(value)


def _to_list(value: object) -> list[object]:
    if hasattr(value, "cpu"):
        value = cast("_CpuConvertible", value).cpu()
    if hasattr(value, "numpy"):
        value = cast("_NumpyConvertible", value).numpy()
    if hasattr(value, "tolist"):
        listed = cast("_ListConvertible", value).tolist()
        if isinstance(listed, list):
            return cast("list[object]", listed)
        value = listed
    return list(cast("Iterable[object]", value))


def _class_name(names: Mapping[int, str], class_id: int) -> str:
    return names.get(class_id, str(class_id))


def _track_id_at(track_ids: list[object] | None, index: int) -> str | None:
    if track_ids is None:
        return None

    track_id = track_ids[index]
    if track_id is None:
        return None
    if isinstance(track_id, float) and track_id.is_integer():
        return str(int(track_id))
    return str(track_id)


def _required_int(value: object) -> int:
    return int(cast("Any", value))


def _required_float(value: object) -> float:
    return float(cast("Any", value))
