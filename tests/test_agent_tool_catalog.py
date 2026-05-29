"""Tests for Agent tool catalog resolution."""

from __future__ import annotations

import pytest

from cereal.agents import AgentDefinition, AgentDefinitionKind
from cereal.agents.tools import AgentToolCatalog


def test_agent_tool_catalog_resolves_declared_tools() -> None:
    first_tool = object()
    second_tool = object()
    catalog = AgentToolCatalog(
        {
            "find_detection_events": first_tool,
            "list_detection_labels": second_tool,
        },
    )

    resolved = catalog.resolve(
        AgentDefinition(
            name="detection-lookup",
            description="Finds Detection events.",
            kind=AgentDefinitionKind.SPECIALIZED_SUBAGENT,
            instructions="Lookup detections.",
            tools=("find_detection_events", "list_detection_labels"),
        ),
    )

    assert resolved == (first_tool, second_tool)


def test_agent_tool_catalog_rejects_missing_declared_tool() -> None:
    catalog = AgentToolCatalog({})

    with pytest.raises(KeyError, match="find_detection_events"):
        catalog.resolve(
            AgentDefinition(
                name="detection-lookup",
                description="Finds Detection events.",
                kind=AgentDefinitionKind.SPECIALIZED_SUBAGENT,
                instructions="Lookup detections.",
                tools=("find_detection_events",),
            ),
        )
