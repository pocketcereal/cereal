"""Agent tool catalog resolution."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

    from cereal.agents.types import AgentDefinition

__all__ = ["AgentToolCatalog"]


class AgentToolCatalog:
    """Resolve Agent definition tool names to callables or tool objects."""

    def __init__(self, tools: Mapping[str, object]) -> None:
        """Create a catalog from stable tool names to tool objects."""
        self._tools = dict(tools)

    def resolve(self, definition: AgentDefinition) -> tuple[object, ...]:
        """Return tools declared by an Agent definition in declaration order."""
        resolved: list[object] = []
        for tool_name in definition.tools:
            try:
                resolved.append(self._tools[tool_name])
            except KeyError as error:
                raise KeyError(tool_name) from error
        return tuple(resolved)
