# GroundWork Planning Sub-skill

## Purpose

Provide an opt-in, gated planning workflow for users who want GroundWork to turn an application idea into implementation-ready planning artifacts before production code is written.

This is a planning workflow, not a replacement for the default lightweight `/init-project` scaffold flow.

## Activation

Activate when the user explicitly requests planning before implementation, or uses the planning entry point:

```text
/init-project --plan
```

Equivalent natural-language intent includes requests such as:

- "plan this application before we code"
- "walk me through the requirements first"
- "design the schema and flows before implementation"

Do not force this workflow on users who only request the normal `/init-project` scaffold.

## Planning contract

GroundWork must guide the user through the stages in order. Do not generate all planning artifacts at once.

```text
User idea
  ↓
Interactive discovery / clarification
  ↓
PRD
  ↓ approval + lock
User personas
  ↓ approval + lock
User flows
  ↓ approval + lock
Requirements
  ↓ approval + lock
Domain model
  ↓ approval + lock
Data flow diagram
  ↓ approval + lock
Database schema
  ↓ approval + lock
Planning completeness check
  ↓
Implementation may begin
```

Each stage is a gate. The next stage cannot be treated as approved until the current stage has been explicitly approved by the user.

## Stage behavior

### 1. Discovery

Ask focused questions needed to understand the product. Reuse answers already provided and infer safe defaults where appropriate. Identify ambiguity, conflicting goals, missing actors, important constraints, and MVP boundaries.

Produce a concise discovery summary for approval. Do not prematurely create downstream technical artifacts.

### 2. PRD

Use approved discovery to draft the PRD. Cover at minimum:

- problem and objective
- target users
- product scope
- MVP capabilities
- success criteria
- functional requirements at product level
- non-goals / out of scope
- constraints and assumptions

Critique obvious gaps or contradictions before asking for approval.

### 3. User personas

Derive personas from the approved PRD. Keep personas useful for design decisions rather than biographies. Capture goals, important behaviors, pain points, permissions/roles where relevant, and success criteria.

### 4. User flows

For each important MVP journey, describe the user/system flow, alternate paths, failure paths, and important state transitions. Use Mermaid where supported for diagrams; also provide a readable textual flow so the artifact remains useful in plain Markdown environments.

### 5. Requirements

Turn the approved PRD and flows into traceable requirements. Give each requirement a stable ID and acceptance criteria. Distinguish functional, non-functional, security, data, and operational requirements where relevant.

### 6. Domain model

Derive domain entities, value objects, relationships, ownership boundaries, lifecycle/state concepts, and important invariants from approved requirements. Flag unresolved business rules instead of inventing them silently.

### 7. Data flow diagram

Design how information moves through the proposed system before implementation. Identify actors, client/UI boundaries, services, external integrations, data stores, inputs/outputs, trust boundaries, and important transformations. Use Mermaid where supported and preserve a textual explanation.

### 8. Database schema

Derive the logical schema from the approved domain model, requirements, and data flow. Include entities/tables, keys, relationships, important constraints, indexes where justified, and lifecycle/audit considerations. Clearly separate confirmed decisions from assumptions.

Do not write application code as part of this stage.

## Approval and locking

After each stage, present:

1. what was decided
2. important assumptions
3. unresolved questions or risks
4. the proposed artifact
5. a direct approval question

Use a clear gate:

```text
Stage N complete.
Approve and lock this artifact, or request changes?
```

Only an explicit user approval may transition the artifact to `LOCKED`.

Recommended front matter:

```yaml
---
status: LOCKED
version: 1
approved_by: human
approved_at: <timestamp>
---
```

Drafts should use `status: DRAFT` and must never be treated as authoritative downstream.

## Dependency guard

Planning artifacts are downstream-dependent in sequence. If a locked upstream artifact changes, GroundWork must not silently continue using stale downstream artifacts.

Example:

```text
PRD changes
 ↓
personas may need review
 ↓
flows may need review
 ↓
requirements may need review
 ↓
domain/data/schema may need review
```

GroundWork should identify affected downstream artifacts and ask the user whether to revise and re-lock them before implementation continues.

## Planning state

Maintain a machine-readable state file such as `docs/planning/planning-state.yaml`:

```yaml
planning:
  mode: active
  current_stage: discovery
  implementation_ready: false
  stages:
    discovery: {status: draft, version: 0}
    prd: {status: pending, version: 0}
    personas: {status: pending, version: 0}
    user_flows: {status: pending, version: 0}
    requirements: {status: pending, version: 0}
    domain_model: {status: pending, version: 0}
    data_flow: {status: pending, version: 0}
    database_schema: {status: pending, version: 0}
```

The state file records workflow state; the individual artifacts remain the authoritative content for their respective decisions.

## Artifact layout

Use a dedicated planning directory so planning documents are not confused with implementation/runtime documents:

```text
 docs/
   planning/
     discovery.md
     prd.md
     personas.md
     user-flows.md
     requirements.md
     domain-model.md
     data-flow.md
     database-schema.md
     planning-state.yaml
```

If an existing project already has a relevant artifact, read it first and propose an update rather than silently replacing it.

## Excel task tracker handoff

After the planning gates are complete, GroundWork may derive implementation tasks into the human-facing Excel tracker:

```text
approved requirements/domain/schema
          ↓
     task breakdown
          ↓
 docs/task-tracker.xlsx
```

Excel is a human-facing task-management interface, not the canonical semantic planning state. Preserve stable task IDs and do not overwrite unrelated user edits.

The planner should not make implementation-ready tasks authoritative until the prerequisite planning artifacts are locked.

## Completion gate

Before saying planning is complete, verify that all required stages are locked:

```text
[✓] Discovery
[✓] PRD
[✓] Personas
[✓] User flows
[✓] Requirements
[✓] Domain model
[✓] Data flow
[✓] Database schema
```

Only then set:

```yaml
implementation_ready: true
```

The completion message should summarize the approved planning baseline and identify any explicitly accepted assumptions or risks.
