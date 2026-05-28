---
id: detection-store-02
title: Add queryable SQLite Detection store
status: done
parent: ./PRD.md
depends_on: ["detection-store-01"]
external_ref:
---

## Goal

Persist and quickly query **Detection events** through a **Detection store** port
backed by SQLite.

## Acceptance Criteria

- [x] A **Detection store** port can append **Detection events** and query by a **Detection event query**.
- [x] Appending an empty sequence is allowed and does not write rows.
- [x] The store is append-only for this issue and does not deduplicate rerun detections.
- [x] The **Detection store** port does not expose delete, clear, or retention behavior in this issue.
- [x] A **Detection event query** supports optional source name, class name, **Observed time** bounds, **Media time** bounds, minimum confidence, and limit.
- [x] **Detection event query** filters by class name only; class ID filtering is deferred because class IDs are detector-specific.
- [x] Query results return **Detection events** rather than database rows or dictionaries.
- [x] Query results are deterministic: observed-time queries sort by observed time then frame index, media-time queries sort by media time then frame index, and unbounded queries use a stable source/time/frame ordering.
- [x] SQLite schema stores source name, observed time, media time, frame index, frame width, frame height, evidence URI, model name, class ID, class name, confidence, bounding box coordinates, and optional track ID.
- [x] SQLite schema does not add `created_at` or insert-time metadata in this issue.
- [x] Observed time is stored as UTC ISO-8601 text and reconstructed as `datetime`.
- [x] Media time is stored as integer milliseconds.
- [x] SQLite schema includes minimal schema version record `1`.
- [x] The backend initializes its schema in a caller-provided database path and creates missing parent directories.
- [x] Schema includes indexes for source plus observed time, source plus media time, source plus class name, source plus class name plus observed time, and source plus class name plus media time.
- [x] Tests verify persistence and query behavior through the **Detection store** port.
- [x] `task check` passes.

## Notes

- SQLite is the first **Store backend**, not a broad storage abstraction.
- Default database path selection is deferred to ingestion/composition.
- Do not add a migration framework in this issue.
