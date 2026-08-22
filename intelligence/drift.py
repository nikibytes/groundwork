#!/usr/bin/env python3
"""Detect deterministic gaps between PRD intent and observed repository state."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TEST_RE = re.compile(r"(^|/)(test|tests|spec|specs)(/|$)|(_test|\\.test|\\.spec)", re.I)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def detect(root: Path) -> dict:
    intelligence = root / ".groundwork"
    feature_path = intelligence / "feature-map.json"
    repo_path = intelligence / "repo-map.json"
    graph_path = intelligence / "dependency-graph.json"
    if not feature_path.exists():
        raise SystemExit(".groundwork/feature-map.json not found; run scripts/analyze.sh first")

    feature_map = load(feature_path)
    repo_map = load(repo_path) if repo_path.exists() else {"files": []}
    graph = load(graph_path) if graph_path.exists() else {"nodes": [], "edges": []}
    findings: list[dict] = []

    for req in feature_map.get("requirements", []):
        if not req.get("implementation_files"):
            findings.append({
                "type": "MISSING",
                "severity": "high",
                "requirement": req["id"],
                "title": req["title"],
                "message": "No implementation file was deterministically mapped to this PRD requirement.",
                "source": req.get("source"),
            })
        if req.get("implementation_files") and not req.get("test_files"):
            findings.append({
                "type": "UNTESTED",
                "severity": "medium",
                "requirement": req["id"],
                "title": req["title"],
                "message": "Implementation candidates exist, but no test file was mapped to the requirement.",
                "source": req.get("source"),
            })

    # Surface suspiciously isolated implementation files: application source that has no
    # imports in either direction is useful drift signal, but only for files outside docs/tests/scripts.
    incoming = {edge["to"] for edge in graph.get("edges", [])}
    outgoing = {edge["from"] for edge in graph.get("edges", [])}
    for item in repo_map.get("files", []):
        path = item["path"]
        if TEST_RE.search(path) or path.startswith(("docs/", "scripts/", ".github/", ".agents/")):
            continue
        if item.get("language") and path not in incoming and path not in outgoing:
            findings.append({
                "type": "ORPHANED",
                "severity": "low",
                "path": path,
                "message": "Source file has no detected local import relationships.",
            })

    counts = {}
    for finding in findings:
        counts[finding["type"]] = counts.get(finding["type"], 0) + 1
    return {
        "schema_version": "0.1",
        "findings": findings,
        "counts": counts,
        "status": "drift" if findings else "clean",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect GroundWork project drift.")
    parser.add_argument("path", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.path).resolve()
    result = detect(root)
    out = root / ".groundwork" / "drift.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"GroundWork drift status: {result['status']}")
    for kind, count in sorted(result["counts"].items()):
        print(f"  {kind}: {count}")
    print(f"  Output: {out}")
    return 1 if result["status"] == "drift" else 0


if __name__ == "__main__":
    raise SystemExit(main())
