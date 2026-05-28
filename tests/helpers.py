"""Shared test helpers for Cereal."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

ConfigSource = tuple[str, str] | tuple[str, str, str]


def write_config(  # noqa: PLR0913
    config_path: Path,
    *,
    storage: Path,
    source_name: str = "sample",
    source_uri: str | None = None,
    sources: Sequence[ConfigSource] | None = None,
    orchestrator_model: str = "ollama:qwen2.5:7b",
) -> None:
    """Write a minimal valid Cereal settings file."""
    configured_sources = sources
    if configured_sources is None:
        source_path = config_path.parent / f"{source_name}.mp4"
        configured_sources = ((source_name, source_uri or source_path.as_uri()),)

    source_lines = "\n".join(_source_config_line(source) for source in configured_sources)
    config_path.write_text(
        f"""
storage: {storage}
orchestrator:
  model: {orchestrator_model}
sources:
{source_lines}
""".strip(),
        encoding="utf-8",
    )


def _source_config_line(source: ConfigSource) -> str:
    name, uri, *extra = source
    line = f"  - name: {name}\n    uri: {uri}"
    if extra:
        line = f"{line}\n    write: {extra[0]}"
    return line


def make_static_frame(*, width: int, height: int) -> np.ndarray:
    """Return a plain RGB test frame."""
    return np.zeros((height, width, 3), dtype=np.uint8)


def write_static_video(
    path: Path,
    *,
    width: int,
    height: int,
    frame_count: int = 1,
) -> None:
    """Write a small MJPG video for OpenCV-backed tests."""
    cv2 = pytest.importorskip("cv2")
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*"MJPG"),
        1,
        (width, height),
    )
    if not writer.isOpened():
        msg = f"could not create static test video: {path}"
        raise RuntimeError(msg)
    for _ in range(frame_count):
        writer.write(make_static_frame(width=width, height=height))
    writer.release()
