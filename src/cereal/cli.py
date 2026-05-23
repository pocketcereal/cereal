"""Command-line entrypoint for Cereal."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cereal.media.preview import run_preview
from cereal.settings import Settings, load_settings, select_config_path

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence


def run(settings: Settings, *, preview: Callable[[Settings], None] = run_preview) -> int:
    """Run the Cereal CLI."""
    preview(settings)
    return 0


def main(
    argv: Sequence[str] | None = None,
    *,
    preview: Callable[[Settings], None] = run_preview,
) -> int:
    """Run the Cereal process entrypoint."""
    config_path = select_config_path(argv)
    settings = load_settings(config_path)
    return run(settings, preview=preview)
