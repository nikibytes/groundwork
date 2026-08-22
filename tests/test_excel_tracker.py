import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "excel_tracker.py"


class ExcelTrackerTests(unittest.TestCase):
    def test_write_then_read_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workbook = root / "task-tracker.xlsx"
            tasks = root / "tasks.json"
            tasks.write_text(json.dumps([{
                "ID": "GW-101",
                "Milestone": "v0.5",
                "Task": "Test Excel tracker",
                "Requirement": "PRD-001",
                "Status": "Backlog",
                "Priority": 80,
                "Risk": "Low",
                "Dependencies": "",
                "Owner": "qa",
                "Files": "scripts/excel_tracker.py",
                "Tests": "tests/test_excel_tracker.py",
                "Notes": "round trip",
            }]), encoding="utf-8")

            subprocess.run([sys.executable, str(SCRIPT), "write", str(workbook), "--tasks-json", str(tasks)], check=True)
            result = subprocess.run([sys.executable, str(SCRIPT), "read", str(workbook)], check=True, capture_output=True, text=True)
            rows = json.loads(result.stdout)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["ID"], "GW-101")
            self.assertEqual(rows[0]["Status"], "Backlog")
            self.assertEqual(rows[0]["Priority"], 80)


if __name__ == "__main__":
    unittest.main()
