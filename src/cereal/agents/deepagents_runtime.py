"""Deep Agents runtime composition for Cereal agents."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, Protocol, cast

from deepagents import create_deep_agent

from cereal.agents.binding import AgentRuntimeBinding, bind_agent_runtime
from cereal.agents.deepagents_adapter import (
    DeepAgentsSubagentConfig,
    to_deepagents_subagent_config,
)
from cereal.agents.types import AgentDefinition, AgentDefinitionKind

if TYPE_CHECKING:
    from collections.abc import Callable

    from cereal.agents.registry import AgentRegistry
    from cereal.agents.tools import AgentToolCatalog
    from cereal.settings import OrchestratorSettings

__all__ = [
    "DETECTION_LOOKUP_SMOKE_PROMPT",
    "ORCHESTRATOR_SMOKE_PROMPT",
    "compose_deepagents_agent",
    "compose_detection_lookup_agent",
    "compose_orchestrator_agent",
    "final_message_content",
    "run_detection_lookup_smoke",
    "run_orchestrator_smoke",
]

ORCHESTRATOR_SMOKE_PROMPT = "Output only the literal token ready."
DETECTION_LOOKUP_SMOKE_PROMPT = (
    'Use the list_detection_labels tool with source_name="smoke_fixture". '
    "Reply with exactly the detected labels, comma-separated, and no extra text."
)


class InvokableAgent(Protocol):
    """Minimal protocol for smoke-invoked agent runtimes."""

    def invoke(self, payload: dict[str, Any]) -> object:
        """Invoke the agent with one payload."""


def compose_deepagents_agent(
    definition: AgentDefinition,
    *,
    model: str,
    subagents: Sequence[AgentRuntimeBinding] = (),
    tools: Sequence[Any] = (),
    create_agent: Callable[..., object] = create_deep_agent,
) -> object:
    """Compose one Cereal Agent definition with the Deep Agents harness."""
    return create_agent(
        model=model,
        tools=list(tools),
        system_prompt=definition.instructions,
        subagents=[
            _subagent_binding_to_deepagents_dict(subagent_binding) for subagent_binding in subagents
        ],
        name=definition.name,
    )


def compose_orchestrator_agent(  # noqa: PLR0913 - composition receives explicit deps.
    orchestrator: AgentDefinition,
    registry: AgentRegistry,
    settings: OrchestratorSettings,
    tool_catalog: AgentToolCatalog,
    *,
    tools: Sequence[Any] = (),
    create_agent: Callable[..., object] = create_deep_agent,
) -> object:
    """Compose the Cereal Orchestrator agent with registered subagents."""
    if orchestrator.kind != AgentDefinitionKind.ORCHESTRATOR:
        msg = "Orchestrator composition requires an orchestrator Agent definition"
        raise ValueError(msg)
    subagents = tuple(
        bind_agent_runtime(definition, tool_catalog)
        for definition in registry.list()
        if definition.kind == AgentDefinitionKind.SPECIALIZED_SUBAGENT
    )
    return compose_deepagents_agent(
        orchestrator,
        model=settings.model,
        subagents=subagents,
        tools=tools,
        create_agent=create_agent,
    )


def compose_detection_lookup_agent(
    definition: AgentDefinition,
    settings: OrchestratorSettings,
    tool_catalog: AgentToolCatalog,
    *,
    create_agent: Callable[..., object] = create_deep_agent,
) -> object:
    """Compose the detection-lookup Specialized subagent in isolation."""
    if definition.kind != AgentDefinitionKind.SPECIALIZED_SUBAGENT:
        msg = "Detection lookup composition requires a specialized-subagent Agent definition"
        raise ValueError(msg)
    if definition.name != "detection-lookup":
        msg = "Detection lookup composition requires the detection-lookup Agent definition"
        raise ValueError(msg)
    return compose_deepagents_agent(
        definition,
        model=settings.model,
        tools=tool_catalog.resolve(definition),
        create_agent=create_agent,
    )


def run_orchestrator_smoke(agent: InvokableAgent) -> str:
    """Invoke the Orchestrator agent with the fixed local smoke prompt."""
    return _invoke_with_prompt(agent, ORCHESTRATOR_SMOKE_PROMPT)


def run_detection_lookup_smoke(agent: InvokableAgent) -> str:
    """Invoke the Detection lookup agent with the fixed local smoke prompt."""
    return _invoke_with_prompt(agent, DETECTION_LOOKUP_SMOKE_PROMPT)


def _invoke_with_prompt(agent: InvokableAgent, prompt: str) -> str:
    result = agent.invoke(
        {"messages": [{"role": "user", "content": prompt}]},
    )
    return final_message_content(result)


def _subagent_binding_to_deepagents_dict(binding: AgentRuntimeBinding) -> dict[str, Any]:
    subagent = _subagent_config_to_deepagents_dict(
        to_deepagents_subagent_config(binding.definition),
    )
    if binding.tools:
        subagent["tools"] = list(binding.tools)
    return subagent


def _subagent_config_to_deepagents_dict(config: DeepAgentsSubagentConfig) -> dict[str, Any]:
    return {
        "name": config.name,
        "description": config.description,
        "system_prompt": config.system_prompt,
    }


def final_message_content(result: object) -> str:
    """Extract final text content from a harness invocation result."""
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
