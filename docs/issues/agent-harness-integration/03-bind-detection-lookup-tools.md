---
id: agent-harness-integration-03
title: Bind Detection lookup tools
status: done
parent: ./PRD.md
depends_on: [agent-harness-integration-02]
external_ref:
labels: []
---

# Bind Detection Lookup Tools

## Goal

Make `detection-lookup` a self-contained **Specialized subagent** by giving its
**Agent definition** an explicit tool contract for querying structured Detection
store data without hardcoding a specific user-question workflow.

## Acceptance Criteria

- [x] Add one or more narrow Detection lookup tools at the **Agent harness**
      boundary.
- [x] Declare the Detection lookup tools in `agents/detection-lookup.agent`
      rather than wiring them only from the **Orchestrator agent**.
- [x] Add a tool catalog or equivalent resolver that maps declared Agent
      definition tool names to Python callables.
- [x] Construct Detection lookup tools from explicit dependencies such as a
      `DetectionStore`; tools must not open databases or read settings
      internally.
- [x] Keep Detection store querying in existing Detection/Analysis domain
      boundaries; the agent tool should compose those boundaries rather than
      owning persistence.
- [x] Add a narrow Detection store label-listing query instead of fetching all
      Detection events and counting labels in the agent tool.
- [x] Let `detection-lookup` use its own declared tools in isolated composition
      tests.
- [x] Add a lookup callable that accepts an explicit detector label plus
      optional source/time filters and returns structured Detection event lookup
      results.
- [x] Name the first tool `find_detection_events`.
- [x] Add a discovery callable named `list_detection_labels` with optional
      source/time filters so the agent can inspect available detector labels
      when an explicit lookup comes up empty.
- [x] Return label summaries with event counts from `list_detection_labels`,
      not a bare string list.
- [x] Declare `tools = ["find_detection_events", "list_detection_labels"]` in
      `agents/detection-lookup.agent/agent.toml`.
- [x] Return a small agent-facing result shape rather than raw
      `DetectionEvent` domain objects.
- [x] Keep lookup results serializable and stable for LLM/tool inspection.
- [x] Accept observed time filters as ISO-8601 strings and parse them at the
      tool boundary.
- [x] Reject invalid observed time strings with `ValueError`.
- [x] Do not parse natural-language time phrases inside Detection lookup tools.
- [x] Test the Detection lookup tool without a live model.
- [x] Test `detection-lookup` composition in isolation before using it through
      the **Orchestrator agent**.
- [x] Compose `detection-lookup` with an injected tool catalog or equivalent
      dependency; do not make the existing Orchestrator smoke depend on a real
      Detection store yet.
- [x] Do not visually validate attributes such as color in this issue.
- [x] Do not answer broad natural-language video questions in this issue.

## Implementation Notes

- Added `DetectionLabelQuery` and `DetectionLabelCount` to the Detection store
  port, with SQLite `GROUP BY class_name` support.
- Added `AgentToolCatalog` for resolving tool names declared by Agent
  definitions.
- Added `cereal.agents.detection_lookup` with `find_detection_events`,
  `list_detection_labels`, typed result shapes, ISO observed-time parsing, and
  dependency-bound tool construction.
- Updated `agents/detection-lookup.agent` to declare its tools and explain how
  the subagent should use label discovery.

## Notes

- This is the next step before broad visual-query planning because the
  **Orchestrator agent** should depend on tested, self-contained
  **Specialized subagent** capabilities, not hidden prompt hopes.
- The agent does the reasoning about which labels to try. The tool executes
  explicit structured lookups; it should not contain prompt-specific synonym
  policy.
- The Cereal boundary should be typed; the Deep Agents tool return can be
  rendered as JSON-like data if required by the harness.
- Bind dependencies at tool-construction time so tests can inject fake stores
  and runtime composition can inject SQLite-backed stores.
- Label counts are store behavior. The SQLite backend should use a grouped
  query rather than relying on the agent tool to count raw events.
- Natural-language time resolution belongs to future Orchestrator/task-planning
  behavior; Detection lookup tools receive structured filters only.
- `task agent-smoke` can remain an Orchestrator harness smoke in this issue.
  Detection lookup tool behavior should be tested directly and through isolated
  `detection-lookup` composition.
- Do not add count summaries or broad analytics tools until the agent needs
  them.
- Label similarity reasoning stays with the agent. `list_detection_labels`
  exists so the agent can discover actual labels in scope before deciding what
  other explicit lookups to run.
- Count-style answers may still require **Object tracks** before they are
  semantically correct.
