---
id: detection-store-01
title: Define Detection event and stream defaults
status: done
parent: ./PRD.md
depends_on: []
external_ref:
---

## Goal

Define the core **Detection** domain types and prototype-owned stream defaults
needed to represent detections sampled from video.

## Acceptance Criteria

- [x] A **Bounding box** type represents pixel-space `xyxy` coordinates as floats.
- [x] **Bounding box** validation requires `x1 <= x2` and `y1 <= y2`.
- [x] **Detection event** validation requires positive frame width and height.
- [x] **Bounding box** values are not clamped to frame bounds in this issue.
- [x] A **Detection candidate** type represents class ID, class name, confidence, **Bounding box**, and optional `track_id: str | None`.
- [x] `class_name` is stored as returned by the detector; no class taxonomy normalization is added in this issue.
- [x] **Detection candidate** does not include raw detector metadata, tensors, masks, keypoints, or segmentation data.
- [x] A **Detection event** type adds **Source name**, **Observed time** or **Media time**, frame index, frame width, frame height, **Evidence URI**, and model name to a **Detection candidate**.
- [x] A **Detection event** stores **Source name** but does not duplicate **Source URI**.
- [x] `model_name` is required on every **Detection event**.
- [x] A **Detection event** does not include a domain ID in this issue; stores may assign backend IDs later.
- [x] A **Detection event** requires at least one of **Observed time** or **Media time**; both are allowed, neither is invalid.
- [x] **Evidence URI** is required on every **Detection event** and is represented as a string URI rather than a local-only `Path`.
- [x] `DetectionStreamDefaults` carries prototype-owned time-based sample interval and confidence threshold values.
- [x] The default sample interval is 3 seconds.
- [x] The default confidence threshold is `0.5`.
- [x] The stream defaults do not include a max detections cap; first pass stores all detections above threshold.
- [x] The stream defaults do not include an allowed-classes filter; first pass stores all detector classes above threshold.
- [x] Confidence threshold filtering happens before persistence; below-threshold candidates do not become **Detection events**.
- [x] Domain conversion from **Detection candidate** to **Detection event** receives all external effects as explicit inputs.
- [x] Unit tests cover conversion and defaults without OpenCV, Ultralytics, SQLite, or filesystem access.
- [x] `task check` passes.

## Notes

- Place contracts in the **Detection** domain area rather than `cereal.media`.
- Do not add the **Detection store** port in this issue.
- Do not create **Object tracks** in this issue.
- Do not expose stream defaults as user-facing **Settings** yet.
