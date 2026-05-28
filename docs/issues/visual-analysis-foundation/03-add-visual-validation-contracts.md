---
id: visual-analysis-foundation-03
title: Add Visual validation contracts
status: done
parent: ./PRD.md
depends_on: ["visual-analysis-foundation-02"]
external_ref:
---

## Goal

Define provider-free **Visual validation** contracts and compose them with
selected **Evidence windows**.

## Acceptance Criteria

- [x] `cereal.validation` defines **Visual claim**, **Visual validation
  request**, **Visual validation**, and **Visual validator** contracts.
- [x] Blank **Visual claims** are rejected.
- [x] **Visual validation** confidence must be between 0 and 1.
- [x] **Visual validation** explanations cannot be blank.
- [x] **Analysis** can apply one **Visual claim** to a sequence of
  **Evidence windows** through an injected **Visual validator**.
- [x] Empty Evidence window input returns an empty validation tuple.
- [x] Tests cover validation type guards and Analysis composition with a fake
  validator.
- [x] `task check` passes.

## Notes

- Do not add a concrete VLM provider adapter in this slice.
- Keep provider prompts and model-specific response parsing out of the domain
  contracts.
