---
id: source-recording-01
title: Add recording path and writer boundaries
status: done
parent: ./PRD.md
depends_on: []
external_ref:
---

## Goal

Add the pure path and small writer boundaries needed to record **Frames** without introducing OpenCV writing or preview startup policy yet.

## Acceptance Criteria

- [x] A pure recording path function derives `Storage root / Source name / date / Unix timestamp.mp4` paths from explicit inputs.
- [x] The path function does not create directories or touch the filesystem.
- [x] A runtime-only **Writer context** carries Cereal-owned prototype defaults for extension, codec, and FPS.
- [x] A tiny **Frame writer** interface can write **Frames** and release resources.
- [x] The **Preview window** loop can accept an optional **Frame writer**, write each displayed **Frame**, and release it during cleanup.
- [x] Tests cover path derivation, optional loop writing, and writer cleanup with fakes.
- [x] `task check` passes.

## Blocked by

None - can start immediately.

## Notes

- Keep Modules under `cereal.media.recording`.
- Keep **Frame** opaque.
- Do not add OpenCV `VideoWriter` or `write: true` startup wiring in this issue.
