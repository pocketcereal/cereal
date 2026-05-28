---
id: detection-store
title: Detection store fed by YOLO-backed Detection events
status: done
external_ref:
---

# Detection Store Fed by YOLO-backed Detection Events

## Problem Statement

Cereal can open, preview, and record a configured **Source**, but it does not yet
persist model observations that later analysis can query. Without persisted
**Detection events** linked back to recoverable video evidence, an **Analysis
agent** has nothing reliable to inspect retroactively.

## Solution

Add the first detection foundation: run a detector over the first configured
**Source**, convert raw **Detection candidates** into persisted **Detection
events**, and store enough **Evidence reference** data to recover the relevant
**Frames** from a **Recording artifact** or original file later.

The first implementation remains intentionally minimal. It proves the
**Detection store** port, a SQLite **Store backend**, a detector boundary, and a
single-source ingestion path before adding continuous background processing,
**Object track** creation, **Visual validation**, a **Semantic index**, or agent
orchestration.

## Current State

Implemented in `cereal.detection`:

- Detection domain types, event conversion, and prototype stream defaults.
- SQLite **Detection store** at `Settings.storage / "cereal.sqlite3"`.
- Local detection query helper through `cereal detections` and `task detections`.
- `ObjectDetector` protocol and `UltralyticsObjectDetector` adapter.
- Sampled detection stream using a 3 second default interval and `0.5` confidence threshold.
- Capture-device evidence recording to a **Recording artifact** regardless of source `write` flag.
- File-source evidence references to the original file URI.
- Default `uv run cereal` first-source detection path with preview enabled.
- `task dev` runs the same path with **Detection overlays** enabled.
- `--no-preview` for automated/headless detection runs.
- `--overlays` for optional preview bounding boxes and class/confidence labels.
- Standard Python logging for startup, source opening, sampled frame counts, and store writes.

Downstream library foundation now exists outside this PRD:

- `cereal.evidence` can recover in-memory **Evidence windows** from selected **Detection events**.
- `cereal.analysis` can compose **Detection event queries**, **Detection stores**, Evidence readers, and **Visual validators** into transient **Visual inspections**.
- `cereal.validation` defines provider-free **Visual claim**, **Visual validation**, and **Visual validator** contracts.

## User Stories

1. As a Cereal user, I want detections from the first configured **Source** to be stored, so that later analysis can query what appeared in the video.
2. As a Cereal user, I want each **Detection event** to include source, time, class, confidence, and bounding box data, so that answers can be grounded in structured evidence.
3. As a Cereal user, I want each live **Detection event** to point back to recorded video evidence, so that future VLM validation can replay the relevant **Frames**.
4. As a Cereal user, I want file-source **Detection events** to point back to the original file and frame position, so that file-based analysis does not create unnecessary duplicate artifacts.
5. As a Cereal developer, I want the detector hidden behind a small port, so that Ultralytics can be replaced or configured later without changing persistence code.
6. As a Cereal developer, I want the **Detection store** hidden behind a small port, so that SQLite is a first **Store backend** rather than a permanent coupling.
7. As a Cereal developer, I want first-slice model defaults owned by runtime composition, so that Cereal avoids premature user-facing detector configuration.
8. As a Cereal developer, I want **Object track** creation deferred while preserving optional track IDs, so that tracking can be added without reworking stored events.

## Implementation Decisions

- Use **Detection event** for one persisted model observation in one **Frame** from one **Source**.
- Use **Detection candidate** for one raw detector output before Cereal adds source, timestamp, evidence, and persistence identity.
- Use **Detection store** as the domain port for storing and querying **Detection events**.
- Keep detection contracts in the **Detection** domain area rather than the media runtime.
- Use a SQLite **Store backend** for the first implementation.
- Do not introduce a generic storage engine or builder until more than one backend exists.
- Add optional track ID storage, but defer **Object track** creation and count semantics.
- Store first-slice event fields: source name, observed time or media time, frame index, evidence URI, model name, class ID, class name, confidence, bounding box coordinates, and optional track ID.
- For capture-device **Sources**, write recoverable evidence to a **Recording artifact** in the same run that writes **Detection events**.
- For file **Sources**, use the original file as the recoverable evidence artifact when possible.
- Keep command shape minimal; avoid a robust CLI and broad configuration surface.
- Keep detector model settings as prototype-owned runtime defaults.
- Keep future architecture clear: continuous background detection over active **Sources** remains the target after this foundation.

## Testing Decisions

- Test domain conversion with fake **Frames**, fake **Detection candidates**, and explicit timestamps.
- Test the SQLite **Store backend** through its public **Detection store** behavior.
- Test ingestion orchestration with fake source capture, fake detector, fake writer, fake clock, and temporary storage.
- Test observable behavior: persisted rows, evidence references, cleanup, and query results.
- Test headless file-source ingestion with a generated static video and SQLite query.
- Do not assert exact terminal output strings.
- Leave real capture-device and visual playback verification to manual checks, matching existing preview/recording testing boundaries.

## Out of Scope

- **Orchestrator agent** orchestration.
- Provider-backed **Visual validation** and concrete **Validation roles**.
- **Semantic index** or vector storage.
- **Object track** creation and object-count semantics.
- Multi-source detection.
- Continuous background job runtime.
- Robust CLI or detector configuration in **Settings**.
- Retention policies, recording indexes, or artifact lifecycle management.
- A generic storage engine/builder abstraction.

## Further Notes

This PRD intentionally starts with the durable evidence foundation. Later passes
should split the child work further until each issue has narrow acceptance
criteria and can be implemented with test-first slices.
