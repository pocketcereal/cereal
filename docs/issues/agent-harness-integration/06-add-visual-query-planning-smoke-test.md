---
id: agent-harness-integration-06
title: Add visual query planning smoke test
status: done
parent: ./PRD.md
depends_on: [agent-harness-integration-05]
external_ref:
labels: []
---

# Add Visual Query Planning Smoke Test

## Goal

Prove that the **Orchestrator agent** can choose a simple visual-analysis
strategy from available Cereal tools and **Specialized subagents** without a
hardcoded workflow for a specific question. This issue proves planner shape and
boundary correctness, not final answer quality.

## Acceptance Criteria

- [x] Provide a smoke-test scenario that exercises Detection lookup, Evidence
      window retrieval, and Visual validation without a concrete hardcoded
      object workflow.
- [x] Expose Evidence window retrieval and Visual validation as tool-like
      capabilities at the harness boundary.
- [x] Expose Evidence retrieval as one focused `retrieve_evidence_window`
      agent-facing data tool; keep Detection event selection in Orchestrator
      planning behavior.
- [x] Have `retrieve_evidence_window` accept a serialized **Detection event
      reference** derived from Detection lookup output, not a private SQLite row
      ID or raw Detection event object.
- [x] Use `detection_event_ref` as the Evidence retrieval input field and
      `evidence_window_ref` as the run-local Evidence window handle field.
- [x] Implement agent-facing Evidence and Visual validation tools under
      `cereal.agents.*`, not in `cereal.analysis`.
- [x] Keep `cereal.evidence`, `cereal.validation`, and `cereal.analysis`
      provider- and harness-neutral.
- [x] Compose `cereal.evidence` and `cereal.validation` ports directly from
      agent-facing data tools rather than routing through a broad
      `cereal.analysis` helper.
- [x] Exercise real `cereal.evidence` retrieval against deterministic local
      recoverable frame evidence.
- [x] Use a tiny local video fixture for Evidence retrieval rather than
      extracted still frames or live camera data.
- [x] Generate the tiny local video fixture at test/smoke runtime instead of
      committing a binary test asset.
- [x] Generate three to five simple deterministic frames with visually distinct
      colors or labels for retrieval debugging, not visual semantics.
- [x] Treat direct Orchestrator access to Evidence and Visual validation tools
      as staged exposure for this smoke, not permanent capability ownership.
- [x] Record that Evidence and Visual validation capabilities should later be
      registered with focused **Specialized subagents** once those subagents are
      defined and tested.
- [x] Do not create placeholder Evidence or Visual validation subagent issues
      before this smoke reveals the natural boundaries.
- [x] Use a fake/injected **Visual validator** for deterministic smoke behavior.
- [x] Have the fake Visual validation tool validate only a structured
      **Visual claim** plus serialized evidence-window reference.
- [x] Name the fake Visual validation tool `validate_visual_claim`.
- [x] Use `claim`, `status`, `class_name`, and `evidence_window_ref` fields in
      fake Visual validation payloads.
- [x] Return a fixed fake Visual validation status of `supported`.
- [x] Treat the evidence-window reference as an opaque run-local handle, not a
      durable external identifier.
- [x] Do not call a real VLM provider in this issue.
- [x] Do not inspect pixels or simulate real VLM answer quality in this issue.
- [x] Let the **Orchestrator agent** select the sequence of capabilities.
- [x] Verify the planned capability sequence is Detection lookup, Evidence
      window retrieval, then fake Visual validation.
- [x] Assert the exact trace order for the planning sequence, not only that all
      three capabilities appeared somewhere in the run.
- [x] Represent Detection lookup as Orchestrator delegation to the
      `detection-lookup` **Specialized subagent**, not as direct Orchestrator
      ownership of Detection lookup tools.
- [x] Assert the deterministic trace includes Orchestrator ->
      `detection-lookup` delegation, `detection-lookup.find_detection_events`,
      Orchestrator `retrieve_evidence_window`, and Orchestrator
      `validate_visual_claim` in that order.
- [x] Use a focused Detection lookup for `find_detection_events(label="car",
      source_name="smoke_fixture", limit=1)`.
- [x] Validate one selected candidate Detection event only.
- [x] Do not require `list_detection_labels` or semantic label discovery in
      this smoke.
- [x] Treat a passing smoke as proof of planner shape and boundary correctness,
      not as proof of natural-language answer quality or model quality.
- [x] Require the final smoke output to include the fixed validation status and
      label, such as `supported: car`, as a completion sanity check.
- [x] Keep final-output assertions secondary to **Agent run trace** assertions.
- [x] Use a fixed structured planning prompt rather than broad natural-language
      video QA.
- [x] Reuse **Agent run trace** vocabulary from issue 05 for harness-visible
      action checks.
- [x] Add `task visual-query-planning-smoke` as a separate boundary-specific
      smoke path rather than reusing `task orchestrator-delegation-smoke`.
- [x] Keep deterministic fake-harness coverage authoritative for automated
      trace and sequence assertions.
- [x] Treat the real Deep Agents/Ollama smoke task as manual runtime-wiring
      confidence, not as the source of deterministic planner proof.
- [x] Keep deterministic fixtures or fake providers available for repeatable
      tests.
- [x] Record whether count-style answers require **Object tracks** before they
      can be considered semantically correct.

## Notes

- This issue may reveal that **Object track** creation is the more important
  next domain slice before natural-language query answering.
- The smoke test should measure planning shape and boundary correctness, not
  model quality.
- The smoke result may use a minimal final response; the important assertion is
  the **Agent run trace** showing the planned capability sequence.
- A minimal final output such as `supported: car` is enough; the smoke should
  not grade answer prose.
- A trace that calls fake Visual validation before Evidence retrieval, or
  Evidence retrieval before Detection lookup, should fail the deterministic
  smoke even if all three capabilities appear.
- The first expected trace shape is:
  Orchestrator delegates to `detection-lookup`; `detection-lookup` calls and
  returns `find_detection_events`; Orchestrator calls and returns
  `retrieve_evidence_window`; Orchestrator calls and returns
  `validate_visual_claim`.
- The structured prompt may explicitly ask for candidate car detections; label
  discovery was already covered by the `detection-lookup` smoke path.
- Multiple candidate ranking, selection policy, and partial validation behavior
  are out of scope until the single-candidate planning path is stable.
- Real VLM provider adapters, prompt design, image formatting, latency, and
  cost controls belong to a later issue after the orchestration boundary is
  proven with fake providers.
- Agent-facing Evidence and Visual validation tools should compose existing
  domain ports and return serializable result shapes for agent inspection.
- Evidence retrieval should be real and deterministic in this smoke; Visual
  validation should remain fake and deterministic.
- Use a tiny local video fixture so Evidence retrieval exercises center-frame
  and neighbor-frame window behavior.
- Generate the video fixture in a temp directory so the fixture remains
  self-describing in test/smoke code and avoids binary asset churn.
- The generated video does not need to depict a real car; Detection events seed
  the candidate, and fake Visual validation does not inspect pixels.
- Evidence retrieval should be one tool in this slice: `retrieve_evidence_window`.
  Splitting selection into a separate tool waits until the planner trace shows
  that boundary is useful.
- The first **Detection event reference** should include stable event context
  already exposed by Detection lookup output, such as source name, frame index,
  media or observed time, class name, and **Evidence URI**.
- `retrieve_evidence_window` input shape:

  ```json
  {
    "detection_event_ref": {
      "source_name": "smoke_fixture",
      "frame_index": 2,
      "media_time_ms": 200,
      "observed_time": null,
      "class_name": "car",
      "confidence": 0.91,
      "evidence_uri": "file:///tmp/...",
      "bounding_box": [10, 20, 80, 90]
    },
    "frame_radius": 1
  }
  ```

- `retrieve_evidence_window` output shape:

  ```json
  {
    "evidence_window_ref": "run-local:smoke_fixture:2:car",
    "source_name": "smoke_fixture",
    "center_frame_index": 2,
    "frame_count": 3,
    "target": {
      "class_name": "car",
      "confidence": 0.91,
      "bounding_box": [10, 20, 80, 90]
    },
    "evidence_uri": "file:///tmp/..."
  }
  ```

- `validate_visual_claim` input shape:

  ```json
  {
    "claim": "the object is a car",
    "evidence_window_ref": "run-local:smoke_fixture:2:car"
  }
  ```

- `validate_visual_claim` output shape:

  ```json
  {
    "claim": "the object is a car",
    "status": "supported",
    "class_name": "car",
    "evidence_window_ref": "run-local:smoke_fixture:2:car"
  }
  ```

- The fake Visual validation tool should consume the serialized reference
  returned by Evidence retrieval, with any in-memory **Evidence window** object
  held behind an injected smoke-runtime map.
- Fake Visual validation should return fixed `supported`; negative, uncertain,
  or configurable validation outcomes belong to later validation-policy work.
- The first evidence-window reference should include enough summary metadata for
  agent planning, but durability and cross-run identity belong to future
  **Evidence packets**.
- Include only evidence-window handle, source name, center frame index, frame
  count, target class name, target confidence, target bounding box, and
  **Evidence URI** in the first evidence-window reference.
- Do not include raw frames, pixels, per-frame image data, or a durable evidence
  ID in the evidence-window reference.
- Do not move agent/harness concerns into `cereal.analysis`.
- Keep this slice small: the **Orchestrator agent** may use the new tools
  directly for planning smoke, while long-term ownership belongs with future
  focused **Specialized subagents**.
- Defer new subagent issue creation until this smoke clarifies whether the next
  focused agent boundary is Evidence retrieval, Visual validation, Visual
  inspection, or another task-shaped capability.
- A suitable first prompt is shaped like: "Find candidate car detections in
  `smoke_fixture`, retrieve evidence for one candidate, and validate the claim
  `the object is a car`."
- Broad natural-language questions such as "how many white trucks were there
  between 2-3pm?" wait until delegation, trace verification, evidence tools,
  fake validation, Object-track count semantics, and provider boundaries are
  clearer.
- Do not broaden **Agent run trace** into a full observability platform in this
  issue; persistence, UI, hosted tracing, export formats, and run comparison
  belong to a later PRD when needed.
- Keep the smoke ladder explicit: `agent-smoke` for harness liveness,
  `detection-lookup-smoke` for isolated tool use,
  `orchestrator-delegation-smoke` for subagent delegation, and
  `visual-query-planning-smoke` for Detection lookup -> Evidence retrieval ->
  fake Visual validation planning.
- Automated tests should use an injected fake harness/runtime so planner-shape
  assertions do not depend on a local model making the expected choices.
- The real `visual-query-planning-smoke` task should still run through the
  actual **Agent harness** as a manual confidence check for runtime wiring.
