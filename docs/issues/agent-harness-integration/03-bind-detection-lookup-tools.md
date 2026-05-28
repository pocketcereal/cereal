---
id: agent-harness-integration-03
title: Bind Detection lookup tools
status: ready
parent: ./PRD.md
depends_on: [agent-harness-integration-02]
external_ref:
labels: []
---

# Bind Detection Lookup Tools

## Goal

Give the `detection-lookup` **Specialized subagent** a small, testable tool
boundary for querying structured Detection store data without hardcoding a
specific user-question workflow.

## Acceptance Criteria

- [ ] Add one or more narrow Detection lookup tools at the **Agent harness**
      boundary.
- [ ] Keep Detection store querying in existing Detection/Analysis domain
      boundaries; the agent tool should compose those boundaries rather than
      owning persistence.
- [ ] Let `detection-lookup` receive object-language input and produce detector
      label query candidates or structured lookup results.
- [ ] Keep label expansion simple and explicit for the first slice.
- [ ] Test the Detection lookup tool without a live model.
- [ ] Test `detection-lookup` composition in isolation before using it through
      the **Orchestrator agent**.
- [ ] Do not visually validate attributes such as color in this issue.
- [ ] Do not answer broad natural-language video questions in this issue.

## Notes

- This is the next step before broad visual-query planning because the
  **Orchestrator agent** should depend on tested **Specialized subagent**
  capabilities, not hidden prompt hopes.
- Count-style answers may still require **Object tracks** before they are
  semantically correct.
