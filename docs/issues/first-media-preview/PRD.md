---
id: first-media-preview
title: First media preview
status: done
external_ref:
---

# First Media Preview

## Goal

Load the first configured `file:` **Source** and display it in a lightweight local **Preview window** from the default `cereal` **CLI command**.

## Scope

- Register **Source adapters** by **Source URI** scheme.
- Use OpenCV as the simple file-reading and preview-window backend for this phase.
- Preview only the first configured **Source**.
- Start preview from the existing `cereal` command after loading **Settings**.
- Let unsupported or broken media paths error naturally.
- Unit test non-visual control flow and resource handling.
- Manually verify actual visual playback.
- Prefer more small, focused media modules over large monolithic modules so each boundary stays testable.

## Out Of Scope

- VLC or GStreamer integration.
- Audio playback.
- USB cameras.
- RTSP sources.
- Writing media to disk.
- Multi-source runtime behavior.
- Video preprocessing.
- Visual assertions in automated tests.
