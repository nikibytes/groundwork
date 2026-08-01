Fill `.agents/config.json` — used when multiple agent personas/tools work the same repo (e.g. a reviewer agent + a coding agent):

```json
{
  "personas": {
    "coder": {
      "scope": "src/, docs/task-tracker.md (write)",
      "excludes": [".git/", "node_modules/", "*.env", "CODEOWNERS"]
    },
    "reviewer": {
      "scope": "read-only, everything",
      "excludes": []
    }
  },
  "default_persona": "coder"
}
```

Agent: never widen a persona's scope without explicit human confirmation.
