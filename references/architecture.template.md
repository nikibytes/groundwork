# Architecture — {{project_name}}

## Data Flow (high level)
{{data_flow_summary}}

## Directory Map
```
{{ascii_tree}}
```

## Schemas
{{schema_notes}}
<!-- Agent: reference the actual schema/migration/model file paths here (e.g. "user schema: src/models/user.py") — don't reproduce full field lists that already live in those files. Only add what isn't obvious from the file itself: intent, relationships, why a field exists. -->

## Key Modules
| Module | Path | Responsibility |
|--------|------|-----------------|
| {{module_1}} | {{path_1}} | {{responsibility_1}} |

## External Dependencies
{{integrations}}

## Update Rule
This file is updated by the agent whenever a new module, schema, or external dependency is added — same commit as the code change, never deferred.
