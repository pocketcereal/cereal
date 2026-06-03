"""Visual-query planning smoke composition."""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Protocol, cast

import numpy as np

from cereal.agents import AgentRegistry, load_agent_definition
from cereal.agents.deepagents_runtime import (
    InvokableAgent,
    compose_orchestrator_agent,
    final_message_content,
)
from cereal.agents.detection_lookup import make_detection_lookup_tool_catalog
from cereal.agents.detection_lookup_smoke import SMOKE_SOURCE_NAME
from cereal.agents.evidence import make_retrieve_evidence_window_tool
from cereal.agents.trace import AgentRunTrace
from cereal.agents.validation import make_validate_visual_claim_tool
from cereal.detection.store import SqliteDetectionStore
from cereal.detection.types import BoundingBox, DetectionEvent
from cereal.evidence.video import OpenCvEvidenceFrameReader

if TYPE_CHECKING:
    from collections.abc import Callable

    from cereal.evidence.types import EvidenceWindow
    from cereal.settings import OrchestratorSettings


class _OpenCvSmokeModule(Protocol):
    def VideoWriter_fourcc(self, code_1: str, code_2: str, code_3: str, code_4: str) -> int:  # noqa: N802
        """Return an OpenCV video codec code."""


__all__ = [
    "VISUAL_QUERY_PLANNING_SMOKE_PROMPT",
    "VisualQueryPlanningSmokeResult",
    "run_visual_query_planning_smoke",
]

VISUAL_QUERY_PLANNING_SMOKE_PROMPT = (
    "Use detection-lookup to find one candidate car Detection event in "
    f'source_name="{SMOKE_SOURCE_NAME}", retrieve its evidence window, validate '
    'the claim "the object is a car", and reply exactly with supported: car.'
)
SMOKE_OBSERVED_TIME = datetime(2026, 5, 29, 12, tzinfo=UTC)


@dataclass(frozen=True)
class VisualQueryPlanningSmokeResult:
    """Result of one visual-query planning smoke run."""

    output: str
    trace: AgentRunTrace


def run_visual_query_planning_smoke(
    settings: OrchestratorSettings,
    *,
    create_agent: Callable[..., object] | None = None,
) -> VisualQueryPlanningSmokeResult:
    """Run visual-query planning smoke against deterministic local evidence."""
    with TemporaryDirectory() as directory:
        root = Path(directory)
        evidence_uri = _write_smoke_video(root / "visual-query-planning-smoke.avi")
        store = SqliteDetectionStore(root / "detections.sqlite3")
        try:
            store.insert_many([_smoke_detection_event(evidence_uri)])
            evidence_windows: dict[str, EvidenceWindow] = {}
            evidence_tool = make_retrieve_evidence_window_tool(
                reader=OpenCvEvidenceFrameReader(),
                evidence_windows=evidence_windows,
            )
            validation_tool = make_validate_visual_claim_tool(evidence_windows=evidence_windows)
            orchestrator = load_agent_definition("agents/orchestrator.agent")
            detection_lookup = load_agent_definition("agents/detection-lookup.agent")
            if create_agent is None:
                agent = compose_orchestrator_agent(
                    orchestrator,
                    AgentRegistry((detection_lookup,)),
                    settings,
                    make_detection_lookup_tool_catalog(store),
                    tools=(evidence_tool, validation_tool),
                )
            else:
                agent = compose_orchestrator_agent(
                    orchestrator,
                    AgentRegistry((detection_lookup,)),
                    settings,
                    make_detection_lookup_tool_catalog(store),
                    tools=(evidence_tool, validation_tool),
                    create_agent=create_agent,
                )
            result = cast("InvokableAgent", agent).invoke(
                {"messages": [{"role": "user", "content": VISUAL_QUERY_PLANNING_SMOKE_PROMPT}]},
            )
            return VisualQueryPlanningSmokeResult(
                output=final_message_content(result),
                trace=_trace_from_result(result),
            )
        finally:
            with suppress(Exception):
                store.close()


def _smoke_detection_event(evidence_uri: str) -> DetectionEvent:
    return DetectionEvent(
        source_name=SMOKE_SOURCE_NAME,
        observed_time=SMOKE_OBSERVED_TIME,
        media_time_ms=200,
        frame_index=2,
        frame_width=64,
        frame_height=48,
        evidence_uri=evidence_uri,
        model_name="smoke-detector",
        class_id=2,
        class_name="car",
        confidence=0.91,
        bounding_box=BoundingBox(10, 20, 40, 42),
        track_id=None,
    )


def _write_smoke_video(path: Path) -> str:
    import cv2  # noqa: PLC0415

    fourcc = cast("_OpenCvSmokeModule", cv2).VideoWriter_fourcc(*"MJPG")
    writer = cv2.VideoWriter(
        str(path),
        fourcc,
        10,
        (64, 48),
    )
    if not writer.isOpened():
        msg = f"could not create visual-query planning smoke video: {path}"
        raise RuntimeError(msg)
    try:
        for index in range(5):
            frame = np.zeros((48, 64, 3), dtype=np.uint8)
            frame[:, :] = (index * 40, 80, 200 - index * 30)
            writer.write(frame)
    finally:
        writer.release()
    return path.as_uri()


def _trace_from_result(result: object) -> AgentRunTrace:
    if isinstance(result, Mapping):
        trace = cast("Mapping[str, object]", result).get("trace")
        if isinstance(trace, AgentRunTrace):
            return trace
    return AgentRunTrace()
