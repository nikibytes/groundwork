# Testing Playbook — {{project_name}}

## How to run tests
```
{{test_command}}
```

## Before marking any task-tracker item Completed
1. Run `{{test_command}}` — must pass with zero failures.
2. Run `{{lint_command}}` if configured.
3. Manually verify the feature against its PRD acceptance line.
4. Update `docs/task-tracker.md` and `docs/changelog-agent.md` in the same commit.

## Adding new tests
Place new tests following the existing convention in {{test_dir}}. One test file per module/feature; name it after the module.

## What "done" means
A task is not Completed until it has a passing automated test. "It works when I tried it manually" is not sufficient for anything in the MVP scope.
