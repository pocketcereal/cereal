---
id: media-architecture-deepening-03
title: Concentrate OpenCV capture adapter behavior
status: ready
parent: ./PRD.md
depends_on: ["media-architecture-deepening-02"]
external_ref:
labels: ["needs-triage"]
---

## Goal

Keep **Frame** opaque while concentrating OpenCV-specific capture lifecycle details inside the OpenCV/file Source adapter implementation.

## Acceptance Criteria

- [ ] OpenCV-specific lifecycle behavior such as `isOpened()` is only required inside the OpenCV/file Source adapter implementation and its focused tests.
- [ ] Media Modules outside the OpenCV/file adapter depend on Cereal's `MediaCapture` Interface, not OpenCV-shaped captures.
- [ ] Preview window tests that do not exercise the adapter can use fakes shaped like `MediaCapture`.
- [ ] No Cereal Frame pixel wrapper is introduced.
- [ ] `task check` passes.

## Blocked by

- media-architecture-deepening-02

## Notes

- This is not a request to model pixel data.
- Defer richer **Frame** structure until preprocessing, writing, metadata, or shape validation becomes real.
