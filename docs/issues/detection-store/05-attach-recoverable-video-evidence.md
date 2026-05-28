---
id: detection-store-05
title: Attach recoverable video evidence
status: done
parent: ./PRD.md
depends_on: ["detection-store-04"]
external_ref:
---

## Goal

Ensure stored **Detection events** can point back to recoverable video evidence
from either a **Recording artifact** or an original file **Source**.

## Acceptance Criteria

- [x] The detection stream loop can accept an optional **Frame writer**.
- [x] Capture-device detection writes every read **Frame** to a **Recording artifact**, not only sampled frames.
- [x] Capture-device detection records recoverable evidence regardless of the source **Write flag**.
- [x] Capture-device detection reuses the existing **Recording artifact** path derivation.
- [x] Detection still runs only on sampled frames.
- [x] If writing a **Frame** fails, detection and store append do not run for that frame and the error surfaces.
- [x] For capture devices, frame handling order is read, write evidence, preview if enabled, detect if sampled, then store detections.
- [x] For file **Sources**, frame handling order is read, preview if enabled, detect if sampled, then store detections.
- [x] Capture-device **Detection events** use an **Evidence URI** pointing to the **Recording artifact** for that run.
- [x] Capture-device **Detection event** frame indexes align with the frame order written to the **Recording artifact**.
- [x] Local **Recording artifact** evidence uses a standard `file://` **Evidence URI** derived from the artifact path.
- [x] File-source detection can use the original file as a standard `file://` **Evidence URI** without creating duplicate frame artifacts.
- [x] File-source **Detection event** frame indexes and **Media time** refer to the original file frame sequence.
- [x] Writer cleanup happens in `finally` even when ingestion stops early.
- [x] Writer release errors surface naturally after cleanup is attempted.
- [x] Tests cover recording writer use, evidence URI assignment, and cleanup with fakes.
- [x] `task check` passes.

## Notes

- Prefer evidence references back to video artifacts over saved frame images.
- Do not introduce a custom `recording:` URI scheme until Cereal has an artifact catalog.
- Keep recording format/configuration unchanged.
