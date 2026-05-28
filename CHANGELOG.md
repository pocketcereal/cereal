# Changelog

All notable changes to Cereal are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
adopts [Semantic Versioning](https://semver.org/spec/v2.0.0.html) once a
release is cut.

## [Unreleased]

### Added

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

### Fixed

- Detection startup now cleans up opened resources on composition failures.
- Detection now rejects non-file sources without `write: true` instead of
  silently creating recording evidence.
- Preview overlay samples are persisted before honoring a stop request.
- SQLite Detection store creation now creates missing parent directories.

### Dependencies

- Uses the system `ffmpeg` binary for default MP4 recording.
- Added `opencv-python>=4.13.0.92`.
- Added `pydantic-settings[yaml]>=2.14.1`.
- Added `ultralytics>=8.4.55`.
