"""Command-line entrypoint for Cereal."""

import sys

from cereal.settings import Settings, load_settings


def run(settings: Settings) -> int:
    """Run the Cereal CLI."""
    sys.stdout.write(f"{settings.app_name}\n")
    return 0


def main() -> None:
    """Run the Cereal process entrypoint."""
    raise SystemExit(run(load_settings()))
