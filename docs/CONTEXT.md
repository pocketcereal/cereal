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
- Media architecture scope was ambiguous — resolved: this phase only loads and validates configuration; media backend, source registry, monitor windows, source execution, output formats, and field-level environment overrides are deferred.
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
