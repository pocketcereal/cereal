---
id: visual-analysis-foundation-01
title: Add Evidence window retrieval
status: done
parent: ./PRD.md
depends_on: ["detection-store-05"]
external_ref:
---

## Goal

Recover in-memory **Evidence windows** around selected **Detection events** so
later validation can inspect the actual frames behind stored detections.

## Acceptance Criteria

- [x] `cereal.evidence` defines **Evidence frame**, **Evidence target**,
  **Evidence window request**, and **Evidence window** types.
- [x] Retrieval is centered on one caller-provided **Detection event**.
- [x] The default radius is 2 frames.
- [x] Returned **Evidence windows** contain full frames, not crops.
- [x] The **Evidence target** carries class name, confidence, **Bounding box**,
  and center frame index.
- [x] The center frame is required.
- [x] Neighbor frames are best-effort.
- [x] The first video adapter supports local `file://` **Evidence URIs**.
- [x] The OpenCV Evidence reader checks failed seek attempts instead of
  labeling the wrong frame as recovered evidence.
- [x] Tests cover retrieval rules and local video reading.
- [x] `task check` passes.

## Notes

- Do not query the **Detection store** from `cereal.evidence`.
- Do not write extracted frames or clips in this slice.
