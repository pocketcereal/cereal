# Starting spec

For each of the items below we must define the programming patterns to use, implementation details, and structure to ensure long term maintainability and ease of extendability. Each of the top level sections should have clear acceptance criteria per element. This is not a concrete plan by any means. We are going to pick apart each item and write proper issues and track them.

## config loading

- it should read in a yaml config from `config/settings.yaml` with the following format into a pydandic object

```yaml
storage: /path/to/root/store

sources:
- name: <cannonical name>
  url: <rtsp stream url|path-on-disk>
  write: bool
```

## Foundation

- Architectural design of the sources interface at a deep level: able to register "source" so that we can extend later.
- it should load a sample file from disk as a source using sources array from the yaml and display in a pop up basic monitor. We need to research a modern and performant tool. Is it possible to send the output to VLC for example? Audio not required for now.

## Sources setup

- it should connect a live media source. To start with a system usb camera.
- it should connect a live media source: rtsp stream

## Writing sources

- it should write from the source in realtime and write to disk.
- it should write the media output of multiple sources at once.

- it should be able to preprocess the video by adjusting resolution
- it should be able to preprocess the video by adjusting the size

