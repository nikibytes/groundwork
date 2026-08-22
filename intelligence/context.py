#!/usr/bin/env python3
"""Build a compact, evidence-backed context package for an engineering request."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

STOP = {"the", "and", "for", "with", "from", "this", "that", "fix", "add", "make", "into", "can", "how", "bug"}
TOKEN_RE = re.compile(r"[A-Za-z0-9_./-]+")


def load(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def tokens(text: str) -> set[str]:
    return {x.lower() for x in TOKEN_RE.findall(text) if len(x) > 2 and x.lower() not in STOP}


def score_path(path: str, query: set[str]) -> int:
    parts = tokens(path.replace("/", " ").replace("_", " ").replace("-", " "))
    return len(parts & query) * 10


def build(root: Path, request: str, limit: int = 12) -> dict:
    gw = root / ".groundwork"
    project = load(gw / "project.json", {})
    repo = load(gw / "repo-map.json", {"files": []})
    feature = load(gw / "feature-map.json", {"requirements": []})
    drift = load(gw / "drift.json", {"findings": []})
    query = tokens(request)

    ranked_files = []
    for item in repo.get("files", []):
        path = item.get("path", "")
        score = score_path(path, query)
        if score:
            ranked_files.append((score, path, item))
    ranked_files.sort(key=lambda x: (-x[0], x[1]))

    requirements = []
    for req in feature.get("requirements", []):
        text = f"{req.get('title', '')} {req.get('description', '')}"
        score = len(tokens(text) & query)
        if score:
            requirements.append((score, req))
    requirements.sort(key=lambda x: (-x[0], x[1].get("id", "")))

    selected_requirements = [x[1] for x in requirements[:8]]
    selected_paths = {x[1] for x in ranked_files[:limit]}
    # Requirements provide stronger evidence than path-name matching alone.
    for req in selected_requirements:
        selected_paths.update(x["path"] for x in req.get("implementation_files", [])[:4])
        selected_paths.update(x["path"] for x in req.get("test_files", [])[:4])

    relevant_drift = []
    for finding in drift.get("findings", []):
        text = json.dumps(finding)
        if not query or tokens(text) & query:
            relevant_drift.append(finding)

    return {
        "schema_version": "0.1",
        "request": request,
        "project": {k: project.get(k) for k in ("name", "languages", "frameworks", "package_managers") if k in project},
        "requirements": selected_requirements,
        "files": sorted(selected_paths),
        "tests": sorted(p for p in selected_paths if re.search(r"(^|/)(test|tests|spec|specs)(/|$)|(_test|\\.test|\\.spec)", p, re.I)),
        "drift": relevant_drift[:12],
        "selection": {
            "method": "deterministic token/path matching plus existing feature-map evidence",
            "confidence": "candidate_context",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build relevant GroundWork context for an engineering request.")
    parser.add_argument("request")
    parser.add_argument("--path", default=".")
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()
    root = Path(args.path).resolve()
    result = build(root, args.request, max(1, args.limit))
    out = root / ".groundwork" / "context.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("GroundWork context")
    print(f"  Request: {result['request']}")
    print(f"  Requirements: {len(result['requirements'])}")
    print(f"  Files: {len(result['files'])}")
    print(f"  Tests: {len(result['tests'])}")
    print(f"  Drift findings: {len(result['drift'])}")
    print(f"  Output: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
