---
id: object-tracks-foundation-01
title: Define Object track builder
status: done
parent: ./PRD.md
depends_on: []
external_ref:
labels: []
---

# Define Object Track Builder

## Goal

Create the first provider-free **Object track** value type and pure builder so
Cereal can group **Detection events** without involving SQLite, OpenCV, or an
agent harness.

## Acceptance Criteria

- [x] Add an **Object track** value type that contains ordered **Detection
      events**, source name, class name, frame range, time range, optional
      detector track ID, and a representative **Detection event**.
- [x] Add a pure builder that accepts **Detection events** and returns **Object
      tracks**.
- [x] Group events with the same source name, class name, and explicit
      detector `track_id` into one track.
- [x] Keep events without `track_id` as singleton tracks in this first slice.
- [x] Keep track ordering deterministic.
- [x] Add focused tests for grouping, source separation, class separation, and
      singleton fallback.

## Notes

- This slice establishes the interface before adding heuristic linking.
- Events without `track_id` intentionally remain singleton tracks here; overlap
  linking starts in the next issue.
- It should not introduce a SQLite schema or CLI surface.
