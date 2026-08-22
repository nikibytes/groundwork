#!/usr/bin/env bash
# Rank eligible task-tracker work using project intelligence.
# Usage: ./scripts/planning.sh [path]
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$ROOT/intelligence/planning.py" "${1:-.}"
