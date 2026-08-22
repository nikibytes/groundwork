#!/usr/bin/env python3
"""Rank eligible task-tracker work using GroundWork project intelligence."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TASK_RE = re.compile(r"^[-*]\s*(?:\[[^]]*\]\s*)?(?:(GW[-_ ]?\d+)\s*[-:]\s*)?(.+?)\s*$", re.I)
SECTION_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$")
STATUS_RE = re.compile(r"\b(backlog|ready|todo|blocked|in progress|ready for qa|ready for review|completed|done)\b", re.I)


def load(path: Path, default: dict) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def tokens(text: str) -> set[str]:
    return {x for x in re.findall(r"[a-z0-9]+", text.lower()) if len(x) > 2}


def parse_tasks(path: Path) -> list[dict]:
    tasks = []
    if not path.exists():
        return tasks
    section = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        heading = SECTION_RE.match(line)
        if heading:
            section = heading.group(1).strip()
            continue
        match = TASK_RE.match(line.strip())
        if not match:
            continue
        task_id, title = match.groups()
        status_match = STATUS_RE.search(section + " " + line)
        status = status_match.group(1).lower() if status_match else "backlog"
        if status in {"completed", "done"}:
            continue
        tasks.append({"id": task_id, "title": title.strip(), "status": status, "section": section})
    return tasks


def rank(root: Path) -> dict:
    intelligence = root / ".groundwork"
    features = load(intelligence / "feature-map.json", {"requirements": []})
    drift = load(intelligence / "drift.json", {"findings": []})
    graph = load(intelligence / "dependency-graph.json", {"edges": []})
    tasks = parse_tasks(root / "docs" / "task-tracker.md")

    drift_by_req = {}
    for finding in drift.get("findings", []):
        req = finding.get("requirement")
        if req:
            drift_by_req.setdefault(req, []).append(finding)

    scored = []
    for task in tasks:
        tt = tokens(task["title"])
        matched = []
        for req in features.get("requirements", []):
            rt = tokens(req.get("title", "")) | tokens(req.get("description", ""))
            overlap = len(tt & rt)
            if overlap:
                matched.append((overlap, req))
        matched.sort(key=lambda x: x[0], reverse=True)
        requirements = [req for _, req in matched[:3]]
        score = 20
        reasons = []
        if requirements:
            score += min(30, sum(x for x, _ in matched[:3]) * 8)
            reasons.append(f"matches {len(requirements)} PRD requirement(s)")
        affected_drift = [f for req in requirements for f in drift_by_req.get(req.get("id"), [])]
        if any(f.get("type") == "MISSING" for f in affected_drift):
            score += 25
            reasons.append("addresses a missing requirement")
        if any(f.get("type") == "UNTESTED" for f in affected_drift):
            score += 15
            reasons.append("addresses an untested requirement")
        # A task that explicitly mentions tests/bugs/risk is usually more urgent than ordinary work.
        if tt & {"bug", "fix", "security", "critical", "test", "tests"}:
            score += 10
            reasons.append("contains a high-signal maintenance/risk term")
        if "blocked" in task["status"]:
            score = 0
            reasons = ["blocked"]
        score = min(100, score)
        scored.append({
            **task,
            "priority_score": score,
            "matched_requirements": [{"id": r["id"], "title": r["title"]} for r in requirements],
            "reasons": reasons or ["eligible backlog work"],
        })

    scored.sort(key=lambda x: (-x["priority_score"], x["title"].lower()))
    return {"schema_version": "0.1", "tasks": scored, "recommended": scored[0] if scored else None}


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank GroundWork tasks using project intelligence.")
    parser.add_argument("path", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.path).resolve()
    result = rank(root)
    out = root / ".groundwork" / "planning.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    recommended = result["recommended"]
    if not recommended:
        print("GroundWork task planning: no eligible tasks found")
        return 0
    print("GroundWork recommended task")
    print(f"  {recommended['id'] or '-'} — {recommended['title']}")
    print(f"  Priority: {recommended['priority_score']}/100")
    for reason in recommended["reasons"]:
        print(f"  Why: {reason}")
    print(f"  Output: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
