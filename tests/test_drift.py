import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "intelligence" / "analyze.py"
DRIFT = ROOT / "intelligence" / "drift.py"


class DriftTests(unittest.TestCase):
    def run(self, script: Path, repo: Path, check: bool = True):
        return subprocess.run([sys.executable, str(script), str(repo)], text=True, capture_output=True, check=check)

    def analyze(self, repo: Path):
        self.run(ANALYZER, repo)

    def test_reports_missing_and_untested_requirements(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src").mkdir()
            (repo / "docs").mkdir()
            (repo / "src" / "login.py").write_text("def login(): pass\n", encoding="utf-8")
            (repo / "docs" / "prd.md").write_text(
                "# Product\n\n## User login\nUsers can login to their account.\n\n## Billing\nUsers can manage billing.\n",
                encoding="utf-8",
            )
            self.analyze(repo)
            result = self.run(DRIFT, repo, check=False)
            self.assertEqual(result.returncode, 1)
            drift = json.loads((repo / ".groundwork" / "drift.json").read_text(encoding="utf-8"))
            types = {f["type"] for f in drift["findings"]}
            self.assertIn("MISSING", types)
            self.assertIn("UNTESTED", types)

    def test_clean_repository_has_no_drift_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src" / "auth").mkdir(parents=True)
            (repo / "tests" / "auth").mkdir(parents=True)
            (repo / "docs").mkdir()
            (repo / "src" / "auth" / "login.py").write_text("def login(): pass\n", encoding="utf-8")
            (repo / "tests" / "auth" / "test_login.py").write_text("def test_login(): assert True\n", encoding="utf-8")
            (repo / "docs" / "prd.md").write_text("# Product\n\n## User login\nUsers can login.\n", encoding="utf-8")
            self.analyze(repo)
            result = self.run(DRIFT, repo, check=False)
            self.assertEqual(result.returncode, 0)
            drift = json.loads((repo / ".groundwork" / "drift.json").read_text(encoding="utf-8"))
            self.assertEqual(drift["status"], "clean")


if __name__ == "__main__":
    unittest.main()
