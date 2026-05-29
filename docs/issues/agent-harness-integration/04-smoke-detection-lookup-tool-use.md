---
id: agent-harness-integration-04
title: Smoke Detection lookup tool use
status: done
parent: ./PRD.md
depends_on: [agent-harness-integration-03]
external_ref:
labels: []
---

# Smoke Detection Lookup Tool Use

## Goal

Prove that the `detection-lookup` **Specialized subagent** can use its own
declared Detection lookup tools through the **Agent harness** before the
**Orchestrator agent** depends on delegated tool use.

## Acceptance Criteria

- [x] Add a narrow local smoke path for `detection-lookup` direct tool use.
- [x] Keep automated tests deterministic with fake/injected agent runtimes and
      stores.
- [x] Seed a tiny local Detection store fixture for the smoke path rather than
      depending on the live camera database.
- [x] Compose `detection-lookup` with its declared tools resolved from an
      injected tool catalog.
- [x] Use a fixed smoke prompt that requires calling a Detection lookup tool.
- [x] Use a local Ollama tool-capable model for manual smoke verification.
- [x] Prefer `qwen3:8b` for this smoke path if it fits local GPU memory and can
      call tools reliably.
- [x] Do not route through the **Orchestrator agent** yet.
- [x] Do not parse broad user questions or natural-language time phrases.

## Notes

- The point is to prove agent-to-tool behavior in isolation, not detector-label
  reasoning quality.
- Manual verification used `qwen3:8b` and `task detection-lookup-smoke`.
- `qwen3:8b` called `list_detection_labels` successfully and the smoke returned
  `car, person` from the seeded Detection store.
- The first manual smoke exposed that LangGraph runs tool calls in a worker
  thread; the SQLite Detection store now serializes access around a
  cross-thread-capable connection.
