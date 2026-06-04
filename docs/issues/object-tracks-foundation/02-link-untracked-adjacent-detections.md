---
id: object-tracks-foundation-02
title: Link untracked adjacent detections
status: done
parent: ./PRD.md
depends_on: [object-tracks-foundation-01]
external_ref:
labels: []
---

# Link Untracked Adjacent Detections

## Goal

Improve count semantics for **Detection events** without detector `track_id` by
linking likely same-object events across adjacent sampled **Frames**.

## Acceptance Criteria

- [x] Add a conservative same-source, same-class linking policy for untracked
      **Detection events**.
- [x] Use a configurable frame-gap threshold with a default of one sampled
      frame gap.
- [x] Use plain bounding-box IoU as the first matching signal.
- [x] Use a configurable IoU threshold with a conservative default around
      `0.3`.
- [x] Keep matching deterministic when multiple candidates are possible.
- [x] Link to the highest-IoU candidate only when it is uniquely best by a
      small margin.
- [x] Start a new track for tied or near-tied candidate matches.
- [x] Do not merge events across different sources or classes.
- [x] Add tests for one moving object, two separated objects, low-overlap
      objects, and frame-gap boundaries.

## Notes

- Prefer splitting ambiguous tracks over over-merging unrelated objects.
- The one-frame-gap default exists to tolerate a single missed sampled
  detection without making long-range identity claims.
- The unique-best rule should be covered by tests with competing candidate
  tracks.
- Center-distance matching, velocity prediction, and appearance matching are
  out of scope for the first heuristic linker.
- This is not visual re-identification and should not call a VLM.
- `frame_index` is the raw decoded-frame counter, so the frame gap is measured
  over each source's sampled-frame timeline (sorted unique frame indices among
  events), not by raw `frame_index` difference. A gap therefore means a missed
  sampled detection, which is what the threshold is meant to tolerate.
