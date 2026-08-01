## Project Init Protocol (auto-injected, do not remove)

Before writing or editing any production code in this repo:
1. Read `docs/prd.md`, `docs/architecture.md`, `docs/task-tracker.md`.
2. Confirm the change maps to an item in `docs/task-tracker.md`. If it doesn't, add it first (Backlog → In Progress) rather than doing untracked work.
3. Check the action against `.agents/permissions.json` and `.config/ai/safety-rules.md` before running any shell command.

After writing or editing code:
1. Run the test command from `docs/testing-playbook.md`. Do not mark anything done without a pass.
2. Update `docs/task-tracker.md` (move item to Completed).
3. Append one line to `docs/changelog-agent.md`: `{{date}} — <what changed> — <task-tracker item>`.
4. If a new module, schema, or dependency was introduced, update `docs/architecture.md` in the same commit.

This loop applies to every future session in this repo, not just the first one.

## Documentation discipline (always applies)

**Don't duplicate — reference.** When writing to any doc in `docs/`, `.agents/coordination.md`, or `docs/changelog-agent.md`, never restate content that already lives in a spec, ADR, PR, commit, or diff — link or point to it instead (file path, commit hash, PR/issue number). E.g. write "see ADR-0003 for the reasoning" not a re-explanation of ADR-0003; write "implements the schema in `src/models/user.py`" not a copy of its field list; write "see commit `a1b2c3d`" not a restated diff. This keeps every doc a single source of truth instead of N stale copies.

**Redact before writing.** Before adding anything to `docs/changelog-agent.md`, `.agents/coordination.md`, `docs/security.md`, error notes, or any other file, strip real API keys, passwords, tokens, connection strings, and personally identifiable information (names, emails, phone numbers tied to real people, not placeholder contacts) — even when quoting an error message or log line that contained one. Replace with a placeholder like `<redacted>` and note that redaction happened. This applies everywhere, not just `.env`.

**If the `squad` module is installed**: before Step 1, run `scripts/next_task.sh <your-persona>` to get your next item, then `scripts/claim.sh <persona> <item-id> <files...>` before editing anything — do not edit without a successful claim, even for a "quick fix." After Step 2 (updating the changelog), run `scripts/release.sh <persona> <item-id> "<handoff note>" <files...>` and update `docs/task-tracker.md`'s status/claimed_by fields. Stay inside your persona's scope in `.agents/config.json` — e.g. `coder` never approves its own item; that's `reviewer`'s job.
