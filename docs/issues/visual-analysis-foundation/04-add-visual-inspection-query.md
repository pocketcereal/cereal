---
id: visual-analysis-foundation-04
title: Add Visual inspection query composition
status: done
depends_on: ["visual-analysis-foundation-01", "visual-analysis-foundation-02", "visual-analysis-foundation-03"]
external_ref:
---

# Add Visual Inspection Query Composition

## Problem Statement

Cereal can query **Detection events**, retrieve **Evidence windows**, and apply
one **Visual claim** through an injected **Visual validator**, but callers still
need to compose those steps manually. The next slice should prove the
provider-free orchestration contract before adding VLM provider adapters,
prompt templates, user question parsing, or persisted analysis results.

## Acceptance Criteria

- [x] Add a **Visual inspection** value type in the **Analysis** domain.
- [x] A **Visual inspection** includes the original **Detection event**, the
      full in-memory **Evidence window**, the explicit **Visual claim**, and
      the resulting **Visual validation**.
- [x] Add an **Analysis query** function that accepts a **Detection event
      query**, **Detection store**, Evidence frame reader, explicit **Visual
      claim**, and injected **Visual validator**.
- [x] The query composes existing Detection, Evidence, and Validation ports
      without adding provider-specific code.
- [x] The query returns one **Visual inspection** per selected **Detection
      event**.
- [x] Missing center-frame evidence keeps the current Evidence selection
      behavior: fail the request rather than silently dropping selected
      detections.
- [x] If the injected **Visual validator** fails on any selected **Evidence
      window**, the whole query fails.
- [x] If the **Detection event query** selects no events, the query returns an
      empty tuple.
- [x] Tests use fake stores, fake Evidence readers, and fake **Visual
      validators**.
- [x] The slice remains library-only; no CLI or Taskfile command is added.

## Non-Goals

- Do not add a VLM provider adapter.
- Do not add prompt templates.
- Do not generate **Visual claims** from user questions.
- Do not persist **Visual inspections**.
- Do not add a broad CLI surface.
- Do not add a debug command until there is either a real validator or a useful
  deterministic debug validator.

## Notes

- This remains part of `visual-analysis-foundation` because it composes the
  provider-free foundation rather than introducing a new product-facing flow.
- First-slice **Visual inspections** are transient values with no durable ID,
  database row, or serialization contract.
- Verification includes a narrow integration test with a real SQLite
  **Detection store**, real local `file://` Evidence video reader, and fake
  **Visual validator**.
