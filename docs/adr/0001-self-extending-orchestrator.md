# Cereal is a self-extending Orchestrator over narrow capabilities

Cereal is a continuous monitor: conventional detection (YOLO) runs in the
background over active Sources and accumulates Detection events in the Detection
store before any question is asked. Questions are answered at query time by an
Orchestrator agent that composes narrow, serializable capabilities (detection
lookup, object-track lookup, evidence retrieval, visual validation) rather than
by bespoke subsystems. Query understanding, correlation / emergent tagging, and
structured reporting are therefore Orchestrator responsibilities, not standalone
modules.

The north-star goal is a *self-extending* Orchestrator: it can select existing
Agent definitions and also author new reusable Self-authored agents and Authored
tools, persisting them as canonical `.agent` directories and registering them in
a durable, writable Agent registry for reuse across runs.

We build bottom-up — hand-made capabilities first (object tracks, a real Visual
validator, query composition, answer composition) — because the proven
capability set plus the capability contract become the template the Orchestrator
authors against. Building the authoring machinery before the template exists
would mean generating code against an unvalidated contract. Authored tools
additionally require a trust / execution boundary and validation-before-reuse,
deferred until that template is real.

## Consequences

- The static in-memory registry and "dynamic generation out of scope" framings
  are first-slice scope, not the project goal.
- A writable Agent registry, a tool-authoring trust boundary, and dynamic
  tool-catalog loading are committed future work.
- Accepted risk: agent-composed answers are less deterministic than bespoke
  query-understanding and reporting modules would be.
