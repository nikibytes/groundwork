# GroundWork v2 Evolution Plan

> Working product/design artifact. This document describes the intended evolution of GroundWork from a passive scaffold generator into an intuitive engineering collaborator. It is a planning reference, not approval that every capability is already implemented.

## Vision

GroundWork should guide a user through the software-planning and engineering lifecycle, while maintaining a machine-readable model of project intent and implementation reality.

The long-term workflow is:

```text
User idea
  ↓
Interactive discovery / clarification
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
AI knowledge pipeline (for AI applications)
  ↓
Tasks / milestones
  ↓
Risks / trade-offs / improvements
  ↓
Implementation
  ↓
Repository intelligence
  ↓
Drift / impact / validation
  ↓
Feedback into planning
```

The collaborator should be interactive rather than a form generator: ask only what is needed, infer safe defaults, explain trade-offs, challenge weak decisions, and make approval/state transitions explicit.

## Planning artifacts

Where applicable, GroundWork should be able to create and maintain connected artifacts such as:

- `docs/prd.md` — product scope and source of truth
- `docs/personas.md` — user/persona definitions
- `docs/user-flows.md` — primary journeys and flows
- `docs/requirements.md` — functional/non-functional requirements
- `docs/domain-model.md` — domain entities and relationships
- `docs/database-schema.md` — logical/physical data design
- `docs/api-design.md` — API contracts and behavior
- `docs/architecture.md` — high-level system architecture
- `docs/ai-knowledge-pipeline.md` — data/knowledge ingestion, indexing, retrieval, evaluation and observability for AI applications
- `docs/task-tracker.xlsx` — human-facing task and milestone tracker
- `docs/risks.md` — risks, mitigations and trade-offs
- ADRs — durable records of important architectural decisions

These should form a connected project-planning model rather than isolated generated documents.

## Excel task tracker

The task tracker should use Excel (`.xlsx`) as the human-facing planning and task-management interface while keeping GroundWork's internal intelligence model independent of spreadsheet formatting.

Recommended columns:

```text
ID | Milestone | Task | Requirement | Status | Priority |
Risk | Dependencies | Owner | Files | Tests | Notes
```

The intended flow is:

```text
PRD / requirements / architecture
            ↓
GroundWork project intelligence
            ↓
task planning
            ↓
docs/task-tracker.xlsx
            ↓
human / agent updates
            ↓
GroundWork reads tracker again
            ↓
planning / impact / drift / validation
```

GroundWork should provide reliable read/write support for the workbook and preserve task identity and state across updates. Excel is a user-facing view/control surface, not the canonical semantic project model. The canonical model remains the connected GroundWork project state and source artifacts.

The Excel integration should eventually support:

- creating an initial workbook from approved requirements/tasks
- reading human status and ownership changes
- writing GroundWork recommendations and derived fields
- preserving stable task IDs
- preserving user-entered notes where possible
- validating required columns/status values
- detecting conflicting or malformed spreadsheet edits
- round-trip tests: write → read → equivalent task state
- incremental updates rather than rewriting unrelated rows

## Interactive peer-review loop

GroundWork should not blindly accept important user artifacts.

Future capability:

```text
/init-project critique [artifact]
```

For a PRD, ERD, schema, API design, or similar artifact, perform a structured review:

1. **PROS** — identify sound decisions and clear boundaries.
2. **CONS** — identify gaps, bottlenecks, security concerns, edge cases, scaling constraints and ambiguity.
3. **PROACTIVE OPTIMIZATION** — suggest 1–2 concrete improvements.
4. **INTERACTIVE DIALOGUE** — ask a targeted decision question, such as MVP simplicity vs enterprise scale.

The review should critique without silently rewriting or changing user intent.

## Proactive scaffolding

Once a planning step is explicitly approved, GroundWork should propose and, when authorized, draft the immediate next logical artifact using the actual project context and stack.

Examples:

- approved PRD → derive granular machine-readable tasks in `docs/task-tracker.xlsx`
- approved domain/database schema → draft matching API contracts
- approved architecture → identify implementation milestones and risks
- approved AI application scope → draft the AI knowledge pipeline plan

The next artifact must be proposed explicitly before it is treated as approved project state.

## State Guard

Approved planning artifacts need an explicit authority/version state.

Future lock capability:

```text
/init-project lock <artifact-name>
```

A possible metadata representation is:

```yaml
---
status: LOCKED
version: 1.0
locked_at: 2026-08-22
authority: human_approved
---
```

The exact schema is subject to implementation design.

When a relevant artifact is `LOCKED`, GroundWork should treat it as an authoritative constraint. If a later request, generated artifact, or implementation contradicts it, GroundWork must stop, surface the conflict, and ask the human to either version the locked artifact or change the request.

A lock represents human-approved project state; it is not merely an operating-system file permission. Git history remains the audit trail.

## Intelligence foundation

The existing repository-intelligence work is the reality-understanding half of this larger system:

```text
v0.1  Repository observation
v0.2  Project understanding + drift
v0.3  Change impact
v0.4  Agent context
v0.5  Intelligent task planning
v0.6  Semantic reasoning
v0.7  Architecture / ADR intelligence
v0.8  Change validation
v1.0  Unified intelligence
```

This foundation should remain deterministic wherever facts can be derived reliably. The existing agent's LLM should provide semantic reasoning over grounded evidence rather than becoming a second source of repository facts.

## AI application planning

For AI-enabled products, GroundWork should extend ordinary software planning with a knowledge/model pipeline where relevant:

```text
Sources
 ↓
Ingestion
 ↓
Cleaning / normalization
 ↓
Chunking / transformation
 ↓
Embeddings / indexing
 ↓
Retrieval / ranking
 ↓
Context assembly
 ↓
Model / agent
 ↓
Evaluation
 ↓
Observability / feedback
```

The plan should identify which stages actually apply, their data contracts, quality risks, evaluation strategy, privacy/security considerations, and operational costs.

## Principles

1. Interactive, not form-filling.
2. Critique before commitment.
3. Explicit human approval for authoritative state.
4. No silent scope changes.
5. Evidence before inference.
6. Keep deterministic facts separate from LLM interpretation.
7. Excel is a human-facing tracker, not the canonical semantic model.
8. MVP-aware trade-offs: simplicity, cost, time-to-market and scale should be explicit.
9. AI-app planning must include the knowledge/evaluation pipeline when relevant.
10. Planning artifacts should be connected and versioned.
11. Every capability should be delivered as a complete, independently testable PR milestone.
12. When a milestone becomes a prerequisite for later work, stop at a clearly declared test gate and require validation before continuing.

## Implementation considerations

- Parse project state and artifact metadata rather than relying only on file existence.
- Preserve coder/non-coder adaptation: use business-level trade-offs for non-coders and detailed engineering analysis for technical users.
- Prefer a canonical task model behind the Excel interface so other tooling does not depend on spreadsheet formatting.
- Consolidate overlapping legacy task/repository mechanisms instead of creating parallel sources of truth.
- Future lock tooling may use `scripts/lock.sh`, but metadata/state is the primary authority mechanism.
- Critique findings should be persisted and linkable to decisions/ADRs where useful.
- Semantic conclusions should retain evidence references and confidence, and support an explicit `insufficient evidence` result.

## Open decisions

- Final command namespace: keep `/init-project critique/lock` or move planning operations under `/groundwork`.
- Exact lock metadata/version semantics.
- Exact Excel schema and synchronization/conflict policy.
- Canonical internal task schema and migration from the legacy Markdown tracker.
- How planning artifacts map into `feature-map.json` and the future project knowledge graph.
- How AI-app pipeline stages are represented for different application types.
