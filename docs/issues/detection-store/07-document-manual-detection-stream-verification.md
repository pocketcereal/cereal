---
id: detection-store-07
title: Document manual Detection stream verification
status: done
parent: ./PRD.md
depends_on: ["detection-store-06"]
external_ref:
---

## Goal

Document the minimal manual path for verifying real object detections are stored
and quickly retrievable from the first configured **Source**.

## Acceptance Criteria

- [x] Manual verification explains how to run the first-source detection path with `task dev`.
- [x] Manual verification explains where the SQLite **Store backend** writes persisted **Detection events**.
- [x] Manual verification explains how to query by source, class, and time range.
- [x] Manual verification explains how to confirm **Evidence URIs** point to recoverable video evidence.
- [x] Manual verification covers capture-device and file-source expectations where both are supported.
- [x] Manual verification explains stopping detection through preview quit or window close.
- [x] Documentation avoids presenting the first slice as the final background/agent architecture.
- [x] `task check` passes.

## Notes

- Keep docs short and operational.
- Do not document future agent workflows as implemented behavior.
- Manual verification now documents preview-on, headless `--no-preview`, and overlay `--overlays` paths.
