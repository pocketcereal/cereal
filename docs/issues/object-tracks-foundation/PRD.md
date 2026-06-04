---
id: object-tracks-foundation
title: Object tracks foundation
status: approved
external_ref:
---

# Object Tracks Foundation

## Problem Statement

Cereal can persist **Detection events**, recover **Evidence windows**, and prove
that the **Orchestrator agent** can plan a single-candidate visual validation
path. Count-style questions still are not semantically correct because raw
**Detection events** are one-frame model observations, not physical objects.

Users need Cereal to group repeated **Detection events** for the same physical
object into **Object tracks** so local queries and future agents can inspect
candidate physical objects, retrieve evidence, validate claims, and decide how
to answer count-style tasks without treating frame-level observations as final
objects.

## Solution

Add a small, deterministic **Object track** foundation:

- Define provider-free **Object track** value types derived from **Detection
  events**.
- Start with a pure track builder that can be tested without SQLite, OpenCV, or
  an agent harness.
- Prefer explicit detector `track_id` when present.
- Add a conservative overlap-and-adjacency fallback for untracked sampled
  **Detection events**.
- Add local query/reporting paths that count **Object tracks**, not raw
  **Detection events**.
- Expose track lookup to the agent harness as one focused agent-facing
  capability only after local track semantics are testable.

## User Stories

1. As a Cereal user, I want repeated detections of the same physical object to
   be grouped, so that counts are not inflated by frame sampling.
2. As a Cereal user, I want object counts to come from **Object tracks**, so
   that count-style answers mean physical objects rather than detections.
3. As a Cereal user, I want each **Object track** to preserve its source
   **Detection events**, so that answers remain auditable.
4. As a Cereal user, I want each **Object track** to expose representative
   evidence context, so that visual validation can inspect the object later.
5. As a Cereal developer, I want track-building behavior to be deterministic,
   so that tests can pin count semantics.
6. As a Cereal developer, I want explicit detector `track_id` values preserved,
   so that provider tracking can be used when available.
7. As a Cereal developer, I want untracked detections handled conservatively,
   so that Cereal can still improve count semantics before stateful detector
   tracking is introduced.
8. As a Cereal developer, I want ambiguous grouping decisions to be visible,
   so that future policy work can improve tracking without hiding uncertainty.
9. As a Cereal developer, I want track query helpers to compose the existing
   **Detection store**, so that the first slice avoids a premature storage
   schema for derived tracks.
10. As a Cereal developer, I want the agent-facing track tools to return
    serializable summaries, so that **Specialized subagents** can reason over
    tracks without receiving raw domain objects.
11. As a Cereal developer, I want track lookup to return candidate groups and
    uncertainty signals, so that the **Orchestrator agent** can decide whether
    to validate, split, merge, or ask another capability for help.

## Implementation Decisions

- Keep **Object track** creation in `cereal.detection` because tracks are derived
  from **Detection events**.
- Use pure functions for first-slice track construction.
- Represent one **Object track** as a source, class name, ordered **Detection
  events**, frame range, time range, representative event, and optional detector
  track ID.
- Treat **Object tracks** as inspectable candidates for agent planning rather
  than final answers or durable identity claims.
- Treat explicit detector `track_id` as a strong grouping signal within the
  same source and class.
- In the first issue, keep events without `track_id` as singleton tracks so the
  **Object track** type and explicit grouping semantics land before heuristic
  policy.
- In the second issue, add a conservative same-source, same-class,
  nearby-frame, bounding-box-overlap policy for events without `track_id`.
- The first heuristic policy should allow a small configurable frame gap with a
  conservative default of one sampled frame gap, so a single missed sampled
  detection does not split an obvious **Object track**.
- The first overlap signal should be plain bounding-box IoU with a conservative
  default threshold around `0.3`; center-distance and appearance-based matching
  wait until IoU behavior proves insufficient.
- When multiple open **Object tracks** can match one untracked **Detection
  event**, choose the highest-IoU match only when it is uniquely best by a small
  margin; tied or near-tied matches should start a new track rather than
  over-merge crowded scenes.
- Compute tracks from queried **Detection events** first; persist derived
  **Object tracks** only after the policy stabilizes.
- Keep track counts separate from Detection label event counts.
- Add agent-facing track lookup only after local track query behavior is stable.
- Agent-facing track lookup should expose grouping basis and uncertainty
  metadata so the **Orchestrator agent** can choose follow-up capabilities.

## Testing Decisions

- Unit-test the pure track builder with deterministic **Detection events**.
- Cover explicit `track_id` grouping, singleton fallback, and overlap-based
  grouping.
- Test boundary cases such as different source names, different class names,
  frame gaps, and low-overlap boxes.
- Add store-backed integration tests only when track query helpers compose with
  SQLite **Detection store**.
- Keep live agent/model tests out of the first Object track issues; use
  deterministic fake harness coverage when track tools reach agents.

## Out of Scope

- Real-time stateful detector tracking.
- Training or tuning a tracker model.
- Multi-camera identity reconciliation.
- Long-term persisted track identity across unrelated Cereal runs.
- Natural-language count answering.
- Visual re-identification or VLM-based track merging.

## Further Notes

- A first conservative policy is allowed to under-count or split ambiguous
  tracks as long as behavior is explicit and tested.
- Ambiguous matches should be visible as split tracks until Cereal has better
  identity evidence.
- The first local query path should make it obvious when results are event
  counts versus **Object track** counts.
- Track counts are useful planning facts, not the whole answer; final
  count-style responses still require agent composition with evidence and
  validation capabilities when the question asks for visual attributes or
  uncertain identity.
