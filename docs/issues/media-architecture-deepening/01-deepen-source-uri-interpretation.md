---
id: media-architecture-deepening-01
title: Deepen Source URI interpretation
status: ready
parent: ./PRD.md
depends_on: []
external_ref:
labels: ["needs-triage"]
---

## Goal

Load configured **Source URI** strings into one typed interpretation Module so validation, scheme lookup, and `file:` path conversion no longer repeat URI parsing across media Modules.

## Acceptance Criteria

- [ ] YAML configuration still accepts **Source URI** values as strings.
- [ ] Loaded **Settings** exposes each **Source URI** through one parsed value or equivalent typed Module.
- [ ] **Source URI** scheme validation and Source adapter lookup use the same interpretation path.
- [ ] `file:` local path conversion lives with **Source URI** interpretation.
- [ ] Unsupported schemes continue to fail naturally through Source adapter lookup.
- [ ] Tests cover Settings loading, adapter lookup, and `file:` path conversion through the new Source URI surface.
- [ ] `task check` passes.

## Blocked by

None - can start immediately.

## Notes

- Do not add a polished unsupported-scheme error yet.
- Keep the Module pure: no IO, OpenCV import, registry construction, or adapter behavior.
