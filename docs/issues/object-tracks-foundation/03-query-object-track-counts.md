---
id: object-tracks-foundation-03
title: Query Object track counts
status: draft
parent: ./PRD.md
depends_on: [object-tracks-foundation-02]
external_ref:
labels: []
---

# Query Object Track Counts

## Goal

Add a local query path that reports **Object track** counts from stored
**Detection events** so developers can verify count semantics without relying on
agent behavior.

## Acceptance Criteria

- [ ] Compose the existing SQLite **Detection store** query with the **Object
      track** builder.
- [ ] Return track summaries with class name, track count, event count, and
      frame range metadata.
- [ ] Keep Detection label event counts separate from **Object track** counts.
- [ ] Add a CLI or task path for local inspection of **Object track** summaries.
- [ ] Add store-backed tests with repeated events that produce fewer tracks
      than raw events.

## Notes

- This slice may compute tracks on read rather than persisting a new table.
- Persisted track identity can wait until the grouping policy proves useful.
