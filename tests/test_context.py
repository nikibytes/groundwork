import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "intelligence" / "analyze.py"
CONTEXT = ROOT / "intelligence" / "context.py"


class ContextTests(unittest.TestCase):
    def run(self, script: Path, repo: Path, *args):
        return subprocess.run([sys.executable, str(script), *args, "--path", str(repo)] if script == CONTEXT else [sys.executable, str(script), str(repo)], text=True, capture_output=True, check=True)

    def test_request_selects_related_files_requirements_and_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src" / "auth").mkdir(parents=True)
            (repo / "tests" / "auth").mkdir(parents=True)
            (repo / "src" / "billing").mkdir(parents=True)
            (repo / "docs").mkdir()
            (repo / "src" / "auth" / "login.py").write_text("def login(): pass\n", encoding="utf-8")
            (repo / "tests" / "auth" / "test_login.py").write_text("def test_login(): assert True\n", encoding="utf-8")
            (repo / "src" / "billing" / "invoice.py").write_text("def invoice(): pass\n", encoding="utf-8")
            (repo / "docs" / "prd.md").write_text("# Product\n\n## Authentication\nUsers can login securely.\n\n## Billing\nUsers can manage invoices.\n", encoding="utf-8")
            self.run(ANALYZER, repo)
            self.run(CONTEXT, repo, "fix the login authentication bug")
            context = json.loads((repo / ".groundwork" / "context.json").read_text(encoding="utf-8"))
            paths = set(context["files"])
            self.assertIn("src/auth/login.py", paths)
            self.assertIn("tests/auth/test_login.py", paths)
            self.assertNotIn("src/billing/invoice.py", paths)
            self.assertTrue(context["requirements"])
            self.assertEqual(context["selection"]["confidence"], "candidate_context")


if __name__ == "__main__":
    unittest.main()
