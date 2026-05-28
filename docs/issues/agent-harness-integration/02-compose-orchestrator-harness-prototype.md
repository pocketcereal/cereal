---
id: agent-harness-integration-02
title: Compose Orchestrator harness prototype
status: done
parent: ./PRD.md
depends_on: [agent-harness-integration-01]
external_ref:
labels: []
---

# Compose Orchestrator Harness Prototype

## Goal

Create the first local **Orchestrator agent** composition using the selected
**Agent harness** and the adapter from issue 01.

## Acceptance Criteria

- [x] Compose an **Orchestrator agent** from a Cereal **Agent definition**.
- [x] Add a small generic Deep Agents composition helper for isolated agent
      composition tests.
- [x] Add a named **Orchestrator agent** composition wrapper over the generic
      helper.
- [x] Register all `specialized-subagent` definitions from the provided
      **Agent registry** for this first wrapper.
- [x] Add repo-local **Agent definitions** under `agents/`.
- [x] Add `agents/orchestrator.agent` for the first **Orchestrator agent**.
- [x] Add `agents/detection-lookup.agent` as the first generic
      **Detection lookup subagent** definition.
- [x] Load basic **Orchestrator settings** from the existing Cereal
      **Configuration file**.
- [x] Include the **Orchestrator model** in loaded **Orchestrator settings**.
- [x] Add an `orchestrator:` section to `config/settings.yaml` alongside
      `storage` and `sources`.
- [x] Keep first-slice **Orchestrator settings** limited to `model`.
- [x] Require `orchestrator.model` when loading **Settings**.
- [x] Register one or more **Specialized subagents** from the **Agent registry**.
- [x] Keep Cereal Detection, Evidence, Analysis, and Validation domain modules
      independent from harness imports.
- [x] Make tools explicit at the harness boundary.
- [x] Keep **Orchestrator agent** composition and **Specialized subagent**
      composition separately testable.
- [x] Support deterministic automated tests through an injected fake
      `create_deep_agent` factory.
- [x] Add a local Ollama smoke path that invokes the composed **Agent harness**
      with a tiny non-video prompt.
- [x] Use `OLLAMA_HOST` when present and configure the local smoke model as
      `ollama:qwen2.5:7b`.
- [x] Add `uv run cereal --agent orchestrator` as a narrow local smoke path.
- [x] Support only `--agent orchestrator` in this issue.
- [x] Add `task agent-smoke` as a developer shortcut for the local smoke path.
- [x] Document any unsupported **Agent definition** fields before they are
      silently ignored.
- [x] Add any Deep Agents dependency through `uv add` only when the runtime
      composition actually imports it.
- [x] Add any Ollama/LangChain integration dependency through `uv add` only when
      the runtime smoke path actually imports it.

## Implementation Notes

- Added `OrchestratorSettings` with required `model`.
- Added repo-local `orchestrator` and `detection-lookup` **Agent definitions**.
- Added `cereal.agents.deepagents_runtime` for pure Deep Agents composition and
  fixed-prompt smoke invocation.
- Added `uv run cereal --agent orchestrator` and `task agent-smoke`.
- Verified the local Ollama smoke path printed `ready`.

## Notes

- This issue should start only after issue 01 proves the adapter shape.
- The target behavior is harness composition plus a local LLM smoke invocation,
  not broad user-question solving.
- Automated checks should not require a running Ollama service.
- Manual smoke verification should use the locally exposed Ollama service and
  the installed `qwen2.5:7b` model.
- The smoke invocation should use a tiny fixed prompt such as "Reply with
  exactly: ready"; arbitrary prompt input is out of scope.
- The smoke prompt should live as a code constant in the smoke command/runtime
  function, not in **Agent definitions** or **Orchestrator settings**.
- Do not make subagent execution user-facing in this issue.
- The first runtime config should live in the existing YAML **Configuration
  file**, not in command arguments.
- Repo-local **Agent definitions** live under `agents/` because they are
  runtime assets, not Python source and not environment-specific config.
- Cereal's canonical **Agent definition** source remains
  `agent.toml` plus `instructions.md`; Deep Agents `AGENTS.md` conventions are
  harness details for now.
- The first **Specialized subagent** should be named `detection-lookup`: it can
  reason about Detection store details for labels or selected Detection events,
  but it should not encode the earlier vehicle/color example as a concrete
  implementation.
- The first **Specialized subagent** should not be named or scoped as a visual
  inspector because it works over detector output and label semantics, not raw
  frames.
- A prompt such as "find me white trucks between 2-4PM" should let the
  **Orchestrator agent** delegate label/time lookup work to this subagent, while
  color confirmation remains future evidence/visual-validation work.
- The `detection-lookup` instructions may mention that current detector output
  is YOLO-backed and that YOLO label semantics are relevant, but the Agent
  definition name should not be `YOLOAgent`.
- Do not bind real Detection store tools in this issue. `detection-lookup`
  should be registered as an available **Specialized subagent**, while concrete
  tool binding and isolated tool-bearing subagent tests belong to a later slice.
- Architecture guardrail: each agent must be testable through its own
  composition boundary before it is depended on by the **Orchestrator agent**.
- Prefer pure functions for first composition helpers. Do not introduce a broad
  Agent runtime class in this slice.
- The long-term direction is a harness and tool map that lets the
  **Orchestrator agent** choose, create, and run work, including future
  code-writing/execution capabilities. Do not hardcode question-solving
  strategies into the wrapper.
- First configuration shape:

  ```yaml
  orchestrator:
    model: ollama:qwen2.5:7b
  ```
- Do not add temperature, max tokens, timeout, provider config, tool policy,
  memory paths, subagent selection, or permissions until runtime behavior needs
  them.
- Do not provide a hidden code default for the **Orchestrator model**.
