"""Tests for Orchestrator to Detection lookup delegation smoke."""

from __future__ import annotations

from typing import Any

from cereal.agents.detection_lookup_smoke import SMOKE_SOURCE_NAME
from cereal.agents.orchestrator_delegation_smoke import run_orchestrator_delegation_smoke
from cereal.agents.trace import AgentRunTrace, AgentTraceEvent, AgentTraceEventKind
from cereal.settings import OrchestratorSettings


def test_run_orchestrator_delegation_smoke_records_delegated_tool_use() -> None:
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

        class FakeAgent:
            def invoke(self, payload: dict[str, Any]) -> dict[str, object]:
                del payload
                trace = AgentRunTrace().record(
                    AgentTraceEvent(
                        kind=AgentTraceEventKind.AGENT_INVOKED,
                        agent_name=name,
                    ),
                )
                subagent = subagents[0]
                trace = trace.record(
                    AgentTraceEvent(
                        kind=AgentTraceEventKind.SUBAGENT_DELEGATED,
                        agent_name=name,
                        subagent_name=str(subagent["name"]),
                    ),
                )
                list_labels = next(
                    tool
                    for tool in subagent["tools"]
                    if getattr(tool, "__name__", "") == "list_detection_labels"
                )
                arguments = {"source_name": SMOKE_SOURCE_NAME}
                trace = trace.record(
                    AgentTraceEvent(
                        kind=AgentTraceEventKind.TOOL_CALLED,
                        agent_name=str(subagent["name"]),
                        tool_name="list_detection_labels",
                        arguments=arguments,
                    ),
                )
                result = list_labels(**arguments)
                trace = trace.record(
                    AgentTraceEvent(
                        kind=AgentTraceEventKind.TOOL_RETURNED,
                        agent_name=str(subagent["name"]),
                        tool_name="list_detection_labels",
                        result=result,
                    ),
                )
                labels = ", ".join(label["label"] for label in result["labels"])
                return {"messages": [{"content": labels}], "trace": trace}

        return FakeAgent()

    result = run_orchestrator_delegation_smoke(
        OrchestratorSettings(model="ollama:qwen3:8b"),
        create_agent=create_agent,
    )

    assert result.output == "car, person"
    assert [
        (event.kind, event.agent_name, event.subagent_name, event.tool_name)
        for event in result.trace.events
    ] == [
        (AgentTraceEventKind.AGENT_INVOKED, "orchestrator", None, None),
        (AgentTraceEventKind.SUBAGENT_DELEGATED, "orchestrator", "detection-lookup", None),
        (AgentTraceEventKind.TOOL_CALLED, "detection-lookup", None, "list_detection_labels"),
        (AgentTraceEventKind.TOOL_RETURNED, "detection-lookup", None, "list_detection_labels"),
    ]
    assert result.trace.events[2].arguments == {"source_name": SMOKE_SOURCE_NAME}
    assert result.trace.events[3].result == {
        "labels": [
            {"label": "car", "event_count": 2},
            {"label": "person", "event_count": 1},
        ],
    }
