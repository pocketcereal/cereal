---
id: agent-harness-integration-04
title: Add visual query planning smoke test
status: draft
parent: ./PRD.md
depends_on: [agent-harness-integration-03]
external_ref:
labels: []
---

# Add Visual Query Planning Smoke Test

## Goal

Prove that the **Orchestrator agent** can choose a simple visual-analysis
strategy from available Cereal tools and **Specialized subagents** without a
hardcoded workflow for a specific question.

## Acceptance Criteria

- [ ] Provide a smoke-test scenario such as "how many white trucks are there in
      this time window?"
- [ ] Expose Detection lookup, Evidence window retrieval, and Visual validation
      as tool-like capabilities at the harness boundary.
- [ ] Let the **Orchestrator agent** select the sequence of capabilities.
- [ ] Keep deterministic fixtures or fake providers available for repeatable
      tests.
- [ ] Record whether count-style answers require **Object tracks** before they
      can be considered semantically correct.

## Notes

- This issue may reveal that **Object track** creation is the more important
  next domain slice before natural-language query answering.
- The smoke test should measure planning shape and boundary correctness, not
  model quality.
