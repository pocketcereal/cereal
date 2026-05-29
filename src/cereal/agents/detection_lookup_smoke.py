"""Direct Detection lookup Agent smoke composition."""

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, cast

from cereal.agents import load_agent_definition
from cereal.agents.deepagents_runtime import (
    InvokableAgent,
    compose_detection_lookup_agent,
    run_detection_lookup_smoke,
)
from cereal.agents.detection_lookup import make_detection_lookup_tool_catalog
from cereal.detection.store import SqliteDetectionStore
from cereal.detection.types import BoundingBox, DetectionEvent

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from cereal.detection.store import DetectionStore
    from cereal.settings import OrchestratorSettings

__all__ = [
    "run_detection_lookup_tool_smoke",
    "seed_detection_lookup_smoke_store",
]

SMOKE_SOURCE_NAME = "smoke_fixture"
SMOKE_OBSERVED_TIME = datetime(2026, 5, 29, 12, tzinfo=UTC)


@dataclass(frozen=True)
class _SmokeDetectionSpec:
    class_id: int
    class_name: str
    confidence: float
    frame_index: int
    media_time_ms: int
    evidence_uri: str
    bounding_box: BoundingBox


def run_detection_lookup_tool_smoke(
    settings: OrchestratorSettings,
    *,
    create_agent: Callable[..., object] | None = None,
) -> str:
    """Run a local direct Detection lookup Agent smoke against a seeded store."""
    with TemporaryDirectory() as directory:
        store = SqliteDetectionStore(_database_path(directory))
        try:
            seed_detection_lookup_smoke_store(store)
            definition = load_agent_definition("agents/detection-lookup.agent")
            agent = compose_detection_lookup_agent(
                definition,
                settings,
                make_detection_lookup_tool_catalog(store),
                **({} if create_agent is None else {"create_agent": create_agent}),
            )
            return run_detection_lookup_smoke(cast("InvokableAgent", agent))
        finally:
            with suppress(Exception):
                store.close()


def seed_detection_lookup_smoke_store(store: DetectionStore) -> None:
    """Seed deterministic Detection events for the direct Agent smoke."""
    store.insert_many(_smoke_detection_events())


def _smoke_detection_events() -> Sequence[DetectionEvent]:
    return (
        _smoke_event(
            _SmokeDetectionSpec(
                2,
                "car",
                0.91,
                10,
                1000,
                "frame-10.jpg",
                BoundingBox(10, 20, 80, 90),
            ),
        ),
        _smoke_event(
            _SmokeDetectionSpec(
                2,
                "car",
                0.87,
                11,
                1100,
                "frame-11.jpg",
                BoundingBox(100, 30, 180, 120),
            ),
        ),
        _smoke_event(
            _SmokeDetectionSpec(
                0,
                "person",
                0.95,
                12,
                1200,
                "frame-12.jpg",
                BoundingBox(200, 40, 260, 160),
            ),
        ),
    )


def _smoke_event(spec: _SmokeDetectionSpec) -> DetectionEvent:
    return DetectionEvent(
        source_name=SMOKE_SOURCE_NAME,
        observed_time=SMOKE_OBSERVED_TIME,
        media_time_ms=spec.media_time_ms,
        frame_index=spec.frame_index,
        frame_width=640,
        frame_height=480,
        evidence_uri=f"file:///tmp/cereal-smoke/{spec.evidence_uri}",
        model_name="smoke-detector",
        class_id=spec.class_id,
        class_name=spec.class_name,
        confidence=spec.confidence,
        bounding_box=spec.bounding_box,
        track_id=None,
    )


def _database_path(directory: str) -> Path:
    return Path(directory) / "detection-lookup-smoke.sqlite3"
