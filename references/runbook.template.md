# Runbook — {{project_name}}

## Local Setup
```
{{setup_commands}}
```

## Environment Variables
See `.env.template` for the full list. Copy to `.env` and fill in real values — never commit `.env`.

## Database / Migrations
{{migration_commands}}

## Local Run
```
{{run_command}}
```

## Deploy
Target: {{stack_deploy}}
{{deploy_notes}}

## Troubleshooting
(Agent: append entries here as real issues get resolved, in the form "Symptom → Cause → Fix".)
