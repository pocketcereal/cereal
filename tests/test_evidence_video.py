"""Tests for local video Evidence readers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
import pytest

from cereal.evidence.video import EvidenceVideoReadError, OpenCvEvidenceFrameReader
from tests.helpers import write_static_video

if TYPE_CHECKING:
    from pathlib import Path

FRAME_HEIGHT = 24
FRAME_WIDTH = 32


def test_opencv_evidence_frame_reader_reads_local_file_uri_frame(tmp_path: Path) -> None:
    source_file = tmp_path / "sample.avi"
    write_static_video(source_file, width=FRAME_WIDTH, height=FRAME_HEIGHT)
    reader = OpenCvEvidenceFrameReader()

    frame = reader.read_frame(source_file.as_uri(), 0)

    assert frame is not None
    assert frame.frame_index == 0
    assert frame.image.shape == (FRAME_HEIGHT, FRAME_WIDTH, 3)


def test_opencv_evidence_frame_reader_rejects_non_file_uri() -> None:
    reader = OpenCvEvidenceFrameReader()

    with pytest.raises(EvidenceVideoReadError, match="file://"):
        reader.read_frame("device:0", 0)


def test_opencv_evidence_frame_reader_returns_none_for_unavailable_frame(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "sample.avi"
    write_static_video(source_file, width=FRAME_WIDTH, height=FRAME_HEIGHT)
    reader = OpenCvEvidenceFrameReader()

    assert reader.read_frame(source_file.as_uri(), 999) is None


def test_opencv_evidence_frame_reader_returns_none_when_seek_fails(tmp_path: Path) -> None:
    source_file = tmp_path / "sample.avi"
    source_file.touch()
    reader = OpenCvEvidenceFrameReader(
        opencv_factory=lambda: FakeOpenCvModule(FakeCapture(opened=True, seek_succeeds=False)),
    )

    assert reader.read_frame(source_file.as_uri(), 0) is None


@dataclass
class FakeCapture:
    opened: bool
    seek_succeeds: bool
    released: bool = False

    def isOpened(self) -> bool:  # noqa: N802 - mirrors OpenCV API.
        return self.opened

    def set(self, property_id: int, value: float) -> bool:
        del property_id, value
        return self.seek_succeeds

    def get(self, property_id: int) -> float:
        del property_id
        return 0

    def read(self) -> tuple[bool, np.ndarray | None]:
        return True, np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)

    def release(self) -> None:
        self.released = True


@dataclass(frozen=True)
class FakeOpenCvModule:
    capture: FakeCapture
    CAP_PROP_POS_MSEC: int = 0
    CAP_PROP_POS_FRAMES: int = 1

    def VideoCapture(self, filename: str) -> FakeCapture:  # noqa: N802 - mirrors OpenCV API.
        del filename
        return self.capture
