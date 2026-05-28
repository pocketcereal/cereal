---
id: agent-harness-integration-01
title: Map Agent definitions to Deep Agents config
status: done
parent: ./PRD.md
depends_on: []
external_ref:
labels: []
---

# Map Agent Definitions To Deep Agents Config

## Goal

Add a provider-free adapter that converts Cereal **Agent definitions** into the
small Deep Agents configuration shape needed for future **Specialized subagent**
registration.

## Acceptance Criteria

- [x] Add `cereal.agents.deepagents_adapter` for pure Deep Agents adapter
      logic.
- [x] Convert a `specialized-subagent` **Agent definition** into a
      Cereal-owned frozen adapter result that represents the Deep Agents
      subagent fields we need for the next slice.
- [x] Map Cereal `name`, `description`, and `instructions` directly.
- [x] Return `tools`, `skills`, `permissions`, and `response_format` as
      explicit deferred fields rather than binding runtime behavior.
- [x] Succeed when deferred fields are present, but expose them structurally so
      they cannot be silently dropped.
- [x] Reject `orchestrator` **Agent definitions** when converting to a
      subagent config.
- [x] Raise `ValueError` for wrong-kind adapter calls, because this is
      programmer misuse rather than a local definition load failure.
- [x] Do not instantiate Deep Agents.
- [x] Do not add the Deep Agents dependency.
- [x] Do not invoke a live model provider.
- [x] Do not require LangSmith Deployment or any hosted service.
- [x] Cover the adapter with focused unit tests.

## Implementation Notes

- Added `DeepAgentsSubagentConfig` as the Cereal-owned typed adapter result.
- Added `DeferredAgentDefinitionFields` so unsupported runtime fields remain
  visible to later harness composition.
- Added `to_deepagents_subagent_config` as the pure conversion boundary.

## Notes

- This issue proves the harness boundary without committing the core Cereal
  domains to Deep Agents.
- The first adapter slice maps inert configuration only: `name`,
  `description`, and `instructions`.
- Runtime tool binding belongs to the harness composition slice, not to this
  adapter proof.
- Keep `cereal.agents.deepagents_adapter` pure: no model calls, no
  `create_deep_agent`, and no runtime composition.
- Add the Deep Agents dependency only when a later slice composes an actual
  **Agent harness** runtime.
- The adapter result should be typed before it is rendered to any plain
  Deep Agents dictionary shape.
- If the official Deep Agents config object would require importing the package,
  prefer the tiny local typed adapter result first unless the dependency
  clearly simplifies the implementation.
