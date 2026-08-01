#!/usr/bin/env bash
# Releases claims taken by claim.sh and appends a handoff line to
# .agents/coordination.md so there's a human-readable trail alongside
# the machine-enforced locks.
#
# Usage: ./release.sh <persona> <task-item-id> <note> <file1> [file2 ...]

set -euo pipefail
LOCK_DIR=".agents/claims"
COORD_FILE=".agents/coordination.md"

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'EOF'
Usage: ./release.sh <persona> <task-item-id> <note> <file1> [file2 ...]

Releases file claims created by claim.sh and appends a handoff line to
.agents/coordination.md for a human-readable audit trail.

Arguments:
  persona        The persona releasing the files (must match original claimer)
  task-item-id   The task tracker item ID
  note           Short handoff note (e.g. "done", "ready for QA", "blocked on design")
  file1 ...      One or more file paths to release

Options:
  --help, -h     Show this help and exit

Exit codes:
  0  Files released (or a warning printed if persona mismatch)
  2  Bad usage / missing arguments

Side effects:
  Appends a row to .agents/coordination.md:
    | <task-item-id> | <persona> | <note> |

Example:
  ./release.sh coder task-001 "implementation done" src/auth.ts src/auth.test.ts
EOF
  exit 0
fi

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
