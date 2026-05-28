---
id: agent-definition-foundation
title: Agent definition foundation
status: done
external_ref:
---

# Agent Definition Foundation

## Problem Statement

Cereal now has Detection, Evidence, Validation, and Analysis primitives, but the
future **Orchestrator agent** still needs a provider-free way to discover which
agents or subagents are available. Without a small **Agent definition** contract,
agent behavior risks becoming hardcoded in Python modules or prompt strings
before the Deep Agents integration exists.

## Solution

Add a first library-only **Agent definition** foundation:

- A local `.agent` directory shape with `agent.toml` and `instructions.md`.
- Frozen **Agent definition** values.
- A loader for local **Agent definition** directories.
- A static **Agent registry** for lookup by stable name.

This slice stays independent of LangChain Deep Agents. The field names are
chosen to map cleanly to Deep Agents concepts later: instructions, tools,
skills, permissions, response format, and subagent kind.

## Current State

Implemented:

- `cereal.agents.AgentDefinition`
- `cereal.agents.AgentDefinitionKind`
- `cereal.agents.load_agent_definition`
- `cereal.agents.AgentRegistry`
- Local directory loading from `agent.toml` plus `instructions.md`
- Validation for blank required fields and duplicate registry names

## Implementation Decisions

- **Agent definitions** are data, not executable orchestration behavior.
- The first **Agent registry** is in-memory/static.
- The loader uses Python standard-library TOML parsing.
- The first supported kinds are `orchestrator` and `specialized-subagent`.
- Missing or invalid local definition files fail fast.

## Testing Decisions

- Test loading through real temporary `.agent` directories.
- Test validation failures through the public loader and value types.
- Test registry lookup and duplicate-name rejection through public methods.

## Out of Scope

- LangChain Deep Agents runtime integration.
- Creating or running an **Orchestrator agent**.
- Dynamic Agent definition generation.
- Agent definition persistence beyond local files.
- CLI commands for listing Agent definitions.
