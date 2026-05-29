---
id: agent-harness-integration-05
title: Smoke Orchestrator Detection lookup delegation
status: done
parent: ./PRD.md
depends_on: [agent-harness-integration-04]
external_ref:
labels: []
---

# Smoke Orchestrator Detection Lookup Delegation

## Goal

Prove that the **Orchestrator agent** can delegate a narrow Detection lookup
task to the `detection-lookup` **Specialized subagent** and return the delegated
result, without hardcoding the question-solving workflow in Python or making
Deep Agents' subagent dictionary the canonical Cereal agent shape.

## Acceptance Criteria

- [x] Add a Cereal-owned **Agent runtime binding** value that pairs an
      **Agent definition** with resolved tools.
- [x] Resolve `detection-lookup` declared tool names through an injected
      **Agent tool catalog** before rendering to any concrete **Agent harness**.
- [x] Keep tool ownership on the `detection-lookup` **Agent definition**; do
      not move Detection lookup tools to the **Orchestrator agent**.
- [x] Render **Agent runtime bindings** into Deep Agents subagent configuration
      as an adapter concern.
- [x] Add a narrow **Agent run trace** test/smoke boundary for harness-visible
      actions in this delegation slice.
- [x] Place first **Agent run trace** types in `cereal.agents.trace`.
- [x] Support the minimal first event set: `agent_invoked`,
      `subagent_delegated`, `tool_called`, and `tool_returned`.
- [x] Keep trace payloads action-focused: agent names, subagent names, tool
      names, structured tool arguments, and JSON-like tool results.
- [x] Verify through the **Agent run trace** that the **Orchestrator agent**
      invoked `detection-lookup`.
- [x] Verify through the **Agent run trace** that `detection-lookup` called
      `list_detection_labels` with the seeded `smoke_fixture` scope.
- [x] Add a narrow local smoke path for **Orchestrator agent** to
      `detection-lookup` delegation.
- [x] Use a seeded Detection store fixture rather than depending on the live
      camera database.
- [x] Bind the `detection-lookup` **Specialized subagent** to its declared
      Detection lookup tools through the Cereal runtime binding boundary.
- [x] Use a fixed smoke prompt that requires the **Orchestrator agent** to use
      the `detection-lookup` capability.
- [x] Require the smoke result to include the seeded `car` and `person` labels.
- [x] Keep automated trace assertions deterministic with fake/injected agent
      runtimes and stores.
- [x] Keep real Deep Agents smoke as a manual confidence check for final output
      rather than the deterministic source of trace truth.
- [x] Add `task orchestrator-delegation-smoke` as the explicit seeded
      delegation smoke path.
- [x] Keep `task agent-smoke` as the tiny Orchestrator harness-liveness check.
- [x] Do not expose Evidence window retrieval or Visual validation tools yet.
- [x] Do not parse broad user questions or natural-language time phrases.
- [x] Do not claim semantic object counts without **Object tracks**.

## Notes

- This issue proves delegation shape, not broad visual-query planning quality.
- Runtime observability and evaluation are separate: this issue observes
  harness-visible actions through an **Agent run trace** and only evaluates the
  narrow smoke result.
- The **Agent run trace** should not capture chain-of-thought or hidden model
  reasoning.
- First-slice traces should not store raw full prompts or full model messages
  by default.
- Automated trace verification should use an injected fake harness/runtime that
  records Cereal **Agent trace events**; real Deep Agents callback/event tracing
  can wait until the Cereal boundary is stable.
- Manual Deep Agents smoke should verify the narrow final result shape, not
  serve as the only proof of delegation internals.
- Use a separate delegation smoke task so the existing `task agent-smoke`
  remains a cheap "is the Orchestrator harness alive?" check.
- `cereal.agents.trace` is the intended home for trace value types because the
  concern is agent execution observability, not visual-analysis composition.
- Deep Agents supports tool-bearing subagent configs, but Cereal should render
  that from an **Agent runtime binding** rather than treating the Deep Agents
  config shape as canonical.
- The expected manual smoke result should reflect the seeded Detection store
  labels, not a detector-label reasoning benchmark.
- Evidence and Visual validation become the next phase only after delegation to
  a tool-bearing **Specialized subagent** is observable and testable.
- For this slice, delegation means the **Orchestrator agent** invokes a
  harness-visible `detection-lookup` subagent or capability. A Python branch
  that calls Detection lookup from the Orchestrator smoke function does not
  count as delegation.
