"""Tests for Agent definition loading and registry lookup."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from cereal.agents import (
    AgentDefinition,
    AgentDefinitionKind,
    AgentDefinitionLoadError,
    AgentRegistry,
    load_agent_definition,
)

if TYPE_CHECKING:
    from pathlib import Path


def test_load_agent_definition_from_local_agent_directory(tmp_path: Path) -> None:
    agent_dir = write_agent_definition(
        tmp_path,
        AgentDefinitionFixture(
            name="vehicle-color-validator",
            description="Validates vehicle color claims against visual evidence.",
            instructions="Validate whether the vehicle color claim is supported.",
            tools=("visual_validation",),
            skills=("vehicle-color",),
            permissions=("read-evidence",),
            response_format="visual-validation",
        ),
    )

    definition = load_agent_definition(agent_dir)

    assert definition == AgentDefinition(
        name="vehicle-color-validator",
        description="Validates vehicle color claims against visual evidence.",
        kind=AgentDefinitionKind.SPECIALIZED_SUBAGENT,
        instructions="Validate whether the vehicle color claim is supported.",
        tools=("visual_validation",),
        skills=("vehicle-color",),
        permissions=("read-evidence",),
        response_format="visual-validation",
    )


def test_load_agent_definition_rejects_non_agent_directory_suffix(tmp_path: Path) -> None:
    agent_dir = write_agent_definition(
        tmp_path,
        AgentDefinitionFixture(
            directory_name="vehicle-color-validator",
            name="vehicle-color-validator",
            description="Validates vehicle color claims against visual evidence.",
            instructions="Validate whether the vehicle color claim is supported.",
        ),
    )

    with pytest.raises(AgentDefinitionLoadError, match=r"\.agent"):
        load_agent_definition(agent_dir)


def test_load_agent_definition_rejects_non_directory_path(tmp_path: Path) -> None:
    agent_path = tmp_path / "vehicle-color-validator.agent"
    agent_path.write_text("", encoding="utf-8")

    with pytest.raises(AgentDefinitionLoadError, match="directory"):
        load_agent_definition(agent_path)


def test_load_agent_definition_rejects_missing_metadata(tmp_path: Path) -> None:
    agent_dir = tmp_path / "vehicle-color-validator.agent"
    agent_dir.mkdir()
    (agent_dir / "instructions.md").write_text(
        "Validate whether the vehicle color claim is supported.",
        encoding="utf-8",
    )

    with pytest.raises(AgentDefinitionLoadError, match=r"agent\.toml"):
        load_agent_definition(agent_dir)


def test_load_agent_definition_rejects_missing_instructions(tmp_path: Path) -> None:
    agent_dir = tmp_path / "vehicle-color-validator.agent"
    agent_dir.mkdir()
    (agent_dir / "agent.toml").write_text(
        """
name = "vehicle-color-validator"
description = "Validates vehicle color claims against visual evidence."
kind = "specialized-subagent"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(AgentDefinitionLoadError, match=r"instructions\.md"):
        load_agent_definition(agent_dir)


def test_load_agent_definition_rejects_unknown_kind(tmp_path: Path) -> None:
    agent_dir = write_agent_definition(
        tmp_path,
        AgentDefinitionFixture(
            name="vehicle-color-validator",
            description="Validates vehicle color claims against visual evidence.",
            kind="worker",
            instructions="Validate whether the vehicle color claim is supported.",
        ),
    )

    with pytest.raises(AgentDefinitionLoadError, match="kind"):
        load_agent_definition(agent_dir)


def test_load_agent_definition_rejects_blank_required_fields(tmp_path: Path) -> None:
    agent_dir = write_agent_definition(
        tmp_path,
        AgentDefinitionFixture(
            name=" ",
            description="Validates vehicle color claims against visual evidence.",
            instructions="Validate whether the vehicle color claim is supported.",
        ),
    )

    with pytest.raises(AgentDefinitionLoadError, match="name"):
        load_agent_definition(agent_dir)


def test_agent_registry_returns_definitions_by_name(tmp_path: Path) -> None:
    vehicle_color = load_agent_definition(
        write_agent_definition(
            tmp_path,
            AgentDefinitionFixture(
                name="vehicle-color-validator",
                description="Validates vehicle color claims against visual evidence.",
                instructions="Validate whether the vehicle color claim is supported.",
            ),
        ),
    )
    track_finder = load_agent_definition(
        write_agent_definition(
            tmp_path,
            AgentDefinitionFixture(
                name="track-finder",
                description="Groups detection events into likely object tracks.",
                instructions="Find likely object tracks from detection events.",
            ),
        ),
    )
    registry = AgentRegistry((vehicle_color, track_finder))

    assert registry.get("vehicle-color-validator") == vehicle_color
    assert registry.get("missing") is None
    assert registry.require("track-finder") == track_finder
    assert registry.list() == (track_finder, vehicle_color)


def test_agent_registry_rejects_duplicate_names(tmp_path: Path) -> None:
    first = load_agent_definition(
        write_agent_definition(
            tmp_path,
            AgentDefinitionFixture(
                name="vehicle-color-validator",
                description="Validates vehicle color claims against visual evidence.",
                instructions="Validate whether the vehicle color claim is supported.",
            ),
        ),
    )
    second = load_agent_definition(
        write_agent_definition(
            tmp_path,
            AgentDefinitionFixture(
                directory_name="vehicle-color-validator-copy.agent",
                name="vehicle-color-validator",
                description="Another definition with the same stable name.",
                instructions="Validate whether the vehicle color claim is supported.",
            ),
        ),
    )

    with pytest.raises(ValueError, match="duplicate"):
        AgentRegistry((first, second))


def test_repo_local_agent_definitions_load() -> None:
    orchestrator = load_agent_definition("agents/orchestrator.agent")
    detection_lookup = load_agent_definition("agents/detection-lookup.agent")

    assert orchestrator.kind == AgentDefinitionKind.ORCHESTRATOR
    assert detection_lookup.kind == AgentDefinitionKind.SPECIALIZED_SUBAGENT
    assert detection_lookup.tools == ("find_detection_events", "list_detection_labels")


@dataclass(frozen=True)
class AgentDefinitionFixture:
    name: str
    description: str
    instructions: str
    directory_name: str | None = None
    kind: str = "specialized-subagent"
    tools: tuple[str, ...] = ()
    skills: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    response_format: str | None = None


def write_agent_definition(
    root: Path,
    fixture: AgentDefinitionFixture,
) -> Path:
    agent_dir = root / (fixture.directory_name or f"{fixture.name.strip() or 'blank'}.agent")
    agent_dir.mkdir()
    optional_response_format = (
        f'\nresponse_format = "{fixture.response_format}"'
        if fixture.response_format is not None
        else ""
    )
    (agent_dir / "agent.toml").write_text(
        f"""
name = "{fixture.name}"
description = "{fixture.description}"
kind = "{fixture.kind}"
tools = [{quoted_csv(fixture.tools)}]
skills = [{quoted_csv(fixture.skills)}]
permissions = [{quoted_csv(fixture.permissions)}]{optional_response_format}
""".strip(),
        encoding="utf-8",
    )
    (agent_dir / "instructions.md").write_text(fixture.instructions, encoding="utf-8")
    return agent_dir


def quoted_csv(values: tuple[str, ...]) -> str:
    return ", ".join(f'"{value}"' for value in values)
