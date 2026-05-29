"""Agent run trace values."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = ["AgentRunTrace", "AgentTraceEvent", "AgentTraceEventKind"]


class AgentTraceEventKind(StrEnum):
    """Harness-visible Agent trace event kinds."""

    AGENT_INVOKED = "agent_invoked"
    SUBAGENT_DELEGATED = "subagent_delegated"
    TOOL_CALLED = "tool_called"
    TOOL_RETURNED = "tool_returned"


@dataclass(frozen=True)
class AgentTraceEvent:
    """One harness-visible action in an Agent run trace."""

    kind: AgentTraceEventKind
    agent_name: str
    subagent_name: str | None = None
    tool_name: str | None = None
    arguments: Mapping[str, object] = field(default_factory=dict)
    result: object | None = None

    def __post_init__(self) -> None:
        """Snapshot payload values so later caller mutations do not change history."""
        object.__setattr__(self, "arguments", _snapshot(self.arguments))
        object.__setattr__(self, "result", _snapshot(self.result))


@dataclass(frozen=True)
class AgentRunTrace:
    """Structured record of harness-visible Agent actions."""

    events: tuple[AgentTraceEvent, ...] = ()

    def record(self, event: AgentTraceEvent) -> AgentRunTrace:
        """Return a trace with one additional event."""
        return AgentRunTrace(events=(*self.events, event))


def _snapshot(value: object) -> object:
    return deepcopy(value)
