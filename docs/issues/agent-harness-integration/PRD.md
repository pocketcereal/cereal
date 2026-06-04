---
id: agent-harness-integration
title: Agent harness integration
status: done
external_ref:
---

# Agent Harness Integration

## Problem Statement

Cereal has provider-free **Agent definitions**, a static **Agent registry**, a
Deep Agents **Agent harness** runtime, and isolated `detection-lookup` tool-use
smoke coverage. The next risk is proving **Orchestrator agent** delegation
through a tool-bearing **Specialized subagent** without turning the smoke path
into a hardcoded Python workflow.

The **Orchestrator agent** should be able to choose an analysis strategy from
available tools and **Specialized subagents**. That strategy must not become a
hardcoded Python workflow for each user question, and framework details should
not leak into the core Cereal domains.

## Solution

Continue the adapter-first **Agent harness** path:

- Treat LangChain Deep Agents as the first **Agent harness** target.
- Keep Cereal-owned **Agent definitions** provider-free.
- Add a small adapter that maps Cereal **Agent definitions** to Deep Agents
  configuration shapes.
- Fail or defer explicitly when Cereal fields do not have a clear harness
  mapping yet.
- Keep runtime composition testable with injected fakes before relying on a
  live model provider.
- Load the first **Orchestrator agent** runtime values from Cereal's existing
  **Configuration file**.

## Current State

Implemented:

- Provider-free **Agent definition** value types.
- Local `.agent` directory loading.
- Static in-memory **Agent registry** lookup.
- Pure Deep Agents subagent config adapter for `specialized-subagent`
  **Agent definitions**.
- Required **Orchestrator settings** with `orchestrator.model`.
- Repo-local `orchestrator` and `detection-lookup` **Agent definitions**.
- Deep Agents runtime composition for the **Orchestrator agent** with registered
  `specialized-subagent` definitions.
- Local Ollama smoke path through `uv run cereal --agent orchestrator` and
  `task agent-smoke`.
- Direct local Ollama smoke path through `uv run cereal --agent detection-lookup`
  and `task detection-lookup-smoke`.
- Self-contained `detection-lookup` tool declaration with `find_detection_events`
  and `list_detection_labels`.
- Agent tool catalog resolution from declared tool names to Python callables.
- Cereal-owned **Agent runtime binding** for pairing **Agent definitions** with
  resolved tools before harness rendering.
- Deep Agents subagent rendering from **Agent runtime bindings**, including
  tool-bearing `detection-lookup` subagent config.
- First **Agent run trace** value types under `cereal.agents.trace`.
- Deterministic Orchestrator-to-`detection-lookup` delegation smoke coverage
  with trace assertions for subagent delegation and `list_detection_labels`
  tool use against seeded `smoke_fixture`.
- Explicit local delegation smoke path through
  `uv run cereal --agent orchestrator-delegation` and
  `task orchestrator-delegation-smoke`.
- Agent-facing Evidence and fake Visual validation data tools for visual-query
  planning smoke.
- Deterministic visual-query planning smoke coverage with exact trace-order
  assertions for `detection-lookup.find_detection_events`,
  `retrieve_evidence_window`, and `validate_visual_claim`.
- Explicit local visual-query planning smoke path through
  `uv run cereal --agent visual-query-planning` and
  `task visual-query-planning-smoke`.
- Detection store label listing with event counts.
- SQLite Detection store access serialized for LangGraph worker-thread tool
  calls.

Deferred beyond this initiative:

- User-question planning.

## Key Decisions

- **Agent definitions** remain Cereal-owned domain data.
- Deep Agents is the first **Agent harness** target, not a Cereal domain concept.
- LangGraph can remain an implementation escape hatch under or beside Deep
  Agents.
- LangSmith Deployment is managed hosting and observability infrastructure; it
  is not required for local library-level Deep Agents or LangGraph use.
- The first slice tested configuration mapping only, with no provider key,
  model call, or hosted service.
- This decision does not need an ADR yet because the first slice is a
  reversible pure adapter. Reconsider an ADR when Cereal adds the runtime
  harness dependency and composition.
- The first runtime composition slice should use local Ollama for manual smoke
  verification while keeping automated tests fake/injected.
- The **Orchestrator model** belongs in loaded **Orchestrator settings**, not in
  an ad hoc CLI argument.
- **Orchestrator settings** live in the existing Cereal **Configuration file**
  under `orchestrator:`.
- Detection lookup tools should be bound and tested in isolation before broad
  visual-query planning.
- Direct `detection-lookup` tool use should be proven with a local
  tool-capable Ollama model before Orchestrator delegation.
- `qwen3:8b` is the current local Ollama smoke model because it fits the local
  12GB GPU budget and successfully called the Detection lookup tool in smoke.
- Deep Agents/LangGraph may execute tool calls in worker threads, so injected
  store implementations must be safe at that boundary.
- **Orchestrator agent** delegation to `detection-lookup` is the completed
  boundary before visual-query planning; Evidence window retrieval and Visual
  validation stayed out of that delegation slice.
- Orchestrator delegation means the **Orchestrator agent** invokes a
  harness-visible **Specialized subagent** or capability; direct Python routing
  inside the smoke function is not enough.

## Out of Scope

- Choosing final production hosting.
- LangSmith Deployment integration.
- Durable orchestrator memory.
- Dynamic **Agent definition** generation.
- Broad answer composition from natural-language user questions.
- Object-track creation for count-style questions.
