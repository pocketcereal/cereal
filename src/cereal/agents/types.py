"""Agent definition value types."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

__all__ = ["AgentDefinition", "AgentDefinitionKind"]


class AgentDefinitionKind(StrEnum):
    """Supported Agent definition kinds."""

    ORCHESTRATOR = "orchestrator"
    SPECIALIZED_SUBAGENT = "specialized-subagent"


@dataclass(frozen=True)
class AgentDefinition:
    """Packaged description of an agent or subagent."""

    name: str
    description: str
    kind: AgentDefinitionKind
    instructions: str
    tools: tuple[str, ...] = ()
    skills: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    response_format: str | None = None

    def __post_init__(self) -> None:
        """Validate required Agent definition fields."""
        _require_non_blank("name", self.name)
        _require_non_blank("description", self.description)
        _require_non_blank("instructions", self.instructions)
        _require_non_blank_values("tools", self.tools)
        _require_non_blank_values("skills", self.skills)
        _require_non_blank_values("permissions", self.permissions)
        if self.response_format is not None:
            _require_non_blank("response_format", self.response_format)


def _require_non_blank(field_name: str, value: str) -> None:
    if not value.strip():
        msg = f"{field_name} must not be blank"
        raise ValueError(msg)


def _require_non_blank_values(field_name: str, values: tuple[str, ...]) -> None:
    for value in values:
        if not value.strip():
            msg = f"{field_name} values must not be blank"
            raise ValueError(msg)
