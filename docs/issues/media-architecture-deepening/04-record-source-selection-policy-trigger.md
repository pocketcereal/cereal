---
id: media-architecture-deepening-04
title: Record Source selection policy trigger
status: ready
parent: ./PRD.md
depends_on: []
external_ref:
labels: ["needs-triage"]
---

## Goal

Record that first-Source selection remains intentionally shallow until Cereal has a second real Source runtime policy.

## Acceptance Criteria

- [ ] Project documentation records that phase-one **Source** selection stays as first configured **Source** behavior.
- [ ] Documentation names the trigger conditions for deepening Source selection, such as multi-Source runtime, Write flag behavior, named Source selection, or Source adapter capability checks.
- [ ] No new Source selection Seam or Adapter is introduced by this issue.
- [ ] `task check` passes.

## Blocked by

None - can start immediately.

## Notes

- The current `first_configured_source` Module is shallow by design.
- This issue exists to prevent future refactors from deepening that Module before the domain has another policy.
