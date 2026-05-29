"""Agent runtime binding values."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cereal.agents.tools import AgentToolCatalog
    from cereal.agents.types import AgentDefinition

__all__ = ["AgentRuntimeBinding", "bind_agent_runtime"]


@dataclass(frozen=True)
class AgentRuntimeBinding:
    """Agent definition paired with runtime-resolved dependencies."""

    definition: AgentDefinition
    tools: tuple[object, ...] = ()


def bind_agent_runtime(
    definition: AgentDefinition,
    tool_catalog: AgentToolCatalog,
) -> AgentRuntimeBinding:
    """Resolve one Agent definition into a harness-neutral runtime binding."""
    return AgentRuntimeBinding(
        definition=definition,
        tools=tool_catalog.resolve(definition),
    )
