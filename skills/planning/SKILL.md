---
name: groundwork-planning
description: Opt-in gated application planning for GroundWork. Use only when the user explicitly asks to plan an application before implementation or invokes `/init-project --plan`. Guides the user through discovery, PRD, personas, user flows, requirements, domain model, data flow, and database schema; requires explicit human approval before locking each stage and proceeding.
---

# GroundWork Planning

This is an opt-in sub-skill of GroundWork. Do not activate it for ordinary `/init-project` requests unless the user asks for planning before implementation or uses `/init-project --plan`.

## Goal

Reduce tedious planning/documentation work while keeping the developer in control of product and architecture decisions.

GroundWork progressively turns the user's idea into implementation-ready planning artifacts. It must not dump all planning documents at once.

## Activation and onboarding

Repository Intelligence is always active when available in GroundWork and supplies repository facts to this workflow. It is not a reason to interrupt planning.

Project Initialization and Guided Planning are default available workflows. On a fresh GroundWork installation, offer the user a simple choice of what to start with rather than forcing a planning interview.

Optional Team, Enterprise and Squad capabilities are contextual recommendations only. If the user's language indicates a team, regulated/enterprise environment, or multiple specialized agents, offer the relevant capability and ask for explicit approval before activation. Never silently activate optional capabilities.

Planning activation is explicit:

```text
/init-project --plan
```

Natural-language requests such as "plan this application before we code" also activate planning when GroundWork routing is available.

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

## Deterministic workflow state

The planning workflow must maintain `docs/planning/planning-state.yaml` and use it to resume rather than infer progress from chat history alone.

Use the bundled state engine where available:

```bash
python3 skills/planning/scripts/planning_state.py init --root .
python3 skills/planning/scripts/planning_state.py status --root .
python3 skills/planning/scripts/planning_state.py approve <stage> --root .
```

The engine is the deterministic gatekeeper for stage ordering, approval, versioning and the final `implementation_ready` transition. The conversational agent must not claim a stage is locked unless the state transition has succeeded.

## Conversation protocol

At each stage:

1. Read the current planning state.
2. Confirm the current stage is the next allowed stage.
3. Read all already-approved upstream artifacts.
4. Ask only questions needed to resolve ambiguity for this stage.
5. Draft or update only the current artifact.
6. Critique the draft: gaps, contradictions, risks, edge cases and assumptions.
7. Explicitly label provenance as **USER DECISION**, **GROUNDED INFERENCE**, **ASSUMPTION**, or **UNRESOLVED**.
8. Present the proposed artifact and concise decision summary.
9. Ask: **"Approve and lock this stage, or request changes?"**
10. Do not proceed until the user explicitly approves.
11. On approval, invoke the state engine to lock the artifact and advance.
12. If the transition fails, report the failure and do not pretend the stage advanced.

Do not silently rewrite an approved artifact while generating later artifacts.

## Stage requirements

### Discovery

Establish objective, target users, problem, MVP boundary, important constraints, integrations, assumptions and unresolved decisions. Avoid unnecessary technical detail until it is relevant.

### PRD

Produce a concise product requirements document covering objective/problem, users, scope, MVP capabilities, success criteria, product-level requirements, non-goals, assumptions and constraints.

### User personas

Create decision-useful personas from the locked PRD: goals, behaviors, pain points, roles/permissions where relevant, and success criteria. Avoid decorative biography.

### User flows

Map important MVP journeys, including happy paths, alternate paths, failure paths and state transitions. Prefer Mermaid diagrams where supported, with a readable textual representation as fallback.

### Requirements

Convert the locked PRD and flows into traceable requirements with stable IDs and acceptance criteria. Include relevant functional, non-functional, security, data and operational requirements.

### Domain model

Define entities, value objects, relationships, ownership boundaries, lifecycle/state concepts and business invariants. Surface unresolved business rules instead of inventing them.

### Data flow diagram

Design information movement before implementation. Show actors, clients/UI, services, external integrations, data stores, trust boundaries, inputs/outputs and important transformations. Prefer Mermaid plus a textual explanation.

### Database schema

Derive the logical schema from the locked domain model, requirements and data flow. Include entities/tables, keys, relationships, constraints and justified indexes. Identify audit/lifecycle needs and clearly mark assumptions.

Do not write production application code during planning.

## Artifact contract

Use the contract in `references/artifact-contract.md`.

Planning artifacts live under:

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

Drafts use `status: DRAFT`. Locked artifacts use `status: LOCKED`, a monotonically increasing version, `approved_by: human`, and an approval timestamp.

A locked artifact is authoritative for its stage and must not be downgraded or silently edited in place by the planning workflow.

## Change guard and invalidation

If a locked upstream artifact needs to change, do not directly overwrite it.

1. Explain the requested change and why it matters.
2. Identify all downstream stages that may be affected.
3. Ask the human to explicitly approve reopening/revising the upstream artifact.
4. Create the next version through the approval workflow.
5. Mark affected downstream stages `REVIEW_REQUIRED` in planning state.
6. Re-run those stages in order and require fresh approval before implementation can become ready.

A downstream artifact must never remain apparently `LOCKED` and implementation-ready when its locked upstream source has changed.

## Resume behavior

When planning is invoked on an existing project:

- Read `docs/planning/planning-state.yaml` first.
- If state exists, resume at `current_stage`.
- Never restart an already locked stage unless its upstream dependency is marked for review.
- If artifacts exist without planning state, inspect their front matter, report the ambiguity, and ask whether to initialize planning state from those artifacts. Do not silently guess.

## Excel task tracker handoff

Only after all required planning stages are locked may GroundWork derive implementation tasks into `docs/task-tracker.xlsx` when the Excel tracker capability is installed.

The task tracker should use stable task IDs and retain human edits. GroundWork should update only fields it owns and must not overwrite unrelated rows or notes. Excel is a human-facing task-management interface, not the canonical semantic planning model.

## Completion gate

Before saying planning is complete, verify the state engine reports every required stage as `LOCKED` and `implementation_ready: true`.

Report:

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

Also list accepted assumptions, unresolved risks and intentionally deferred items.

If any stage is not locked, explicitly say implementation is **not** planning-ready.
