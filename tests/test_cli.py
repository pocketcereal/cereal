"""Smoke tests for the Cereal CLI runtime."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest

from cereal.cli import main, parse_cli_options
from cereal.detection.query import DetectionQueryOptions
from tests.helpers import write_config

if TYPE_CHECKING:
    from pathlib import Path

    from cereal.settings import Settings


def noop_preview(
    _settings: Settings,
    *,
    preview_enabled: bool = True,
    enable_overlays: bool = False,
) -> None:
    del preview_enabled
    del enable_overlays


def test_parse_cli_options_defaults_to_preview_enabled() -> None:
    options = parse_cli_options([])

    assert options.preview_enabled is True


def test_parse_cli_options_accepts_no_preview() -> None:
    options = parse_cli_options(["--no-preview"])

    assert options.preview_enabled is False


def test_parse_cli_options_accepts_explicit_preview() -> None:
    options = parse_cli_options(["--preview"])

    assert options.preview_enabled is True


def test_parse_cli_options_accepts_overlays() -> None:
    options = parse_cli_options(["--overlays"])

    assert options.overlays_enabled is True


def test_parse_cli_options_accepts_orchestrator_agent() -> None:
    options = parse_cli_options(["--agent", "orchestrator"])

    assert options.command == "agent"
    assert options.agent_name == "orchestrator"


def test_parse_cli_options_accepts_detection_lookup_agent() -> None:
    options = parse_cli_options(["--agent", "detection-lookup"])

    assert options.command == "agent"
    assert options.agent_name == "detection-lookup"


def test_parse_cli_options_accepts_orchestrator_delegation_agent() -> None:
    options = parse_cli_options(["--agent", "orchestrator-delegation"])

    assert options.command == "agent"
    assert options.agent_name == "orchestrator-delegation"


def test_parse_cli_options_accepts_detection_query_filters() -> None:
    options = parse_cli_options(
        [
            "detections",
            "--source",
            "camera",
            "--class",
            "person",
            "--min-confidence",
            "0.8",
            "--observed-start",
            "2026-05-24T12:00:00Z",
            "--media-start-ms",
            "1000",
            "--limit",
            "5",
        ],
    )

    assert options.command == "detections"
    assert options.detection_query == DetectionQueryOptions(
        source_name="camera",
        class_name="person",
        observed_time_start=datetime(2026, 5, 24, 12, tzinfo=UTC),
        media_time_start=1000,
        min_confidence=0.8,
        limit=5,
    )


def test_parse_cli_options_accepts_detection_query_config_after_subcommand(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "settings.yaml"

    options = parse_cli_options(["detections", "--config", str(config_path)])

    assert options.config_path == config_path


def test_main_passes_preview_flag_to_runtime(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yaml"
    write_config(config_path, storage=tmp_path / "storage")
    preview_values: list[bool] = []

    def preview(_settings: Settings, *, preview_enabled: bool, enable_overlays: bool) -> None:
        del enable_overlays
        preview_values.append(preview_enabled)

    assert main(["--config", str(config_path), "--no-preview"], preview=preview) == 0
    assert preview_values == [False]


def test_main_passes_overlay_flag_to_runtime(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yaml"
    write_config(config_path, storage=tmp_path / "storage")
    overlay_values: list[bool] = []

    def preview(_settings: Settings, *, preview_enabled: bool, enable_overlays: bool) -> None:
        assert preview_enabled is True
        overlay_values.append(enable_overlays)

    assert main(["--config", str(config_path), "--overlays"], preview=preview) == 0
    assert overlay_values == [True]


def test_main_runs_detection_query_command(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yaml"
    write_config(config_path, storage=tmp_path / "storage")
    queried: list[DetectionQueryOptions] = []

    def query(_settings: Settings, options: DetectionQueryOptions) -> int:
        queried.append(options)
        return 0

    assert (
        main(
            ["--config", str(config_path), "detections", "--class-name", "person"],
            preview=noop_preview,
            query=query,
        )
        == 0
    )
    assert queried == [
        DetectionQueryOptions(class_name="person"),
    ]


def test_main_runs_orchestrator_agent_smoke(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yaml"
    write_config(config_path, storage=tmp_path / "storage", orchestrator_model="fake-model")
    smoked: list[str] = []

    def agent_smoke(settings: Settings, agent_name: str) -> int:
        smoked.append(f"{agent_name}:{settings.orchestrator.model}")
        return 0

    assert (
        main(
            ["--config", str(config_path), "--agent", "orchestrator"],
            preview=noop_preview,
            agent_smoke=agent_smoke,
        )
        == 0
    )
    assert smoked == ["orchestrator:fake-model"]


def test_main_runs_detection_lookup_agent_smoke(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yaml"
    write_config(config_path, storage=tmp_path / "storage", orchestrator_model="fake-model")
    smoked: list[str] = []

    def agent_smoke(settings: Settings, agent_name: str) -> int:
        smoked.append(f"{agent_name}:{settings.orchestrator.model}")
        return 0

    assert (
        main(
            ["--config", str(config_path), "--agent", "detection-lookup"],
            preview=noop_preview,
            agent_smoke=agent_smoke,
        )
        == 0
    )
    assert smoked == ["detection-lookup:fake-model"]


def test_main_rejects_unsupported_agent_name(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yaml"
    write_config(config_path, storage=tmp_path / "storage")

    with pytest.raises(SystemExit):
        main(["--config", str(config_path), "--agent", "missing-agent"], preview=noop_preview)


def test_main_rejects_conflicting_preview_flags(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yaml"
    write_config(config_path, storage=tmp_path / "storage")

    with pytest.raises(SystemExit):
        main(["--config", str(config_path), "--preview", "--no-preview"], preview=noop_preview)


def test_main_accepts_config_flag(tmp_path: Path) -> None:
    """The CLI accepts a config file selected by flag."""
    config_path = tmp_path / "settings.yaml"
    write_config(config_path, storage=tmp_path / "storage")

    assert main(["--config", str(config_path)], preview=noop_preview) == 0


def test_main_starts_preview_after_loading_settings(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yaml"
    write_config(config_path, storage=tmp_path / "storage")
    previewed_storage_paths: list[Path] = []

    def preview(
        settings: Settings,
        *,
        preview_enabled: bool,
        enable_overlays: bool,
    ) -> None:
        assert preview_enabled is True
        assert enable_overlays is False
        previewed_storage_paths.append(settings.storage)

    assert main(["--config", str(config_path)], preview=preview) == 0
    assert previewed_storage_paths == [tmp_path / "storage"]


def test_main_accepts_config_flag_from_process_argv(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The installed CLI accepts a config file selected by flag."""
    config_path = tmp_path / "settings.yaml"
    write_config(config_path, storage=tmp_path / "storage")
    monkeypatch.setattr("sys.argv", ["cereal", "--config", str(config_path)])

    assert main(preview=noop_preview) == 0


def test_main_loads_default_settings_path_without_config_flag(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config" / "settings.yaml"
    config_path.parent.mkdir()
    write_config(config_path, storage=tmp_path / "storage")
    previewed_storage_paths: list[Path] = []
    monkeypatch.chdir(tmp_path)

    def preview(
        settings: Settings,
        *,
        preview_enabled: bool,
        enable_overlays: bool,
    ) -> None:
        assert preview_enabled is True
        assert enable_overlays is False
        previewed_storage_paths.append(settings.storage)

    assert main([], preview=preview) == 0
    assert previewed_storage_paths == [tmp_path / "storage"]
