"""Agent definition contracts."""

from cereal.agents.binding import AgentRuntimeBinding, bind_agent_runtime
from cereal.agents.deepagents_adapter import (
    DeepAgentsSubagentConfig,
    DeferredAgentDefinitionFields,
    to_deepagents_subagent_config,
)
from cereal.agents.loader import AgentDefinitionLoadError, load_agent_definition
from cereal.agents.registry import AgentRegistry
from cereal.agents.tools import AgentToolCatalog
from cereal.agents.types import AgentDefinition, AgentDefinitionKind

__all__ = [
    "AgentDefinition",
    "AgentDefinitionKind",
    "AgentDefinitionLoadError",
    "AgentRegistry",
    "AgentRuntimeBinding",
    "AgentToolCatalog",
    "DeepAgentsSubagentConfig",
    "DeferredAgentDefinitionFields",
    "bind_agent_runtime",
    "load_agent_definition",
    "to_deepagents_subagent_config",
]
