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

## Relationships

- The **Project** contains the **Cereal** package.
- The **Cereal** package exposes the `cereal` **CLI command**.
- The package name, import name, **CLI command**, and initial command output are all `cereal`.
- The **CLI command** loads **Settings** through a factory and passes them into runtime functions.

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
