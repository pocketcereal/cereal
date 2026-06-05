"""Tests for Object track planning smoke composition."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from cereal.agents.object_track_planning_smoke import run_object_track_planning_smoke
from cereal.agents.trace import AgentRunTrace, AgentTraceEvent, AgentTraceEventKind
from cereal.settings import OrchestratorSettings

EXPECTED_CAR_TRACK_COUNT = 1
EXPECTED_CAR_EVENT_COUNT = 3


def test_run_object_track_planning_smoke_chooses_track_lookup_for_count_prompt() -> None:
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
        detection_lookup = subagents[0]
        tool_by_name = {tool.__name__: tool for tool in detection_lookup["tools"]}

        class FakeAgent:
            def invoke(self, payload: dict[str, Any]) -> dict[str, object]:
                del payload
                trace = AgentRunTrace().record(
                    AgentTraceEvent(kind=AgentTraceEventKind.AGENT_INVOKED, agent_name=name),
                )
                trace = trace.record(
                    AgentTraceEvent(
                        kind=AgentTraceEventKind.SUBAGENT_DELEGATED,
                        agent_name=name,
                        subagent_name=str(detection_lookup["name"]),
                    ),
                )
                lookup_args = {"label": "car", "source_name": "smoke_fixture"}
                trace = trace.record(
                    AgentTraceEvent(
                        kind=AgentTraceEventKind.TOOL_CALLED,
                        agent_name=str(detection_lookup["name"]),
                        tool_name="lookup_object_tracks",
                        arguments=lookup_args,
                    ),
                )
                lookup_result = tool_by_name["lookup_object_tracks"](**lookup_args)
                trace = trace.record(
                    AgentTraceEvent(
                        kind=AgentTraceEventKind.TOOL_RETURNED,
                        agent_name=str(detection_lookup["name"]),
                        tool_name="lookup_object_tracks",
                        result=lookup_result,
                    ),
                )
                return {"messages": [{"content": str(lookup_result)}], "trace": trace}

        return FakeAgent()

    result = run_object_track_planning_smoke(
        OrchestratorSettings(model="ollama:qwen3:8b"),
        create_agent=create_agent,
    )

    assert [
        (event.kind, event.agent_name, event.subagent_name, event.tool_name)
        for event in result.trace.events
    ] == [
        (AgentTraceEventKind.AGENT_INVOKED, "orchestrator", None, None),
        (AgentTraceEventKind.SUBAGENT_DELEGATED, "orchestrator", "detection-lookup", None),
        (AgentTraceEventKind.TOOL_CALLED, "detection-lookup", None, "lookup_object_tracks"),
        (AgentTraceEventKind.TOOL_RETURNED, "detection-lookup", None, "lookup_object_tracks"),
    ]
    lookup_result = result.trace.events[3].result
    assert isinstance(lookup_result, Mapping)
    lookup_mapping = cast("Mapping[str, object]", lookup_result)
    assert lookup_mapping["label"] == "car"
    assert lookup_mapping["track_count"] == EXPECTED_CAR_TRACK_COUNT
    assert lookup_mapping["event_count"] == EXPECTED_CAR_EVENT_COUNT
    assert lookup_mapping["follow_up_capabilities"] == [
        "retrieve_evidence_window",
        "validate_visual_claim",
        "compare_candidates",
    ]
    candidates = cast("list[Mapping[str, object]]", lookup_mapping["candidates"])
    assert len(candidates) == EXPECTED_CAR_TRACK_COUNT
    assert candidates[0]["event_count"] == EXPECTED_CAR_EVENT_COUNT
    assert candidates[0]["grouping_basis"] == "detector_track_id"
