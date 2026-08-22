#!/usr/bin/env bash
# Analyze the likely impact of changing a repository file.
# Usage: ./scripts/impact.sh <file> [repo]
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FILE="${1:?Usage: scripts/impact.sh <file> [repo]}"
REPO="${2:-.}"
exec python3 "$ROOT/intelligence/impact.py" "$FILE" --path "$REPO"
