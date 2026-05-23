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

**Preview window**:
A lightweight local desktop window used to display frames from one **Source** during development and manual verification.
_Avoid_: Browser view, VLC output, production monitor

**Write flag**:
The optional per-**Source** setting that decides whether Cereal records that **Source**.
_Avoid_: Output policy, recording profile

**Storage root**:
The required root directory where Cereal writes files it owns.
_Avoid_: Source path, config path, cache path

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
- The **Configuration file** defines exactly one **Storage root**, and Cereal derives owned child paths under it.

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
- Multiple-source preview scope was ambiguous — resolved: phase one previews only the first configured **Source**.
- Preview backend was ambiguous — resolved: phase one uses OpenCV as the simple file-reading and desktop-window backend, without committing to OpenCV as the long-term media stack.
- Source adapter lifecycle scope was ambiguous — resolved: phase one keeps the adapter interface test-first and tiny, deferring async streaming, capabilities, metadata, and health checks.
- Preview testing scope was ambiguous — resolved: unit test non-visual control flow and resource handling, but leave actual **Preview window** appearance and playback verification to manual testing.
- Future media branches were ambiguous during the first file-preview phase — resolved historically: USB cameras, RTSP, writing, multi-source runtime, and preprocessing were outside that phase.
