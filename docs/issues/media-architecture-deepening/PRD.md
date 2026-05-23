---
id: media-architecture-deepening
title: Media architecture deepening
status: approved
external_ref:
---

# Media Architecture Deepening

## Goal

Deepen the Cereal media runtime after the first **Preview window** phase by concentrating repeated **Source URI** interpretation, **Preview window** startup composition, and OpenCV-specific capture behavior behind clearer Modules.

## Scope

- Parse configured **Source URI** values into one reusable domain Module after YAML loading.
- Keep unsupported **Source URI** schemes failing naturally through Source adapter lookup.
- Keep the **CLI command** surface thin while moving **Preview window** startup composition behind the **Preview window** Module.
- Keep the preview loop focused on frame display and resource cleanup.
- Keep **Frame** opaque for now.
- Concentrate OpenCV-specific lifecycle details inside the OpenCV/file Source adapter implementation.
- Record that first-Source selection remains intentionally shallow until a second Source runtime policy exists.

## Out Of Scope

- New Source adapter schemes.
- Polished unsupported-scheme error handling.
- Multi-Source runtime behavior.
- Writing media to disk.
- A Cereal Frame pixel wrapper.
- Preview subcommands.
- VLC or GStreamer integration.

## Architecture Notes

- Use a pure value Module for **Source URI** interpretation.
- Use functional core with injected adapters for **Preview window** behavior.
- Do not create a new Source selection policy Module until another policy appears, such as multi-Source runtime, Write flag behavior, named Source selection, or adapter capability checks.
