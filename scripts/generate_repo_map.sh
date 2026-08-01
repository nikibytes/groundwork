#!/usr/bin/env bash
# Regenerates repo_map.txt: one line per tracked file/dir with a placeholder
# description the agent should fill in with a real one-sentence purpose.
# Usage: ./generate_repo_map.sh > repo_map.txt

set -euo pipefail

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'EOF'
Usage: ./generate_repo_map.sh > repo_map.txt

Generates a repo map listing every tracked file with a <TODO> placeholder
description. Redirect stdout to repo_map.txt; the agent should then replace
each <TODO> with a real one-sentence purpose for that file.

Options:
  --help, -h    Show this help and exit

Output format (stdout):
  # repo_map.txt — auto-generated <date>. Agent: replace <TODO> with real one-line descriptions.
  <filepath padded to 50 chars>   <TODO: one-sentence purpose>

Behavior:
  - In a git repo: lists all git-tracked files (git ls-files)
  - Outside a git repo: lists all files excluding node_modules/ and .git/

Example:
  ./generate_repo_map.sh > docs/repo_map.txt
EOF
  exit 0
fi

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  FILES=$(git ls-files)
else
  FILES=$(find . -type f -not -path '*/node_modules/*' -not -path '*/.git/*')
fi

echo "# repo_map.txt — auto-generated $(date +%Y-%m-%d). Agent: replace <TODO> with real one-line descriptions."
echo "$FILES" | sort | while read -r f; do
  printf '%-50s <TODO: one-sentence purpose>\n' "$f"
done
