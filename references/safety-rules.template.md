# AI Safety Rules — {{project_name}}

These are absolute, non-negotiable for any agent working in this repo.

1. Never hardcode secrets, API keys, or credentials in source. Use `.env` + `.env.template`.
2. Never run a command outside `.agents/permissions.json`'s allowlist without explicit human confirmation for that specific command.
3. Never force-push, never rewrite git history on a shared branch.
4. Never delete a file outside `.agents/scratchpad/` without explicit confirmation.
5. Never edit `docs/prd.md`'s "Out of Scope" section to justify scope creep — flag the conflict to the human instead.
6. Never modify `.agents/permissions.json` or `.config/ai/safety-rules.md` itself without explicit human confirmation.
7. If a task requires a command not on the allowlist, stop and ask — do not improvise an equivalent.
8. Never duplicate content already captured in a spec, ADR, PR, commit, or diff — reference it by path/URL/hash instead of restating it in a doc.
9. Redact real API keys, passwords, tokens, and PII from any file before writing — including changelog entries, coordination notes, and error/log excerpts — not just `.env`.
