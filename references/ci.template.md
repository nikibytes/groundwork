Place at `.github/workflows/ci.yml` (adapt runner/commands to stack):

```yaml
name: CI
on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup
        run: {{setup_command}}
      - name: Lint
        run: {{lint_command}}
      - name: Test
        run: {{test_command}}
```

Agent: CI passing is a gate for merge, not a substitute for running tests locally before opening the PR.
