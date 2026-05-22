"""Shared test helpers for Cereal."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def write_config(config_path: Path, *, storage: Path, source_name: str = "sample") -> None:
    """Write a minimal valid Cereal settings file."""
    source_path = config_path.parent / f"{source_name}.mp4"
    config_path.write_text(
        f"""
storage: {storage}
sources:
  - name: {source_name}
    uri: {source_path.as_uri()}
""".strip(),
        encoding="utf-8",
    )
