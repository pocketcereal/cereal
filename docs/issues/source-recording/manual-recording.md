# Manual Source Recording Verification

Use a local **Capture device** and enable the first **Source** **Write flag**:

```yaml
storage: data/storage
sources:
  - name: camera
    uri: device:0
    write: true
```

Run Cereal:

```bash
uv run cereal
```

The default recording writer expects `ffmpeg` on `PATH`.

Verify that the **Preview window** opens and that pressing `q` or `Ctrl-C`
creates one `.mp4`
**Recording artifact** under
`data/storage/camera/<date>/<unix-timestamp>.mp4`.
