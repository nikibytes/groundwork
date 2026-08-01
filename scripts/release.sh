#!/usr/bin/env bash
# Releases claims taken by claim.sh and appends a handoff line to
# .agents/coordination.md so there's a human-readable trail alongside
# the machine-enforced locks.
#
# Usage: ./release.sh <persona> <task-item-id> <note> <file1> [file2 ...]

set -euo pipefail
LOCK_DIR=".agents/claims"
COORD_FILE=".agents/coordination.md"

if [ "$#" -lt 4 ]; then
  echo "Usage: $0 <persona> <task-item-id> <note> <file1> [file2 ...]" >&2
  exit 2
fi

PERSONA="$1"; ITEM="$2"; NOTE="$3"; shift 3
FILES=("$@")

slug() { echo "$1" | tr '/ ' '__'; }

for f in "${FILES[@]}"; do
  lock="$LOCK_DIR/$(slug "$f").lock"
  if [ -d "$lock" ]; then
    owner=$(grep '^persona=' "$lock/meta" 2>/dev/null | cut -d= -f2- || echo "")
    if [ "$owner" != "$PERSONA" ]; then
      echo "WARNING: $f is claimed by '$owner', not '$PERSONA' — not releasing. Ask the human." >&2
      continue
    fi
    rm -rf "$lock"
  fi
done

if [ -f "$COORD_FILE" ]; then
  printf '| %s | %s | %s |\n' "$ITEM" "$PERSONA" "$NOTE" >> "$COORD_FILE"
fi

echo "Released ${#FILES[@]} file(s) for persona=$PERSONA item=$ITEM."
