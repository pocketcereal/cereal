---
id: source-recording
title: Source recording
status: approved
external_ref:
---

# Source Recording

## Goal

Record the first configured **Source** into a **Recording artifact** while the existing **Preview window** path is running, when that **Source** has `write: true`.

## Scope

- Use the existing per-**Source** **Write flag** as the only user-facing recording control.
- Record only the first configured **Source** in this phase.
- Write one `.mp4` **Recording artifact** per run under `Storage root / Source name / date / Unix timestamp`.
- Derive **Recording artifact** paths in a pure recording Module.
- Create owned recording directories under **Storage root** as needed.
- Add a small **Frame writer** boundary used by the existing **Preview window** loop.
- Add a runtime-only **Writer context** for Cereal-owned prototype defaults.
- Use Cereal-owned prototype defaults of `.mp4`, `libx264`, and `30 fps`.
- Open the concrete ffmpeg-backed **Frame writer** lazily on the first **Frame**.
- Unit test path derivation, Write flag attachment, loop writes, and writer cleanup with fakes.
- Document manual verification with `write: true` on the local **Capture device**.

## Out Of Scope

- Recording multiple Sources.
- Headless recording.
- User-facing recording format configuration.
- Configurable filenames or retention.
- Segmented recordings.
- Recording indexes or metadata catalogs.
- A top-level recording package.
- Deep error handling or a new error taxonomy.

## Architecture Notes

- Keep recording Modules under `cereal.media.recording` while recording remains part of the media runtime.
- Keep the preview loop simple: it displays frames, optionally writes frames, and releases resources.
- Keep recording policy in preview startup composition, where **Settings**, **Source**, **Storage root**, and runtime dependencies are available.
- Inject time into recording startup so **Recording artifact** paths are deterministic in tests.
- Keep **Frame** opaque in this phase; derive writer frame size from the first concrete frame in the writer adapter.
