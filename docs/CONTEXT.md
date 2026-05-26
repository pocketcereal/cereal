# Cereal

Cereal is the Python project for the Cereal command-line tool. The repository directory may still be named `campipe`, but project language should use Cereal.

## Language

**Cereal**:
The main Python command-line tool provided by this workspace.
_Avoid_: Campipe, Campie, app, project

**Project**:
The single-package uv-managed Cereal codebase.
_Avoid_: Workspace, multi-package workspace, monorepo

**CLI command**:
The executable entry point users run from a shell.
_Avoid_: Script, binary

**Settings**:
The typed runtime configuration loaded for Cereal.
_Avoid_: Globals, singleton config

**Configuration file**:
The YAML file that is the primary source for Cereal's structured **Settings**.
_Avoid_: Env config, defaults file

**Config flag**:
The CLI option that selects which **Configuration file** to load.
_Avoid_: Settings argument, config env var

**Source**:
A configured media input in Cereal settings.
_Avoid_: Stream, feed, input source

**Source URI**:
The URI locator that tells Cereal how to resolve a **Source**.
_Avoid_: URL, source kind, path

**Source name**:
The strict stable identifier for a **Source**.
_Avoid_: Display name, title

**Source label**:
The optional human-facing label for a **Source**.
_Avoid_: ID, source name

**Source adapter**:
The runtime component that turns a configured **Source URI** into decoded media frames.
_Avoid_: Source, plugin, stream handler

**Source adapter registry**:
The runtime map that selects a **Source adapter** from a **Source URI** scheme.
_Avoid_: Source registry, plugin manager, factory

**Capture device**:
A local media device that Cereal can open as a **Source** through a `device:` **Source URI**.
_Avoid_: USB camera, webcam, camera source

**Device index**:
The numeric local capture-device identifier inside a `device:` **Source URI**.
_Avoid_: Camera name, device path, port

**Frame**:
A single video frame from a **Source** at runtime.
_Avoid_: OpenCV frame, PyAV frame, image

**Frame timestamp**:
The time assigned to a **Frame** for later query and evidence lookup.
_Avoid_: Detection time, clock time, video time

**Frame time**:
A value carrying the **Observed time** or **Media time** assigned to one **Frame**.
_Avoid_: Timestamp, time provider result, clock value

**Observed time**:
The wall-clock time when Cereal reads a **Frame** from a live **Source**.
_Avoid_: Media time, detection time, timestamp

**Media time**:
The offset into a file **Source** where a **Frame** appears.
_Avoid_: Observed time, clock time, timestamp

**Detection event**:
One model observation of one object candidate in one **Frame** from one **Source**.
_Avoid_: Object, tag, frame result

**Detection candidate**:
One raw detector output before it becomes a persisted **Detection event**.
_Avoid_: Detection event, object, prediction

**Bounding box**:
Pixel-space `x1`, `y1`, `x2`, `y2` coordinates in a decoded **Frame**.
_Avoid_: Normalized box, region, crop

**Object track**:
A sequence of **Detection events** believed to describe the same physical object across adjacent **Frames** from one **Source**.
_Avoid_: Object, detection group, tracklet

**Detection store**:
The canonical structured store for **Detection events** and **Object tracks**.
_Avoid_: Vector store, semantic cache, analytics database

**Detection event query**:
A structured request for **Detection events** filtered by source, class, **Observed time**, or **Media time**.
_Avoid_: SQL query, search prompt, vector query

**Detection stream defaults**:
The prototype-owned sample interval and confidence threshold values for the **Detection** stream loop.
_Avoid_: Detection config, stream settings, detector options

**Detection**:
The Cereal domain area that turns **Frames** into persisted **Detection events**.
_Avoid_: Media detection, vision utils, detector module

**Object detector**:
The replaceable boundary that accepts one **Frame** and returns **Detection candidates**.
_Avoid_: YOLO, model, classifier, vision service

**Store backend**:
A concrete persistence implementation behind a domain store.
_Avoid_: Storage engine, database client, builder

**Semantic index**:
An optional retrieval aid for fuzzy visual or text similarity over stored evidence.
_Avoid_: Detection store, source of truth, vector database

**Evidence window**:
A bounded group of nearby **Frames** around one or more **Detection events** or one **Object track**.
_Avoid_: Clip, segment, frame group

**Visual validation**:
A focused VLM judgment about one claim against one **Evidence window**.
_Avoid_: Detection, confirmation, VLM result

**Analysis agent**:
The agent that turns a user question into **Detection store** queries, **Evidence windows**, **Visual validations**, and a final answer.
_Avoid_: Main agent, deep agent, reporter

**Validation role**:
A reusable role contract for focused **Visual validation** work.
_Avoid_: Free-form subagent, worker, persona

**Frame writer**:
The runtime component that writes **Frames** into a **Recording artifact**.
_Avoid_: Sink, recorder, output handler

**Writer context**:
The injected runtime value that carries Cereal's recording defaults for creating a **Frame writer**.
_Avoid_: Recording config, writer settings, output profile

**Preview window**:
A lightweight local desktop window used to display frames from one **Source** during development and manual verification.
_Avoid_: Browser view, VLC output, production monitor

**Write flag**:
The optional per-**Source** setting that decides whether Cereal records that **Source**.
_Avoid_: Output policy, recording profile

**Storage root**:
The required root directory where Cereal writes files it owns.
_Avoid_: Source path, config path, cache path

**Recording artifact**:
A video file Cereal writes for one recorded **Source** run.
_Avoid_: Output file, capture file, export

**Evidence reference**:
A stored pointer from derived evidence back to a **Recording artifact**, **Frame timestamp**, and frame position.
_Avoid_: Screenshot, crop file, frame dump

**Evidence URI**:
A URI string that identifies the recoverable evidence artifact for an **Evidence reference**.
_Avoid_: File path, artifact path, storage key

## Relationships

- The **Project** contains the **Cereal** package.
- The **Cereal** package exposes the `cereal` **CLI command**.
- The package name, import name, **CLI command**, and initial command output are all `cereal`.
- The **CLI command** loads **Settings** from the **Configuration file** through a factory and passes them into runtime functions.
- The **Config flag** may select a **Configuration file** other than `config/settings.yaml`.
- Missing **Configuration file** is a startup error for the **CLI command**.
- The **Configuration file** defines one or more **Sources**.
- Each **Source** has one **Source URI**.
- Each **Source** has one **Source name** and may have one **Source label**.
- A **Source adapter** resolves a **Source URI** for one or more supported URI schemes.
- A **Source adapter** reads **Frames** from a **Source**; the concrete in-memory representation is an implementation detail for now.
- A file **Source** **Frame timestamp** is stored as **Media time** when available.
- A capture-device **Source** **Frame timestamp** is stored as **Observed time** when Cereal reads the **Frame**.
- **Frame time** carries the **Observed time** or **Media time** for one **Frame** and is provided to detection ingestion from outside the loop.
- A **Detection event** must have at least one of **Observed time** or **Media time**; both are allowed when both are known.
- A **Detection candidate** becomes a **Detection event** when Cereal adds **Source**, **Frame timestamp**, and **Evidence reference** data and persists it.
- A **Frame** may produce zero or more **Detection events**.
- A **Detection event** belongs to exactly one **Frame** from exactly one **Source**.
- A first-slice **Detection event** includes source name, **Observed time** or **Media time**, frame index, frame width, frame height, **Evidence URI**, model name, class ID, class name, confidence, a **Bounding box**, and an optional track ID.
- An **Object track** contains one or more **Detection events** from one **Source**.
- Count-style questions about physical objects should count **Object tracks**, not raw **Detection events**.
- The **Detection store** is the source of truth for **Detection events** and **Object tracks**.
- The first **Detection store** should be a domain port with a SQLite **Store backend**.
- The first implementation focus is the **Detection store** fed by real YOLO-backed **Detection events**.
- The first **Detection store** slice runs detection over the first configured **Source** before adding the future background processing runtime.
- **Detection** consumes **Frames** from media runtime boundaries but is not part of the media runtime itself.
- A **Semantic index** may reference evidence in the **Detection store**, but it does not own canonical detection history.
- An **Evidence window** references nearby **Frames** around **Detection events** or an **Object track** for later visual review.
- A **Visual validation** evaluates one claim against one **Evidence window** and does not replace the underlying **Detection events**.
- An **Analysis agent** may query the **Detection store**, select **Evidence windows**, request **Visual validations**, and compose an answer.
- A **Validation role** defines the focused instructions and output contract for one kind of **Visual validation**.
- A **Frame writer** writes **Frames** from one **Source** into one **Recording artifact**.
- A **Writer context** provides the default recording values needed to create a **Frame writer**.
- Cereal selects a **Source adapter** through the **Source adapter registry** from the **Source URI** scheme, not from a separate source type field.
- A **Capture device** uses the `device:` **Source URI** scheme.
- In the first **Capture device** phase, `device:` **Source URI** values identify a **Device index**, such as `device:0`.
- File and **Capture device** adapters may share the same OpenCV capture factory while keeping **Source URI** interpretation in separate **Source adapters**.
- `device:` **Source URI** interpretation lives with other pure **Source URI** helpers.
- Default **Source adapter registry** composition lives in a small dedicated media registry Module once more than one adapter is registered.
- The first **Capture device** phase is a lean prototype and should keep failures natural unless a small message makes manual verification clearer.
- A **Preview window** displays **Frames** from one **Source** for manual verification.
- In the first media phase, the **CLI command** starts the **Preview window** directly after loading **Settings**.
- In the first media phase, the **CLI command** previews only the first configured **Source**.
- In the first **Capture device** phase, Cereal proves `device:` support through the existing first-**Source** **Preview window** path.
- Each **Source** may set one **Write flag**; omitted means Cereal does not record that **Source**.
- In the first recording phase, Cereal records only the first configured **Source** while the existing **Preview window** path is running and only when that **Source** has `write: true`.
- The **Configuration file** defines exactly one **Storage root**, and Cereal derives owned child paths under it.
- In the first recording phase, a **Recording artifact** is one `.mp4` file under `Storage root / Source name / date / Unix timestamp`.
- Cereal creates owned directories for **Recording artifacts** under **Storage root** as needed.
- **Recording artifact** path derivation is pure and receives **Storage root**, **Source name**, and an injected timestamp.
- An **Evidence reference** points back to the **Recording artifact** and frame position needed to recover visual evidence.
- An **Evidence URI** identifies the recoverable evidence artifact without assuming it is always a local filesystem path.
- Local **Recording artifacts** and original file evidence use standard `file://` **Evidence URIs** until Cereal has an artifact catalog.
- A **Detection event** should retain enough **Evidence reference** data to recover its source **Frame** later.
- A capture-device **Detection event** should reference a **Recording artifact** created while detection runs.
- A file-source **Detection event** may reference the original file as its recoverable evidence artifact.
- Detecting a capture-device **Source** should record recoverable evidence in the same run that writes **Detection events**.
- In the first recording phase, recording format details use Cereal-owned prototype defaults and are not configurable.
- The first recording defaults write `.mp4` artifacts through ffmpeg with `libx264`, a silent AAC track, MP4 v2 branding, BT.709 color metadata, and no B-frames for local player compatibility.
- In the first recording phase, **Writer context** is runtime-only and not part of **Settings**.
- Recording Modules live under `cereal.media.recording` while recording is still part of the media runtime.
- **Preview window** startup composition decides whether the first **Source** gets a **Frame writer** from its **Write flag**.
- The first ffmpeg-backed **Frame writer** opens lazily when the first **Frame** is written.
- **Frame time** is a frozen data type validated to carry at least one of **Observed time** or **Media time**.
- **Observed time** is represented as a `datetime` in Python and stored as UTC ISO-8601 text in SQLite.
- **Media time** is represented as integer milliseconds in Python and stored as integer milliseconds in SQLite.
- Track IDs are normalized to strings; numeric detector tracker IDs are converted to `str` by the adapter.
- **Detection stream defaults** carry a sample interval of 3 seconds and a confidence threshold of 0.5 as prototype-owned values.
- **Detection stream defaults** are not exposed as user-facing **Settings** until detection behavior is proven.
- The detection stream loop samples based on **Frame time**, not wall-clock time.
- Confidence threshold filtering is owned by the stream loop, not the **Object detector** adapter.
- The **Object detector** protocol accepts one `np.ndarray` **Frame** and returns a sequence of **Detection candidates**.
- The **Object detector** exposes model identity through a side-effect-free `model_name` property.
- Domain conversion from **Detection candidate** to **Detection event** is a pure function receiving all external effects as explicit inputs.
- The **Detection store** write interface is batch-only: `insert_many` accepts a sequence of **Detection events**.
- The **Detection store** SQLite backend self-bootstraps its schema on initialization.
- The **Detection store** SQLite file lives at `Storage root / cereal.sqlite3`.
- Capture-device detection records evidence to a **Recording artifact** regardless of the **Write flag**.
- For capture devices, frame handling order is read, write evidence, preview if enabled, detect if sampled, then store detections.
- For file **Sources**, frame handling order is read, preview if enabled, detect if sampled, then store detections.
- The detection stream loop is built as an independently testable unit before being composed with **Preview window** and evidence recording.
- Detection stream sampling, threshold filtering, and event conversion are pure helper functions reused by both the standalone loop and the composed runtime.
- **Detection** types and contracts live in `cereal.detection`, a flat package sibling to `cereal.media`.

## Example dialogue

> **Dev:** "Should the root directory name show up in the command?"
> **Domain expert:** "No. Even if the directory is still `campipe`, the user-facing **CLI command** is `cereal`."

## Flagged ambiguities

- "campipe", "campie", and "cereal" were all used for the initial tool name — resolved: **Cereal** is the canonical project and package name; `campipe` is only the current filesystem directory name.
- The first scaffold output was described as `campie` before the rename — resolved: the command prints `cereal`.
- "sub-project" was used for Preprocess — resolved: no Preprocess module or package is part of the initial scaffold.
- "workspace" was considered as a multi-package uv workspace — resolved: keep a basic single-package uv project for now.
- "workspace" was used for the repo-level shape — resolved: use **Project** unless Cereal later adopts uv workspaces.
- Global settings were considered — resolved: define a **Settings** type and factory, but no module-level settings singleton.
- Settings sources were ambiguous between `.env`, defaults, and YAML — resolved: the **Configuration file** is the structured source for this phase.
- Config file selection was ambiguous — resolved: add a **Config flag** so CLI users can choose a YAML file instead of the default `config/settings.yaml`.
- Media architecture scope was ambiguous after configuration loading — resolved historically as `file:` **Source** preview in a **Preview window**; current media scope also includes **Capture device** preview through `device:`.
- "source", "stream", and "feed" were all possible names for configured media inputs — resolved: use **Source** for Cereal's settings term.
- Source locators were ambiguous between `url`, `uri`, and `kind` — resolved: use **Source URI** as the canonical locator and defer source-dispatch architecture to a later media phase.
- URI validation scope was ambiguous — resolved: require **Source URI** values to be URI-shaped with a scheme, but do not restrict supported schemes in this configuration-loading phase.
- Source identity and display text were ambiguous — resolved: **Source name** is the strict stable identifier, while **Source label** is optional human-facing text.
- Recording was ambiguous between a full output policy and a source-local toggle — resolved: use a per-**Source** **Write flag** until recording options need their own structure.
- The default recording behavior was ambiguous — resolved: omitted **Write flag** means `false`.
- Storage was ambiguous between several configurable directories — resolved: **Storage root** is the single configured directory, and Cereal owns child paths below it.
- Optional storage behavior was ambiguous — resolved: every **Configuration file** must define exactly one **Storage root**.
- Missing configuration behavior was ambiguous — resolved: a missing **Configuration file** is a **CLI command** startup error.
- Empty source configuration was ambiguous — resolved: the **Configuration file** must define at least one **Source**.
- "source interface" was ambiguous between configured input and runtime implementation — resolved: **Source** is the configured input, while **Source adapter** is the runtime component that reads media frames.
- Frame ownership was ambiguous between the video-domain concept and a concrete pixel representation — resolved: **Frame** means one video frame from a **Source**; its in-memory representation is an implementation detail for the current phase.
- Timestamp ownership was ambiguous between media time and wall-clock time — resolved: store file **Source** timing as **Media time** and capture-device timing as **Observed time** rather than overloading one timestamp field.
- "stream of object detection" was ambiguous between the video input and derived model observations — resolved: use **Source** for the media input and **Detection event** for one model observation in one **Frame**.
- "object" was ambiguous between a one-frame model observation and a physical thing over time — resolved: use **Detection event** for the observation and **Object track** for the inferred physical object over adjacent **Frames**.
- Tracking scope was ambiguous for the first detection slice — resolved: first persist **Detection events** with optional track IDs, then handle **Object track** creation and count semantics in a later pass.
- Vector storage was ambiguous as either the primary detection history or a retrieval aid — resolved: the **Detection store** owns canonical structured detection history, while a **Semantic index** is optional and non-canonical.
- "storage engine" was considered for persistence abstraction — resolved: use domain stores as ports and **Store backends** for concrete persistence implementations; defer factories/builders until more than one backend exists.
- "main agent", "deep agent", and "reporter" were ambiguous between product roles and library concepts — resolved: use **Analysis agent** for the Cereal domain role that plans and answers user questions.
- Agent creation scope is intentionally staged — resolved: first use predefined **Validation roles** for testable **Visual validations**, while leaving long-term room for the **Analysis agent** to create and manage its own specialist roles.
- First implementation focus was ambiguous between agents, vectors, tracking, and persistence — resolved: start with the **Detection store** fed by YOLO-backed **Detection events**, then break that domain into child tasks after the high-level pass.
- Detection module placement was ambiguous between media and a separate domain package — resolved: use **Detection** as a separate domain area because it consumes media **Frames** but owns persisted model observations.
- Background processing scope was ambiguous for the first detection slice — resolved: first run detection over the first configured **Source**, while the future architecture keeps continuous background detection over active **Sources** as the target.
- "basic monitor" was ambiguous between a durable product feature and a small local playback surface — resolved: use **Preview window** for the phase-one manual verification window.
- VLC and GStreamer integration were considered for media preview — resolved: phase one uses a simple Python preview path and explicitly does not integrate VLC or GStreamer.
- Source dispatch was ambiguous between URI schemes and a separate source type field — resolved: choose **Source adapters** by **Source URI** scheme for now, without adding polished unsupported-scheme behavior in the phase-one prototype.
- "USB camera" was used for the next device work — resolved: use **Capture device** for the domain term and `device:` as the **Source URI** scheme, because not every local media device is a USB camera.
- **Capture device** locator scope was ambiguous between numeric indexes, platform device paths, and human-readable names — resolved: first support numeric **Device index** locators such as `device:0`.
- The OpenCV capture factory boundary was ambiguous between one adapter per argument type and one shared backend factory — resolved: keep separate file and **Capture device** **Source adapters**, both using the same injected OpenCV capture factory.
- `device:` parsing location was ambiguous between settings, the adapter, and shared URI helpers — resolved: keep it in the pure **Source URI** helper Module.
- Error handling scope for **Capture device** work was ambiguous — resolved: keep the prototype lean with natural failures and only add logging where it clarifies an operational boundary.
- "clear registry" was ambiguous between a settings registry and runtime adapter dispatch — resolved: use **Source adapter registry** for the runtime map from **Source URI** scheme to **Source adapter**.
- Default registry composition location was ambiguous between the **Preview window** Module and a dedicated registry Module — resolved: once `file:` and `device:` are both registered, use a small dedicated media registry Module to keep files single-purpose.
- **Capture device** implementation scope was ambiguous between a broad media-registry refactor and a vertical slice — resolved: first prove `device:` by previewing the first configured **Source** with a **Capture device** URI.
- Planning location for `device:` support was ambiguous because the media architecture deepening PRD excludes new **Source adapter** schemes — resolved: track **Capture device** preview in its own small PRD.
- Preview command shape was ambiguous between a subcommand and default startup behavior — resolved: phase one starts preview directly from the existing **CLI command** and defers subcommands until the command surface needs them.
- Detection command shape is intentionally minimal for now; avoid a robust CLI or broad configuration surface until detection behavior is proven.
- `task dev` is the prototype entrypoint and should run the first-source detection path once that path exists.
- Detector model settings use prototype-owned runtime defaults in the first detection slice, with model selection deferred until the model boundary and future agent responsibilities are clearer.
- Multiple-source preview scope was ambiguous — resolved: phase one previews only the first configured **Source**.
- Preview backend was ambiguous — resolved: phase one uses OpenCV as the simple file-reading and desktop-window backend, without committing to OpenCV as the long-term media stack.
- Source adapter lifecycle scope was ambiguous — resolved: phase one keeps the adapter interface test-first and tiny, deferring async streaming, capabilities, metadata, and health checks.
- Preview testing scope was ambiguous — resolved: unit test non-visual control flow and resource handling, but leave actual **Preview window** appearance and playback verification to manual testing.
- Future media branches were ambiguous during the first file-preview phase — resolved historically: USB cameras, RTSP, writing, multi-source runtime, and preprocessing were outside that phase.
- First recording scope was ambiguous between headless recording, recording all configured **Sources**, and recording through the existing **Preview window** path — resolved: first record only the first configured **Source** during preview when its **Write flag** is true.
- First **Recording artifact** shape was ambiguous between configurable filenames, segmented files, and one artifact per run — resolved: first write one `.mp4` under `Storage root / Source name / date / Unix timestamp`.
- "device" was used as a possible recording path segment — resolved: use **Source name** so file, device, and future Source schemes share the same path model.
- Recording directory ownership was ambiguous — resolved: Cereal creates required child directories under **Storage root** and lets filesystem failures remain natural.
- Evidence persistence was ambiguous between saved frame images and recorded video lookup — resolved: prefer **Evidence references** back to **Recording artifacts** so later analysis can recover the relevant **Frames** from recorded video.
- Detection and recording coordination was ambiguous for capture devices — resolved: the first detection path should write **Detection events** and record recoverable evidence in the same run.
- Recording loop shape was ambiguous between bolting writes into preview and a broad recording service — resolved: introduce a tiny **Frame writer** boundary used by the existing **Preview window** loop.
- Recording format configuration was ambiguous — resolved: recording format details will become configurable later, but the first slice uses Cereal-owned prototype defaults.
- The first recording codec default was ambiguous after OpenCV-produced MP4 files proved player-fragile — resolved: keep MP4, but use a more flexible ffmpeg-backed writer instead of OpenCV `VideoWriter`.
- Recording default ownership was ambiguous between hard-coded writer values and user-facing config — resolved: first use an injected **Writer context** carrying Cereal-owned prototype defaults, with user-facing configuration deferred.
- **Writer context** placement was ambiguous between YAML **Settings** and runtime dependencies — resolved: keep it runtime-only for the first recording slice.
- Recording package placement was ambiguous between `cereal.media` and a new top-level package — resolved: use `cereal.media.recording` now and defer broader restructuring until Cereal has a second runtime mode beyond preview.
- Recording policy placement was ambiguous between the preview loop and startup composition — resolved: startup composition decides whether to attach a **Frame writer**, while the loop only writes frames when one is present.
- **Frame writer** opening time was ambiguous between startup and first frame — resolved: open lazily on the first written **Frame** so frame size can come from actual media.
- **Recording artifact** path derivation was ambiguous between writer-side filesystem behavior and a pure path rule — resolved: derive the path in a pure Module and create directories at the writer boundary.
- **Detection event** identity was ambiguous between domain ID and backend ID — resolved: no domain ID on the type in the first types issue; the SQLite **Store backend** assigns auto-increment integer IDs.
- **Frame time** representation was ambiguous between floats, datetimes, and a wrapper type — resolved: **Frame time** is a frozen dataclass with `observed: datetime | None` and `media_ms: int | None`, validated to carry at least one.
- **Observed time** storage format was ambiguous — resolved: store as UTC ISO-8601 text in SQLite, reconstruct as `datetime` in Python.
- **Media time** storage format was ambiguous between float seconds and integer milliseconds — resolved: integer milliseconds avoids float precision issues.
- Track ID type was ambiguous between integer and string — resolved: normalize numeric tracker IDs to `str`; store as `TEXT` in SQLite.
- **Detection event query** class filter scope was ambiguous — resolved: filter by class name only; class ID filtering is deferred because class IDs are detector-specific.
- **Detection store** database filename was ambiguous — resolved: `cereal.sqlite3` at `Storage root`.
- **Detection store** index strategy was ambiguous — resolved: include composite indexes for source+observed time, source+media time, source+class name, source+class name+observed time, source+class name+media time.
- Capture-device evidence recording and the **Write flag** were ambiguous — resolved: capture-device detection records evidence regardless of the **Write flag**; the **Write flag** controls user-requested recording only.
- Detection loop architecture was ambiguous between injecting into preview and a standalone loop — resolved: build the detection stream loop as an independently testable unit, then compose it with **Preview window** and evidence recording in a separate wiring issue.
- Detection overlay default was ambiguous — resolved: overlays are optional and off by default unless enabled by prototype composition.
- Detection overlay persistence between samples was ambiguous — resolved: persist last-sampled detections as overlay on every frame until the next sample replaces them.
- **Object detector** frame input type was ambiguous — resolved: accept `np.ndarray` directly without a wrapper type.
- YOLO adapter naming was ambiguous — resolved: use `UltralyticsObjectDetector` because it implements the **Object detector** protocol, not just YOLO.
- Ultralytics dependency packaging was ambiguous between hard and optional — resolved: hard dependency for the prototype phase.
- Detection activation was ambiguous between CLI flag and always-on — resolved: detection always runs when wired at composition; no CLI flag for the prototype.
