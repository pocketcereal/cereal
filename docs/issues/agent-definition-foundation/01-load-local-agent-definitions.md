---
id: agent-definition-foundation-01
title: Load local Agent definitions
status: done
parent: ./PRD.md
depends_on: []
external_ref:
---

# Load Local Agent Definitions

## Goal

Make packaged `.agent` directories loadable as typed **Agent definitions** and
available through a small static **Agent registry**.

## Acceptance Criteria

- [x] `cereal.agents` exposes an immutable **Agent definition** value type.
- [x] **Agent definition** kind supports `orchestrator` and
      `specialized-subagent`.
- [x] A local `.agent` directory is loaded from `agent.toml` plus
      `instructions.md`.
- [x] Required fields include stable name, description, kind, and instructions.
- [x] Optional fields include tools, skills, permissions, and response format.
- [x] Missing `agent.toml` or `instructions.md` fails the load.
- [x] Blank required fields fail the load.
- [x] A static **Agent registry** can return definitions by name.
- [x] Duplicate Agent definition names are rejected.
- [x] Tests use real temporary `.agent` directories.
- [x] The slice is library-only; no CLI, Taskfile, or Deep Agents dependency is
      added.

## Non-Goals

- Do not instantiate Deep Agents.
- Do not run or delegate to subagents.
- Do not generate Agent definitions dynamically.
- Do not add a user-facing Agent definition registry command.
