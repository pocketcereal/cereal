# Changelog

All notable changes to Cereal are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
adopts [Semantic Versioning](https://semver.org/spec/v2.0.0.html) once a
release is cut.

## [Unreleased]

### Added

- `cereal.detection.tracks` with a provider-free `ObjectTrack` value type and a
  pure `build_object_tracks` builder that groups Detection events by source,
  class, and detector track ID, keeps untracked events as singleton tracks,
  orders events and tracks deterministically, and selects a highest-confidence
  representative event.
- Conservative untracked-detection linking in `build_object_tracks`: same-source,
  same-class events without a detector track ID are joined across adjacent
  sampled frames by bounding-box IoU, with a configurable frame gap (default 1)
  and IoU threshold (default 0.3), starting a new track for tied or near-tied
  candidate matches.

- `MASTER_DOMAIN_LIST.md` first-pass domain extraction for the planned VLM
  video-question architecture.
- Draft `detection-store` PRD and child issue breakdown for sampled object
  detection persistence.
- `cereal.detection` domain with Detection event types, SQLite persistence,
  YOLO adapter, sampled stream ingestion, evidence recording, manual
  verification notes, and optional preview overlays.
- `cereal.evidence` domain with DetectionEvent-centered Evidence window
  retrieval and a local `file://` OpenCV frame reader.
- `cereal.analysis` composition for selecting Evidence windows from Detection
  store query results and returning provider-free Visual inspections.
- `cereal.validation` provider-free Visual claim, Visual validation, and Visual
  validator contracts, plus Analysis composition for applying validators to
  Evidence windows.
- `cereal.agents` provider-free Agent definition loading from local `.agent`
  directories and a static Agent registry.
- `cereal.agents.deepagents_adapter` with a pure typed adapter from
  `specialized-subagent` Agent definitions to Deep Agents subagent config.
- `cereal.agents.deepagents_runtime` with pure Deep Agents composition helpers,
  repo-local `orchestrator` and `detection-lookup` Agent definitions, and a
  local Ollama Orchestrator smoke path.
- `cereal.agents.detection_lookup` with dependency-bound
  `find_detection_events` and `list_detection_labels` tools for the
  `detection-lookup` Specialized subagent.
- Direct `detection-lookup` Agent smoke path with a seeded Detection store,
  bound lookup tools, `qwen3:8b`, and `task detection-lookup-smoke`.
- `AgentToolCatalog` for resolving Agent definition tool names to callables.
- `AgentRuntimeBinding` and first `cereal.agents.trace` values for
  harness-visible Agent run traces.
- Orchestrator-to-`detection-lookup` delegation smoke path with seeded labels,
  trace assertions, `uv run cereal --agent orchestrator-delegation`, and
  `task orchestrator-delegation-smoke`.
- Agent-facing Evidence and fake Visual validation data tools plus
  visual-query planning smoke coverage with generated local video evidence,
  exact trace-order assertions, `uv run cereal --agent visual-query-planning`,
  and `task visual-query-planning-smoke`.
- Required `orchestrator.model` settings loaded from the Cereal YAML
  configuration file.
- Draft `agent-harness-integration` PRD and issue path for mapping Agent
  definitions into a Deep Agents harness adapter without hosted-service
  coupling.
- Added the next `agent-harness-integration` issue path for isolated
  `detection-lookup` tool binding before visual-query planning.
- Added the next `agent-harness-integration` issue path for direct
  `detection-lookup` LLM tool-use smoke before Orchestrator delegation.
- Split the next `agent-harness-integration` path so Orchestrator-to-
  `detection-lookup` delegation is proven before visual-query planning.
- `cereal detections` query command and `task detections` shortcut for local
  Detection store inspection.
- `cereal.media` package with `file:` and `device:` source adapters, a
  source-URI helper, a source-adapter registry, and an OpenCV-backed
  preview loop.
- Source recording during preview when the first configured source has
  `write: true`, including `.mp4` artifact path derivation and lazy
  ffmpeg-backed frame writing.
- Default `cereal` CLI command now opens the first configured source in a
  preview window after loading settings.
- Default `config/settings.yaml` now points at `device:0` with recording
  enabled for local source-recording verification.
- `--config` flag for selecting a non-default configuration file.
- `pydantic-settings`-backed `Settings` and `SourceSettings` types loaded
  from a YAML configuration file.
- Default `config/settings.yaml` matching `DEFAULT_CONFIG_PATH`.

### Changed

- Strict ruff `ALL` ruleset, with test-only docstring and assert-use ignores
  documented inline in `pyproject.toml`.
- `cereal.media.preview` no longer exports `load_opencv`; OpenCV is resolved
  once when either `capture_factory` or `backend` is omitted.
- Recording defaults now use ffmpeg-backed `.mp4` + `libx264`, and `Ctrl-C`
  is treated as a graceful preview stop so recording artifacts are finalized.
- Default `cereal` CLI command now runs the first-source Detection stream
  prototype while retaining Preview window feedback.
- `task dev` now enables preview Detection overlays for local object-detection
  inspection.
- Added `--preview` / `--no-preview` CLI flags so Detection can run with or
  without the desktop Preview window.
- Added `--overlays` so the Preview window can draw sampled Detection boxes.
- Added operational Detection logs for startup, source opening, sampled frame
  results, and persisted event counts.
- Detection store now supports grouped detector-label listing with Detection
  event counts.
- Default local Agent smoke model changed to `ollama:qwen3:8b` for tool-calling
  verification.
- Documentation now reflects the completed source-recording and capture-device
  PRDs, current Agent harness issue status, and the `write: true` requirement
  for non-file Detection evidence.

### Fixed

- Detection startup now cleans up opened resources on composition failures.
- Detection now rejects non-file sources without `write: true` instead of
  silently creating recording evidence.
- Preview overlay samples are persisted before honoring a stop request.
- SQLite Detection store creation now creates missing parent directories.
- SQLite Detection store access now works when Agent harness tool calls run in a
  worker thread.

### Dependencies

- Uses the system `ffmpeg` binary for default MP4 recording.
- Added `deepagents>=0.6.6`.
- Added `langchain-ollama>=1.1.0`.
- Added `opencv-python>=4.13.0.92`.
- Added `pydantic-settings[yaml]>=2.14.1`.
- Added `ultralytics>=8.4.55`.
