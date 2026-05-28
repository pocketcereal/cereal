# Manual Detection Stream Verification

This verifies the first-source Detection stream prototype. It runs detection for the first configured Source only and keeps local Preview window feedback visible while the stream runs.

## Run

Confirm `config/settings.yaml` has the Source you want as the first entry, then run:

```bash
task dev
```

`task dev` enables preview Detection overlays for local visual inspection.
Press `q` in the Preview window or close the window to stop ingestion.

For automated or headless verification, disable the Preview window:

```bash
uv run cereal --no-preview --config config/settings.yaml
```

`--preview` can be passed explicitly to keep the default preview-on behavior.

## Logs

Cereal emits standard Python `INFO` logs while detection runs. The useful lines are:

- startup options: configuration storage, preview state, and overlay state
- source opening: source name, URI, preview state, overlay state, and database path
- runtime readiness: detector model and evidence URI
- sampled frames: raw detector candidate count and kept-above-threshold count
- store writes: persisted event count and evidence URI

## Store

Detection events are written to:

```text
data/storage/cereal.sqlite3
```

Use `sqlite3` to inspect recent events:

```bash
sqlite3 data/storage/cereal.sqlite3 \
  "SELECT source_name, class_name, confidence, observed_time_s, media_time_ms, frame_index, evidence_uri FROM detection_events ORDER BY id DESC LIMIT 20;"
```

Or use Cereal's local query helper:

```bash
task detections
uv run cereal detections --source camera --class person --min-confidence 0.5 --limit 20
```

Query one source and class:

```bash
sqlite3 data/storage/cereal.sqlite3 \
  "SELECT class_name, confidence, frame_index, evidence_uri FROM detection_events WHERE source_name = 'camera' AND class_name = 'person' ORDER BY observed_time_s, frame_index LIMIT 20;"
```

Query an observed-time range for a capture device:

```bash
sqlite3 data/storage/cereal.sqlite3 \
  "SELECT class_name, confidence, observed_time_s, frame_index FROM detection_events WHERE observed_time_s >= '2026-05-24T12:00:00+00:00' AND observed_time_s <= '2026-05-24T13:00:00+00:00' ORDER BY observed_time_s, frame_index;"
```

Query a media-time range for a file Source:

```bash
sqlite3 data/storage/cereal.sqlite3 \
  "SELECT class_name, confidence, media_time_ms, frame_index FROM detection_events WHERE media_time_ms >= 0 AND media_time_ms <= 30000 ORDER BY media_time_ms, frame_index;"
```

## Evidence

Capture-device Sources record recoverable video evidence for the run under `data/storage/<source>/<date>/<timestamp>.mp4`, even when the Source `write` flag is false. Stored events should have `evidence_uri` values pointing at that artifact with a standard `file://` URI.

File Sources do not create duplicate evidence artifacts. Stored events should keep the original file Source URI as `evidence_uri`, with `frame_index` and `media_time_ms` referring to the original file frame sequence.

## Overlays

Detection overlays are a local development aid. They are enabled by `task dev`
and can also be enabled directly with:

```bash
uv run cereal --preview --overlays --config config/settings.yaml
```

The Preview window draws detections on the sampled frame and keeps drawing the most recent sampled detections on later preview frames until the next sampled frame replaces or clears them.
