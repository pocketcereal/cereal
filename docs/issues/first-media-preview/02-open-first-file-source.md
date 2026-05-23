---
id: first-media-preview-02
title: Open the first configured file Source through a Source adapter
status: done
parent: ./PRD.md
depends_on: ["first-media-preview-01"]
external_ref:
labels: []
---

## Goal

Select the first configured **Source**, resolve its `file:` **Source URI**, and open it through a tiny scheme-based **Source adapter** path.

## Acceptance Criteria

- [x] The runtime selects only the first configured **Source**.
- [x] A `file:` **Source URI** is converted into the local path OpenCV expects.
- [x] **Source adapter** resolution is based on the **Source URI** scheme.
- [x] Unsupported or broken media paths are allowed to error naturally.
- [x] Unit tests cover first-source selection, file URI path conversion, and scheme-based adapter selection without opening a real preview window.

## Notes

- Do not add a separate source type field.
- Defer async streaming, capabilities, metadata, and health checks.
