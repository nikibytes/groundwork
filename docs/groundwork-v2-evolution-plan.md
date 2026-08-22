# GroundWork v2 Evolution Plan

> Working product/design artifact. This document defines the intended evolution of GroundWork into an intuitive engineering collaborator. This branch intentionally implements only this planning artifact plus the Excel task-tracker foundation; other capabilities remain in their separate PRs and future milestones.

## Vision

GroundWork should guide a user through the software-planning and engineering lifecycle rather than only generating a static document scaffold.

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
```

The collaborator should be interactive: ask only what is needed, explain trade-offs, challenge weak decisions, preserve user intent, and make approval/state transitions explicit.

## Planning artifacts

The eventual connected planning model may include:

- `docs/prd.md` — product scope
- `docs/personas.md` — user/persona definitions
- `docs/user-flows.md` — primary journeys
- `docs/requirements.md` — functional and non-functional requirements
- `docs/domain-model.md` — domain entities and relationships
- `docs/database-schema.md` — data design
- `docs/api-design.md` — API contracts
- `docs/architecture.md` — high-level architecture
- `docs/ai-knowledge-pipeline.md` — AI data/knowledge pipeline where applicable
- `docs/task-tracker.xlsx` — human-facing task tracker
- `docs/risks.md` — risks, mitigations and trade-offs
- ADRs — important architectural decisions

These should eventually form a connected planning model rather than isolated documents. Their generation, critique, locking, and downstream automation are separate future work and are **not implemented in this branch**.

## Excel task tracker — implemented in this branch

Excel is the human-facing task-management interface. GroundWork's semantic/project state must remain independent of spreadsheet formatting.

Recommended columns:

```text
ID | Milestone | Task | Requirement | Status | Priority |
Risk | Dependencies | Owner | Files | Tests | Notes
```

### Read / write / synchronize

`scripts/excel_tracker.py` provides the initial workbook boundary:

```bash
python3 scripts/excel_tracker.py write docs/task-tracker.xlsx --json tasks.json
python3 scripts/excel_tracker.py read docs/task-tracker.xlsx
python3 scripts/excel_tracker.py sync docs/task-tracker.xlsx --json updates.json
```

The synchronization model is intentionally narrow:

```text
GroundWork project/task state
          ↓
       write.xlsx
          ↓
Human / agent edits workbook
          ↓
       read.xlsx
          ↓
validated task records
          ↓
GroundWork can consume/update the task state
```

`sync` updates existing rows by stable `ID` and rejects unknown IDs instead of silently creating ambiguous tasks. The script preserves the declared task columns and does not attempt to become the project's semantic source of truth.

This branch does **not** wire Excel into the intelligence/planning commands from other branches. That integration remains with the corresponding task-planning PR and future work.

Excel support uses `openpyxl`; environments that use this feature must have that dependency installed.

## Future collaborator behavior — design only

### Peer-review loop

A future capability may support:

```text
/init-project critique [artifact]
```

For a PRD, ERD, schema, API design, or similar artifact, the review should provide:

1. **PROS** — sound decisions and boundaries.
2. **CONS** — gaps, bottlenecks, security concerns, edge cases, scaling constraints and ambiguity.
3. **PROACTIVE OPTIMIZATION** — 1–2 concrete improvements.
4. **INTERACTIVE DIALOGUE** — a targeted trade-off choice such as MVP simplicity vs enterprise scale.

The reviewer should not silently rewrite or change user intent.

### Proactive scaffolding

After an explicitly approved planning step, GroundWork should propose the next logical artifact using project context and technology choices. Examples include deriving task work from an approved PRD or drafting API contracts after an approved data model. This is design intent only in this branch.

### State Guard

A future lock operation may support:

```text
/init-project lock <artifact-name>
```

Possible metadata:

```yaml
---
status: LOCKED
version: 1.0
locked_at: 2026-08-22
authority: human_approved
---
```

If a locked artifact is contradicted by a later request or downstream artifact, GroundWork should surface the conflict and require an explicit human decision. The exact lock schema and implementation are future work.

## AI application planning — design only

For AI-enabled products, the planning workflow should eventually cover the applicable knowledge/model pipeline:

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

The plan should identify applicable stages, data contracts, quality risks, evaluation, privacy/security and operational cost. This is not implemented in this branch.

## Relationship to the separate intelligence PRs

Repository observation, project understanding, drift, change impact, agent context, task planning, semantic reasoning, architecture intelligence, and validation are being developed in their own PRs. **This branch does not duplicate or reimplement those capabilities.**

The v2 plan is the product-level direction that those capabilities will eventually support.

## Principles

1. Interactive, not form-filling.
2. Critique before commitment.
3. Explicit human approval for authoritative state.
4. No silent scope changes.
5. Evidence before inference.
6. Keep deterministic facts separate from agent/LLM interpretation.
7. Excel is a human-facing tracker, not the canonical semantic model.
8. Make MVP/scale trade-offs explicit.
9. Keep AI-app planning aware of the knowledge/evaluation pipeline.
10. Deliver future capabilities as complete, independently testable PR milestones.
11. Stop at explicit test gates before building dependent milestones.
