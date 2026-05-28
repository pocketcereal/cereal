"""Tests for Deep Agents adapter boundaries."""

from __future__ import annotations

import pytest

from cereal.agents import (
    AgentDefinition,
    AgentDefinitionKind,
    DeepAgentsSubagentConfig,
    DeferredAgentDefinitionFields,
    to_deepagents_subagent_config,
)


def test_specialized_subagent_definition_maps_to_deepagents_config() -> None:
    definition = AgentDefinition(
        name="vehicle-color-validator",
        description="Validates vehicle color claims against visual evidence.",
        kind=AgentDefinitionKind.SPECIALIZED_SUBAGENT,
        instructions="Validate whether the vehicle color claim is supported.",
    )

    config = to_deepagents_subagent_config(definition)

    assert config == DeepAgentsSubagentConfig(
        name="vehicle-color-validator",
        description="Validates vehicle color claims against visual evidence.",
        system_prompt="Validate whether the vehicle color claim is supported.",
    )


def test_deepagents_config_preserves_deferred_fields() -> None:
    definition = AgentDefinition(
        name="vehicle-color-validator",
        description="Validates vehicle color claims against visual evidence.",
        kind=AgentDefinitionKind.SPECIALIZED_SUBAGENT,
        instructions="Validate whether the vehicle color claim is supported.",
        tools=("visual_validation",),
        skills=("vehicle-color",),
        permissions=("read-evidence",),
        response_format="visual-validation",
    )

    config = to_deepagents_subagent_config(definition)

    assert config.deferred == DeferredAgentDefinitionFields(
        tools=("visual_validation",),
        skills=("vehicle-color",),
        permissions=("read-evidence",),
        response_format="visual-validation",
    )


def test_deepagents_subagent_config_rejects_orchestrator_definition() -> None:
    definition = AgentDefinition(
        name="orchestrator",
        description="Plans Cereal analysis strategies.",
        kind=AgentDefinitionKind.ORCHESTRATOR,
        instructions="Choose an analysis strategy.",
    )

    with pytest.raises(ValueError, match="specialized-subagent"):
        to_deepagents_subagent_config(definition)
