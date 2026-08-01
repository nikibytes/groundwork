#!/usr/bin/env bash
# Atomic file claim for the squad module. Uses `mkdir` as the lock primitive
# (mkdir is atomic on every POSIX filesystem — two processes racing to mkdir
# the same path, exactly one wins). This is what makes claims real locks
# instead of just a markdown row someone might race past.
#
# Usage: ./claim.sh <persona> <task-item-id> <file1> [file2 ...]
# Exit 0  = all files claimed, safe to edit.
# Exit 1  = at least one file is locked by another persona (see stderr).
# Exit 2  = bad usage.

set -euo pipefail

STALE_LOCK_SECONDS=7200   # 2 hours — a claim older than this is treated as abandoned
LOCK_DIR=".agents/claims"

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'EOF'
Usage: ./claim.sh <persona> <task-item-id> <file1> [file2 ...]

Atomically claims one or more files for a persona using mkdir as a POSIX-safe
lock primitive. Claims are all-or-nothing: if any requested file is already
locked, none are claimed and existing claims are rolled back.

Arguments:
  persona        One of: coder, qa, reviewer, architect
  task-item-id   The task tracker item ID these files belong to
  file1 ...      One or more file paths to claim (relative to repo root)

Options:
  --help, -h     Show this help and exit

Exit codes:
  0  All files claimed successfully
  1  At least one file is locked by another persona (see stderr for details)
  2  Bad usage / missing arguments

Stale locks:
  Locks older than 2 hours are treated as abandoned and auto-cleared.

Example:
  ./claim.sh coder task-001 src/auth.ts src/auth.test.ts
EOF
  exit 0
fi

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <persona> <task-item-id> <file1> [file2 ...]" >&2
  exit 2
fi

PERSONA="$1"; ITEM="$2"; shift 2
FILES=("$@")
mkdir -p "$LOCK_DIR"

acquired=()
fail=0

slug() { echo "$1" | tr '/ ' '__'; }

for f in "${FILES[@]}"; do
  lock="$LOCK_DIR/$(slug "$f").lock"
  if mkdir "$lock" 2>/dev/null; then
    printf 'persona=%s\nitem=%s\nfile=%s\nclaimed_at=%s\n' \
      "$PERSONA" "$ITEM" "$f" "$(date -u +%FT%TZ)" > "$lock/meta"
    acquired+=("$f")
  else
    # Lock exists — check if it's stale
    meta="$lock/meta"
    if [ -f "$meta" ]; then
      claimed_at=$(grep '^claimed_at=' "$meta" | cut -d= -f2-)
      claimed_epoch=$(date -u -d "$claimed_at" +%s 2>/dev/null || echo 0)
      now_epoch=$(date -u +%s)
      age=$(( now_epoch - claimed_epoch ))
      if [ "$age" -gt "$STALE_LOCK_SECONDS" ]; then
        echo "STALE lock on $f (age ${age}s) — clearing and re-claiming." >&2
        rm -rf "$lock"
        mkdir "$lock"
        printf 'persona=%s\nitem=%s\nfile=%s\nclaimed_at=%s\n' \
          "$PERSONA" "$ITEM" "$f" "$(date -u +%FT%TZ)" > "$lock/meta"
        acquired+=("$f")
        continue
      fi
      owner=$(grep '^persona=' "$meta" | cut -d= -f2-)
      owner_item=$(grep '^item=' "$meta" | cut -d= -f2-)
      echo "BLOCKED: $f is claimed by persona=$owner for item=$owner_item (age ${age}s)." >&2
    else
      echo "BLOCKED: $f is locked (no metadata found)." >&2
    fi
    fail=1
  fi
done

if [ "$fail" -eq 1 ]; then
  # Roll back any locks we did manage to grab this call — all-or-nothing claim
  for f in "${acquired[@]}"; do
    rm -rf "$LOCK_DIR/$(slug "$f").lock"
  done
  echo "Claim failed — released the ${#acquired[@]} lock(s) acquired this call. Retry once unblocked, or ask the human to resolve." >&2
  exit 1
fi

echo "Claimed ${#FILES[@]} file(s) for persona=$PERSONA item=$ITEM."
exit 0
