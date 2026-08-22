#!/usr/bin/env python3
import importlib.util
from pathlib import Path
import tempfile

SCRIPT = Path(__file__).parents[1] / "scripts" / "planning_state.py"
spec = importlib.util.spec_from_file_location("planning_state", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_init_creates_ordered_drafts():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        mod.init(root)
        data = mod.read_state(mod.state_path(root))
        assert data["current_stage"] == "discovery"
        assert data["stages"]["discovery"]["status"] == "draft"
        assert data["stages"]["prd"]["status"] == "pending"


def test_approval_locks_and_advances():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        mod.init(root)
        mod.approve(root, "discovery")
        data = mod.read_state(mod.state_path(root))
        assert data["stages"]["discovery"]["status"] == "LOCKED"
        assert data["current_stage"] == "prd"
        text = (root / "docs/planning/discovery.md").read_text()
        assert "status: LOCKED" in text
        assert "approved_by: human" in text


def test_cannot_skip_stage():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        mod.init(root)
        try:
            mod.approve(root, "requirements")
        except RuntimeError as exc:
            assert "current stage" in str(exc)
        else:
            raise AssertionError("expected skip-stage failure")


def test_locked_artifact_cannot_be_downgraded():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        mod.init(root)
        mod.approve(root, "discovery")
        artifact = root / "docs/planning/discovery.md"
        try:
            mod.set_status(artifact, "DRAFT", 2)
        except RuntimeError as exc:
            assert "locked artifact" in str(exc)
        else:
            raise AssertionError("expected locked-artifact failure")
