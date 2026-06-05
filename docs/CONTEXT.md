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

**Preview flag**:
The CLI option that controls whether the **Preview window** is opened while detection runs.
_Avoid_: Display mode, UI switch, headless flag

**Overlay flag**:
The CLI option that enables **Detection overlay** rendering in the **Preview window**.
_Avoid_: Draw flag, debug UI, box mode

**Detection log**:
An operational log line emitted at detection startup, source opening, sampling, or persistence boundaries.
_Avoid_: Debug print, trace spam, audit event

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
A query-local candidate group of **Detection events** believed to describe the same physical object across adjacent **Frames** from one **Source**.
_Avoid_: Object, detection group, tracklet

**Detection store**:
The canonical structured store for **Detection events**.
_Avoid_: Vector store, semantic cache, analytics database

**Detection event query**:
A structured request for **Detection events** filtered by source, class, **Observed time**, or **Media time**.
_Avoid_: SQL query, search prompt, vector query

**Analysis query**:
A provider-free orchestration request that selects **Detection events**, retrieves **Evidence windows**, and applies one explicit **Visual claim** through an injected **Visual validator**.
_Avoid_: User question, VLM prompt, detection query

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
A transient, in-memory group of nearby full **Frames** around one **Detection event** or one **Object track**.
_Avoid_: Clip, segment, frame group, evidence packet

**Evidence window reference**:
A serializable run-local handle plus summary metadata for one **Evidence window**, used between agent-facing tools during one invocation.
_Avoid_: Durable Evidence packet ID, stable evidence history, raw Evidence window

**Evidence packet**:
A future durable and shareable unit of visual evidence with metadata stable enough for agents, memory, and audit trails.
_Avoid_: Evidence window, raw frames, recording artifact

**Evidence target**:
The **Detection event** context carried with an **Evidence window**, including class name, confidence, **Bounding box**, and center frame index.
_Avoid_: Crop, object image, validation target

**Evidence artifact**:
A persisted derivative of recoverable evidence, such as extracted still frames or a short clip.
_Avoid_: Evidence reference, recording artifact, source video

**Visual validation**:
A focused VLM judgment about one claim against one **Evidence window**.
_Avoid_: Detection, confirmation, VLM result

**Visual inspection**:
A structured **Analysis** result that ties together the original **Detection event**, **Evidence window**, **Visual claim**, and **Visual validation**.
_Avoid_: Answer, validated event, evidence packet, generic analysis result

**Orchestrator agent**:
The main agent that turns user intent into an analysis strategy using Cereal's tools, roles, and evidence primitives.
_Avoid_: Main agent, deep agent, reporter, hardcoded analysis workflow, SupervisorAgent

**Orchestrator settings**:
The loaded runtime configuration for the **Orchestrator agent**, including the model used by the **Agent harness**.
_Avoid_: CLI-only model flag, module-level model constant, environment-only config

**Orchestrator model**:
The model identifier passed to the **Agent harness** for the **Orchestrator agent**.
_Avoid_: Detector model, YOLO model, provider key

**Agent harness**:
The runtime scaffold that gives agents planning, memory, filesystem or context, tools, and subagent delegation.
_Avoid_: Agent definition, individual agent, tool catalog

**Harness adapter**:
A boundary that converts Cereal-owned **Agent definitions** and tool contracts into the configuration shape required by one **Agent harness**.
_Avoid_: Domain model, direct framework dependency, runtime agent

**Agent definition**:
A packaged agent description that includes instructions, tools, skills, permissions, model choice, response schema, memory or context, and other configuration needed to instantiate an agent or subagent.
_Avoid_: Agent building block, Lego agent, agent bundle, prompt only

**Agent registry**:
A catalog of available **Agent definitions** that the **Orchestrator agent** can inspect or select from.
_Avoid_: Tool registry, plugin registry, import list

**Self-authored agent**:
An **Agent definition** the **Orchestrator agent** creates, registers, and persists at runtime for later reuse, rather than one shipped in the repo.
_Avoid_: Dynamic prompt, throwaway subagent, hardcoded specialist

**Authored tool**:
A tool whose implementation the **Orchestrator agent** generates at runtime, validated and persisted before it enters the **Agent tool catalog**.
_Avoid_: Hardcoded tool, repo-only callable, prompt-only capability

**Agent tool catalog**:
A resolver that maps tool names declared by an **Agent definition** to Python callables exposed at the **Agent harness** boundary.
_Avoid_: Hidden Orchestrator wiring, prompt-only capability, persistence owner

**Agent-facing data tool**:
A tool exposed at the **Agent harness** boundary that returns compact, serializable, JSON-like data for agent planning or validation.
_Avoid_: Raw domain object, frame array, byte payload, prose-only answer, Data agent

**Agent-facing capability**:
A focused tool, **Specialized subagent**, or staged **Orchestrator agent** tool exposure that the **Orchestrator agent** can choose while planning how to answer a task.
_Avoid_: Lego block, Agent building block, hardcoded workflow step

**Agent-facing capability contract**:
The shared descriptive shape for an **Agent-facing capability**: purpose, structured inputs, serializable outputs, uncertainty fields, evidence references when available, and the follow-up work it enables.
_Avoid_: Tool framework, broad plugin system, hardcoded workflow

**Capability facet**:
One named part of the **Agent-facing capability contract** that describes how a capability can be chosen and composed, such as purpose, inputs, outputs, uncertainty, evidence, follow-up capabilities, or boundaries.
_Avoid_: Implementation detail, arbitrary metadata, hidden prompt convention

**Agent runtime binding**:
A Cereal-owned runtime value that pairs an **Agent definition** with resolved tools and other injected dependencies before a specific **Agent harness** renders it.
_Avoid_: Deep Agents config, bound agent definition, agent instance, harness binding

**Agent run trace**:
A structured record of harness-visible agent actions during one agent invocation, such as delegated subagent calls, tool calls, tool arguments, and tool results.
_Avoid_: Debug log, transcript, chain-of-thought, telemetry

**Agent trace event**:
One structured action in an **Agent run trace**, such as `agent_invoked`, `subagent_delegated`, `tool_called`, or `tool_returned`.
_Avoid_: Log line, message, thought, span

**Subagent**:
An agent delegated to by the **Orchestrator agent** for focused work with its own context and tool scope.
_Avoid_: Worker, random helper, tool

**Specialized subagent**:
A **Subagent** with focused instructions, tool access, permissions, and output contract for a narrow kind of work.
_Avoid_: Specialist agent, expert agent, worker

**Detection lookup subagent**:
A generic **Specialized subagent** focused on retrieving or summarizing structured Detection store details for labels, Detection events, and future Object tracks.
_Avoid_: Vehicle-color validator, example-specific subagent, Agent building block

**Detection lookup result**:
A small serializable agent-facing result for Detection lookup tools, derived from Detection events without exposing raw domain objects directly to the agent harness.
_Avoid_: Raw DetectionEvent, prose-only tool output, Object track count

**Detection event reference**:
A serializable agent-facing reference to one **Detection event** using stable event context such as source name, frame index, time fields, class name, and **Evidence URI**.
_Avoid_: SQLite row ID, raw DetectionEvent, Object track ID

**Detection label summary**:
A serializable label plus Detection event count returned by label discovery tools for a source or time scope.
_Avoid_: Label ontology, semantic synonym, Object track count

**Analysis**:
The Cereal domain area that coordinates **Detection store** results, **Evidence window** retrieval, future **Visual validations**, and answer composition.
_Avoid_: Detection, evidence, VLM utilities

**Validation role**:
A reusable role contract for focused **Visual validation** work.
_Avoid_: Free-form **Subagent**, worker, persona

**Visual claim**:
One focused claim to validate against an **Evidence window**.
_Avoid_: Prompt, user question, detection label

**Visual claim generation**:
The planning step that turns a user question or analysis task into focused **Visual claims**.
_Avoid_: Visual validation, prompt template, detector label

**Visual validator**:
A replaceable port that evaluates one **Visual claim** against one **Evidence window**.
_Avoid_: VLM client, model, agent

**Visual-query planning smoke**:
A narrow **Agent harness** smoke that verifies the **Orchestrator agent** chooses the expected capability sequence for a structured visual-analysis task.
_Avoid_: Answer-quality benchmark, broad video QA, model evaluation, natural-language parser test

**Frame writer**:
The runtime component that writes **Frames** into a **Recording artifact**.
_Avoid_: Sink, recorder, output handler

**Writer context**:
The injected runtime value that carries Cereal's recording defaults for creating a **Frame writer**.
_Avoid_: Recording config, writer settings, output profile

**Preview window**:
A lightweight local desktop window used to display frames from one **Source** during development and manual verification.
_Avoid_: Browser view, VLC output, production monitor

**Detection overlay**:
Bounding box and class/confidence label rendering for sampled detections in the **Preview window**.
_Avoid_: Detection result, annotation file, UI layer

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
- The **Configuration file** defines **Orchestrator settings** once Cereal composes an **Orchestrator agent**.
- **Orchestrator settings** live under the `orchestrator:` key in the existing **Configuration file**.
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
- An **Object track** is an inspectable candidate for a physical object, not a final answer or a permanent identity claim.
- Count-style questions about physical objects should count **Object tracks**, not raw **Detection events**.
- The **Detection store** is the source of truth for **Detection events**; the first **Object track** foundation derives tracks from queried events before adding a persisted track schema.
- First-slice **Object track** identity is query-local and derived from grouped **Detection events**; it is not a durable SQLite row or cross-run object identity.
- First-slice explicit detector tracking groups **Detection events** by `source_name`, `class_name`, and detector `track_id`; cross-class identity reconciliation is deferred to a later explicit policy.
- First-slice **Object track** representative event is the highest-confidence **Detection event** in the track, with deterministic tie-breakers by earliest frame and time.
- **Object track** lookup should return candidate groups and uncertainty metadata for agent planning, not hide grouping judgment behind one final count.
- The first **Detection store** should be a domain port with a SQLite **Store backend**.
- The first implementation focus is the **Detection store** fed by real YOLO-backed **Detection events**.
- The first **Detection store** slice runs detection over the first configured **Source** before adding the future background processing runtime.
- **Detection** consumes **Frames** from media runtime boundaries but is not part of the media runtime itself.
- A **Semantic index** may reference evidence in the **Detection store**, but it does not own canonical detection history.
- An **Evidence window** references nearby full **Frames** around a **Detection event** or an **Object track** for later visual review.
- The first **Evidence window** retrieval slice is centered on one **Detection event**, uses a frame-radius window, and requires the center **Frame**.
- Neighbor **Frames** in an **Evidence window** are best-effort so start-of-file and end-of-file windows can still be useful.
- An **Evidence window** is not an **Evidence packet**; windows are temporary retrieval results, while packets are future durable evidence units.
- An **Evidence window reference** is run-local and not stable across invocations; durable external evidence identity belongs to future **Evidence packets**.
- Agent-facing tools may pass **Evidence window references** during one run, but should not store them as canonical evidence history.
- The first **Evidence window reference** includes only summary metadata needed for planning and trace readability: evidence-window handle, source name, center frame index, frame count, target class name, target confidence, target **Bounding box**, and **Evidence URI**.
- An **Evidence window reference** must not include raw **Frames**, pixels, per-frame image data, or a durable evidence ID.
- An **Evidence packet** may be created from one or more **Detection events** plus recovered **Frames**, but it does not become the source of truth for those detections or frames.
- An **Evidence packet** preserves its original evidence basis; later **Visual validations** may agree or disagree with that basis without mutating the underlying **Detection events**.
- An **Evidence target** preserves the **Detection event** context inside an **Evidence window** without cropping the recovered **Frames**.
- An **Evidence artifact** is a future persisted derivative; first-slice retrieval returns in-memory **Frames** only.
- A **Visual validation** evaluates one claim against one **Evidence window** and does not replace the underlying **Detection events**.
- A **Visual inspection** is an intermediate **Analysis** product, not a user-facing answer or a promoted **Validated event**.
- A **Visual inspection** preserves the original **Detection event**, the selected **Evidence window**, the **Visual claim**, and the resulting **Visual validation** together.
- First-slice **Visual inspections** carry the full in-memory **Evidence window** and do not define a durable ID, database row, or serialization contract.
- A **Visual claim** is narrower than a user question; it should be focused enough for one **Visual validator** call.
- **Visual claim generation** belongs to future **Orchestrator agent** or task-planning behavior, not to **Validation**.
- A deterministic `cereal.analysis.claims` helper may exist later only as a provider-free first slice for end-to-end testing.
- A **Visual validator** is a port so provider-specific VLM behavior stays outside the **Analysis**, **Detection**, and **Evidence** domains.
- First-slice **Visual validation** validates exactly one **Visual claim** against exactly one **Evidence window**.
- Broader questions are answered by **Analysis** composition over many focused **Visual validations**, not by broadening the **Visual validator** contract.
- A **Visual-query planning smoke** measures planner shape and boundary correctness, not final answer quality or model quality.
- The first **Visual-query planning smoke** should verify the **Orchestrator agent** selects Detection lookup, Evidence retrieval, and fake **Visual validation** in sequence for a structured prompt.
- The first **Visual-query planning smoke** should assert exact capability order, not merely capability presence.
- The first **Visual-query planning smoke** final output is a completion sanity check, such as `supported: car`; **Agent run trace** assertions remain authoritative.
- In the first **Visual-query planning smoke**, Detection lookup remains `detection-lookup` **Specialized subagent** delegation; Evidence retrieval and fake **Visual validation** are direct **Orchestrator agent** tool calls as staged exposure.
- The first **Visual-query planning smoke** should use a focused `find_detection_events` lookup for `car` in `smoke_fixture`; it should not retest detector-label discovery.
- The first **Visual-query planning smoke** validates one selected candidate Detection event only; multiple-candidate ranking and partial validation behavior wait for later slices.
- The first **Visual-query planning smoke** should exercise real `cereal.evidence` retrieval against deterministic local recoverable frame evidence while keeping **Visual validation** fake.
- The deterministic Evidence fixture for the first **Visual-query planning smoke** should be a tiny local video, not extracted still frames, so Evidence retrieval exercises frame-window behavior.
- The tiny local video fixture for the first **Visual-query planning smoke** should be generated at test/smoke runtime in a temp directory, not committed as a binary test asset.
- The generated video fixture should contain only three to five simple deterministic frames with distinct colors or labels for retrieval debugging; it does not need visual object semantics.
- An **Orchestrator agent** may query the **Detection store**, select **Evidence windows**, request **Visual validations**, create or choose **Agent definitions**, delegate to **Specialized subagents**, and compose an answer.
- The **Orchestrator agent** should choose an analysis strategy from available tools and **Agent definitions** rather than following a hardcoded workflow for each user question.
- **Agent definitions** may be static or future runtime-created definitions, but they need explicit capabilities, context, and permission boundaries.
- The first **Agent definition** implementation loads local `.agent` directories from `agent.toml` plus `instructions.md`.
- The first **Agent registry** is static and in-memory; it supports lookup by stable Agent definition name.
- Repo-local **Agent definitions** live under `agents/`.
- Cereal's canonical **Agent definition** file shape remains `agent.toml` plus `instructions.md`; Deep Agents `AGENTS.md` conventions are harness details until Cereal explicitly adopts or exports them.
- The first concrete **Specialized subagent** definition should be a generic **Detection lookup subagent**, not a subagent based on an illustrative user-question example.
- A **Detection lookup subagent** may translate user object language into detector label candidates and query constraints, but it does not visually confirm attributes that are absent from Detection store data.
- The first **Detection lookup subagent** Agent definition is named `detection-lookup`; YOLO awareness belongs in instructions, not in the canonical agent name.
- **Specialized subagents** should be testable through their own composition boundaries instead of only through the **Orchestrator agent**.
- **Specialized subagents** should be self-contained at the **Agent definition** level: instructions, declared tools, permissions, and expected usage live with the agent definition.
- Tool implementations may live in shared Python modules, but they are attached to an agent by resolving tool names declared by that agent's **Agent definition**.
- **Agent-facing data tools** return serializable data rather than raw **Frames**, **Evidence windows**, provider objects, bytes, or prose-only answers.
- **Agent-facing capabilities** should be narrow enough for the **Orchestrator agent** to choose and compose; they should not bake one fixed question-answering workflow into Python.
- First-slice **Agent-facing capability contracts** should stay lightweight and descriptive: name, purpose, structured input, serializable output, uncertainty signals, evidence references when available, and suggested follow-up capability types.
- An **Agent-facing capability contract** helps the **Orchestrator agent** compare and compose capabilities; it should not become a broad plugin framework before repeated capabilities reveal stable needs.
- Keep the **Agent-facing capability contract** documented for one more slice; promote it to typed repo data only after multiple implemented capabilities prove the metadata shape.
- **Capability facets** are documented in `docs/agents/capability-contract.md`; code and tests should use those facets as a shared vocabulary before Cereal promotes them into typed repo data.
- The central **Agent-facing capability contract** remains canonical, while each `.agent` definition should include a short **Capability facet** summary for capabilities it owns.
- `follow_up_capabilities` are capability hints, not workflow instructions; the **Orchestrator agent** still chooses the next planning step.
- Do not introduce **Data agent** or **Data subagent** as a first-class Cereal term until repeated data-returning **Specialized subagents** reveal a stable category.
- The first agent-facing Evidence data tool should be one focused `retrieve_evidence_window` capability; event selection remains **Orchestrator agent** planning behavior, not a separate tool.
- `retrieve_evidence_window` should accept a serialized **Detection event reference** derived from Detection lookup output; Cereal should not expose SQLite row IDs as the first agent-facing event identity.
- The first `retrieve_evidence_window` input field should be `detection_event_ref`; its run-local output handle field should be `evidence_window_ref`.
- The first fake agent-facing **Visual validation** data tool validates only a structured **Visual claim** plus serialized evidence-window reference; it does not inspect pixels or simulate VLM quality.
- The first fake agent-facing **Visual validation** data tool should return fixed `supported`; negative or uncertain validation outcomes wait for later validation-policy work.
- The first fake **Visual validation** data tool should be named `validate_visual_claim` and use `claim`, `status`, `class_name`, and `evidence_window_ref` fields.
- Agent-facing Evidence and fake **Visual validation** tools should compose lower-level `cereal.evidence` and `cereal.validation` ports directly for the planning smoke, not hide the sequence behind one broad `cereal.analysis` call.
- An **Agent runtime binding** is the Cereal-owned place where declared tool names become actual tool objects for one runtime composition.
- **Agent runtime bindings** should be created before rendering into a specific **Agent harness** so Cereal's modular agent shape is not defined by Deep Agents dictionaries.
- An **Agent run trace** observes harness-visible actions and artifacts, not hidden model reasoning or chain-of-thought.
- First-slice **Agent run trace** verification belongs to tests and smoke paths; a broader observability backend can wait until the runtime surface is less fluid.
- Agent runtime observability asks what happened during one run; evaluation asks whether the run was good enough for the task.
- **Agent run trace** types live under `cereal.agents.trace` because they describe agent execution observability, not Detection, Evidence, Analysis, or Validation domain state.
- The first **Agent run trace** event set is `agent_invoked`, `subagent_delegated`, `tool_called`, and `tool_returned`.
- First-slice **Agent trace events** may include agent names, subagent names, tool names, structured tool arguments, and JSON-like tool results.
- First-slice **Agent trace events** should not store raw full prompts or full model messages by default.
- Detection lookup tools should return **Detection lookup results**, not raw **Detection events**, so harness-facing output stays stable and serializable.
- Agent-facing tools should pass **Detection event references** between capabilities instead of raw **Detection events** or private database row IDs.
- Detection lookup tools receive dependencies such as a **Detection store** at construction time; they should not open databases or read **Settings** internally.
- The first Detection lookup tools are `find_detection_events` and `list_detection_labels`, declared by `agents/detection-lookup.agent`.
- First-slice **Object track** lookup should attach to the existing `detection-lookup` **Specialized subagent** because it is still structured Detection store interpretation.
- Split a future `object-track-lookup` **Specialized subagent** only if track lookup grows distinct policy ownership, uncertainty reporting, or validation handoff behavior that no longer fits Detection lookup.
- `list_detection_labels` lets the **Detection lookup subagent** discover actual detector labels in a source/time scope; label similarity reasoning remains the agent's responsibility.
- `list_detection_labels` returns **Detection label summaries** so the agent can see both available labels and their Detection event counts.
- Label counting for Detection lookup belongs behind the **Detection store** port, not inside the agent tool.
- Detection lookup tools accept structured observed-time filters as ISO-8601 strings and do not parse natural-language time phrases.
- The `detection-lookup` composition should receive an injected tool catalog or equivalent dependency; the existing Orchestrator smoke should not require a populated Detection store yet.
- Direct `detection-lookup` LLM tool use is proven with `qwen3:8b`, a seeded Detection store, and `task detection-lookup-smoke`.
- Orchestrator-to-`detection-lookup` delegation is proven through a seeded smoke path and `task orchestrator-delegation-smoke`; deterministic assertions use a fake harness with an **Agent run trace**.
- Long-term agent-facing capabilities should be registered with the **Specialized subagents** that own their focused work, not permanently accumulated as broad **Orchestrator agent** tools.
- A small planning slice may expose a new capability directly to the **Orchestrator agent** before its owning **Specialized subagent** exists, but that is staged exposure rather than final ownership.
- Direct **Orchestrator agent** access to Evidence retrieval and fake **Visual validation** tools in the first **Visual-query planning smoke** is staged exposure, not a decision that those capabilities permanently belong to the **Orchestrator agent**.
- The **Orchestrator agent** may depend on a **Specialized subagent** only after that subagent's definition, harness mapping, and tool boundary can be tested in isolation.
- The completed **Agent harness** proof after Orchestrator-to-`detection-lookup` delegation is the first **Visual-query planning smoke**, where Evidence retrieval and fake **Visual validation** are staged direct **Orchestrator agent** tools.
- **Orchestrator delegation** means the **Orchestrator agent** invokes a harness-visible **Specialized subagent** or capability. Direct Python routing inside an Orchestrator smoke function does not count as delegation.
- The **Agent harness** path binds and tests `detection-lookup` tools before broad visual-query planning.
- The first **Agent harness** composition API should be pure functions: a generic Deep Agents composition helper plus a named **Orchestrator agent** wrapper, not a broad runtime class.
- The first **Orchestrator agent** wrapper registers all available `specialized-subagent` definitions from the provided **Agent registry**.
- Cereal's long-term agent architecture should provide harness and tool mapping so the **Orchestrator agent** can choose, create, and execute work, including future code-writing capabilities, without hardcoded question-solving strategies.
- The product target is a continuous monitor: detection runs in the background over active **Sources** so **Detection events** accumulate in the **Detection store** before any question is asked. Single-**Source** single-run execution is prototype scaffolding, not the product shape.
- The north-star **Orchestrator agent** can both select existing **Agent definitions** and create **Self-authored agents** and **Authored tools**, registering and persisting them as canonical `.agent` directories for reuse across runs.
- The target **Agent registry** is durable and writable, not only the first static in-memory catalog; the **Orchestrator agent** extends it with **Self-authored agents**.
- **Authored tools** require a trust boundary, validation before reuse, and dynamic loading into the **Agent tool catalog**; this is deferred until hand-built capabilities prove the capability template.
- Emergent correlations (such as a person consistently appearing with a detected truck) are an emergent result of the **Orchestrator agent** composing structured **Detection event** and **Object track** queries, not a dedicated correlation or mining subsystem.
- Query understanding and structured answer composition are **Orchestrator agent** responsibilities, not standalone parser or reporting modules; the first user-facing ask-surface is a one-shot CLI query against the **Detection store**.
- A **Harness adapter** maps Cereal-owned **Agent definitions** to a concrete **Agent harness** without making Detection, Evidence, Analysis, or Validation import that harness.
- The first **Harness adapter** slice maps inert **Agent definition** configuration only and defers runtime tool binding.
- Deferred **Agent definition** fields should be exposed structurally by a **Harness adapter** result rather than silently dropped or treated as runtime behavior.
- The first Deep Agents **Harness adapter** should return a Cereal-owned typed result before rendering any plain framework dictionary.
- The first Deep Agents **Harness adapter** lives in `cereal.agents.deepagents_adapter` and stays pure.
- Cereal should not add the Deep Agents package dependency until runtime harness composition actually imports it.
- A subagent **Harness adapter** should raise `ValueError` if given an `orchestrator` **Agent definition**.
- Deep Agents is the first **Agent harness** target for local integration because it already bundles planning, subagents, skills, and context/filesystem concepts.
- The first **Agent harness** runtime composition should support local Ollama smoke invocations, while automated tests use injected fakes.
- `qwen3:8b` is the current local Ollama smoke model because it fits the local 12GB GPU budget and successfully called the Detection lookup tool in smoke.
- The **Orchestrator model** is loaded from **Orchestrator settings** rather than hardcoded in the harness runtime or passed as a broad CLI argument.
- The first **Orchestrator settings** shape requires `orchestrator.model`, for example `ollama:qwen3:8b`.
- First-slice **Orchestrator settings** include only the **Orchestrator model**; other model/runtime knobs wait until behavior requires them.
- `orchestrator.model` is required in the **Configuration file** once **Orchestrator settings** exist; Cereal should not hide a default model in code.
- `uv run cereal --agent orchestrator` is the first narrow local smoke path for the **Orchestrator agent**; arbitrary agent names and prompts are out of scope for that slice.
- `uv run cereal --agent detection-lookup` is the first narrow local smoke path for direct **Detection lookup subagent** tool use.
- `task visual-query-planning-smoke` is the explicit smoke path after `task agent-smoke`, `task detection-lookup-smoke`, and `task orchestrator-delegation-smoke`.
- Smoke tasks should remain boundary-specific so a failure identifies whether harness liveness, isolated tool use, delegation, or visual-query planning broke.
- Automated **Visual-query planning smoke** assertions should use an injected fake harness/runtime; real Deep Agents/Ollama smoke remains a manual runtime-wiring confidence check.
- The first **Orchestrator agent** smoke prompt is developer verification code, not **Agent definition** content or **Orchestrator settings**.
- Deep Agents/LangGraph may execute tool calls in worker threads, so injected store implementations must be safe at that boundary.
- LangGraph may be used as the lower-level graph/orchestration layer under or beside Deep Agents, but it is not itself a Cereal domain concept.
- LangSmith Deployment is managed hosting and observability infrastructure; local Deep Agents or LangGraph library usage should not require it.
- **Analysis** composition may coordinate **Detection store** queries and **Evidence window** retrieval without moving store access into **Evidence**.
- **Analysis** owns orchestration over domain ports, not canonical domain state.
- **Analysis** should not own detection persistence, evidence frame reading rules, provider-specific VLM clients, prompt internals, long-lived memory, or watch/task lifecycle.
- If **Analysis** starts accumulating policies for claim generation, enough-evidence decisions, user-answer composition, or task lifecycle, split those into explicit agent or task modules instead of growing `cereal.analysis`.
- The first provider-free **Analysis query** accepts a **Detection event query** plus one explicit **Visual claim**, retrieves **Evidence windows**, validates each through an injected **Visual validator**, and returns **Visual inspections**.
- The first **Analysis query** slice does not add provider clients, prompt templates, user question parsing, or broad CLI surface.
- First-slice **Analysis query** behavior is fail-fast: missing center-frame evidence or **Visual validator** errors fail the whole query; an empty **Detection event query** result returns an empty tuple.
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
- First-slice **Evidence window** retrieval supports local `file://` **Evidence URIs** only.
- A **Detection event** should retain enough **Evidence reference** data to recover its source **Frame** later.
- A capture-device **Detection event** should reference a **Recording artifact** created while detection runs.
- A file-source **Detection event** may reference the original file as its recoverable evidence artifact.
- Detecting a capture-device **Source** requires `write: true` so Cereal can record recoverable evidence in the same run that writes **Detection events**.
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
- Capture-device detection rejects Sources without `write: true`; it never silently records evidence against the **Write flag** contract.
- For capture devices, frame handling order is read, write evidence, preview if enabled, detect if sampled, then store detections.
- For file **Sources**, frame handling order is read, preview if enabled, detect if sampled, then store detections.
- The detection stream loop is built as an independently testable unit before being composed with **Preview window** and evidence recording.
- Detection stream sampling, threshold filtering, and event conversion are pure helper functions reused by both the standalone loop and the composed runtime.
- **Detection** types and contracts live in `cereal.detection`, a flat package sibling to `cereal.media`.
- **Evidence** types and retrieval rules live in `cereal.evidence`, a flat package sibling to `cereal.detection` and `cereal.media`.
- **Agent definition** loading and static **Agent registry** behavior live in `cereal.agents`.
- **Evidence** does not query the **Detection store**; callers pass a selected **Detection event** into retrieval.
- OpenCV-backed evidence reading lives behind the Evidence video adapter, not in the pure retrieval rules.
- **Analysis** selection retrieves **Evidence windows** for caller-provided **Detection event queries** by composing a **Detection store** and an Evidence frame reader.
- First-slice **Analysis** selection fails the whole request when any selected **Detection event** cannot recover its center **Frame**.
- **Analysis** visual validation composition applies one **Visual claim** to selected **Evidence windows** through an injected **Visual validator**.
- Detection runs by default through the `cereal` **CLI command**.
- The **Preview flag** can disable the **Preview window** for automated or headless runs.
- The **Overlay flag** enables **Detection overlay** rendering; overlays remain off by default.
- **Detection logs** use standard Python logging with module-level `logger = logging.getLogger(__name__)`.

## Current implementation map

The current Cereal foundation is a library-first pipeline:

```text
Source
  -> Detection stream
  -> Detection store
  -> Detection event query
  -> Evidence window
  -> Visual validation
  -> Visual inspection

Agent definition
  -> Agent registry
  -> Harness adapter
  -> Agent harness
```

- `cereal.detection` owns **Detection event** creation, storage, YOLO adapter boundaries, detection querying, query-local **Object track** building, and preview overlays.
- `cereal.evidence` owns **Detection event** to **Evidence window** retrieval and local `file://` frame reading.
- `cereal.analysis` owns composition across **Detection store**, **Evidence window** retrieval, and **Visual validator** calls.
- `cereal.validation` owns provider-free **Visual claim**, **Visual validation**, and **Visual validator** contracts.
- `cereal.agents` owns provider-free **Agent definition** loading and static **Agent registry** lookup.
- `cereal.agents` owns a pure **Harness adapter** that maps **Agent definitions** to Deep Agents subagent configuration without instantiating a live model.
- `cereal.media` still owns **Source adapter**, **Preview window**, and **Recording artifact** mechanics.
- `uv run cereal` runs the first-source detection path; `task dev` runs it with **Detection overlays** enabled.
- `cereal detections` / `task detections` inspect stored **Detection events**; `cereal tracks` / `task tracks` report query-local **Object track** counts.
- First-slice **Object tracks** are derived at query time from stored **Detection events**; there is no concrete VLM provider adapter, no prompt template, no user-facing question parser, no persisted **Object track** schema, and no persisted **Visual validation** result yet.

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
- Tracking scope was ambiguous for the first detection slice — resolved: first persist **Detection events** with optional track IDs; the current **Object tracks foundation** pass derives **Object tracks** and count semantics from stored events before adding persisted track identity.
- **Object track** persistence scope was ambiguous — resolved: first derive **Object tracks** at query time from stored **Detection events**; do not add an `object_tracks` SQLite table or durable track IDs until grouping policy stabilizes.
- Explicit detector `track_id` scope was ambiguous — resolved: treat `track_id` as a strong grouping signal only within the same **Source** and detector class for the first **Object track** slice; do not merge across flickering detector classes yet.
- **Object track** representative evidence was ambiguous — resolved: choose the highest-confidence **Detection event** first, with earliest frame and time as deterministic tie-breakers, so Evidence retrieval starts from the clearest detector-backed candidate.
- **Object track** purpose was drifting toward implementation mechanics — resolved: treat track lookup as one **Agent-facing capability** that returns inspectable object candidates and uncertainty signals for the **Orchestrator agent** to compose with Evidence retrieval and **Visual validation**.
- **Agent-facing capability** shape was ambiguous — resolved: define a lightweight **Agent-facing capability contract** before adding more agent-facing tools, so Detection lookup, Object track lookup, Evidence retrieval, and **Visual validation** expose comparable planning surfaces without becoming one hardcoded workflow.
- **Agent-facing capability contract** implementation timing was ambiguous — resolved: document the contract first and use it to guide the next Object track capability; add typed contract values only after repeated capabilities prove the shape.
- **Object track** agent topology was ambiguous — resolved: attach first-slice track lookup to the existing `detection-lookup` **Specialized subagent** and split only when track-specific policy or handoff behavior becomes distinct enough to justify its own subagent.
- Capability communication was ambiguous — resolved: use `docs/agents/capability-contract.md` as the vocabulary document for **Capability facets** such as purpose, inputs, outputs, uncertainty, evidence, follow-up capabilities, and boundaries.
- Follow-up guidance was ambiguous — resolved: capabilities may return `follow_up_capabilities` hints, but those hints are affordances for the **Orchestrator agent**, not a hardcoded workflow.
- Capability documentation placement was ambiguous — resolved: keep the central contract in `docs/agents/capability-contract.md` and add short owned-capability facet summaries to each `.agent` definition.
- Vector storage was ambiguous as either the primary detection history or a retrieval aid — resolved: the **Detection store** owns canonical structured detection history, while a **Semantic index** is optional and non-canonical.
- "storage engine" was considered for persistence abstraction — resolved: use domain stores as ports and **Store backends** for concrete persistence implementations; defer factories/builders until more than one backend exists.
- "main agent", "deep agent", "supervisor agent", "orchestrator", and "reporter" were ambiguous between product roles and library concepts — resolved: use **Orchestrator agent** for the Cereal domain role that plans an analysis strategy and answers user questions.
- Agent creation scope is intentionally staged — resolved: first use predefined **Validation roles** for testable **Visual validations**, while leaving long-term room for the **Orchestrator agent** to create and manage its own **Specialized subagents**.
- "The main deep agent will be in charge of building its own agents" was ambiguous between dynamic strategy composition and literal runtime authoring — resolved: the north-star goal is both; the **Orchestrator agent** chooses existing agents and authors new reusable **Self-authored agents** and **Authored tools** persisted to disk. The earlier "static in-memory registry" and "dynamic generation out of scope" framings are first-slice scope, superseded as the project goal by this north star.
- Self-extending agent build order was ambiguous — resolved: build hand-made capabilities bottom-up (object tracks, real **Visual validator**, query composition, answer composition) before agent self-authoring, so the proven capability set becomes the template the **Orchestrator agent** authors against.
- "Running in the background on the video in real time" was ambiguous against the single-**Source** prototype — resolved: the product is a continuous background monitor; the single-run path is scaffolding.
- "Lego agent", "Agent building block", and "Agent bundle" were useful conversationally but overloaded — resolved: use **Agent definition** for the packaged `.agent`-style unit and align delegation language with Deep Agents **Subagents**.
- "Specialist agent" and "expert agent" were ambiguous against Deep Agents terminology — resolved: use **Specialized subagent** for focused delegated agents.
- "Vehicle color validator" was used only as an illustrative example — resolved: do not add example-specific subagents yet; use a generic **Detection lookup subagent** first.
- Agent registry scope was ambiguous between a runtime Deep Agents integration and a provider-free catalog — resolved: first add a static in-memory **Agent registry** over loaded local **Agent definitions**.
- LangGraph cost and ownership were ambiguous — resolved: LangGraph is the open-source graph/orchestration library, while LangSmith Deployment is the managed paid hosting/observability path formerly called LangGraph Platform.
- Agent harness coupling was ambiguous — resolved: add a **Harness adapter** boundary before runtime orchestration so Cereal's core domains stay framework-independent.
- Deep Agents ADR scope was ambiguous — resolved: defer an ADR until Cereal adds the runtime harness dependency or other harder-to-reverse composition.
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
- `task dev` is the prototype entrypoint and runs the first-source detection path with preview enabled by default.
- Headless detection verification was ambiguous after detection landed — resolved: add a **Preview flag** so `--no-preview` runs the same first-source detection path without opening the **Preview window**.
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
- Capture-device evidence recording and the **Write flag** were ambiguous — resolved: capture-device detection requires `write: true` because persisted **Detection events** must point at recoverable evidence, and omitted **Write flag** still means no recording.
- Detection loop architecture was ambiguous between injecting into preview and a standalone loop — resolved: build the detection stream loop as an independently testable unit, then compose it with **Preview window** and evidence recording in a separate wiring issue.
- Detection overlay default was ambiguous — resolved: overlays are optional and off by default unless enabled by the **Overlay flag** or injected prototype composition.
- Detection overlay persistence between samples was ambiguous — resolved: persist last-sampled detections as overlay on every frame until the next sample replaces them.
- **Object detector** frame input type was ambiguous — resolved: accept `np.ndarray` directly without a wrapper type.
- YOLO adapter naming was ambiguous — resolved: use `UltralyticsObjectDetector` because it implements the **Object detector** protocol, not just YOLO.
- Ultralytics dependency packaging was ambiguous between hard and optional — resolved: hard dependency for the prototype phase.
- Detection activation was ambiguous between CLI flag and always-on — resolved: detection runs by default in the prototype; CLI flags only control preview display and overlay drawing.
- Evidence retrieval scope was ambiguous between in-memory frames and persisted derivatives — resolved: first retrieve in-memory **Evidence windows** and defer **Evidence artifacts**.
- Evidence window terminology was ambiguous against **Evidence packet** — resolved: **Evidence windows** are transient retrieval shapes; **Evidence packets** are future durable, shareable evidence units.
- Evidence packet authority was ambiguous — resolved: **Evidence packets** bundle evidence and provenance, while the **Detection store** remains canonical for **Detection events** and the source file or **Recording artifact** remains canonical for frames.
- Evidence retrieval input was ambiguous between arbitrary time/source lookups and selected detections — resolved: first center retrieval on a caller-provided **Detection event**.
- Evidence window sizing was ambiguous between seconds and frame counts — resolved: first use a frame radius with a default of 2.
- Evidence frame shape was ambiguous between crops and full frames — resolved: first return full frames and carry the **Bounding box** as **Evidence target** metadata.
- Evidence reader scope was ambiguous between all URI schemes and local evidence — resolved: first support local `file://` **Evidence URIs** only.
- Evidence window failure behavior was ambiguous — resolved: the center **Frame** is required and neighbor **Frames** are best-effort.
- Analysis composition placement was ambiguous after Evidence retrieval landed — resolved: introduce `cereal.analysis` as the coordinator between **Detection** and **Evidence** rather than letting either domain import the other direction.
- Analysis ownership was ambiguous — resolved: **Analysis** owns orchestration over ports and returned values, not canonical state or provider internals.
- Next implementation slice was ambiguous between a VLM adapter and provider-free orchestration — resolved: add an **Analysis query** slice first, using fake/injected **Visual validators** before adding model-provider complexity.
- Analysis evidence selection failure behavior was ambiguous between partial results and hard failure — resolved: first fail the request when any selected **Detection event** cannot recover its center **Frame**.
- Analysis validator failure behavior was ambiguous between partial results and fail-fast — resolved: first fail the whole **Analysis query** if the injected **Visual validator** fails on any selected **Evidence window**.
- Visual validation placement was ambiguous between provider code and analysis code — resolved: add `cereal.validation` for provider-free **Visual claim**, **Visual validation**, and **Visual validator** contracts, with `cereal.analysis` only coordinating calls.
- Visual validation scope was ambiguous between broad user questions and focused checks — resolved: first validate one **Visual claim** against one **Evidence window**, while **Analysis** composes broad answers later.
- Visual inspection naming was ambiguous — resolved: use **Visual inspection** for the structured intermediate **Analysis** result tying together **Detection event**, **Evidence window**, **Visual claim**, and **Visual validation**.
- Visual inspection persistence shape was ambiguous — resolved: first keep **Visual inspections** transient and include the full in-memory **Evidence window**; define durable references only when persistence is introduced.
- Visual claim generation placement was ambiguous — resolved: **Validation** evaluates supplied claims only; claim generation belongs to future **Orchestrator agent** or task-planning behavior, with a deterministic Analysis helper allowed only as a first-slice bridge.
- Cereal wiki maintenance automation is deferred — add a Codex/Claude hook later
  that reminds or enforces updating `docs/CONTEXT.md` after grilling sessions
  that settle durable domain vocabulary or architecture decisions.
