---
name: groundwork
license: MIT
metadata:
  version: "1.0"
description: Bootstraps and plans coding projects with always-on repository intelligence. On the first GroundWork invocation, show the concise welcome choice before initializing anything. Trigger this whenever the user runs /init-project, /bootstrap, /init-project help, or asks to set up a project, plan an application, or similar. Guided planning is opt-in via `/init-project --plan` or explicit planning intent. Do not automatically initialize a project merely because GroundWork was installed.
---

# Project Init

GroundWork has three default entry paths: project initialization, guided application planning, and capability exploration. Repository Intelligence is always active. Optional Team, Enterprise, and Squad capabilities may be recommended from context but require explicit user approval before activation.

## First-run onboarding — mandatory

On the first invocation of GroundWork, before running project initialization or planning, check whether the current GroundWork installation/session has completed onboarding.

If onboarding has not been completed:

1. Do **not** initialize, scaffold, overwrite, or start the planning workflow yet.
2. Show the concise welcome from `WELCOME.md` (or its equivalent content).
3. Ask the user to choose:
   - **1 — Initialize a project** → continue with normal `/init-project` flow.
   - **2 — Plan an application first** → route to the planning sub-skill.
   - **3 — Explore/add capabilities** → show available capabilities and ask what to activate.
4. If the user simply describes what they want to build, recommend the appropriate path and ask for confirmation before starting.
5. Only after the user chooses a path mark onboarding complete using the available first-run state mechanism (`scripts/first_run.py --complete` when installed/available).
6. On later invocations, do not show the welcome again unless the user explicitly asks to see it.

The onboarding choice must be a routing decision, not a project-generation action. Installation alone never starts `/init-project`.

## Commands

| Command | What it does |
| --- | --- |
| `/init-project` | Fresh project initialization; runs only after the user chooses initialization or explicitly invokes this command. |
| `/init-project --plan` | Opt-in gated application planning: discovery → PRD → personas → user flows → requirements → domain model → data flow → database schema, with explicit approval and locking at every stage. |
| `/init-project add <module>` | Adds a specific optional module after confirmation. |
| `/init-project remove <module>` | Removes an optional module after confirmation. |
| `/init-project list-modules` | Lists installed and available capabilities. |
| `/init-project help [keyword]` | Shows the relevant command/capability reference. |

## Step 0 — Existing setup and routing

After first-run onboarding has been completed:

- If the user explicitly invokes `/init-project --plan`, route directly to `skills/planning/SKILL.md`; do not run the normal one-shot interview.
- If the user explicitly asks to plan before implementation, route to the planning sub-skill.
- If the user explicitly invokes `/init-project`, run the normal initialization flow.
- If `docs/prd.md` already exists and the user invokes normal `/init-project`, treat it as an existing project and offer update/module mode rather than silently reinitializing.
- `help` bypasses project changes.

## Optional capability recommendations

Repository Intelligence is always active and must not be presented as an optional install choice.

Project Initialization and Guided Planning are default available workflows.

When context strongly indicates a fit, recommend but do not silently activate:

- **Team** — multiple human developers, shared ownership, code review, onboarding.
- **Enterprise** — regulated, security-sensitive, compliance-heavy, or larger organizational context.
- **Squad** — multiple specialized AI agents or an explicit request for parallel Coder/QA/Reviewer/Architect roles.

Ask for explicit confirmation before activating any of these optional capabilities.

## Normal initialization

When initialization is selected, use the existing interview, profile, scaffold, module, enforcement, permission, and report-back rules below. Do not enter guided planning unless the user selected it.

## Existing setup

Check if `docs/prd.md` exists before a normal fresh initialization. Never silently overwrite an existing project.

## Reference

- `WELCOME.md` — first-run welcome text.
- `skills/planning/SKILL.md` — opt-in gated planning sub-skill.
- `scripts/first_run.py` — deterministic first-run marker.

## Existing initialization behavior

The remainder of this file preserves the existing GroundWork initialization/module behavior: use the saved experience profile when available; interview coders in batches and non-coders one question at a time with useful defaults; collect app name, purpose, audience, stack, database, authentication, hosting, integrations, MVP features, out-of-scope items and squad preference; generate the core scaffold and selected modules; inject enforcement; use allowlisted permissions; and report exactly what was created. Never silently overwrite existing planning or product decisions.
