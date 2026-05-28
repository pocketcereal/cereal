---
id: detection-store-03
title: Add object detector boundary and YOLO adapter
status: done
parent: ./PRD.md
depends_on: ["detection-store-01"]
external_ref:
---

## Goal

Add a replaceable object detector boundary and a first Ultralytics YOLO adapter
that produces **Detection candidates**.

## Acceptance Criteria

- [x] The object detector port is named `ObjectDetector`.
- [x] `ObjectDetector` is expressed as a `Protocol`, accepts one opaque **Frame**, and returns `Sequence[DetectionCandidate]`.
- [x] The detector port exposes model identity through a side-effect-free `model_name` property.
- [x] Core **Detection** contracts import without importing Ultralytics.
- [x] Ultralytics is added through `uv add` so dependency metadata and lockfile stay current.
- [x] The first YOLO adapter is named `UltralyticsObjectDetector`.
- [x] The adapter accepts an injected Ultralytics model name or path.
- [x] The adapter can receive an injected model-like object for tests and dependency injection.
- [x] Runtime composition owns the first prototype default model choice; tests do not assert an exact default model filename.
- [x] The adapter maps YOLO class ID, class name, confidence, and bounding box output into **Detection candidates**.
- [x] Ultralytics result mapping lives in a pure helper function that can be tested without constructing the adapter.
- [x] The adapter does not apply the stream confidence threshold; threshold filtering belongs to the Detection stream loop.
- [x] Optional numeric tracker IDs are normalized to strings when available and omitted when unavailable.
- [x] The adapter uses detection/predict behavior only and does not introduce stateful tracking mode.
- [x] Unit tests cover mapping behavior with fake Ultralytics-like result objects.
- [x] Tests do not require a live camera or network access.
- [x] Any real-model integration test is optional and skipped when model dependencies are unavailable.
- [x] `task check` passes.

## Notes

- YOLO is one replaceable one-stage object detector implementation.
- Do not add detector model configuration to **Settings** yet.
- Ultralytics `track()` behavior and `persist=True` are deferred to the **Object track** pass.
