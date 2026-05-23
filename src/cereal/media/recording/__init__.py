"""Recording path and writer boundaries."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol, cast

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import datetime
    from pathlib import Path

__all__ = [
    "FfmpegFrameWriter",
    "FrameWriter",
    "WriterContext",
    "recording_artifact_path",
]


class FrameWriter(Protocol):
    """Writes preview Frames into a Recording artifact."""

    def write(self, frame: object) -> None:
        """Write one Frame."""

    def release(self) -> None:
        """Release writer resources."""


class FrameWithShape(Protocol):
    """Frame shape needed by raw-video writers."""

    shape: Any


class FrameWithBytes(FrameWithShape, Protocol):
    """Frame shape and bytes needed by ffmpeg raw-video input."""

    def tobytes(self) -> bytes:
        """Return the raw BGR frame bytes."""


class FfmpegProcess(Protocol):
    """Minimal subprocess boundary used by the ffmpeg writer."""

    stdin: Any

    def wait(self) -> int:
        """Wait for ffmpeg to finish."""


def _start_ffmpeg(command: list[str]) -> FfmpegProcess:
    return subprocess.Popen(command, stdin=subprocess.PIPE)  # noqa: S603


@dataclass(frozen=True)
class WriterContext:
    """Runtime recording defaults owned by Cereal."""

    extension: str = ".mp4"
    codec: str = "libx264"
    fps: int = 30


@dataclass
class FfmpegFrameWriter:
    """Lazy ffmpeg-backed Frame writer for player-compatible MP4 output."""

    artifact_path: Path
    writer_context: WriterContext
    process_factory: Callable[[list[str]], FfmpegProcess] = _start_ffmpeg
    _process: FfmpegProcess | None = None

    def write(self, frame: object) -> None:
        """Start ffmpeg on the first Frame, then pipe raw BGR bytes."""
        if self._process is None:
            self._process = self._start_process(frame)

        if self._process.stdin is None:
            msg = "ffmpeg writer stdin is not available"
            raise RuntimeError(msg)

        self._process.stdin.write(cast("FrameWithBytes", frame).tobytes())

    def release(self) -> None:
        """Close stdin so ffmpeg finalizes the MP4 artifact."""
        if self._process is None:
            return

        if self._process.stdin is not None:
            self._process.stdin.close()
        return_code = self._process.wait()
        if return_code != 0:
            msg = f"ffmpeg recording writer failed: {self.artifact_path}"
            raise RuntimeError(msg)

    def _start_process(self, frame: object) -> FfmpegProcess:
        self.artifact_path.parent.mkdir(parents=True, exist_ok=True)
        shape = cast("FrameWithShape", frame).shape
        height, width = shape[:2]
        return self.process_factory(
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
                f"{width}x{height}",
                "-r",
                str(self.writer_context.fps),
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
                self.writer_context.codec,
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
                str(self.artifact_path),
            ],
        )


def recording_artifact_path(
    *,
    storage_root: Path,
    source_name: str,
    recorded_at: datetime,
    writer_context: WriterContext,
) -> Path:
    """Derive the Recording artifact path without touching the filesystem."""
    return (
        storage_root
        / source_name
        / recorded_at.date().isoformat()
        / f"{int(recorded_at.timestamp())}{writer_context.extension}"
    )
