"""Orchestrator to Detection lookup delegation smoke composition."""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import suppress
from dataclasses import dataclass
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
from cereal.agents.detection_lookup_smoke import (
    SMOKE_SOURCE_NAME,
    seed_detection_lookup_smoke_store,
)
from cereal.agents.trace import AgentRunTrace
from cereal.detection.store import SqliteDetectionStore

if TYPE_CHECKING:
    from collections.abc import Callable

    from cereal.settings import OrchestratorSettings

__all__ = [
    "ORCHESTRATOR_DELEGATION_SMOKE_PROMPT",
    "OrchestratorDelegationSmokeResult",
    "run_orchestrator_delegation_smoke",
]

ORCHESTRATOR_DELEGATION_SMOKE_PROMPT = (
    "Use the detection-lookup subagent to list detector labels for "
    f'source_name="{SMOKE_SOURCE_NAME}". Reply with exactly the detected labels, '
    "comma-separated, and no extra text."
)


@dataclass(frozen=True)
class OrchestratorDelegationSmokeResult:
    """Result of one Orchestrator delegation smoke run."""

    output: str
    trace: AgentRunTrace


def run_orchestrator_delegation_smoke(
    settings: OrchestratorSettings,
    *,
    create_agent: Callable[..., object] | None = None,
) -> OrchestratorDelegationSmokeResult:
    """Run a local Orchestrator to Detection lookup smoke against a seeded store."""
    with TemporaryDirectory() as directory:
        store = SqliteDetectionStore(_database_path(directory))
        try:
            seed_detection_lookup_smoke_store(store)
            orchestrator = load_agent_definition("agents/orchestrator.agent")
            detection_lookup = load_agent_definition("agents/detection-lookup.agent")
            agent = compose_orchestrator_agent(
                orchestrator,
                AgentRegistry((detection_lookup,)),
                settings,
                make_detection_lookup_tool_catalog(store),
                **({} if create_agent is None else {"create_agent": create_agent}),
            )
            result = cast("InvokableAgent", agent).invoke(
                {"messages": [{"role": "user", "content": ORCHESTRATOR_DELEGATION_SMOKE_PROMPT}]},
            )
            return OrchestratorDelegationSmokeResult(
                output=final_message_content(result),
                trace=_trace_from_result(result),
            )
        finally:
            with suppress(Exception):
                store.close()


def _trace_from_result(result: object) -> AgentRunTrace:
    if isinstance(result, Mapping):
        trace = cast("Mapping[str, object]", result).get("trace")
        if isinstance(trace, AgentRunTrace):
            return trace
    return AgentRunTrace()


def _database_path(directory: str) -> Path:
    return Path(directory) / "orchestrator-delegation-smoke.sqlite3"
