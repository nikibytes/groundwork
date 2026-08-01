Place at `docs/adr/0001-record-architecture-decisions.md`:

```markdown
# ADR 0001: Record architecture decisions

## Status
Accepted

## Context
We need a lightweight way to track *why* significant technical decisions were made, not just what the code currently does (that's docs/architecture.md's job).

## Decision
Use ADRs (this format) for any decision that would be expensive to reverse: choice of database, auth provider, major library, API design pattern, etc. One file per decision, numbered sequentially, never edited after acceptance — superseded by a new ADR instead.

## Consequences
Future agents/contributors can see why a decision was made before proposing to change it.
```

Agent: create a new numbered ADR (`000X-short-title.md`) whenever such a decision is made — don't retroactively edit old ones.
