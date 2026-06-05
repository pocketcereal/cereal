"""Tests for direct Detection lookup Agent smoke composition."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cereal.agents.detection_lookup_smoke import (
    run_detection_lookup_tool_smoke,
    seed_detection_lookup_smoke_store,
)
from cereal.detection.store import DetectionLabelQuery, SqliteDetectionStore
from cereal.settings import OrchestratorSettings

if TYPE_CHECKING:
    from pathlib import Path


def test_seed_detection_lookup_smoke_store_creates_fixture_labels(tmp_path: Path) -> None:
    store = SqliteDetectionStore(tmp_path / "detections.sqlite3")
    try:
        seed_detection_lookup_smoke_store(store)

        labels = store.list_labels(DetectionLabelQuery())
    finally:
        store.close()

    assert [(label.class_name, label.event_count) for label in labels] == [
        ("car", 2),
        ("person", 1),
    ]


def test_run_detection_lookup_tool_smoke_uses_seeded_store_with_agent_tool_call() -> None:
    created: dict[str, Any] = {}

    class FakeAgent:
        def __init__(self, tools: list[Any]) -> None:
            self._tools = tools

        def invoke(self, payload: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
            created["payload"] = payload
            list_labels = next(
                tool
                for tool in self._tools
                if getattr(tool, "__name__", "") == "list_detection_labels"
            )
            result = list_labels()
            labels = ", ".join(label["label"] for label in result["labels"])
            return {"messages": [{"content": labels}]}

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
        return FakeAgent(tools)

    result = run_detection_lookup_tool_smoke(
        OrchestratorSettings(model="ollama:qwen3:8b"),
        create_agent=create_agent,
    )

    assert result == "car, person"
    assert created["model"] == "ollama:qwen3:8b"
    assert created["name"] == "detection-lookup"
    assert [tool.__name__ for tool in created["tools"]] == [
        "find_detection_events",
        "list_detection_labels",
        "lookup_object_tracks",
    ]
    assert created["subagents"] == []
