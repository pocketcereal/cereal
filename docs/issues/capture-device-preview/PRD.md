---
id: capture-device-preview
title: Capture device preview
status: approved
external_ref:
---

# Capture Device Preview

## Goal

Preview the first configured `device:` **Source** in the existing **Preview window** path so Cereal can manually verify a local **Capture device**.

## Scope

- Support `device:` **Source URI** values that identify a numeric **Device index**, such as `device:0`.
- Add a `device:` **Source adapter** that opens a **Capture device** through the injected OpenCV capture factory.
- Keep `device:` **Source URI** parsing in the pure media URI helper Module.
- Move default **Source adapter registry** composition into a small dedicated media registry Module.
- Keep the existing first-**Source** **Preview window** behavior.
- Unit test the adapter, registry composition, URI parsing, and preview startup with fakes.
- Document manual verification with a local **Capture device**.

## Out Of Scope

- Capture device discovery.
- Human-readable device names.
- Platform-specific device paths.
- Multiple simultaneous Sources.
- Preview subcommands.
- Recording media to disk.
- Deep error handling or a new error taxonomy.
- A generalized plugin system.

## Architecture Notes

- Use the existing **Source URI** scheme dispatch model.
- Keep the prototype lean: rely on natural OpenCV/runtime failures unless a small message makes manual verification clearer.
- Favor small single-purpose media Modules: URI parsing, adapter behavior, registry composition, and preview loop behavior should stay separate.
