# Security — {{project_name}}

## Threat model (fill in as the project grows)
- What data does this handle? {{data_sensitivity}}
- Who can access it? {{access_model}}
- What's the worst-case breach scenario?

## Secrets handling
All secrets via `.env` (never committed). See `.env.template` for the required set.

## Dependency policy
{{dependency_update_policy}}

## Responsible disclosure
{{disclosure_contact_or_policy}}
<!-- Agent: use a role alias (e.g. security@domain) not a personal email/name if the user gives one — this file is often public. -->

## Agent rule
Never commit a real secret, never disable a security check to make a test pass, never weaken an auth check without explicit human confirmation. When logging a real incident here, reference the issue/ticket, don't paste raw logs or stack traces that may contain secrets or PII — redact first.
