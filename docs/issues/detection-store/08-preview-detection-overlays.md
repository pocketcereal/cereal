---
id: detection-store-08
title: Preview Detection overlays
status: done
parent: ./PRD.md
depends_on: ["detection-store-06"]
external_ref:
---

## Goal

Optionally draw sampled **Detection events** on the **Preview window** so local
development can visually inspect detector output.

## Acceptance Criteria

- [x] Preview overlay is optional and off by default unless enabled by prototype composition.
- [x] Overlay draws bounding boxes and class/confidence labels for sampled detections.
- [x] Overlay uses **Detection candidates** or **Detection events** from the current sampled frame without querying SQLite.
- [x] Overlay updates on sampled frames while preview can continue displaying every frame.
- [x] Raw preview behavior remains available.
- [x] Overlay drawing is isolated behind a small pure-ish rendering helper where possible.
- [x] Tests cover overlay helper behavior without opening a real preview window.
- [x] `task check` passes.

## Notes

- Do not block the first detection stream prototype on polished overlay UI.
- Keep this local-dev focused; no product UI work.
- Current CLI enables overlays with `--overlays`; raw `uv run cereal` preview remains available, while `task dev` enables overlays for local object-detection inspection.
