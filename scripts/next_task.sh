#!/usr/bin/env bash
# Pull-based dispatcher: a persona asks "what's my next item?" instead of a
# human manually assigning it. Reads docs/task-tracker.md for lines in the
# format:
#   - [ ] <task text> — status: <Status> — claimed_by: <persona|none>
# and prints the first line whose status is eligible for the given persona.
# This does NOT replace claim.sh — it just tells you which item to claim
# next; you still call claim.sh with the actual files before editing.
#
# Usage: ./next_task.sh <persona>

set -euo pipefail
TRACKER="docs/task-tracker.md"

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <coder|qa|reviewer|architect>" >&2
  exit 2
fi

PERSONA="$1"

case "$PERSONA" in
  coder)     ELIGIBLE_STATUS="Backlog" ;;
  qa)        ELIGIBLE_STATUS="Ready for QA" ;;
  reviewer)  ELIGIBLE_STATUS="Ready for Review" ;;
  architect) ELIGIBLE_STATUS="Architecture Review Needed" ;;
  *) echo "Unknown persona: $PERSONA" >&2; exit 2 ;;
esac

if [ ! -f "$TRACKER" ]; then
  echo "No $TRACKER found." >&2
  exit 1
fi

match=$(grep -F "status: $ELIGIBLE_STATUS" "$TRACKER" | grep -F "claimed_by: none" | head -n 1 || true)

if [ -z "$match" ]; then
  echo "No eligible item for persona=$PERSONA (looking for status: $ELIGIBLE_STATUS, claimed_by: none)."
  exit 0
fi

echo "$match"
