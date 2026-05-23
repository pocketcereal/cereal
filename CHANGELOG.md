# Changelog

All notable changes to Cereal are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
adopts [Semantic Versioning](https://semver.org/spec/v2.0.0.html) once a
release is cut.

## [Unreleased]

### Added

- `cereal.media` package with `file:` and `device:` source adapters, a
  source-URI helper, a source-adapter registry, and an OpenCV-backed
  preview loop.
- Default `cereal` CLI command now opens the first configured source in a
  preview window after loading settings.
- `--config` flag for selecting a non-default configuration file.
- `pydantic-settings`-backed `Settings` and `SourceSettings` types loaded
  from a YAML configuration file.
- Default `config/settings.yaml` matching `DEFAULT_CONFIG_PATH`.

### Changed

- Strict ruff `ALL` ruleset, with test-only docstring and assert-use ignores
  documented inline in `pyproject.toml`.
- `cereal.media.preview` no longer exports `load_opencv`; OpenCV is resolved
  once when either `capture_factory` or `backend` is omitted.

### Dependencies

- Added `opencv-python>=4.13.0.92`.
- Added `pydantic-settings[yaml]>=2.14.1`.
