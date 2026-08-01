Fill `.agents/config.json` for the `squad` module — this replaces the plain `agent-config` template when `squad` is active:

```json
{
  "personas": {
    "coder": {
      "scope": "write: src/, tests/ (own); propose-only: docs/architecture.md",
      "excludes": [".git/", "node_modules/", "*.env", "CODEOWNERS", "docs/adr/"]
    },
    "qa": {
      "scope": "write: tests/, docs/task-tracker.md (bug items only)",
      "excludes": [".git/", "node_modules/", "*.env", "src/ (read-only)"]
    },
    "reviewer": {
      "scope": "read-only, everything",
      "excludes": []
    },
    "architect": {
      "scope": "write: docs/architecture.md, docs/adr/",
      "excludes": [".git/", "node_modules/", "*.env"]
    }
  },
  "coordination_file": ".agents/coordination.md",
  "claim_required_before_edit": true,
  "default_persona": "coder"
}
```

Agent: never widen a persona's scope without explicit human confirmation. `claim_required_before_edit: true` means every persona must add a row to `.agents/coordination.md`'s Active Claims table before touching a file — this is not optional even for a "quick fix."
