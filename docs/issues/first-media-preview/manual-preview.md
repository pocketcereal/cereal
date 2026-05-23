# Manual Preview Verification

To manually verify the original file-preview phase, create a local config that points at the sample video:

```yaml
storage: data/storage
sources:
  - name: example
    uri: file:data/example.mp4
```

Run Cereal with that config:

```sh
uv run cereal --config config/file-preview.yaml
```

Manual check:

- A local **Preview window** opens.
- The sample video plays from `data/example.mp4`.
- Playback exits cleanly at end-of-file, or when quitting/closing the preview window.

Current development note:

`task dev` now runs the checked-in development config:

```sh
uv run cereal --config config/dev.yaml
```

That config is used for the later capture-device preview phase and may point at `device:0`.
See `docs/issues/capture-device-preview/manual-preview.md` for current **Capture device** verification.

Historical file-preview config:

```yaml
storage: data/storage
sources:
  - name: example
    uri: file:data/example.mp4
```

Out of scope for this phase:

- VLC or GStreamer integration.
- Audio playback.
- USB cameras.
- RTSP sources.
- Writing media to disk.
- Multi-source runtime behavior.
- Video preprocessing.
- Automated visual assertions.
