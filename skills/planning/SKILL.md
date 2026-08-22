---
name: groundwork-planning
description: Opt-in gated application planning for GroundWork. Use only when the user explicitly asks to plan an application before implementation or invokes `/init-project --plan`. Guides the user through discovery, PRD, personas, user flows, requirements, domain model, data flow, and database schema; requires explicit human approval before locking each stage and proceeding.
---

# GroundWork Planning

This is an opt-in sub-skill of GroundWork. Do not activate it for ordinary `/init-project` requests unless the user asks for planning before implementation or uses `/init-project --plan`.

## Goal

Reduce tedious planning/documentation work while keeping the developer in control of product and architecture decisions.

GroundWork should progressively turn the user's idea into implementation-ready planning artifacts, not dump a large documentation package on the user.

## Mandatory gated sequence

Run these stages in this exact order:

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

Never skip ahead because a later artifact appears easy to infer. Use the approved upstream artifacts as the input to each downstream stage.

## Conversation protocol

At each stage:

1. Read all already-approved upstream artifacts.
2. Ask only the questions needed to resolve ambiguity for this stage.
3. Draft the artifact.
4. Critique the draft: gaps, contradictions, risks, edge cases and assumptions.
5. Present the proposed artifact and a concise decision summary.
6. Ask explicitly: **"Approve and lock this stage, or request changes?"**
7. Do not proceed until the user explicitly approves.
8. On approval, mark the artifact `LOCKED`, increment its version, record approval metadata, and advance to the next stage.

Do not silently rewrite approved decisions while generating later artifacts.

## Stage requirements

### Discovery

Establish objective, target users, problem, MVP boundary, important constraints, integrations, assumptions and unresolved decisions. Avoid unnecessary technical detail until it is relevant.

### PRD

Produce a concise product requirements document covering objective/problem, users, scope, MVP capabilities, success criteria, requirements at product level, non-goals, assumptions and constraints.

### User personas

Create decision-useful personas from the approved PRD: goals, behaviors, pain points, roles/permissions where relevant, and success criteria. Avoid decorative biography.

### User flows

Map the important MVP journeys, including happy paths, alternate paths, failure paths and state transitions. Prefer Mermaid diagrams where supported, with a textual representation as fallback.

### Requirements

Convert the approved PRD and flows into traceable requirements with stable IDs and acceptance criteria. Include relevant functional, non-functional, security, data and operational requirements.

### Domain model

Define entities, value objects, relationships, ownership boundaries, lifecycle/state concepts and business invariants. Surface unresolved business rules instead of inventing them.

### Data flow diagram

Design information movement before implementation. Show actors, clients/UI, services, external integrations, data stores, trust boundaries, inputs/outputs and important transformations. Prefer Mermaid plus a textual explanation.

### Database schema

Derive the logical schema from the locked domain model, requirements and data flow. Include entities/tables, keys, relationships, constraints and justified indexes. Identify audit/lifecycle needs and clearly mark assumptions.

Do not write production application code during planning.

## Artifact state

Use a planning directory in the target project:

```text
 docs/planning/
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

Draft artifacts use:

```yaml
---
status: DRAFT
version: 0
---
```

Approved artifacts use:

```yaml
---
status: LOCKED
version: 1
approved_by: human
approved_at: <timestamp>
---
```

The exact timestamp format may follow the host environment.

## Planning state

Maintain `docs/planning/planning-state.yaml` as workflow state:

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

When all stages are locked, set `implementation_ready: true` and stop planning unless the user asks for additional planning artifacts.

## Change guard

If a locked upstream artifact must change, stop and identify affected downstream stages. Do not silently continue with stale decisions.

For example:

```text
PRD changed
 ↓
personas → review required
 ↓
flows → review required
 ↓
requirements → review required
 ↓
domain/data/schema → review required
```

The user must explicitly approve/re-lock affected artifacts before implementation is considered ready again.

## Excel handoff

After the required planning stages are locked, derive implementation tasks into the human-facing `docs/task-tracker.xlsx` when the Excel tracker capability is installed.

Excel is not the canonical semantic planning model. Preserve stable task IDs and user edits. Planning artifacts and planning state remain the source of truth for approved decisions.

## Completion message

Before implementation begins, report:

```text
[✓] Discovery
[✓] PRD
[✓] Personas
[✓] User flows
[✓] Requirements
[✓] Domain model
[✓] Data flow
[✓] Database schema

Planning baseline locked. Implementation may begin.
```

Also list explicitly accepted assumptions, unresolved risks, and any items intentionally deferred.
