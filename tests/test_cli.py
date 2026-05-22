"""Smoke tests for the Cereal CLI runtime."""

from cereal.cli import run
from cereal.settings import Settings


def test_run_returns_success() -> None:
    """The CLI runtime reports a successful exit code."""
    assert run(Settings(app_name="cereal")) == 0
