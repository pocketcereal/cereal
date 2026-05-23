---
id: media-architecture-deepening-02
title: Deepen Preview window startup
status: ready
parent: ./PRD.md
depends_on: ["media-architecture-deepening-01"]
external_ref:
labels: ["needs-triage"]
---

## Goal

Move **Preview window** startup composition behind the **Preview window** Module while preserving the current **CLI command** behavior.

## Acceptance Criteria

- [ ] The **CLI command** still loads **Settings** and starts the **Preview window** with the same user-facing behavior.
- [ ] OpenCV loading, capture factory selection, Source adapter registry construction, first Source opening, and backend construction live behind the **Preview window** Module.
- [ ] The preview loop remains focused on frame display, stop conditions, and resource cleanup.
- [ ] Tests cover Preview window startup with fakes without opening a real desktop window.
- [ ] Existing CLI-to-preview wiring tests continue to pass.
- [ ] `task check` passes.

## Blocked by

- media-architecture-deepening-01

## Notes

- Do not add a preview subcommand.
- Do not add multi-Source runtime behavior.
- Keep **Preview window** as the domain name; avoid broad names like media runtime until the domain needs that scope.
