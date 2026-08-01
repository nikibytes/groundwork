# GroundWork

Bootstrap a fully documented, agent-safe coding project with one command. Five minutes of questions instead of hours of writing (or forgetting to write) a PRD, architecture doc, and task tracker by hand.

```
/init-project
```

That's it. Answer a few questions about what you're building, and your repo gets a working scaffold — plus a rule injected into your agent config so every future change stays consistent with the docs, instead of drifting the moment you stop paying attention.

## Install

```bash
npx skills add nikibytes/groundwork
```

No npm publish needed — [`skills`](https://github.com/vercel-labs/agent-skills) uses GitHub as its registry. It detects your installed agent (Claude Code, Cursor, etc.) and copies the skill into the right place automatically.

## Quick start

| Command | What you get |
|---|---|
| `/init-project` | Core scaffold — 6 files, solo/MVP default |
| `/init-project --team` | + code review, CI-friendly commit conventions, onboarding docs |
| `/init-project --enterprise` | + ADRs, security doc, CI workflow, stricter permissions |
| `/init-project --squad` | + a 4-agent dev team (coder/QA/reviewer/architect) with real file locking |
| `/init-project add <module>` | Add one module to an already-initialized repo |
| `/init-project list-modules` | See what's installed, what's not |
| `/init-project help [keyword]` | Full command reference; filter with a keyword, e.g. `help squad` |

## What it asks

One short interview, then it generates everything. If you're not a coder, it explains concepts in plain language and suggests sensible defaults instead of leaving you to guess — and it only asks whether you're a coder or not **once**, ever; the answer is saved to `~/.groundwork/profile.md` and reused for every project you init after that.

- App name, one-line purpose, and target audience — these set the project's context up front
- Tech stack (language + framework, asked as one thing — nobody thinks of these separately)
- Database, auth, hosting, integrations
- Top 3 MVP features, in priority order
- What's explicitly *out* of scope for v1 — this is what keeps the project from drifting later, not filler

## Core scaffold (always generated)

```
docs/
  prd.md               # the source of truth for scope
  task-tracker.md       # backlog → in progress → completed
  architecture.md       # directory map, schemas (by reference, not duplicated)
  testing-playbook.md   # what "done" means
.agents/
  permissions.json      # allowlist model — not a blacklist, those are bypassable
.env.template
AGENTS.md                # the enforcement loop, injected into your agent's config
```

Deliberately small. Everything else is a module you opt into — see the table below.

## Modules

| Module | Adds | For |
|---|---|---|
| `runbook` | `docs/runbook.md` | Deploying somewhere, not just running locally |
| `commit` | `docs/commit.md` | Enforced commit/branch conventions |
| `review` | PR template, `CODEOWNERS` | Code review |
| `contributing` | `CONTRIBUTING.md`, `docs/onboarding.md` | Multi-person teams |
| `changelog` | `docs/changelog-agent.md` | Append-only audit trail of agent changes |
| `ci` | `.github/workflows/ci.yml` | Auto-run tests + lint on PR |
| `adr` | `docs/adr/` | Track *why* decisions were made, not just what the code does |
| `security` | `docs/security.md` | Threat model, disclosure policy |
| `safety-rules` | `.config/ai/safety-rules.md` | Stricter agent guardrails |
| `agent-config` | `.agents/config.json` | Multiple agent personas in one repo |
| `squad` | 4-persona config, real file locking, pull-based task dispatch | An actual multi-agent dev team |

`--team` bundles `runbook` + `commit` + `review` + `contributing` + `changelog`. `--enterprise` adds `ci` + `adr` + `security` + `safety-rules` + `agent-config` on top.

## The squad module

Sets up four fixed personas sharing one repo — `coder`, `qa`, `reviewer`, `architect` — each with a defined scope and a real coordination layer, not just a markdown row someone might race past:

- **`scripts/claim.sh`** — atomic `mkdir`-based file locking. Two agents racing for the same file: exactly one wins, the other gets blocked with the owner's name and how long they've held it.
- **`scripts/release.sh`** — frees the lock, auto-logs a handoff note.
- **`scripts/next_task.sh`** — pull-based dispatch; each persona asks for its next eligible item instead of waiting to be told.

Stale locks (>2 hours, e.g. from a crashed session) auto-clear so nobody gets permanently blocked. What this **doesn't** do: force any agent to take its turn (something still has to invoke each persona) or prevent git merge conflicts between two legitimately-claimed edits. It closes the race condition, not the whole orchestration problem.

## Documentation discipline

Baked into the core enforcement loop, not an afterthought:

- **Reference, don't duplicate.** A doc points at a spec, ADR, commit, or PR instead of restating it — one source of truth instead of N stale copies.
- **Redact before writing.** Real API keys, passwords, tokens, and PII get stripped before anything lands in a changelog, coordination note, or doc — not just `.env`.

## Update mode

Running the command again on a repo that already has `docs/prd.md` won't silently overwrite it. You'll be asked whether to regenerate, update in place (diff-based), or cancel.

## Honest limits

- Enforcement (permissions, safety rules, the docs-first loop) is advisory — it works because the agent reading `SKILL.md` chooses to follow it, not because anything blocks it mechanically. The one exception is squad's file locks, which are real.
- `.agents/permissions.json` and `.agents/config.json` are this skill's own conventions, not something Claude Code or Cursor read natively. For platform-native enforcement, pair this with `.claude/settings.json` permissions or `.cursor/rules/*.mdc`.

## License

MIT
