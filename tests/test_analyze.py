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
        result = subprocess.run(
            [sys.executable, str(ANALYZER), str(repo)],
            text=True,
            capture_output=True,
            check=True,
        )
        return result

    def test_generates_project_repo_map_and_dependency_graph(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src").mkdir()
            (repo / "src" / "main.py").write_text("from src.util import answer\nprint(answer())\n", encoding="utf-8")
            (repo / "src" / "util.py").write_text("def answer():\n    return 42\n", encoding="utf-8")
            (repo / "README.md").write_text("# Example\n", encoding="utf-8")

            self.run_analyzer(repo)

            intelligence = repo / ".groundwork"
            project = json.loads((intelligence / "project.json").read_text(encoding="utf-8"))
            repo_map = json.loads((intelligence / "repo-map.json").read_text(encoding="utf-8"))
            graph = json.loads((intelligence / "dependency-graph.json").read_text(encoding="utf-8"))

            self.assertEqual(project["file_count"], 3)
            self.assertIn("Python", project["languages"])
            self.assertEqual(len(repo_map["files"]), 3)
            self.assertIn(
                {"from": "src/main.py", "to": "src/util.py", "type": "import"},
                graph["edges"],
            )

    def test_git_metadata_is_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            (repo / "main.py").write_text("print('ok')\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
            subprocess.run(
                ["git", "-C", str(repo), "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "init"],
                check=True,
            )

            self.run_analyzer(repo)
            project = json.loads((repo / ".groundwork" / "project.json").read_text(encoding="utf-8"))

            self.assertTrue(project["git"]["is_repository"])
            self.assertEqual(len(project["git"]["head"]), 40)
            self.assertTrue(project["git"]["branch"])


if __name__ == "__main__":
    unittest.main()
