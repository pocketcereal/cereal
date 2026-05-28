---
id: visual-analysis-foundation-02
title: Compose Analysis evidence selection
status: done
parent: ./PRD.md
depends_on: ["visual-analysis-foundation-01", "detection-store-02"]
external_ref:
---

## Goal

Add the first **Analysis** composition helper that turns a
**Detection event query** into selected **Evidence windows** without moving store
access into **Evidence**.

## Acceptance Criteria

- [x] `cereal.analysis` is introduced as a domain coordinator package.
- [x] Evidence selection accepts a **Detection event query**, **Detection store**,
  Evidence frame reader, and frame radius.
- [x] Evidence selection returns a tuple of **Evidence windows**.
- [x] Empty query results return an empty tuple.
- [x] The default radius comes from the Evidence retrieval default.
- [x] A custom radius can be provided.
- [x] Missing center-frame evidence fails the whole selection.
- [x] Tests cover store query use, default/custom radius behavior, empty
  results, and failure propagation.
- [x] `task check` passes.

## Notes

- This is still library-only; do not add Evidence CLI arguments.
- Partial-result behavior can be revisited once user-facing answers need
  warnings instead of hard failures.
