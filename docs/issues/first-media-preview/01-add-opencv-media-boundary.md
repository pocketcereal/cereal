---
id: first-media-preview-01
title: Add OpenCV preview dependency and media module shell
status: done
parent: ./PRD.md
depends_on: []
external_ref:
labels: []
---

## Goal

Add the OpenCV dependency and create a small media module boundary so the first preview backend is isolated from the rest of Cereal.

## Acceptance Criteria

- [x] OpenCV is added with `uv add` so `pyproject.toml` and `uv.lock` stay current.
- [x] Media preview code has a dedicated module boundary under `src/cereal/`.
- [x] OpenCV imports are contained inside the media boundary.
- [x] Existing tests still pass.

## Notes

- This issue does not need to display video yet.
- Do not introduce VLC or GStreamer.
- Keep media code in small, single-purpose modules instead of a broad monolithic media module.
