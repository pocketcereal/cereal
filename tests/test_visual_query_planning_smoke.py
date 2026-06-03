"""Tests for visual-query planning smoke composition."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from cereal.agents.trace import AgentRunTrace, AgentTraceEvent, AgentTraceEventKind
from cereal.agents.visual_query_planning_smoke import run_visual_query_planning_smoke
from cereal.settings import OrchestratorSettings

EXPECTED_EVIDENCE_FRAME_COUNT = 3


def test_run_visual_query_planning_smoke_records_exact_planning_sequence() -> None:
    def create_agent(
        *,
        model: str,
        tools: list[Any],
        system_prompt: str,
        subagents: list[dict[str, Any]],
        name: str,
    ) -> object:
        del model
        del system_prompt
        tool_by_name = {tool.__name__: tool for tool in tools}
        detection_lookup = subagents[0]
        detection_tool_by_name = {tool.__name__: tool for tool in detection_lookup["tools"]}

        class FakeAgent:
            def invoke(self, payload: dict[str, Any]) -> dict[str, object]:
                del payload
                trace = AgentRunTrace().record(
                    AgentTraceEvent(
                        kind=AgentTraceEventKind.AGENT_INVOKED,
                        agent_name=name,
                    ),
                )
                trace = trace.record(
                    AgentTraceEvent(
                        kind=AgentTraceEventKind.SUBAGENT_DELEGATED,
                        agent_name=name,
                        subagent_name=str(detection_lookup["name"]),
                    ),
                )
                detection_args = {
                    "label": "car",
                    "source_name": "smoke_fixture",
                    "limit": 1,
                }
                trace = trace.record(
                    AgentTraceEvent(
                        kind=AgentTraceEventKind.TOOL_CALLED,
                        agent_name=str(detection_lookup["name"]),
                        tool_name="find_detection_events",
                        arguments=detection_args,
                    ),
                )
                detection_result = detection_tool_by_name["find_detection_events"](
                    **detection_args,
                )
                trace = trace.record(
                    AgentTraceEvent(
                        kind=AgentTraceEventKind.TOOL_RETURNED,
                        agent_name=str(detection_lookup["name"]),
                        tool_name="find_detection_events",
                        result=detection_result,
                    ),
                )
                event = detection_result["events"][0]
                evidence_args = {
                    "detection_event_ref": {
                        "source_name": event["source_name"],
                        "frame_index": event["frame_index"],
                        "media_time_ms": event["media_time_ms"],
                        "observed_time": event["observed_time"],
                        "class_name": event["class_name"],
                        "confidence": event["confidence"],
                        "evidence_uri": event["evidence_uri"],
                        "bounding_box": event["bounding_box"],
                    },
                    "frame_radius": 1,
                }
                trace = trace.record(
                    AgentTraceEvent(
                        kind=AgentTraceEventKind.TOOL_CALLED,
                        agent_name=name,
                        tool_name="retrieve_evidence_window",
                        arguments=evidence_args,
                    ),
                )
                evidence_result = tool_by_name["retrieve_evidence_window"](**evidence_args)
                trace = trace.record(
                    AgentTraceEvent(
                        kind=AgentTraceEventKind.TOOL_RETURNED,
                        agent_name=name,
                        tool_name="retrieve_evidence_window",
                        result=evidence_result,
                    ),
                )
                validation_args = {
                    "claim": "the object is a car",
                    "evidence_window_ref": evidence_result["evidence_window_ref"],
                }
                trace = trace.record(
                    AgentTraceEvent(
                        kind=AgentTraceEventKind.TOOL_CALLED,
                        agent_name=name,
                        tool_name="validate_visual_claim",
                        arguments=validation_args,
                    ),
                )
                validation_result = tool_by_name["validate_visual_claim"](**validation_args)
                trace = trace.record(
                    AgentTraceEvent(
                        kind=AgentTraceEventKind.TOOL_RETURNED,
                        agent_name=name,
                        tool_name="validate_visual_claim",
                        result=validation_result,
                    ),
                )
                return {
                    "messages": [{"content": "supported: car"}],
                    "trace": trace,
                }

        return FakeAgent()

    result = run_visual_query_planning_smoke(
        OrchestratorSettings(model="ollama:qwen3:8b"),
        create_agent=create_agent,
    )

    assert result.output == "supported: car"
    assert [
        (event.kind, event.agent_name, event.subagent_name, event.tool_name)
        for event in result.trace.events
    ] == [
        (AgentTraceEventKind.AGENT_INVOKED, "orchestrator", None, None),
        (AgentTraceEventKind.SUBAGENT_DELEGATED, "orchestrator", "detection-lookup", None),
        (AgentTraceEventKind.TOOL_CALLED, "detection-lookup", None, "find_detection_events"),
        (AgentTraceEventKind.TOOL_RETURNED, "detection-lookup", None, "find_detection_events"),
        (AgentTraceEventKind.TOOL_CALLED, "orchestrator", None, "retrieve_evidence_window"),
        (AgentTraceEventKind.TOOL_RETURNED, "orchestrator", None, "retrieve_evidence_window"),
        (AgentTraceEventKind.TOOL_CALLED, "orchestrator", None, "validate_visual_claim"),
        (AgentTraceEventKind.TOOL_RETURNED, "orchestrator", None, "validate_visual_claim"),
    ]
    assert result.trace.events[2].arguments == {
        "label": "car",
        "source_name": "smoke_fixture",
        "limit": 1,
    }
    evidence_result = result.trace.events[5].result
    assert isinstance(evidence_result, Mapping)
    evidence_mapping = cast("Mapping[str, object]", evidence_result)
    assert evidence_mapping["frame_count"] == EXPECTED_EVIDENCE_FRAME_COUNT
    assert result.trace.events[7].result == {
        "claim": "the object is a car",
        "status": "supported",
        "class_name": "car",
        "evidence_window_ref": "run-local:smoke_fixture:2:car",
    }
