---
id: agent-harness-integration-06
title: Add visual query planning smoke test
status: ready
parent: ./PRD.md
depends_on: [agent-harness-integration-05]
external_ref:
labels: []
---

# Add Visual Query Planning Smoke Test

## Goal

Prove that the **Orchestrator agent** can choose a simple visual-analysis
strategy from available Cereal tools and **Specialized subagents** without a
hardcoded workflow for a specific question.

## Acceptance Criteria

- [ ] Provide a smoke-test scenario that exercises Detection lookup, Evidence
      window retrieval, and Visual validation without a concrete hardcoded
      object workflow.
- [ ] Expose Evidence window retrieval and Visual validation as tool-like
      capabilities at the harness boundary.
- [ ] Implement agent-facing Evidence and Visual validation tools under
      `cereal.agents.*`, not in `cereal.analysis`.
- [ ] Keep `cereal.evidence`, `cereal.validation`, and `cereal.analysis`
      provider- and harness-neutral.
- [ ] Treat direct Orchestrator access to Evidence and Visual validation tools
      as staged exposure for this smoke, not permanent capability ownership.
- [ ] Record that Evidence and Visual validation capabilities should later be
      registered with focused **Specialized subagents** once those subagents are
      defined and tested.
- [ ] Do not create placeholder Evidence or Visual validation subagent issues
      before this smoke reveals the natural boundaries.
- [ ] Use a fake/injected **Visual validator** for deterministic smoke behavior.
- [ ] Do not call a real VLM provider in this issue.
- [ ] Let the **Orchestrator agent** select the sequence of capabilities.
- [ ] Use a fixed structured planning prompt rather than broad natural-language
      video QA.
- [ ] Reuse **Agent run trace** vocabulary from issue 05 for harness-visible
      action checks.
- [ ] Keep deterministic fixtures or fake providers available for repeatable
      tests.
- [ ] Record whether count-style answers require **Object tracks** before they
      can be considered semantically correct.

## Notes

- This issue may reveal that **Object track** creation is the more important
  next domain slice before natural-language query answering.
- The smoke test should measure planning shape and boundary correctness, not
  model quality.
- Real VLM provider adapters, prompt design, image formatting, latency, and
  cost controls belong to a later issue after the orchestration boundary is
  proven with fake providers.
- Agent-facing Evidence and Visual validation tools should compose existing
  domain ports and return serializable result shapes for agent inspection.
- Do not move agent/harness concerns into `cereal.analysis`.
- Keep this slice small: the **Orchestrator agent** may use the new tools
  directly for planning smoke, while long-term ownership belongs with future
  focused **Specialized subagents**.
- Defer new subagent issue creation until this smoke clarifies whether the next
  focused agent boundary is Evidence retrieval, Visual validation, Visual
  inspection, or another task-shaped capability.
- A suitable first prompt is shaped like: "Find candidate car detections in
  `smoke_fixture`, retrieve evidence for one candidate, and validate the claim
  `the object is a car`."
- Broad natural-language questions such as "how many white trucks were there
  between 2-3pm?" wait until delegation, trace verification, evidence tools,
  fake validation, Object-track count semantics, and provider boundaries are
  clearer.
- Do not broaden **Agent run trace** into a full observability platform in this
  issue; persistence, UI, hosted tracing, export formats, and run comparison
  belong to a later PRD when needed.
