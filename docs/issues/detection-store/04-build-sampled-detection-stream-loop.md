---
id: detection-store-04
title: Build sampled Detection stream loop
status: done
parent: ./PRD.md
depends_on: ["detection-store-01", "detection-store-02", "detection-store-03"]
external_ref:
---

## Goal

Read **Frames** from an already-open capture, sample at the configured interval,
run the detector, and store every above-threshold **Detection event**.

## Acceptance Criteria

- [x] The loop accepts an already-open media capture, detector, **Detection store**, source name, evidence URI, stream defaults, and explicit frame-time provider.
- [x] The frame-time provider is called with frame index and returns **Frame time**.
- [x] Detection sampling is based on **Frame time** from the frame-time provider, not wall-clock loop runtime.
- [x] If the frame-time provider cannot produce **Observed time** or **Media time**, the loop errors rather than sampling every frame.
- [x] Detection runs only when the stream defaults and **Frame time** indicate the frame should be sampled.
- [x] The first frame is always sampled when it has valid **Frame time**.
- [x] If **Frame time** jumps by more than one interval, the loop samples the current frame once and does not create synthetic catch-up samples.
- [x] Detections below the stream confidence threshold are ignored.
- [x] Confidence threshold filtering is owned by the stream loop, not the detector adapter.
- [x] Below-threshold candidates are not persisted; reruns can use recorded video if the threshold needs to change later.
- [x] Every sampled **Detection candidate** above threshold becomes a persisted **Detection event** with frame dimensions.
- [x] The loop appends events through the **Detection store** port once per sampled frame that has detections.
- [x] The loop skips store writes for sampled frames with zero above-threshold detections.
- [x] The loop stops when capture returns no frame.
- [x] The loop accepts an optional stop predicate for bounded runs and tests.
- [x] The loop releases the media capture when complete.
- [x] Tests cover interval sampling, threshold filtering, event conversion, and store writes with fakes.
- [x] `task check` passes.

## Notes

- Do not open configured **Sources** in this issue.
- Do not coordinate recording in this issue.
- Do not coordinate **Preview window** display in this issue.
- Do not add background runtime or multi-source ingestion.
