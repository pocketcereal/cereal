"""Deep Agents runtime composition for Cereal agents."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, Protocol, cast

from deepagents import create_deep_agent

from cereal.agents.deepagents_adapter import (
    DeepAgentsSubagentConfig,
    to_deepagents_subagent_config,
)
from cereal.agents.types import AgentDefinition, AgentDefinitionKind

if TYPE_CHECKING:
    from collections.abc import Callable

    from cereal.agents.registry import AgentRegistry
    from cereal.settings import OrchestratorSettings

__all__ = [
    "ORCHESTRATOR_SMOKE_PROMPT",
    "compose_deepagents_agent",
    "compose_orchestrator_agent",
    "run_orchestrator_smoke",
]

ORCHESTRATOR_SMOKE_PROMPT = "Reply with exactly: ready"


class InvokableAgent(Protocol):
    """Minimal protocol for smoke-invoked agent runtimes."""

    def invoke(self, payload: dict[str, Any]) -> object:
        """Invoke the agent with one payload."""


def compose_deepagents_agent(
    definition: AgentDefinition,
    *,
    model: str,
    subagents: Sequence[AgentDefinition] = (),
    tools: Sequence[Any] = (),
    create_agent: Callable[..., object] = create_deep_agent,
) -> object:
    """Compose one Cereal Agent definition with the Deep Agents harness."""
    return create_agent(
        model=model,
        tools=list(tools),
        system_prompt=definition.instructions,
        subagents=[
            _subagent_config_to_deepagents_dict(to_deepagents_subagent_config(subagent))
            for subagent in subagents
        ],
        name=definition.name,
    )


def compose_orchestrator_agent(
    orchestrator: AgentDefinition,
    registry: AgentRegistry,
    settings: OrchestratorSettings,
    *,
    create_agent: Callable[..., object] = create_deep_agent,
) -> object:
    """Compose the Cereal Orchestrator agent with registered subagents."""
    if orchestrator.kind != AgentDefinitionKind.ORCHESTRATOR:
        msg = "Orchestrator composition requires an orchestrator Agent definition"
        raise ValueError(msg)
    subagents = [
        definition
        for definition in registry.list()
        if definition.kind == AgentDefinitionKind.SPECIALIZED_SUBAGENT
    ]
    return compose_deepagents_agent(
        orchestrator,
        model=settings.model,
        subagents=subagents,
        create_agent=create_agent,
    )


def run_orchestrator_smoke(agent: InvokableAgent) -> str:
    """Invoke the Orchestrator agent with the fixed local smoke prompt."""
    result = agent.invoke(
        {"messages": [{"role": "user", "content": ORCHESTRATOR_SMOKE_PROMPT}]},
    )
    return _final_message_content(result)


def _subagent_config_to_deepagents_dict(config: DeepAgentsSubagentConfig) -> dict[str, Any]:
    return {
        "name": config.name,
        "description": config.description,
        "system_prompt": config.system_prompt,
    }


def _final_message_content(result: object) -> str:
    if isinstance(result, Mapping):
        result_mapping = cast("Mapping[str, object]", result)
        messages = result_mapping.get("messages")
        if isinstance(messages, Sequence) and messages:
            last_message = messages[-1]
            content = getattr(last_message, "content", None)
            if isinstance(content, str):
                return content
            if isinstance(last_message, Mapping):
                last_message_mapping = cast("Mapping[str, object]", last_message)
                mapped_content = last_message_mapping.get("content")
                if isinstance(mapped_content, str):
                    return mapped_content
    if isinstance(result, str):
        return result
    return str(result)
