---
id: visual-analysis-foundation
title: Evidence and Visual validation foundation
status: done
external_ref:
---

# Evidence and Visual Validation Foundation

## Problem Statement

The **Detection store** can persist YOLO-backed **Detection events**, but later
analysis needs a clean path from structured detections back to visual evidence
and eventually to focused VLM validation. Without explicit domain boundaries,
Cereal risks pushing video-reading, store querying, and model-provider concerns
into the same modules.

## Solution

Add provider-free foundation packages that compose the detection foundation
without broadening it:

- `cereal.evidence` recovers in-memory **Evidence windows** from selected
  **Detection events**.
- `cereal.analysis` coordinates **Detection store** query results, Evidence
  readers, and **Visual validators**.
- `cereal.validation` defines provider-free **Visual claim**, **Visual
  validation**, and **Visual validator** contracts.

## Current State

Implemented:

- **Evidence window** retrieval centered on one caller-provided
  **Detection event**.
- Default evidence radius of 2 frames.
- Full-frame retrieval with **Evidence target** metadata rather than crops.
- Center frame required; neighbor frames best-effort.
- Local `file://` OpenCV-backed Evidence frame reader.
- **Analysis** selection from **Detection event queries** to
  **Evidence windows**.
- **Visual validation** contracts and **Analysis** composition for applying one
  **Visual claim** to selected **Evidence windows** through an injected
  **Visual validator**.
- **Visual inspection** query composition that preserves the selected
  **Detection event**, recovered **Evidence window**, explicit **Visual claim**,
  and resulting **Visual validation**.
- A narrow integration test proves a stored SQLite **Detection event** can
  recover frames from a local `file://` video and produce a **Visual
  inspection** with a fake **Visual validator**.

## Implementation Decisions

- **Evidence** does not query the **Detection store**.
- **Detection** does not read video evidence.
- **Analysis** is the composition layer between **Detection**, **Evidence**, and
  **Validation**.
- First-slice retrieval returns in-memory **Frames** only; persisted
  **Evidence artifacts** are deferred.
- First-slice **Visual validation** is provider-free; concrete VLM adapters are
  deferred.
- Missing center-frame evidence fails the whole **Analysis** selection for now.
- First-slice **Visual inspections** are transient in-memory values, not
  persisted rows or serialized evidence packets.
- The first **Analysis query** uses Evidence retrieval defaults rather than
  exposing additional query knobs.

## Testing Decisions

- Test Evidence retrieval through fake frame readers.
- Test the OpenCV Evidence reader with generated local videos.
- Test Analysis composition with fake **Detection stores**, fake Evidence
  readers, and fake **Visual validators**.
- Test the first **Visual inspection** query through a real SQLite **Detection
  store** and real local video Evidence reader while keeping validation fake.
- Test validation contracts without any model-provider dependency.

## Out of Scope

- VLM provider adapters.
- Prompt templates.
- User-facing question parsing.
- Persisted **Visual validations**.
- Persisted **Visual inspections**.
- Persisted extracted **Evidence artifacts**.
- Object-track creation or count semantics.
- CLI commands for Evidence windows or Visual validation.
