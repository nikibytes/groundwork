import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "intelligence" / "analyze.py"


class AnalyzeTests(unittest.TestCase):
    def run_analyzer(self, repo: Path):
        return subprocess.run([sys.executable, str(ANALYZER), str(repo)], text=True, capture_output=True, check=True)

    def test_generates_project_repo_map_dependency_graph_and_feature_map(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src" / "auth").mkdir(parents=True)
            (repo / "tests" / "auth").mkdir(parents=True)
            (repo / "docs").mkdir()
            (repo / "src" / "auth" / "login.py").write_text("def login():\n    return True\n", encoding="utf-8")
            (repo / "tests" / "auth" / "test_login.py").write_text("def test_login():\n    assert True\n", encoding="utf-8")
            (repo / "README.md").write_text("# Example\n", encoding="utf-8")
            (repo / "docs" / "prd.md").write_text(
                "# Product\n\n## User login\nUsers can login with their account.\n",
                encoding="utf-8",
            )

            self.run_analyzer(repo)
            intelligence = repo / ".groundwork"
            project = json.loads((intelligence / "project.json").read_text(encoding="utf-8"))
            repo_map = json.loads((intelligence / "repo-map.json").read_text(encoding="utf-8"))
            graph = json.loads((intelligence / "dependency-graph.json").read_text(encoding="utf-8"))
            feature_map = json.loads((intelligence / "feature-map.json").read_text(encoding="utf-8"))

            self.assertEqual(project["file_count"], 4)
            self.assertIn("Python", project["languages"])
            self.assertEqual(len(repo_map["files"]), 4)
            self.assertEqual(len(graph["edges"]), 0)
            self.assertEqual(feature_map["requirements"][0]["id"], "PRD-001")
            self.assertEqual(feature_map["requirements"][0]["status"], "mapped")
            self.assertIn("src/auth/login.py", [x["path"] for x in feature_map["requirements"][0]["implementation_files"]])
            self.assertIn("tests/auth/test_login.py", [x["path"] for x in feature_map["requirements"][0]["test_files"]])

    def test_feature_map_is_empty_when_prd_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "main.py").write_text("print('ok')\n", encoding="utf-8")
            self.run_analyzer(repo)
            feature_map = json.loads((repo / ".groundwork" / "feature-map.json").read_text(encoding="utf-8"))
            self.assertEqual(feature_map["requirements"], [])
            self.assertEqual(feature_map["unavailable_reason"], "docs/prd.md not found")

    def test_git_metadata_is_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            (repo / "main.py").write_text("print('ok')\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
            subprocess.run(["git", "-C", str(repo), "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "init"], check=True)
            self.run_analyzer(repo)
            project = json.loads((repo / ".groundwork" / "project.json").read_text(encoding="utf-8"))
            self.assertTrue(project["git"]["is_repository"])
            self.assertEqual(len(project["git"]["head"]), 40)
            self.assertTrue(project["git"]["branch"])


if __name__ == "__main__":
    unittest.main()
