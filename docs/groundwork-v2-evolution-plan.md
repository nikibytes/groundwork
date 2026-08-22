# GroundWork v2 Evolution Plan

> Working design artifact. Consult this document when extending GroundWork's planning, critique, state-guard, and proactive scaffolding capabilities. This is a design reference, not yet an implementation specification for all features described below.

## Objective

Evolve GroundWork from a passive document scaffold generator into an active, intuitive engineering collaborator: an interactive, loop-based engineering peer that critiques ideas, acts as a documentation buffer, proactively prepares the next engineering artifact, and protects approved project state from accidental scope drift.

## Architectural Redesign

### 1. Interactive command modes

Introduce two capabilities:

- `/init-project critique [artifact]` — deeply analyze a supplied engineering artifact such as a PRD, ERD, or schema using a Senior Engineer peer-review protocol.
- `/init-project lock <artifact-name>` — freeze an approved document version as a downstream source of truth.

These commands should eventually become part of the broader GroundWork planning workflow rather than remain isolated utilities.

### 2. Peer Review Loop (`critique`)

When a user provides an engineering artifact, do not immediately accept or rewrite it. Perform a structured review:

1. **PROS** — identify what is architecturally sound, including clear boundaries and appropriate data modeling.
2. **CONS** — identify bottlenecks, missing edge cases, security concerns, scaling constraints, and ambiguity.
3. **PROACTIVE OPTIMIZATION** — suggest 1–2 concrete structural improvements.
4. **INTERACTIVE DIALOGUE** — finish with a targeted choice, such as whether to optimize for enterprise scale or keep the design simple for an MVP.

The review should be evidence-based and preserve the user's intent rather than silently redesigning the system.

### 3. Context-aware proactive scaffolding

After a planning step is explicitly approved, GroundWork should prepare the immediate next logical artifact using the actual project context and technology stack.

Examples:

- Approved ERD/data schema → draft matching API contracts / OpenAPI specification.
- Approved PRD → break MVP features into granular, machine-parseable tasks in `docs/task-tracker.md`.

The agent should propose the next step first, make the proposed transition explicit, and avoid silently changing project scope.

### 4. State Guard / immutable document locking

Approved artifacts should be representable as explicit project state.

A future lock operation may add front matter such as:

```yaml
---
status: LOCKED
version: 1.0
locked_at: 2026-08-22
authority: human_approved
---
```

The exact metadata schema should be finalized during implementation.

The enforcement rule should be conceptually:

> Before generating code or modifying features, inspect the status of relevant planning artifacts. If an artifact is `LOCKED`, treat it as an authoritative constraint. If a new request or downstream artifact contradicts it, stop, surface the conflict, and ask the human to version the locked artifact or change the request.

Important: a lock is a **state/authority mechanism**, not merely an OS file permission trick. Git history remains the audit trail; the lock metadata communicates project intent to agents.

### 5. Implementation considerations

- Extend the project state check to parse metadata such as `status: LOCKED`, not only test whether `docs/prd.md` exists.
- Preserve coder/non-coder adaptation. Non-coder reviews should emphasize cost, complexity, user impact, operational risk, and trade-offs; coder reviews can use detailed engineering terminology.
- A future `scripts/lock.sh` may automate lock metadata updates. If used with the squad module, it should integrate with the existing coordination/permission conventions rather than rely on filesystem permissions as the primary enforcement mechanism.

## Relationship to the Intelligence Roadmap

This artifact extends the existing repository-intelligence roadmap. The current intelligence work primarily helps GroundWork understand and validate an existing project. The long-term planning collaborator should add the **forward engineering lifecycle** on top:

```text
User idea
  ↓
Project discovery / clarification
  ↓
PRD
  ↓
User personas
  ↓
User flows
  ↓
Requirements
  ↓
Domain model
  ↓
Database schema
  ↓
API design
  ↓
High-level architecture
  ↓
AI knowledge pipeline (when applicable)
  ↓
Tasks / milestones
  ↓
Risks / trade-offs
  ↓
Implementation
  ↓
Repository intelligence
  ↓
Drift / impact / validation
  ↓
Feedback into planning
```

The repository-intelligence roadmap (observation, project understanding, change impact, context, planning, semantic reasoning, architecture intelligence, validation) is therefore the **backward-looking/reality-understanding half** of the larger collaborator. This planning artifact describes the **forward-looking/project-creation half**.

## Design principles

1. **Interactive, not form-filling.** Ask only what is needed at the current stage and infer safe defaults where possible.
2. **Critique before commitment.** Important artifacts should be reviewed before becoming downstream sources of truth.
3. **Explicit approval transitions.** Make it clear when a document becomes authoritative.
4. **No silent scope changes.** Contradictions must be surfaced to the human.
5. **Evidence before inference.** Deterministic repository facts remain distinct from LLM interpretation.
6. **Human authority.** A lock represents human-approved intent; the system must never manufacture human approval.
7. **Proactive but not presumptive.** GroundWork can draft the next artifact, but should not silently approve or publish it.
8. **MVP-aware.** Recommendations should distinguish simplicity, cost, time-to-market, scale, and enterprise requirements.
9. **AI-app aware.** For AI applications, planning must eventually include data/knowledge sources, ingestion, chunking, indexing, retrieval, evaluation, model boundaries, and observability where relevant.
10. **Versioned state.** Planning artifacts and their approvals should be traceable through Git and explicit metadata.

## Future planning artifacts

The eventual planning workflow should be capable of producing and relating, where relevant:

- `docs/prd.md`
- `docs/personas.md`
- `docs/user-flows.md`
- `docs/requirements.md`
- `docs/domain-model.md`
- `docs/database-schema.md`
- `docs/api-design.md`
- `docs/architecture.md`
- `docs/ai-knowledge-pipeline.md` for AI applications
- `docs/task-tracker.md`
- `docs/milestones.md`
- `docs/risks.md`
- ADRs for important architectural decisions

These should form a connected planning model rather than a collection of independent generated documents.

## Open implementation questions

- Exact CLI naming: retain `/init-project critique` and `/init-project lock`, or move planning operations under `/groundwork` as the intelligence surface grows.
- Lock metadata schema and versioning semantics.
- Whether locked artifacts are immutable by default or require an explicit `unlock`/`version` operation.
- How critique findings are persisted and linked to subsequent decisions.
- How planning artifacts map into the existing `feature-map.json` and future project knowledge graph.
- How LLM providers are configured and how evidence/citations are stored for semantic conclusions.
- How AI-app knowledge pipeline planning differs from conventional application planning.

## Implementation rule

Each future capability should be delivered as a **complete, independently testable PR milestone**. Avoid building a large amount of hidden infrastructure without a user-visible workflow that can be exercised on a small example project.
