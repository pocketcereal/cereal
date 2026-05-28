"""Pure adapter values for Deep Agents harness configuration."""

from __future__ import annotations

from dataclasses import dataclass

from cereal.agents.types import AgentDefinition, AgentDefinitionKind

__all__ = [
    "DeepAgentsSubagentConfig",
    "DeferredAgentDefinitionFields",
    "to_deepagents_subagent_config",
]


@dataclass(frozen=True)
class DeferredAgentDefinitionFields:
    """Agent definition fields deferred until harness runtime composition."""

    tools: tuple[str, ...] = ()
    skills: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    response_format: str | None = None


@dataclass(frozen=True)
class DeepAgentsSubagentConfig:
    """Cereal-owned representation of a Deep Agents subagent config."""

    name: str
    description: str
    system_prompt: str
    deferred: DeferredAgentDefinitionFields = DeferredAgentDefinitionFields()


def to_deepagents_subagent_config(definition: AgentDefinition) -> DeepAgentsSubagentConfig:
    """Convert a Cereal Agent definition into a Deep Agents subagent config."""
    if definition.kind != AgentDefinitionKind.SPECIALIZED_SUBAGENT:
        msg = "Deep Agents subagent config requires a specialized-subagent Agent definition"
        raise ValueError(msg)
    return DeepAgentsSubagentConfig(
        name=definition.name,
        description=definition.description,
        system_prompt=definition.instructions,
        deferred=DeferredAgentDefinitionFields(
            tools=definition.tools,
            skills=definition.skills,
            permissions=definition.permissions,
            response_format=definition.response_format,
        ),
    )
