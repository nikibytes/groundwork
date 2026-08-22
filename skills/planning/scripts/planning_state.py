#!/usr/bin/env python3
"""Deterministic state engine for GroundWork's gated planning workflow."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
import sys

STAGES = [
    "discovery",
    "prd",
    "personas",
    "user-flows",
    "requirements",
    "domain-model",
    "data-flow",
    "database-schema",
]

FILES = {stage: f"{stage}.md" for stage in STAGES}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def state_path(root: Path) -> Path:
    return root / "docs" / "planning" / "planning-state.yaml"


def parse_scalar(value: str) -> str | int | bool:
    value = value.strip()
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if re.fullmatch(r"\d+", value):
        return int(value)
    return value.strip('"\'')


def read_state(path: Path) -> dict:
    if not path.exists():
        return {"mode": "inactive", "current_stage": STAGES[0], "implementation_ready": False, "stages": {}}
    data = {"mode": "active", "current_stage": STAGES[0], "implementation_ready": False, "stages": {}}
    current = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("current_stage:"):
            data["current_stage"] = parse_scalar(line.split(":", 1)[1])
        elif line.startswith("mode:"):
            data["mode"] = parse_scalar(line.split(":", 1)[1])
        elif line.startswith("implementation_ready:"):
            data["implementation_ready"] = parse_scalar(line.split(":", 1)[1])
        elif line.endswith(":") and line[:-1] in STAGES:
            current = line[:-1]
            data["stages"][current] = {}
        elif current and ":" in line:
            key, value = line.split(":", 1)
            data["stages"].setdefault(current, {})[key.strip()] = parse_scalar(value)
    return data


def write_state(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["planning:", f"  mode: {data['mode']}", f"  current_stage: {data['current_stage']}", f"  implementation_ready: {'true' if data['implementation_ready'] else 'false'}", "  stages:"]
    for stage in STAGES:
        s = data["stages"].get(stage, {"status": "pending", "version": 0})
        lines.append(f"    {stage}: {s.get('status', 'pending')}")
        lines.append(f"      version: {s.get('version', 0)}")
        if s.get("approved_at"):
            lines.append(f"      approved_at: {s['approved_at']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def front_matter(text: str) -> dict:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    result = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = parse_scalar(value)
    return result


def set_status(path: Path, status: str, version: int, approved_at: str | None = None) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    meta = front_matter(text)
    if meta.get("status") == "LOCKED" and status != "LOCKED":
        raise RuntimeError(f"refusing to modify locked artifact: {path}")
    body = text
    if text.startswith("---\n") and "\n---" in text[4:]:
        body = text[text.find("\n---", 4) + 4:].lstrip("\n")
    lines = ["---", f"status: {status}", f"version: {version}"]
    if status == "LOCKED":
        lines.extend(["approved_by: human", f"approved_at: {approved_at or now()}"])
    lines.extend(["---", "", body.rstrip(), ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def init(root: Path) -> None:
    path = state_path(root)
    data = {"mode": "active", "current_stage": STAGES[0], "implementation_ready": False, "stages": {}}
    for stage in STAGES:
        data["stages"][stage] = {"status": "draft" if stage == STAGES[0] else "pending", "version": 0}
        artifact = root / "docs" / "planning" / FILES[stage]
        if not artifact.exists():
            artifact.write_text(f"# {stage.replace('-', ' ').title()}\n\n", encoding="utf-8")
            set_status(artifact, data["stages"][stage]["status"], 0)
    write_state(path, data)


def approve(root: Path, stage: str) -> None:
    path = state_path(root)
    data = read_state(path)
    if stage not in STAGES:
        raise RuntimeError(f"unknown stage: {stage}")
    index = STAGES.index(stage)
    if data["current_stage"] != stage:
        raise RuntimeError(f"cannot approve {stage}; current stage is {data['current_stage']}")
    if index > 0:
        previous = data["stages"].get(STAGES[index - 1], {})
        if previous.get("status") != "LOCKED":
            raise RuntimeError(f"cannot approve {stage}; previous stage is not locked")
    artifact = root / "docs" / "planning" / FILES[stage]
    if not artifact.exists():
        raise RuntimeError(f"missing artifact: {artifact}")
    version = int(data["stages"].get(stage, {}).get("version", 0)) + 1
    approved_at = now()
    set_status(artifact, "LOCKED", version, approved_at)
    data["stages"][stage] = {"status": "LOCKED", "version": version, "approved_at": approved_at}
    if index == len(STAGES) - 1:
        data["implementation_ready"] = True
        data["current_stage"] = stage
    else:
        next_stage = STAGES[index + 1]
        data["current_stage"] = next_stage
        data["stages"][next_stage] = {"status": "draft", "version": data["stages"].get(next_stage, {}).get("version", 0)}
        next_artifact = root / "docs" / "planning" / FILES[next_stage]
        if not next_artifact.exists():
            next_artifact.write_text(f"# {next_stage.replace('-', ' ').title()}\n\n", encoding="utf-8")
        if front_matter(next_artifact.read_text(encoding="utf-8")).get("status") != "LOCKED":
            set_status(next_artifact, "DRAFT", int(data["stages"][next_stage]["version"]))
    write_state(path, data)


def status(root: Path) -> None:
    data = read_state(state_path(root))
    print(f"mode: {data['mode']}")
    print(f"current_stage: {data['current_stage']}")
    print(f"implementation_ready: {str(data['implementation_ready']).lower()}")
    for stage in STAGES:
        s = data["stages"].get(stage, {})
        print(f"{stage}: {s.get('status', 'pending')} v{s.get('version', 0)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["init", "approve", "status"])
    parser.add_argument("stage", nargs="?")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    try:
        if args.command == "init":
            init(root)
        elif args.command == "approve":
            if not args.stage:
                raise RuntimeError("approve requires a stage")
            approve(root, args.stage)
        else:
            status(root)
        return 0
    except (OSError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
