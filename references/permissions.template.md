Fill `.agents/permissions.json` using this shape. This is an ALLOWLIST — anything not listed requires explicit human confirmation before execution. Do not add a "blacklist" section; blacklists are bypassable, allowlists aren't.

```json
{
  "allowlist": {
    "test": ["{{test_command}}"],
    "lint": ["{{lint_command}}"],
    "package_manager": ["{{pkg_install_cmd}}", "{{pkg_add_cmd}}"],
    "git_readonly": ["git status", "git diff", "git log"],
    "git_write_nonmain": ["git add", "git commit", "git checkout -b *"],
    "build": ["{{build_command}}"]
  },
  "requires_confirmation": "anything not in allowlist, including: git push, git push --force, rm, database migrations that drop/alter data, editing .env, editing .agents/ or .config/ai/",
  "never_allowed": [
    "commands that exfiltrate .env or secret files",
    "git push --force to main/master",
    "rm -rf outside .agents/scratchpad/"
  ]
}
```

Fill `{{...}}` per the chosen stack, e.g. Node → `npm test`, `npm run lint`, `npm install`, `npm install <pkg>`, `npm run build`. Python → `pytest`, `ruff check .`, `pip install -r requirements.txt`, `pip install <pkg>`, none/`python -m build`.
