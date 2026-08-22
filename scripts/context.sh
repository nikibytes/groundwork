#!/usr/bin/env bash
# Build relevant context for an engineering request.
# Usage: ./scripts/context.sh "fix the login bug" [repo]
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REQUEST="${1:?Usage: scripts/context.sh \"request\" [repo]}"
REPO="${2:-.}"
exec python3 "$ROOT/intelligence/context.py" "$REQUEST" --path "$REPO"
