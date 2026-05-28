---
id: source-recording-02
title: Record the first Source during preview
status: done
parent: ./PRD.md
depends_on: ["source-recording-01"]
external_ref:
---

## Goal

When the first configured **Source** has `write: true`, record its **Frames** into a **Recording artifact** while the existing **Preview window** path is running.

## Acceptance Criteria

- [x] **Preview window** startup composition checks the first configured **Source** **Write flag**.
- [x] If `write` is false or omitted, preview behavior stays unchanged and no **Frame writer** is attached.
- [x] Only the first configured **Source** controls recording; later **Sources** with `write: true` are ignored in this phase.
- [x] If `write: true`, startup derives a **Recording artifact** path under **Storage root** and attaches an ffmpeg-backed **Frame writer**.
- [x] Startup uses injected time when deriving the **Recording artifact** path.
- [x] Cereal creates required recording directories under **Storage root** when writing.
- [x] The ffmpeg-backed **Frame writer** opens lazily on the first **Frame** using **Writer context** defaults.
- [x] If no **Frames** arrive, no **Recording artifact** is created.
- [x] Tests cover Write flag attachment, directory creation behavior, lazy writer opening, and no-frame behavior with fakes.
- [x] Manual verification docs show `write: true` with `uri: device:0`.
- [x] `task check` passes.

## Blocked by

- source-recording-01

## Notes

- Do not add headless recording.
- Do not record multiple **Sources**.
- Do not add user-facing recording format configuration yet.
- Let filesystem/OpenCV failures remain natural unless a tiny message makes manual verification clearer.
