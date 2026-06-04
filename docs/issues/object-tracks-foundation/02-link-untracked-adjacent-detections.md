---
id: object-tracks-foundation-02
title: Link untracked adjacent detections
status: draft
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

- [ ] Add a conservative same-source, same-class linking policy for untracked
      **Detection events**.
- [ ] Use a configurable frame-gap threshold with a default of one sampled
      frame gap.
- [ ] Use plain bounding-box IoU as the first matching signal.
- [ ] Use a configurable IoU threshold with a conservative default around
      `0.3`.
- [ ] Keep matching deterministic when multiple candidates are possible.
- [ ] Link to the highest-IoU candidate only when it is uniquely best by a
      small margin.
- [ ] Start a new track for tied or near-tied candidate matches.
- [ ] Do not merge events across different sources or classes.
- [ ] Add tests for one moving object, two separated objects, low-overlap
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
