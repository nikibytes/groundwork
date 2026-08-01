# Agent Coordination — {{project_name}}

4 personas share this repo: `coder`, `qa`, `reviewer`, `architect`. Claims are **real file locks**, not just this document — enforced by `scripts/claim.sh` (atomic `mkdir` lock, one winner if two agents race) and `scripts/release.sh`. This file is the human-readable trail those scripts write to; don't hand-edit the Active Claims state, it's derived from `.agents/claims/*.lock`.

## How to work an item
1. `./scripts/next_task.sh <your-persona>` — get the next eligible item for your stage. If nothing comes back, there's no work for you right now.
2. `./scripts/claim.sh <persona> <item-id> <file1> [file2 ...]` — claim every file you expect to touch, all-or-nothing. Exit 1 means something's blocked — check stderr for who owns it and how old the lock is.
3. Do the work.
4. `./scripts/release.sh <persona> <item-id> "<one-line handoff note>" <file1> [file2 ...]` — releases your locks and appends a row to the Handoff Log below.
5. Update the item's `status:` and `claimed_by:` fields in `docs/task-tracker.md` to reflect the next stage.

**Stale locks**: `claim.sh` auto-clears any lock older than 2 hours (a crashed/abandoned session) and re-claims it for you, logging a warning. You don't need to manually clean up after a dead agent.

## Handoff Log
(appended automatically by `release.sh` — notes should reference the item/commit, never restate a diff or include real secrets/PII)
| Item | Persona | Note |
|---|---|---|

## Persona boundaries (enforced via `.agents/config.json`)
- `coder`: writes `src/`, `tests/` (own tests). Proposes but does not commit changes to `docs/architecture.md`.
- `qa`: writes `tests/`, `docs/task-tracker.md` (adds bug sub-items). Read-only on `src/`.
- `reviewer`: read-only everywhere. Approves via `docs/task-tracker.md` status change only.
- `architect`: only persona that writes `docs/architecture.md` and `docs/adr/`.

## Conflict resolution
If `claim.sh` reports BLOCKED and the lock isn't stale, don't retry-loop silently — surface it to the human ("waiting on `<persona>` to finish `<item>`") rather than guessing.
