"""Object track planning smoke composition."""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, cast

from cereal.agents import AgentRegistry, load_agent_definition
from cereal.agents.deepagents_runtime import (
    InvokableAgent,
    compose_orchestrator_agent,
    final_message_content,
)
from cereal.agents.detection_lookup import make_detection_lookup_tool_catalog
from cereal.agents.detection_lookup_smoke import SMOKE_SOURCE_NAME
from cereal.agents.trace import AgentRunTrace
from cereal.detection.store import SqliteDetectionStore
from cereal.detection.types import BoundingBox, DetectionEvent

if TYPE_CHECKING:
    from collections.abc import Callable

    from cereal.detection.store import DetectionStore
    from cereal.settings import OrchestratorSettings

__all__ = [
    "OBJECT_TRACK_PLANNING_SMOKE_PROMPT",
    "ObjectTrackPlanningSmokeResult",
    "run_object_track_planning_smoke",
    "seed_object_track_planning_store",
]

OBJECT_TRACK_PLANNING_SMOKE_PROMPT = (
    "A user asks how many cars appear in "
    f'source_name="{SMOKE_SOURCE_NAME}". Use the detection-lookup subagent to look '
    "up object tracks for the car label and reply with the candidate Object track "
    "summary, not a final natural-language count."
)
SMOKE_OBSERVED_TIME = datetime(2026, 5, 29, 12, tzinfo=UTC)


@dataclass(frozen=True)
class ObjectTrackPlanningSmokeResult:
    """Result of one Object track planning smoke run."""

    output: str
    trace: AgentRunTrace


def run_object_track_planning_smoke(
    settings: OrchestratorSettings,
    *,
    create_agent: Callable[..., object] | None = None,
) -> ObjectTrackPlanningSmokeResult:
    """Run a local Orchestrator to Object track lookup smoke against a seeded store."""
    with TemporaryDirectory() as directory:
        store = SqliteDetectionStore(Path(directory) / "object-track-planning-smoke.sqlite3")
        try:
            seed_object_track_planning_store(store)
            orchestrator = load_agent_definition("agents/orchestrator.agent")
            detection_lookup = load_agent_definition("agents/detection-lookup.agent")
            if create_agent is None:
                agent = compose_orchestrator_agent(
                    orchestrator,
                    AgentRegistry((detection_lookup,)),
                    settings,
                    make_detection_lookup_tool_catalog(store),
                )
            else:
                agent = compose_orchestrator_agent(
                    orchestrator,
                    AgentRegistry((detection_lookup,)),
                    settings,
                    make_detection_lookup_tool_catalog(store),
                    create_agent=create_agent,
                )
            result = cast("InvokableAgent", agent).invoke(
                {"messages": [{"role": "user", "content": OBJECT_TRACK_PLANNING_SMOKE_PROMPT}]},
            )
            return ObjectTrackPlanningSmokeResult(
                output=final_message_content(result),
                trace=_trace_from_result(result),
            )
        finally:
            with suppress(Exception):
                store.close()


def seed_object_track_planning_store(store: DetectionStore) -> None:
    """Seed three car detections that share one detector track plus one person."""
    store.insert_many(
        [
            _smoke_event("car", 0.80, 10, track_id="car-1"),
            _smoke_event("car", 0.93, 11, track_id="car-1"),
            _smoke_event("car", 0.88, 12, track_id="car-1"),
            _smoke_event("person", 0.95, 11, track_id="person-1"),
        ],
    )


def _smoke_event(
    class_name: str,
    confidence: float,
    frame_index: int,
    *,
    track_id: str,
) -> DetectionEvent:
    return DetectionEvent(
        source_name=SMOKE_SOURCE_NAME,
        observed_time=SMOKE_OBSERVED_TIME,
        media_time_ms=frame_index * 100,
        frame_index=frame_index,
        frame_width=640,
        frame_height=480,
        evidence_uri=f"file:///tmp/cereal-smoke/frame-{frame_index}.jpg",
        model_name="smoke-detector",
        class_id=2 if class_name == "car" else 0,
        class_name=class_name,
        confidence=confidence,
        bounding_box=BoundingBox(10, 20, 80, 90),
        track_id=track_id,
    )


def _trace_from_result(result: object) -> AgentRunTrace:
    if isinstance(result, Mapping):
        trace = cast("Mapping[str, object]", result).get("trace")
        if isinstance(trace, AgentRunTrace):
            return trace
    return AgentRunTrace()
