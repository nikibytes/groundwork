#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path
import tempfile

SCRIPT = Path(__file__).with_name("first_run.py")


def run(*args, cwd):
    return subprocess.run([sys.executable, str(SCRIPT), *args, "--root", str(cwd)], text=True, capture_output=True, check=True)


def test_first_run_shows_welcome_then_stays_quiet():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        first = run(cwd=root)
        assert "Initialize a project" in first.stdout
        assert "Plan an application first" in first.stdout
        run("--complete", cwd=root)
        second = run(cwd=root)
        assert second.stdout == ""
