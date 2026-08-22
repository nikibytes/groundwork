import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLANNING = ROOT / "intelligence" / "planning.py"


class PlanningTests(unittest.TestCase):
    def run(self, repo: Path):
        return subprocess.run([sys.executable, str(PLANNING), str(repo)], text=True, capture_output=True, check=True)

    def test_missing_requirement_gets_priority(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "docs").mkdir()
            (repo / ".groundwork").mkdir()
            (repo / "docs" / "task-tracker.md").write_text(
                "# Backlog\n- GW-001 Add billing\n- GW-002 Add authentication\n", encoding="utf-8"
            )
            (repo / ".groundwork" / "feature-map.json").write_text(json.dumps({"requirements": [
                {"id": "PRD-001", "title": "Authentication", "description": "Users can authenticate"},
                {"id": "PRD-002", "title": "Billing", "description": "Users can manage billing"},
            ]}), encoding="utf-8")
            (repo / ".groundwork" / "drift.json").write_text(json.dumps({"findings": [
                {"type": "MISSING", "requirement": "PRD-001"}
            ]}), encoding="utf-8")
            (repo / ".groundwork" / "dependency-graph.json").write_text(json.dumps({"edges": []}), encoding="utf-8")
            self.run(repo)
            result = json.loads((repo / ".groundwork" / "planning.json").read_text(encoding="utf-8"))
            self.assertEqual(result["recommended"]["id"], "GW-002")
            self.assertGreaterEqual(result["recommended"]["priority_score"], 50)

    def test_blocked_tasks_are_not_recommended(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "docs").mkdir()
            (repo / ".groundwork").mkdir()
            (repo / "docs" / "task-tracker.md").write_text(
                "# Blocked\n- GW-001 Blocked payment\n# Backlog\n- GW-002 Add search\n", encoding="utf-8"
            )
            for name, data in {
                "feature-map.json": {"requirements": []},
                "drift.json": {"findings": []},
                "dependency-graph.json": {"edges": []},
            }.items():
                (repo / ".groundwork" / name).write_text(json.dumps(data), encoding="utf-8")
            self.run(repo)
            result = json.loads((repo / ".groundwork" / "planning.json").read_text(encoding="utf-8"))
            self.assertEqual(result["recommended"]["id"], "GW-002")


if __name__ == "__main__":
    unittest.main()
