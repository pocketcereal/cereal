---
id: detection-store-06
title: Wire task dev Detection stream prototype
status: done
parent: ./PRD.md
depends_on: ["detection-store-02", "detection-store-03", "detection-store-05"]
external_ref:
---

## Goal

Wire the first configured **Source**, SQLite **Detection store**, object
detector, evidence handling, and preview feedback into the prototype `task dev`
path.

## Acceptance Criteria

- [x] Composition opens the first configured **Source** through the existing **Source adapter registry**.
- [x] Composition creates or receives a SQLite **Store backend** at an explicit database path.
- [x] Default database path is `Settings.storage / "cereal.sqlite3"` when no path is injected.
- [x] Composition creates or receives the prototype object detector without adding detector config to **Settings**.
- [x] Composition chooses the evidence URI rule for capture-device and file **Sources**.
- [x] Capture-device detection records evidence even if the source **Write flag** is false.
- [x] `task dev` runs the first-source detection path using the existing **Configuration file**.
- [x] The default `uv run cereal` path runs the first-source detection stream prototype.
- [x] The first-source detection path retains visible **Preview window** feedback when practical.
- [x] Preview displays every read **Frame** while detection runs only on sampled frames.
- [x] For capture devices, preview occurs after evidence writing and before sampled detection.
- [x] Preview shows raw frames; detection overlays are scoped to a follow-up issue.
- [x] Preview quit or window close stops first-source detection ingestion.
- [x] No new CLI args, subcommands, or broad configuration are introduced.
- [x] Tests cover composition with fake registry, fake detector, fake store, fake writer, fake preview backend, and fake clock.
- [x] `task check` passes.

## Notes

- Avoid over-CLIing this prototype path.
- Later background runtime may become headless; this issue keeps local feedback for development.
- Do not add continuous background runtime or multi-source detection.
- Follow-up implementation added `--preview`, `--no-preview`, and `--overlays` after this issue was completed. The original no-new-CLI-args criterion describes the initial wiring slice, not the current command surface.
