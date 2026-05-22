"""Smoke tests for the Cereal CLI runtime."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cereal.cli import main
from tests.helpers import write_config

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_main_accepts_config_flag(tmp_path: Path) -> None:
    """The CLI accepts a config file selected by flag."""
    config_path = tmp_path / "settings.yaml"
    write_config(config_path, storage=tmp_path / "storage")

    assert main(["--config", str(config_path)]) == 0


def test_main_accepts_config_flag_from_process_argv(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The installed CLI accepts a config file selected by flag."""
    config_path = tmp_path / "settings.yaml"
    write_config(config_path, storage=tmp_path / "storage")
    monkeypatch.setattr("sys.argv", ["cereal", "--config", str(config_path)])

    assert main() == 0
