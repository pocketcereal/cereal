"""OpenCV-backed Evidence frame reader."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol, cast
from urllib.parse import unquote, urlparse

from cereal.evidence.types import EvidenceFrame

if TYPE_CHECKING:
    from collections.abc import Callable

    import numpy as np

__all__ = ["EvidenceVideoReadError", "OpenCvEvidenceFrameReader"]


class EvidenceVideoReadError(RuntimeError):
    """Raised when durable video evidence cannot be opened or addressed."""


class EvidenceVideoCapture(Protocol):
    """OpenCV-like video capture."""

    def isOpened(self) -> bool:  # noqa: N802 - mirrors OpenCV API.
        """Return whether the video opened."""

    def set(self, property_id: int, value: float) -> bool:
        """Set a capture property."""

    def get(self, property_id: int) -> float:
        """Return a capture property."""

    def read(self) -> tuple[bool, np.ndarray | None]:
        """Read one frame."""

    def release(self) -> None:
        """Release capture resources."""


class OpenCvModule(Protocol):
    """OpenCV module surface used by Evidence retrieval."""

    CAP_PROP_POS_MSEC: int
    CAP_PROP_POS_FRAMES: int

    def VideoCapture(self, filename: str) -> EvidenceVideoCapture:  # noqa: N802 - mirrors OpenCV API.
        """Open a video capture."""


class OpenCvEvidenceFrameReader:
    """Reads full Evidence frames from local file-backed videos."""

    def __init__(
        self,
        *,
        opencv_factory: Callable[[], OpenCvModule] | None = None,
    ) -> None:
        """Create a reader with lazy OpenCV loading."""
        self._opencv_factory = opencv_factory or _load_opencv

    def read_frame(self, evidence_uri: str, frame_index: int) -> EvidenceFrame | None:
        """Return one Evidence frame from a local file URI."""
        if frame_index < 0:
            msg = "frame_index must be non-negative"
            raise ValueError(msg)

        path = _local_file_path(evidence_uri)
        opencv = self._opencv_factory()
        capture = opencv.VideoCapture(str(path))
        try:
            if not capture.isOpened():
                msg = f"could not open evidence video: {path}"
                raise EvidenceVideoReadError(msg)

            if not capture.set(opencv.CAP_PROP_POS_FRAMES, float(frame_index)):
                return None
            has_frame, frame = capture.read()
            if not has_frame or frame is None:
                return None

            media_time_ms = round(capture.get(opencv.CAP_PROP_POS_MSEC))
            return EvidenceFrame(
                frame_index=frame_index,
                media_time_ms=media_time_ms,
                image=frame,
            )
        finally:
            capture.release()


def _local_file_path(evidence_uri: str) -> Path:
    parsed = urlparse(evidence_uri)
    if parsed.scheme != "file":
        msg = f"Evidence video reader only supports file:// URIs: {evidence_uri}"
        raise EvidenceVideoReadError(msg)

    path = Path(unquote(parsed.path))
    if not path.exists():
        msg = f"evidence video does not exist: {path}"
        raise EvidenceVideoReadError(msg)
    return path


def _load_opencv() -> OpenCvModule:
    import cv2  # noqa: PLC0415

    return cast("OpenCvModule", cv2)
