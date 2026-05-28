"""Load Agent definitions from local `.agent` directories."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from cereal.agents.types import AgentDefinition, AgentDefinitionKind

if TYPE_CHECKING:
    from os import PathLike

__all__ = ["AgentDefinitionLoadError", "load_agent_definition"]

AGENT_TOML_FILENAME = "agent.toml"
INSTRUCTIONS_FILENAME = "instructions.md"


class AgentDefinitionLoadError(RuntimeError):
    """Raised when a local Agent definition cannot be loaded."""


def load_agent_definition(agent_dir: str | PathLike[str]) -> AgentDefinition:
    """Load one Agent definition from a local `.agent` directory."""
    path = Path(agent_dir)
    if not path.is_dir():
        msg = f"Agent definition path must be a directory: {path}"
        raise AgentDefinitionLoadError(msg)
    if path.suffix != ".agent":
        msg = f"Agent definition directory must use .agent suffix: {path}"
        raise AgentDefinitionLoadError(msg)

    agent_toml_path = path / AGENT_TOML_FILENAME
    instructions_path = path / INSTRUCTIONS_FILENAME
    if not agent_toml_path.exists():
        msg = f"Agent definition missing {AGENT_TOML_FILENAME}: {path}"
        raise AgentDefinitionLoadError(msg)
    if not instructions_path.exists():
        msg = f"Agent definition missing {INSTRUCTIONS_FILENAME}: {path}"
        raise AgentDefinitionLoadError(msg)

    try:
        raw_metadata = tomllib.loads(agent_toml_path.read_text(encoding="utf-8"))
        instructions = instructions_path.read_text(encoding="utf-8")
        return AgentDefinition(
            name=_required_str(raw_metadata, "name"),
            description=_required_str(raw_metadata, "description"),
            kind=_required_kind(raw_metadata),
            instructions=instructions,
            tools=_optional_str_tuple(raw_metadata, "tools"),
            skills=_optional_str_tuple(raw_metadata, "skills"),
            permissions=_optional_str_tuple(raw_metadata, "permissions"),
            response_format=_optional_str(raw_metadata, "response_format"),
        )
    except (OSError, TypeError, ValueError, tomllib.TOMLDecodeError) as error:
        msg = f"Could not load Agent definition from {path}: {error}"
        raise AgentDefinitionLoadError(msg) from error


def _required_str(metadata: dict[str, Any], field_name: str) -> str:
    value = metadata.get(field_name)
    if not isinstance(value, str):
        msg = f"{field_name} must be a string"
        raise TypeError(msg)
    return value


def _required_kind(metadata: dict[str, Any]) -> AgentDefinitionKind:
    value = _required_str(metadata, "kind")
    try:
        return AgentDefinitionKind(value)
    except ValueError as error:
        msg = f"kind must be one of: {', '.join(kind.value for kind in AgentDefinitionKind)}"
        raise ValueError(msg) from error


def _optional_str(metadata: dict[str, Any], field_name: str) -> str | None:
    value = metadata.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str):
        msg = f"{field_name} must be a string"
        raise TypeError(msg)
    return value


def _optional_str_tuple(metadata: dict[str, Any], field_name: str) -> tuple[str, ...]:
    value = metadata.get(field_name, ())
    if not isinstance(value, list | tuple):
        msg = f"{field_name} must be a list of strings"
        raise TypeError(msg)
    if not all(isinstance(item, str) for item in value):
        msg = f"{field_name} must be a list of strings"
        raise TypeError(msg)
    return cast("tuple[str, ...]", tuple(value))
