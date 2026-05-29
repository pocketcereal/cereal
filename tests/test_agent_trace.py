"""Tests for Agent run trace values."""

from __future__ import annotations

from cereal.agents.trace import AgentRunTrace, AgentTraceEvent, AgentTraceEventKind


def test_agent_run_trace_records_harness_visible_events() -> None:
    trace = AgentRunTrace().record(
        AgentTraceEvent(
            kind=AgentTraceEventKind.TOOL_CALLED,
            agent_name="detection-lookup",
            tool_name="list_detection_labels",
            arguments={"source_name": "smoke_fixture"},
        ),
    )

    assert trace.events == (
        AgentTraceEvent(
            kind=AgentTraceEventKind.TOOL_CALLED,
            agent_name="detection-lookup",
            tool_name="list_detection_labels",
            arguments={"source_name": "smoke_fixture"},
        ),
    )


def test_agent_trace_event_snapshots_payload_values() -> None:
    arguments = {"source_name": "smoke_fixture"}
    result = {"labels": [{"label": "car", "event_count": 2}]}

    trace = AgentRunTrace().record(
        AgentTraceEvent(
            kind=AgentTraceEventKind.TOOL_RETURNED,
            agent_name="detection-lookup",
            tool_name="list_detection_labels",
            arguments=arguments,
            result=result,
        ),
    )
    arguments["source_name"] = "camera"
    result["labels"].append({"label": "person", "event_count": 1})

    event = trace.events[0]
    assert event.arguments == {"source_name": "smoke_fixture"}
    assert event.result == {"labels": [{"label": "car", "event_count": 2}]}
