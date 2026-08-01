# Commit & Branch Conventions

## Commit format (Conventional Commits)
```
<type>(<scope>): <short summary>

<optional body>
```
Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`.

Example: `feat(auth): add magic-link login`

## Branch naming
`<type>/<short-slug>` — e.g. `feat/magic-link-login`, `fix/null-user-crash`

## Rules for the agent
- One logical change per commit. Don't bundle unrelated file edits.
- Never commit directly to `main`/`master` — always via branch + PR, unless the human explicitly says otherwise for this repo.
- Commit message body explains *why*, not just *what* — the diff already shows what.
