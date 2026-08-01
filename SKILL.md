---
name: groundwork
license: MIT
metadata:
  version: "1.0"
description: Bootstraps a new coding project before any production code is written. Trigger this whenever the user runs /init-project, /bootstrap, /init-project help, or asks to "set up a new project", "start a new repo", "scaffold this project", "what commands does this have", or similar. Also handles add-on commands like /init-project add <module> or /init-project --team / --enterprise for teams and larger projects that need CI, code review, security, and ADR docs beyond the solo-dev core set. Interviews the user on app name, purpose, target audience, stack, database, auth, hosting, integrations, and MVP scope — remembers whether the user is a coder or non-coder across all future projects via ~/.groundwork/profile.md, batching questions for coders and proactively suggesting defaults one-at-a-time for non-coders — then generates a docs/ ecosystem plus an agent runtime config that enforces reading/updating those docs on every future change. Do NOT use this on an existing project that already has docs/prd.md — offer update mode instead.
---

# Project Init

One command, five questions, a minimal working scaffold — plus opt-in modules for teams and larger projects. Solo devs get 6 files. Teams get code-review + CI structure. Larger/regulated projects get ADRs, security docs, and stricter agent permissions.

## Commands

| Command                         | What it does                                                                                                                                                      |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/init-project`                 | Fresh init, core module only (default — solo/MVP).                                                                                                                |
| `/init-project --team`          | Core + `team` module bundle (see table below).                                                                                                                    |
| `/init-project --enterprise`    | Core + `team` + `enterprise` module bundles.                                                                                                                      |
| `/init-project --squad`         | Core + `squad` module: sets up a 4-agent dev team (coder, QA, reviewer, architect) with coordination rules, in one shot. Combinable with `--team`/`--enterprise`. |
| `/init-project add <module>`    | Adds one specific module to an already-initialized repo, no re-interview.                                                                                         |
| `/init-project remove <module>` | Deletes that module's files after confirming with the user.                                                                                                       |
| `/init-project list-modules`    | Lists all modules, what's already installed, what's not.                                                                                                          |
| `/init-project help [keyword]`  | Lists every command in this skill with a one-line description. With a keyword, filters to commands/flags/modules whose name or description matches it.            |

`add`/`remove`/`list-modules` work on a repo that already has `docs/prd.md` — they don't re-run the interview, they just read the existing PRD/architecture for context and generate the new module's files.

## Help command

`/init-project help` prints this table, verbatim, in chat — don't paraphrase or shorten the descriptions, the whole point is a complete, accurate reference:

| Command                         | Description                                                                                                              |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `/init-project`                 | Start a fresh project: 10-question interview, generates the 6-file core scaffold.                                        |
| `/init-project --team`          | Core scaffold + team collaboration files (commit conventions, PR template, CODEOWNERS, onboarding, changelog).           |
| `/init-project --enterprise`    | Core + team + CI workflow, ADRs, security doc, stricter agent permissions.                                               |
| `/init-project --squad`         | Core + a 4-persona agent team (coder/qa/reviewer/architect) with real file-locking and task dispatch.                    |
| `/init-project add <module>`    | Add one module to a repo that's already initialized. See module list below.                                              |
| `/init-project remove <module>` | Remove a module's files, with confirmation first.                                                                        |
| `/init-project list-modules`    | Show which modules are installed vs. available for this repo.                                                            |
| `/init-project help [keyword]`  | Show this reference. Add a keyword (e.g. `help squad`, `help security`) to filter to matching commands and modules only. |

**Modules** (usable with `add`/`remove`, or bundled via the flags above): `runbook`, `commit`, `review`, `contributing`, `changelog`, `ci`, `adr`, `security`, `safety-rules`, `lint-config`, `agent-config`, `squad` — full one-line description for each is in the Modules table further down this file; `help <module-name>` should pull that specific row rather than the whole table.

**Keyword filter behavior**: match against command names, flags, module names, and description text (case-insensitive substring match). If nothing matches, say so plainly and show the full command table instead of returning empty — don't leave the user with nothing.

## Step 0 — Check for existing setup

Check if `docs/prd.md` exists.
- **Not present** → fresh init, go to Step 1.
- **Present** and command is `/init-project` (no flags) → this is likely an `add`/`list-modules` intent; ask which module, don't re-run the interview.
- Any command starting with `help` bypasses this check entirely — `help` never touches the repo or the interview, answer it immediately regardless of whether `docs/prd.md` exists.
- **Present** and user explicitly wants to redo everything → confirm before overwriting.

## Step 1 — Interview

**1a. Check for a saved experience-level profile first.** Look for `~/.groundwork/profile.md` (a file outside any repo, shared across all projects this skill sets up for this user). If it exists, read the `experience_level:` field and skip straight to 1c using that — don't ask again.

If it doesn't exist, ask once: *"Quick check — are you comfortable with dev terms like 'stack' and 'API', or should I explain things as we go?"* Then write the answer to `~/.groundwork/profile.md`:
```
experience_level: coder | non-coder
```
so every future `/init-project` run (any project, any repo) uses it automatically without re-asking. If the person's phrasing already makes this obvious (heavy jargon vs. plain language), you can infer it and just confirm in one line rather than asking outright — but still save it.

**1b. Branch on that profile:**
- **coder** → batch all questions below into one message, answer together, don't wait between each.
- **non-coder** → ask **one question at a time**, and for anything technical (stack, database, hosting), **proactively suggest a specific default based on their app idea** rather than just explaining the concept and waiting — e.g. "For a recipe app like this, I'd suggest Node.js with Express and a Postgres database — solid, well-documented default. Want me to go with that, or do you have something else in mind?" Only fall back to open-ended explanation if they push back on the suggestion.

**1c. Questions** (all required — don't skip "out of scope," it's what keeps the project from drifting later):

1. **App name** — what do you want to call it?
2. **Purpose** — one line: what does it do / what problem does it solve? *(stored as `purpose:<short>` in the PRD)*
3. **Target audience** — who is this for? *(stored as `target_audience:<short>` in the PRD — this sets the project's context, so keep it specific: not "everyone," but "who specifically.")*
4. **Tech stack** — language and framework together as one answer (e.g. "Node.js + Express", "Python + Django", "Next.js"). Don't ask these as two separate questions — most people think of them as one choice. Non-coder: suggest one outright per 1b.
5. **Database** — where the app's data lives. Non-coder: suggest one outright per 1b.
6. **Authentication** — does this need user login/accounts? If yes, how (email/password, Google/social login, none for now)?
7. **Hosting** — where will this run when live (e.g. Vercel, Railway, AWS)? "Not sure yet" is a valid answer — note it as undecided rather than blocking.
8. **APIs / integrations** — any third-party services this needs to talk to (payments, maps, email, etc.), or none for MVP?
9. **Top 3 MVP features, in priority order** — not a full feature list; exactly the top 3 that define a shippable v1. If they give more than 3, ask them to rank and cut to 3.
10. **Out of scope for v1** — what are you deliberately *not* building yet? If they're unsure, suggest inferring the obvious ones from what they excluded in Q9 and confirm.
11. **Agentic squad or solo agent?** — *"Would you like a single AI agent helping you build this, or an agentic squad — multiple specialised AI agents running in parallel roles (a Coder, a QA agent, a Reviewer, and an Architect) that divide work, gate each other's output, and avoid file conflicts?"* Non-coder framing: *"Think of it like having one smart assistant vs. a small AI team where each member has a defined job and double-checks the others. More powerful, but also more moving parts — solo is simpler to start."* If they choose squad, treat this as equivalent to passing `--squad` (no separate flag needed). If unsure, default to solo and mention `/init-project add squad` at the end.

Infer from existing files (package.json, README) instead of re-asking when the answer is already visible. If the command included `--team` or `--enterprise`, also confirm: team size/structure (for CODEOWNERS) and whether CI is GitHub Actions, GitLab CI, or other — otherwise default to GitHub Actions. If `--squad` is included (via flag **or** via Q11 answer), no extra questions needed — the 4 personas are fixed (see `squad` module below); just confirm the human wants all 4 or a subset.

**Post-interview branch on Q11:**
- **Solo** → generate core module only (or core + whatever other flags were passed).
- **Agentic squad** → automatically include the `squad` module in this run (same as `--squad`). Also suggest adding `--team` if not already requested, since an agentic squad benefits from commit conventions and a shared changelog — don't block on it, just note it.
- **Unsure/skip** → default to solo; call out `/init-project add squad` in the Step 5 report-back.

## Core module (always generated)

```
docs/
  prd.md
  task-tracker.md
  architecture.md        # includes ASCII dir tree — no separate repo_map.txt
  testing-playbook.md
.agents/
  permissions.json       # allowlist model
.env.template
AGENTS.md                # enforcement loop block
```

Generate each from its `references/*.template.md` file, filling `{{placeholders}}` from interview answers. This set is deliberately small. In `prd.md`, fill the `purpose:` and `target_audience:` tag lines verbatim (short form) from Q2/Q3 — they set the project's context at a glance, above the fold.

**Why these six**: `prd`+`task-tracker`+`architecture` are what an agent actually needs to consult before writing code. `testing-playbook` is what makes "done" mean something. `permissions.json` is the actual safety mechanism. `.env.template` is cheap insurance against leaked secrets. Everything else is situational — hence modules below.

## Modules (opt-in, `add <module>` or via `--team`/`--enterprise`)

| Module         | Files added                                                                                                                                                                                                                  | For                                                                 |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `runbook`      | `docs/runbook.md`                                                                                                                                                                                                            | Anyone deploying somewhere, not just running locally                |
| `commit`       | `docs/commit.md`                                                                                                                                                                                                             | Teams wanting enforced commit/branch conventions                    |
| `review`       | `.github/PULL_REQUEST_TEMPLATE.md`, `CODEOWNERS`                                                                                                                                                                             | Teams doing code review                                             |
| `contributing` | `CONTRIBUTING.md`, `docs/onboarding.md`                                                                                                                                                                                      | Multi-person teams, new-hire ramp-up                                |
| `changelog`    | `docs/changelog-agent.md`                                                                                                                                                                                                    | Anyone wanting an append-only audit trail of agent changes          |
| `ci`           | `.github/workflows/ci.yml`                                                                                                                                                                                                   | Teams — auto-run tests+lint on PR                                   |
| `adr`          | `docs/adr/0001-record-architecture-decisions.md`                                                                                                                                                                             | Larger projects — track *why*, not just *what*                      |
| `security`     | `docs/security.md`                                                                                                                                                                                                           | Regulated/production projects — threat model, disclosure policy     |
| `safety-rules` | `.config/ai/safety-rules.md`                                                                                                                                                                                                 | Stricter agent guardrails beyond permissions.json                   |
| `lint-config`  | `.config/ai/lint-rules.json`                                                                                                                                                                                                 | Tool-agnostic style spec — usually redundant, ask before generating |
| `agent-config` | `.agents/config.json`                                                                                                                                                                                                        | Multiple agent personas/scopes working the same repo                |
| `squad`        | `.agents/config.json` (4 personas), `.agents/coordination.md`, `.agents/claims/.gitkeep`, `scripts/claim.sh`, `scripts/release.sh`, `scripts/next_task.sh`, updates `task-tracker.md` to the machine-parseable status format | Running an actual multi-agent dev team, not just one agent          |

### Bundles
- `--team` = `runbook` + `commit` + `review` + `contributing` + `changelog`
- `--enterprise` = everything in `--team` + `ci` + `adr` + `security` + `safety-rules` + `agent-config`
- `--squad` = `agent-config` (superseded by squad's 4-persona version) + `squad`. Auto-includes `changelog` (agents need a shared history) — add `--team`/`--enterprise` alongside it for the rest.

`lint-config` is never auto-bundled — usually redundant with native linter configs (ESLint/ruff/etc). Only add it if the user asks specifically, and flag the duplication risk once before generating it.

## The `squad` module — multi-agent coordination

Sets up **4 fixed personas** working the same repo: `coder`, `qa`, `reviewer`, `architect`. This is the actual coordination layer, not just 4 named configs — without it, parallel agents step on each other's files and nobody knows who owns what.

**Personas and responsibilities:**
- **coder** — implements task-tracker items, writes unit tests. Can edit `src/`, cannot edit `docs/architecture.md` directly (proposes changes, architect merges).
- **qa** — writes/runs additional test cases against `docs/prd.md` acceptance criteria, files bugs as new task-tracker sub-items tagged `bug: <origin item>`. Read-only on `src/`, write on `tests/` and `docs/task-tracker.md`.
- **reviewer** — read-only everywhere. Approves or requests changes before an item moves to Completed. Checks against `.config/ai/safety-rules.md` and `docs/architecture.md`.
- **architect** — only persona allowed to edit `docs/architecture.md` and `docs/adr/` directly. Reviews coder's proposed architecture changes, keeps the dir tree/schema docs current.

**Task-tracker item lifecycle** (this is what makes 4 agents not collide):
`Backlog → Claimed → In Progress → Ready for QA → In QA → Ready for Review → In Review → Completed`

**Real locking, not just a markdown row.** `scripts/claim.sh` uses `mkdir` as an atomic OS-level lock — if two agents race to claim the same file, exactly one wins; the other gets a BLOCKED exit code with the owner and lock age. Claims are all-or-nothing per call (if any requested file is blocked, none are claimed). Locks older than 2 hours are treated as abandoned and auto-cleared, so a crashed agent doesn't deadlock the repo forever.

**Pull-based dispatch.** Instead of a human manually saying "QA go now," each persona runs `scripts/next_task.sh <persona>` to pull its next eligible item based on the item's `status:` field in `docs/task-tracker.md`. There's still no scheduler forcing anyone to run this — it's a queue you pull from, not a queue that pushes to you. If you're running the 4 personas as unattended parallel processes, something still has to periodically invoke each one; this setup doesn't provide that trigger.

**Workflow**: `next_task.sh` → `claim.sh` → do the work → `release.sh` (auto-logs a handoff row) → update the item's status field. Full mechanics in `references/coordination.template.md`.

**Honest limits**: this closes file-level race conditions and stale-lock deadlocks. It does **not** provide a process scheduler (something has to invoke each persona's turn) and does **not** prevent git merge conflicts from two personas editing adjacent lines in a shared file they each legitimately claimed at different times.

**Fewer than 4 personas**: drop `reviewer` first, then fold `architect` into `coder` for small repos — never drop `qa` silently, ask explicitly first.

## Step 3 — Inject the enforcement loop

Append (don't overwrite) `references/enforcement-block.template.md` to `AGENTS.md` (or `.cursorrules`/`.claudecoderc` if the repo already uses one instead — check in that order). If `ci` module is installed, note in the block that CI is the final gate, not a substitute for local test runs.

## Step 4 — Permissions model (allowlist, not blacklist)

`.agents/permissions.json` whitelists explicit safe commands; everything else needs human confirmation. Never a blacklist. When `enterprise` bundle is active, tighten further: no `git push` to any branch without confirmation (not just main), and confirmation required for any new dependency install.

## Step 5 — Report back

List files created/added this run, and for a fresh init, the enforcement rule now active: read `prd.md`+`architecture.md`+`task-tracker.md` before coding, update `task-tracker.md` (+`changelog-agent.md` if installed) after.

## Existing project (update mode)

Read existing docs, diff against current repo state, propose specific edits. Never silently overwrite PRD scope decisions — flag conflicts.

## Reference files

- `references/prd.template.md`, `architecture.template.md`, `task-tracker.template.md`, `testing-playbook.template.md`, `permissions.template.md`, `enforcement-block.template.md` — core
- `references/runbook.template.md`, `commit.template.md`, `pr-template.template.md`, `codeowners.template.md`, `contributing.template.md`, `onboarding.template.md`, `changelog.template.md` — team module
- `references/ci.template.md`, `adr.template.md`, `security.template.md`, `safety-rules.template.md`, `agent-config.template.md` — enterprise module
- `references/coordination.template.md`, `agent-config-squad.template.md` — squad module
- `scripts/claim.sh`, `scripts/release.sh`, `scripts/next_task.sh` — squad module locking + dispatch (copied into the target repo's `scripts/`, not just referenced)
- `scripts/generate_repo_map.sh` — optional, only for very large monorepos where the inline tree isn't enough
