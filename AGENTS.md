# Agent Instructions

## Agent skills

### Planning workflow

Start with `to-prd`, break the PRD into issues with `to-issues`, then implement one issue at a time with `tdd`. The canonical store and any mirror rules are defined in `docs/agents/issue-tracker.md`.

### External tracker

If this repo uses an external tracker, label and adapter rules live in `docs/agents/triage-labels.md`.

### Decision docs

ADRs live under `docs/adr/` and are created lazily for durable, non-obvious trade-offs.

### Optional context docs

If the repo uses glossary/context docs, they live under `docs/CONTEXT.md` or `docs/CONTEXT-MAP.md`. See `docs/agents/domain.md`.

## Coding guidelines

- Prefer small, focused changes that match the existing project structure.
- Keep tests close to the behavior they cover.
- Do not introduce new dependencies unless they clearly simplify the implementation.
- Update docs when behavior, commands, or workflow expectations change.
- Prefer functional programming patterns: pure functions, explicit inputs, immutable data where practical, and isolated side effects.
- Use dependency injection for configuration, IO, clients, clocks, and other external effects.
- Apply SOLID principles pragmatically; keep modules cohesive, dependencies explicit, and interfaces narrow.
- Avoid module-level mutable global state. Use globals only for true constants or when a library integration requires it.
- Before implementing non-trivial behavior, discuss the programming pattern being used and why it fits the design.
- Keep Taskfile tasks basic. If a task needs more than 3-4 command lines, move the logic into `scripts/*.sh` and call that script from the Taskfile.
- Keep Python linting strict. Ruff should use `select = ["ALL"]` with only documented conflict or test-specific ignores.
- Resolve Python dependencies with `uv add` so `pyproject.toml` and `uv.lock` reflect current package metadata instead of hand-written stale versions.
- Do not assert exact terminal output strings that are likely to change. Prefer testing return codes, structured values, or stable behavioral signals.
