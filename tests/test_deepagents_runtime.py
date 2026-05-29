"""Tests for Deep Agents runtime composition."""

from __future__ import annotations

from typing import Any

import pytest

from cereal.agents import AgentDefinition, AgentDefinitionKind, AgentRegistry
from cereal.agents.deepagents_runtime import (
    DETECTION_LOOKUP_SMOKE_PROMPT,
    ORCHESTRATOR_SMOKE_PROMPT,
    compose_deepagents_agent,
    compose_detection_lookup_agent,
    compose_orchestrator_agent,
    run_detection_lookup_smoke,
    run_orchestrator_smoke,
)
from cereal.agents.tools import AgentToolCatalog
from cereal.settings import OrchestratorSettings


def test_compose_deepagents_agent_passes_definition_to_factory() -> None:
    created: dict[str, Any] = {}

    def create_agent(
        *,
        model: str,
        tools: list[Any],
        system_prompt: str,
        subagents: list[dict[str, Any]],
        name: str,
    ) -> object:
        created.update(
            {
                "model": model,
                "tools": tools,
                "system_prompt": system_prompt,
                "subagents": subagents,
                "name": name,
            },
        )
        return "agent"

    result = compose_deepagents_agent(
        orchestrator_definition(),
        model="ollama:qwen2.5:7b",
        create_agent=create_agent,
    )

    assert result == "agent"
    assert created == {
        "model": "ollama:qwen2.5:7b",
        "tools": [],
        "system_prompt": "Plan the work.",
        "subagents": [],
        "name": "orchestrator",
    }


def test_compose_orchestrator_agent_registers_specialized_subagents() -> None:
    created: dict[str, Any] = {}
    find_tool = object()
    list_tool = object()

    def create_agent(
        *,
        model: str,
        tools: list[Any],
        system_prompt: str,
        subagents: list[dict[str, Any]],
        name: str,
    ) -> object:
        del model
        del tools
        del system_prompt
        del name
        created["subagents"] = subagents
        return "orchestrator-agent"

    result = compose_orchestrator_agent(
        orchestrator_definition(),
        AgentRegistry(
            (
                detection_lookup_definition(
                    tools=("find_detection_events", "list_detection_labels"),
                ),
            ),
        ),
        OrchestratorSettings(model="ollama:qwen2.5:7b"),
        AgentToolCatalog(
            {
                "find_detection_events": find_tool,
                "list_detection_labels": list_tool,
            },
        ),
        create_agent=create_agent,
    )

    assert result == "orchestrator-agent"
    assert created["subagents"] == [
        {
            "name": "detection-lookup",
            "description": "Finds Detection events.",
            "system_prompt": "Lookup detections.",
            "tools": [find_tool, list_tool],
        },
    ]


def test_compose_detection_lookup_agent_resolves_declared_tools() -> None:
    created: dict[str, Any] = {}
    find_tool = object()
    list_tool = object()

    def create_agent(
        *,
        model: str,
        tools: list[Any],
        system_prompt: str,
        subagents: list[dict[str, Any]],
        name: str,
    ) -> object:
        del subagents
        created.update(
            {
                "model": model,
                "tools": tools,
                "system_prompt": system_prompt,
                "name": name,
            },
        )
        return "detection-lookup-agent"

    result = compose_detection_lookup_agent(
        detection_lookup_definition(tools=("find_detection_events", "list_detection_labels")),
        OrchestratorSettings(model="ollama:qwen2.5:7b"),
        AgentToolCatalog(
            {
                "find_detection_events": find_tool,
                "list_detection_labels": list_tool,
            },
        ),
        create_agent=create_agent,
    )

    assert result == "detection-lookup-agent"
    assert created == {
        "model": "ollama:qwen2.5:7b",
        "tools": [find_tool, list_tool],
        "system_prompt": "Lookup detections.",
        "name": "detection-lookup",
    }


def test_compose_orchestrator_agent_rejects_non_orchestrator_definition() -> None:
    with pytest.raises(ValueError, match="orchestrator"):
        compose_orchestrator_agent(
            detection_lookup_definition(),
            AgentRegistry(()),
            OrchestratorSettings(model="ollama:qwen2.5:7b"),
            AgentToolCatalog({}),
            create_agent=lambda **_: object(),
        )


def test_run_orchestrator_smoke_invokes_fixed_prompt() -> None:
    invoked: list[dict[str, Any]] = []

    class FakeMessage:
        content = "ready"

    class FakeAgent:
        def invoke(self, payload: dict[str, Any]) -> dict[str, list[object]]:
            invoked.append(payload)
            return {"messages": [{"content": ORCHESTRATOR_SMOKE_PROMPT}, FakeMessage()]}

    result = run_orchestrator_smoke(FakeAgent())

    assert result == "ready"
    assert invoked == [{"messages": [{"role": "user", "content": ORCHESTRATOR_SMOKE_PROMPT}]}]


def test_run_detection_lookup_smoke_invokes_fixed_prompt() -> None:
    invoked: list[dict[str, Any]] = []

    class FakeAgent:
        def invoke(self, payload: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
            invoked.append(payload)
            return {"messages": [{"content": "car, person"}]}

    result = run_detection_lookup_smoke(FakeAgent())

    assert result == "car, person"
    assert invoked == [
        {"messages": [{"role": "user", "content": DETECTION_LOOKUP_SMOKE_PROMPT}]},
    ]


def orchestrator_definition() -> AgentDefinition:
    return AgentDefinition(
        name="orchestrator",
        description="Plans Cereal analysis strategies.",
        kind=AgentDefinitionKind.ORCHESTRATOR,
        instructions="Plan the work.",
    )


def detection_lookup_definition(*, tools: tuple[str, ...] = ()) -> AgentDefinition:
    return AgentDefinition(
        name="detection-lookup",
        description="Finds Detection events.",
        kind=AgentDefinitionKind.SPECIALIZED_SUBAGENT,
        instructions="Lookup detections.",
        tools=tools,
    )
