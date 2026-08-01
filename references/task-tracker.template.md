# Task Tracker — {{project_name}}

> If `squad` module is installed: use this exact line format so `scripts/next_task.sh` can parse it —
> `- [ ] <task text> — status: Backlog — claimed_by: none`
> Valid statuses: `Backlog`, `Claimed`, `In Progress`, `Ready for QA`, `In QA`, `Ready for Review`, `In Review`, `Architecture Review Needed`, `Completed`. Update the status and claimed_by fields in place as the item moves — don't rewrite it as a new line.

## Backlog
- [ ] {{feature_1}}
  - [ ] Design/schema
  - [ ] Implementation
  - [ ] Tests
- [ ] {{feature_2}}
  - [ ] Design/schema
  - [ ] Implementation
  - [ ] Tests
- [ ] {{feature_3}}
  - [ ] Design/schema
  - [ ] Implementation
  - [ ] Tests

## In Progress
(none yet)

## Completed
(none yet)

## Rules
- Agent moves an item Backlog → In Progress before starting work on it, In Progress → Completed only after tests pass.
- Every completed item gets one line in `docs/changelog-agent.md`.
- Never delete a completed item — it's the project's history.
