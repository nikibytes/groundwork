#!/usr/bin/env python3
"""Read, write, and synchronize GroundWork's human-facing Excel task tracker."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

COLUMNS = [
    "ID", "Milestone", "Task", "Requirement", "Status", "Priority",
    "Risk", "Dependencies", "Owner", "Files", "Tests", "Notes",
]


def _openpyxl():
    try:
        from openpyxl import Workbook, load_workbook
        return Workbook, load_workbook
    except ImportError as exc:
        raise SystemExit("Excel support requires openpyxl: pip install openpyxl") from exc


def read_tasks(path: Path) -> list[dict]:
    _, load_workbook = _openpyxl()
    if not path.exists():
        return []
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    if not rows:
        return []
    headers = [str(x).strip() if x is not None else "" for x in rows[0]]
    missing = [c for c in COLUMNS if c not in headers]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    index = {name: headers.index(name) for name in COLUMNS}
    tasks = []
    for row in rows[1:]:
        values = {name: row[index[name]] if index[name] < len(row) else None for name in COLUMNS}
        if not any(v not in (None, "") for v in values.values()):
            continue
        values["ID"] = str(values["ID"]).strip() if values["ID"] is not None else ""
        tasks.append(values)
    return tasks


def write_tasks(path: Path, tasks: list[dict]) -> None:
    Workbook, _ = _openpyxl()
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "Tasks"
    ws.append(COLUMNS)
    for task in tasks:
        ws.append([task.get(column, "") for column in COLUMNS])
    wb.save(path)
    wb.close()


def sync_tasks(path: Path, updates: list[dict]) -> list[dict]:
    """Update only known task IDs while preserving all other workbook rows."""
    tasks = read_tasks(path)
    by_id = {task["ID"]: task for task in tasks if task["ID"]}
    for update in updates:
        task_id = str(update.get("ID", "")).strip()
        if not task_id or task_id not in by_id:
            raise ValueError(f"Cannot sync unknown task ID: {task_id or '<empty>'}")
        for column in COLUMNS:
            if column in update:
                by_id[task_id][column] = update[column]
    result = list(by_id.values())
    write_tasks(path, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage GroundWork's Excel task tracker")
    sub = parser.add_subparsers(dest="command", required=True)

    write = sub.add_parser("write")
    write.add_argument("file")
    write.add_argument("--json", required=True, help="JSON file containing a list of task objects")

    read = sub.add_parser("read")
    read.add_argument("file")

    sync = sub.add_parser("sync")
    sync.add_argument("file")
    sync.add_argument("--json", required=True, help="JSON file containing task updates keyed by ID")

    args = parser.parse_args()
    path = Path(args.file)

    if args.command == "write":
        tasks = json.loads(Path(args.json).read_text(encoding="utf-8"))
        if not isinstance(tasks, list):
            raise SystemExit("--json must contain a JSON array of task objects")
        write_tasks(path, tasks)
        print(f"Wrote {len(tasks)} tasks to {path}")
    elif args.command == "read":
        print(json.dumps(read_tasks(path), indent=2, default=str))
    else:
        updates = json.loads(Path(args.json).read_text(encoding="utf-8"))
        if not isinstance(updates, list):
            raise SystemExit("--json must contain a JSON array of task updates")
        tasks = sync_tasks(path, updates)
        print(f"Synchronized {len(updates)} task(s); tracker now contains {len(tasks)} task(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
