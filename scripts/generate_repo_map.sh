#!/usr/bin/env bash
# Regenerates repo_map.txt: one line per tracked file/dir with a placeholder
# description the agent should fill in with a real one-sentence purpose.
# Usage: ./generate_repo_map.sh > repo_map.txt

set -euo pipefail

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  FILES=$(git ls-files)
else
  FILES=$(find . -type f -not -path '*/node_modules/*' -not -path '*/.git/*')
fi

echo "# repo_map.txt — auto-generated $(date +%Y-%m-%d). Agent: replace <TODO> with real one-line descriptions."
echo "$FILES" | sort | while read -r f; do
  printf '%-50s <TODO: one-sentence purpose>\n' "$f"
done
