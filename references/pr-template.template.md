Place at `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## What changed
{{summary}}

## Related task-tracker item
- [ ] Links to docs/task-tracker.md item: ____

## Checklist
- [ ] Tests pass ({{test_command}})
- [ ] docs/architecture.md updated if a module/schema/dependency changed
- [ ] docs/changelog-agent.md entry added (if module installed)
- [ ] No secrets committed
```
