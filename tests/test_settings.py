"""Tests for Cereal settings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cereal.settings import load_settings, select_config_path
from tests.helpers import write_config

if TYPE_CHECKING:
    from pathlib import Path


def test_load_settings_accepts_yaml_config(tmp_path: Path) -> None:
    """Settings can load from a YAML configuration file."""
    config_path = tmp_path / "settings.yaml"
    write_config(config_path, storage=tmp_path / "storage")

    load_settings(config_path)


def test_load_settings_includes_orchestrator_model(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yaml"
    write_config(
        config_path,
        storage=tmp_path / "storage",
        orchestrator_model="ollama:qwen2.5:7b",
    )

    settings = load_settings(config_path)

    assert settings.orchestrator.model == "ollama:qwen2.5:7b"


def test_config_flag_selects_yaml_config(tmp_path: Path) -> None:
    """The explicit config flag can select a YAML configuration file."""
    flag_config = tmp_path / "flag.yaml"
    write_config(flag_config, storage=tmp_path / "flag")

    load_settings(select_config_path(["--config", str(flag_config)]))
