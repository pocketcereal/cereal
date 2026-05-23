"""Tests for recording path and writer boundaries."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest

from cereal.media.recording import (
    FfmpegFrameWriter,
    WriterContext,
    recording_artifact_path,
)

if TYPE_CHECKING:
    from pathlib import Path

DEFAULT_RECORDING_FPS = 30
FRAME_HEIGHT = 480
FRAME_WIDTH = 640


def test_recording_path_uses_source_name_date_and_unix_timestamp(tmp_path: Path) -> None:
    recorded_at = datetime(2026, 5, 23, 1, 2, 3, tzinfo=UTC)

    artifact_path = recording_artifact_path(
        storage_root=tmp_path,
        source_name="camera",
        recorded_at=recorded_at,
        writer_context=WriterContext(),
    )

    assert artifact_path == tmp_path / "camera" / "2026-05-23" / "1779498123.mp4"
    assert not artifact_path.parent.exists()


def test_writer_context_carries_prototype_defaults() -> None:
    writer_context = WriterContext()

    assert writer_context.extension == ".mp4"
    assert writer_context.codec == "libx264"
    assert writer_context.fps == DEFAULT_RECORDING_FPS


def test_recording_path_uses_writer_context_extension(tmp_path: Path) -> None:
    recorded_at = datetime(2026, 5, 23, 1, 2, 3, tzinfo=UTC)

    artifact_path = recording_artifact_path(
        storage_root=tmp_path,
        source_name="camera",
        recorded_at=recorded_at,
        writer_context=WriterContext(extension=".mkv", codec="FFV1"),
    )

    assert artifact_path == tmp_path / "camera" / "2026-05-23" / "1779498123.mkv"


def test_ffmpeg_frame_writer_starts_lazily_and_finalizes_on_release(tmp_path: Path) -> None:
    artifact_path = tmp_path / "storage" / "camera" / "2026-05-23" / "1779498123.mp4"
    started_commands: list[list[str]] = []
    process = FakeFfmpegProcess()

    def start_process(command: list[str]) -> FakeFfmpegProcess:
        started_commands.append(command)
        return process

    writer = FfmpegFrameWriter(
        artifact_path=artifact_path,
        writer_context=WriterContext(),
        process_factory=start_process,
    )

    assert not artifact_path.parent.exists()
    assert started_commands == []

    writer.write(FakeBytesFrame(shape=(FRAME_HEIGHT, FRAME_WIDTH, 3), payload=b"frame"))
    writer.release()

    assert artifact_path.parent.exists()
    assert process.stdin.written == [b"frame"]
    assert process.stdin.closed is True
    assert process.waited is True
    assert started_commands == [
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "bgr24",
            "-s",
            f"{FRAME_WIDTH}x{FRAME_HEIGHT}",
            "-r",
            str(DEFAULT_RECORDING_FPS),
            "-i",
            "pipe:0",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-shortest",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-profile:v",
            "high",
            "-bf",
            "0",
            "-pix_fmt",
            "yuv420p",
            "-colorspace",
            "bt709",
            "-color_primaries",
            "bt709",
            "-color_trc",
            "bt709",
            "-c:a",
            "aac",
            "-b:a",
            "96k",
            "-movflags",
            "+faststart",
            "-brand",
            "mp42",
            str(artifact_path),
        ],
    ]


def test_ffmpeg_frame_writer_does_not_create_artifact_parent_without_frames(tmp_path: Path) -> None:
    artifact_path = tmp_path / "storage" / "camera" / "2026-05-23" / "1779498123.mp4"
    writer = FfmpegFrameWriter(
        artifact_path=artifact_path,
        writer_context=WriterContext(),
        process_factory=lambda _command: raise_unexpected_ffmpeg_process(),
    )

    writer.release()

    assert not artifact_path.parent.exists()


def test_ffmpeg_frame_writer_errors_when_process_fails(tmp_path: Path) -> None:
    writer = FfmpegFrameWriter(
        artifact_path=tmp_path / "recording.mp4",
        writer_context=WriterContext(),
        process_factory=lambda _command: FakeFfmpegProcess(return_code=1),
    )

    writer.write(FakeBytesFrame(shape=(FRAME_HEIGHT, FRAME_WIDTH, 3), payload=b"frame"))

    with pytest.raises(RuntimeError):
        writer.release()


def test_default_ffmpeg_frame_writer_creates_readable_mp4_recording(tmp_path: Path) -> None:
    import cv2  # noqa: PLC0415
    import numpy as np  # noqa: PLC0415

    artifact_path = tmp_path / "recording.mp4"
    writer = FfmpegFrameWriter(
        artifact_path=artifact_path,
        writer_context=WriterContext(),
    )

    for frame_index in range(3):
        frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
        frame[:, :, 1] = frame_index * 60
        writer.write(frame)
    writer.release()

    capture = cv2.VideoCapture(str(artifact_path))
    try:
        assert capture.isOpened()
        has_frame, frame = capture.read()
        assert has_frame
        assert frame is not None
    finally:
        capture.release()


class FakeBytesFrame:
    def __init__(self, *, shape: tuple[int, int, int], payload: bytes) -> None:
        self.shape = shape
        self.payload = payload

    def tobytes(self) -> bytes:
        return self.payload


class FakeStdin:
    def __init__(self) -> None:
        self.written: list[bytes] = []
        self.closed = False

    def write(self, payload: bytes) -> int:
        self.written.append(payload)
        return len(payload)

    def close(self) -> None:
        self.closed = True


class FakeFfmpegProcess:
    def __init__(self, *, return_code: int = 0) -> None:
        self.stdin = FakeStdin()
        self.return_code = return_code
        self.waited = False

    def wait(self) -> int:
        self.waited = True
        return self.return_code


def raise_unexpected_ffmpeg_process() -> FakeFfmpegProcess:
    msg = "ffmpeg process should not start"
    raise AssertionError(msg)
