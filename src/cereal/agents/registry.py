"""Static Agent definition registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cereal.agents.types import AgentDefinition

__all__ = ["AgentRegistry"]


@dataclass(frozen=True)
class AgentRegistry:
    """Lookup table for available Agent definitions."""

    definitions: tuple[AgentDefinition, ...]

    def __post_init__(self) -> None:
        """Reject ambiguous registry contents."""
        names = [definition.name for definition in self.definitions]
        if len(names) != len(set(names)):
            msg = "duplicate Agent definition name"
            raise ValueError(msg)

    def get(self, name: str) -> AgentDefinition | None:
        """Return an Agent definition by name if registered."""
        return self._definitions_by_name().get(name)

    def require(self, name: str) -> AgentDefinition:
        """Return an Agent definition by name or raise KeyError."""
        if (definition := self.get(name)) is None:
            raise KeyError(name)
        return definition

    def list(self) -> tuple[AgentDefinition, ...]:
        """Return all Agent definitions sorted by stable name."""
        return tuple(sorted(self.definitions, key=lambda definition: definition.name))

    def _definitions_by_name(self) -> dict[str, AgentDefinition]:
        return {definition.name: definition for definition in self.definitions}
