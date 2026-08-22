#!/usr/bin/env python3
"""Explain the likely impact of changing a repository file."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

TEST_RE = re.compile(r"(^|/)(test|tests|spec|specs)(/|$)|(_test|\\.test|\\.spec)", re.I)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=True).stdout.strip()


def analyze(root: Path, changed: str) -> dict:
    out = root / ".groundwork"
    graph = load(out / "dependency-graph.json")
    features = load(out / "feature-map.json")
    edges = graph.get("edges", [])
    changed = changed.replace("\\", "/").lstrip("./")

    # Walk reverse dependencies: if A imports B, changing B can affect A.
    reverse: dict[str, set[str]] = {}
    for edge in edges:
        reverse.setdefault(edge["to"], set()).add(edge["from"])
    affected_files: set[str] = set()
    queue = [changed]
    while queue:
        current = queue.pop()
        for parent in reverse.get(current, set()):
            if parent not in affected_files:
                affected_files.add(parent)
                queue.append(parent)

    affected_files.discard(changed)
    requirements = []
    tests = set()
    for req in features.get("requirements", []):
        implementation = {x["path"] for x in req.get("implementation_files", [])}
        test_files = {x["path"] for x in req.get("test_files", [])}
        if changed in implementation or implementation & affected_files:
            requirements.append({"id": req["id"], "title": req["title"], "status": req.get("status")})
            tests.update(test_files)

    affected_tests = sorted(tests | {f for f in affected_files if TEST_RE.search(f)})
    affected_non_tests = sorted(f for f in affected_files if not TEST_RE.search(f))
    score = min(100, 30 + len(affected_non_tests) * 10 + len(requirements) * 15 + len(affected_tests) * 5)
    risk = "high" if score >= 75 else "medium" if score >= 50 else "low"

    try:
        commit = git(root, "rev-parse", "HEAD")
    except (subprocess.CalledProcessError, FileNotFoundError):
        commit = None
    return {
        "schema_version": "0.1",
        "commit": commit,
        "changed_file": changed,
        "affected_files": affected_non_tests,
        "affected_requirements": requirements,
        "affected_tests": affected_tests,
        "impact_score": score,
        "risk": risk,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze the impact of changing a repository file.")
    parser.add_argument("file", help="Repository-relative file path")
    parser.add_argument("--path", default=".", help="Repository path")
    args = parser.parse_args()
    root = Path(args.path).resolve()
    result = analyze(root, args.file)
    out = root / ".groundwork" / "impact.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"GroundWork change impact: {result['risk'].upper()}")
    print(f"  Changed: {result['changed_file']}")
    print(f"  Affected files: {len(result['affected_files'])}")
    print(f"  Requirements: {len(result['affected_requirements'])}")
    print(f"  Tests: {len(result['affected_tests'])}")
    print(f"  Score: {result['impact_score']}/100")
    print(f"  Output: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
