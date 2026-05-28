---
id: agent-harness-integration
title: Agent harness integration
status: draft
external_ref:
---

# Agent Harness Integration

## Problem Statement

Cereal has provider-free **Agent definitions** and a static **Agent registry**,
but no **Agent harness** integration yet. The next risk is coupling Cereal's
Detection, Evidence, Analysis, and Validation domains directly to a specific
agent framework before proving the boundary.

The **Orchestrator agent** should be able to choose an analysis strategy from
available tools and **Specialized subagents**. That strategy must not become a
hardcoded Python workflow for each user question, and framework details should
not leak into the core Cereal domains.

## Solution

Introduce an adapter-first **Agent harness** path:

- Treat LangChain Deep Agents as the first **Agent harness** target.
- Keep Cereal-owned **Agent definitions** provider-free.
- Add a small adapter that maps Cereal **Agent definitions** to Deep Agents
  configuration shapes.
- Fail or defer explicitly when Cereal fields do not have a clear harness
  mapping yet.
- Add runtime composition only after the adapter boundary is testable without a
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

Not implemented:

- Tool-bearing **Specialized subagent** delegation.
- User-question planning.

## Key Decisions

- **Agent definitions** remain Cereal-owned domain data.
- Deep Agents is the first **Agent harness** target, not a Cereal domain concept.
- LangGraph can remain an implementation escape hatch under or beside Deep
  Agents.
- LangSmith Deployment is managed hosting and observability infrastructure; it
  is not required for local library-level Deep Agents or LangGraph use.
- The next slice should test configuration mapping only, with no provider key,
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
- The next slice should bind and test `detection-lookup` tools in isolation
  before broad visual-query planning.

## Out of Scope

- Choosing final production hosting.
- LangSmith Deployment integration.
- Durable orchestrator memory.
- Dynamic **Agent definition** generation.
- Broad answer composition from natural-language user questions.
- Object-track creation for count-style questions.
