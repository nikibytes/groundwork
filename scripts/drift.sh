#!/usr/bin/env bash
# Detect drift between PRD requirements and observed repository state.
# Usage: ./scripts/drift.sh [path]

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$ROOT/intelligence/drift.py" "${1:-.}"
