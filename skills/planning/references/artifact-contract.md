# Planning Artifact Contract

All planning artifacts must use this contract so the workflow can resume and guard state deterministically.

## Required metadata

```yaml
---
status: DRAFT | LOCKED
version: <integer>
approved_by: human          # required when LOCKED
approved_at: <UTC timestamp> # required when LOCKED
---
```

`DRAFT` artifacts may be edited. `LOCKED` artifacts are authoritative and must not be edited in place by the planning workflow.

## Decision provenance

Inside each artifact, distinguish statements as:

- **USER DECISION** — explicitly supplied or approved by the user.
- **GROUNDED INFERENCE** — directly derived from approved upstream artifacts.
- **ASSUMPTION** — a temporary assumption needed to proceed.
- **UNRESOLVED** — a question that remains unanswered.

GroundWork must not convert an assumption or inference into a user decision without explicit approval.

## Revision protocol

If a locked artifact needs to change:

1. Explain why the change is needed.
2. Identify downstream artifacts that may be affected.
3. Ask the user to approve reopening/revising it.
4. Create the next version rather than silently mutating the locked version.
5. Mark affected downstream stages `REVIEW_REQUIRED` until they are re-approved.

Git history is the audit trail; filesystem permissions are not used as the source of truth.
