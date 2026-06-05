---
id: object-tracks-foundation-04
title: Expose Object track lookup to agents
status: done
parent: ./PRD.md
depends_on: [object-tracks-foundation-03]
external_ref:
labels: []
---

# Expose Object Track Lookup To Agents

## Goal

Expose **Object track** summaries at the agent harness boundary as a focused
agent-facing capability so count-style planning can choose candidate physical
objects instead of raw Detection event counts.

## Acceptance Criteria

- [x] Add an agent-facing track lookup data tool that returns serializable
      **Object track** summaries.
- [x] Include grouping basis and uncertainty metadata so the **Orchestrator
      agent** can decide whether to validate, split, merge, or delegate.
- [x] Include `follow_up_capabilities` hints such as Evidence retrieval,
      Visual validation, or candidate comparison without forcing a fixed
      workflow.
- [x] Keep the tool attached to a focused **Specialized subagent** or clearly
      document any staged **Orchestrator agent** exposure.
- [x] Add deterministic fake-harness coverage proving the agent can choose the
      track lookup capability for count-style prompts.
- [x] Assert that track lookup returns candidates for agent planning, not a
      final natural-language answer.
- [x] Keep live model smoke optional and secondary to deterministic trace
      assertions.
- [x] Do not answer broad natural-language video questions in this slice.

## Notes

- This should wait until local track query behavior is stable.
- Agent-facing results should not expose raw **Detection events** or private
  database row IDs.
- The capability should help the agent choose the next step; it should not
  collapse Detection lookup, Evidence retrieval, Visual validation, and answer
  composition into one broad tool.
