---
id: detection-store-09
title: Add local Detection query helper
status: done
parent: ./PRD.md
depends_on: ["detection-store-02"]
external_ref:
---

## Goal

Add a small local query path so developers can inspect stored **Detection events**
without writing raw SQLite queries.

## Acceptance Criteria

- [x] The `cereal detections` command queries the configured SQLite **Detection store**.
- [x] `task detections` lists recent stored **Detection events** with a safe default limit.
- [x] Query filters support source name, class name, minimum confidence, observed-time bounds, media-time bounds, and limit.
- [x] Negative limits are rejected instead of widening debug output.
- [x] Output is stable TSV with source, class, confidence, timestamps, frame index, bounding box, and **Evidence URI**.
- [x] Tests cover query option mapping, CLI dispatch, TSV rendering, and configured store reads.
- [x] `task check` passes.

## Notes

- This is a developer inspection helper, not a final analytics or reporting UI.
- Keep the query command narrow until the future **Orchestrator agent** owns broader question planning.
