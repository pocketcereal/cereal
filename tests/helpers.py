"""Shared test helpers for Cereal."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path


def write_config(
    config_path: Path,
    *,
    storage: Path,
    source_name: str = "sample",
    source_uri: str | None = None,
    sources: Sequence[tuple[str, str]] | None = None,
) -> None:
    """Write a minimal valid Cereal settings file."""
    configured_sources = sources
    if configured_sources is None:
        source_path = config_path.parent / f"{source_name}.mp4"
        configured_sources = ((source_name, source_uri or source_path.as_uri()),)

    source_lines = "\n".join(
        f"  - name: {name}\n    uri: {uri}" for name, uri in configured_sources
    )
    config_path.write_text(
        f"""
storage: {storage}
sources:
{source_lines}
""".strip(),
        encoding="utf-8",
    )
