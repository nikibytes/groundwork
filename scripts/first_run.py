#!/usr/bin/env python3
"""Small deterministic first-run marker for GroundWork onboarding."""

from __future__ import annotations

import argparse
from pathlib import Path

MARKER = ".groundwork/onboarding-complete"

WELCOME = """# Welcome to GroundWork

Repository Intelligence is always active.

What would you like to do?

1. 🚀 Initialize a project
2. 🧭 Plan an application first
3. 🧩 Explore/add capabilities

You can also simply describe what you want to build. GroundWork will recommend the best path.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--complete", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    marker = root / MARKER
    if args.complete:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("completed\n", encoding="utf-8")
        return 0
    if marker.exists():
        return 0
    print(WELCOME)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
