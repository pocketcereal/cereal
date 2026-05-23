# Capture Device Preview Verification

Create a local config that selects the first capture device:

```yaml
storage: data/storage
sources:
  - name: camera
    uri: device:0
```

Run Cereal with that config:

```sh
uv run cereal --config config/dev.yaml
```

Manual check:

- A local **Preview window** opens.
- Frames from the local **Capture device** are visible.
- Preview exits cleanly when quitting or closing the preview window.

Notes:

- `device:0` is the first numeric **Device index** passed to OpenCV.
- This phase does not include device discovery, named devices, platform-specific device paths, or automated visual assertions.
