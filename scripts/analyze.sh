#!/usr/bin/env bash
# Build GroundWork's machine-readable repository intelligence snapshot.
# Usage: ./scripts/analyze.sh [path]

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$ROOT/intelligence/analyze.py" "${1:-.}"
