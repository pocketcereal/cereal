---
id: capture-device-preview-01
title: Preview the first capture device Source
status: done
parent: ./PRD.md
depends_on: []
external_ref:
---

## Goal

Open a numeric `device:` **Source URI** through a **Source adapter** and display it in the existing first-**Source** **Preview window** path.

## Acceptance Criteria

- [x] A `device:` **Source URI** such as `device:0` is interpreted as numeric **Device index** `0`.
- [x] A `DeviceSourceAdapter` opens a **Capture device** by passing the parsed **Device index** to the injected OpenCV capture factory.
- [x] The default **Source adapter registry** is composed in a small dedicated media registry Module.
- [x] The default **Source adapter registry** includes both `file:` and `device:` adapters.
- [x] The existing **Preview window** startup path can preview the first configured `device:` **Source**.
- [x] Tests cover pure `device:` URI parsing, device adapter opening, default registry composition, and preview startup with fakes.
- [x] Manual verification docs describe running Cereal with `uri: device:0`.
- [x] `task check` passes.

## Blocked by

None - can start immediately.

## Notes

- Keep the prototype lean; do not add device discovery, named devices, platform-specific device paths, or a new error taxonomy.
- Keep the existing first configured **Source** selection behavior.
- Keep `device:` parsing in the pure media URI helper Module.
- Keep OpenCV-specific lifecycle checks concentrated inside Source adapters.
