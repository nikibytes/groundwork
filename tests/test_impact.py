import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "intelligence" / "analyze.py"
IMPACT = ROOT / "intelligence" / "impact.py"


class ImpactTests(unittest.TestCase):
    def run(self, script: Path, repo: Path, *args):
        return subprocess.run([sys.executable, str(script), *args, "--path", str(repo)] if script == IMPACT else [sys.executable, str(script), str(repo)], text=True, capture_output=True, check=True)

    def test_change_propagates_through_dependencies_and_requirements(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src" / "auth").mkdir(parents=True)
            (repo / "tests" / "auth").mkdir(parents=True)
            (repo / "docs").mkdir()
            (repo / "src" / "auth" / "session.py").write_text("def session(): pass\n", encoding="utf-8")
            (repo / "src" / "auth" / "login.py").write_text("from .session import session\ndef login(): return session()\n", encoding="utf-8")
            (repo / "tests" / "auth" / "test_login.py").write_text("def test_login(): assert True\n", encoding="utf-8")
            (repo / "docs" / "prd.md").write_text("# Product\n\n## Authentication\nUsers can login with a session.\n", encoding="utf-8")
            self.run(ANALYZER, repo)
            self.run(IMPACT, repo, "src/auth/session.py")
            impact = json.loads((repo / ".groundwork" / "impact.json").read_text(encoding="utf-8"))
            self.assertIn("src/auth/login.py", impact["affected_files"])
            self.assertTrue(impact["affected_requirements"])
            self.assertIn("tests/auth/test_login.py", impact["affected_tests"])
            self.assertIn(impact["risk"], {"low", "medium", "high"})


if __name__ == "__main__":
    unittest.main()
