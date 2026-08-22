#!/usr/bin/env python3
"""Read and write the GroundWork Excel task tracker.

Usage:
  python3 scripts/excel_tracker.py write <path> [--tasks-json FILE]
  python3 scripts/excel_tracker.py read <path>

Requires openpyxl.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from openpyxl import Workbook, load_workbook
except ImportError as exc:  # pragma: no cover
    raise SystemExit("openpyxl is required: pip install openpyxl") from exc

HEADERS = [
    "ID", "Milestone", "Task", "Requirement", "Status", "Priority",
    "Risk", "Dependencies", "Owner", "Files", "Tests", "Notes",
]
DEFAULT_TASKS = [
    {"ID": "GW-001", "Milestone": "v0.1", "Task": "Analyze repository", "Requirement": "", "Status": "Backlog", "Priority": 50, "Risk": "Low", "Dependencies": "", "Owner": "", "Files": "", "Tests": "", "Notes": ""},
    {"ID": "GW-002", "Milestone": "v0.2", "Task": "Map PRD requirements", "Requirement": "", "Status": "Backlog", "Priority": 60, "Risk": "Medium", "Dependencies": "GW-001", "Owner": "", "Files": "", "Tests": "", "Notes": ""},
]


def write_tracker(path: Path, tasks: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Tasks"
    sheet.append(HEADERS)
    for task in tasks:
        sheet.append([task.get(header, "") for header in HEADERS])
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for column in sheet.columns:
        width = min(max(len(str(cell.value or "")) for cell in column) + 2, 40)
        sheet.column_dimensions[column[0].column_letter].width = width
    workbook.save(path)


def read_tracker(path: Path) -> list[dict]:
    workbook = load_workbook(path, read_only=True, data_only=True)
    sheet = workbook["Tasks"]
    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        return []
    headers = [str(value) if value is not None else "" for value in rows[0]]
    missing = [header for header in HEADERS if header not in headers]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    return [dict(zip(headers, row)) for row in rows[1:] if any(value is not None for value in row)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Read and write the GroundWork Excel task tracker.")
    sub = parser.add_subparsers(dest="command", required=True)

    writer = sub.add_parser("write", help="Create/update a tracker")
    writer.add_argument("path")
    writer.add_argument("--tasks-json", help="JSON file containing an array of task objects")

    reader = sub.add_parser("read", help="Read a tracker as JSON")
    reader.add_argument("path")

    args = parser.parse_args()
    path = Path(args.path)
    if args.command == "write":
        tasks = DEFAULT_TASKS
        if args.tasks_json:
            tasks = json.loads(Path(args.tasks_json).read_text(encoding="utf-8"))
            if not isinstance(tasks, list):
                raise SystemExit("--tasks-json must contain a JSON array")
        write_tracker(path, tasks)
        print(f"Wrote {len(tasks)} tasks to {path}")
        return 0

    print(json.dumps(read_tracker(path), indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
