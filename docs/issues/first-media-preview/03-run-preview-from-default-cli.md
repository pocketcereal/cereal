---
id: first-media-preview-03
title: Run the Preview window from the default CLI command
status: done
parent: ./PRD.md
depends_on: ["first-media-preview-02"]
external_ref:
labels: []
---

## Goal

Running `cereal --config ...` loads **Settings** and starts playback for the first configured file **Source** in a lightweight **Preview window** by default.

## Acceptance Criteria

- [x] The existing `cereal` **CLI command** starts preview after loading **Settings**.
- [x] The preview loop displays frames from the first configured file **Source** in a local desktop window.
- [x] The preview stops on end-of-file or user quit/window close.
- [x] Capture and window resources are released when playback ends.
- [x] Unit tests cover CLI-to-preview wiring and non-visual resource cleanup behavior.
- [x] Automated tests do not assert visual output.

## Notes

- Do not add a preview subcommand yet.
- Audio is not required.
