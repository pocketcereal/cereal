# Agent-Facing Capability Contract

This document describes the lightweight contract for Cereal capabilities that
the **Orchestrator agent** can choose and compose while planning a task.

The contract is documentation-first for now. It should guide tool outputs,
agent instructions, issue acceptance criteria, and tests before becoming typed
repo data.

The central contract is canonical. Each `.agent` definition should carry a
short capability-facet summary for the capabilities it owns, so agent behavior
stays aligned with this vocabulary at runtime.

## Vocabulary

**Agent-facing capability**:
A focused tool, **Specialized subagent**, or staged **Orchestrator agent** tool
exposure that the **Orchestrator agent** can choose while planning how to answer
a task.

**Capability facet**:
One named part of the capability contract that helps the **Orchestrator agent**
understand what the capability does, what it needs, what it returns, and what
follow-up work it enables.

**Agent-facing capability contract**:
The shared descriptive shape made from capability facets.

## Required Facets

Each agent-facing capability should be described with these facets:

- `name`: stable capability name, usually matching the tool or subagent-facing
  operation.
- `owner`: the **Specialized subagent** or staged **Orchestrator agent** surface
  that exposes the capability.
- `purpose`: the narrow planning job the capability performs.
- `inputs`: structured input fields and accepted filter scope.
- `outputs`: compact serializable result shape.
- `uncertainty`: explicit confidence, ambiguity, missing-data, or policy-limit
  signals the agent should consider.
- `evidence`: **Evidence URI**, **Detection event reference**, **Evidence window
  reference**, or other evidence handle when available.
- `follow_up_capabilities`: suggested next capability types that may help the
  **Orchestrator agent** continue planning.
- `boundaries`: what the capability deliberately does not decide.

## Follow-Up Hints

`follow_up_capabilities` are hints, not workflow instructions.

They help the **Orchestrator agent** see affordances such as:

- `find_detection_events`
- `lookup_object_tracks`
- `retrieve_evidence_window`
- `validate_visual_claim`
- `compare_candidates`

The **Orchestrator agent** still decides which capability to use next.

## Current Capability Shapes

### Detection Lookup

- `owner`: `detection-lookup`
- `purpose`: find structured **Detection events** or label summaries in a
  source/time scope.
- `uncertainty`: no visual confirmation of attributes beyond stored detector
  data.
- `evidence`: **Detection event references** and **Evidence URI** values when
  event results are returned.
- `follow_up_capabilities`: `lookup_object_tracks`,
  `retrieve_evidence_window`, `validate_visual_claim`
- `boundaries`: does not count physical objects or validate visual attributes.

### Object Track Lookup

- `owner`: first slice attaches to `detection-lookup`
- `purpose`: return query-local candidate physical-object groups derived from
  **Detection events**.
- `uncertainty`: grouping basis, split/merge ambiguity, event count,
  confidence range, and policy limits.
- `evidence`: representative **Detection event reference** plus source/time and
  frame range metadata.
- `follow_up_capabilities`: `retrieve_evidence_window`,
  `validate_visual_claim`, `compare_candidates`
- `boundaries`: does not produce final natural-language answers or durable
  cross-run object identity.

### Evidence Retrieval

- `owner`: staged direct **Orchestrator agent** exposure until a focused owner
  is defined.
- `purpose`: recover an **Evidence window** around a selected **Detection event**
  or future **Object track** candidate.
- `uncertainty`: missing center frame is a failure; neighbor frames are
  best-effort.
- `evidence`: run-local **Evidence window reference**.
- `follow_up_capabilities`: `validate_visual_claim`
- `boundaries`: does not validate claims or answer user questions.

### Visual Validation

- `owner`: staged direct **Orchestrator agent** exposure until a focused owner
  is defined.
- `purpose`: evaluate one focused **Visual claim** against one **Evidence
  window**.
- `uncertainty`: validation status and provider-specific confidence once real
  providers exist.
- `evidence`: **Evidence window reference**.
- `follow_up_capabilities`: `compare_candidates`, `compose_answer`
- `boundaries`: does not retrieve detections or decide the full answer plan.
