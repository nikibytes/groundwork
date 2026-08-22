#!/usr/bin/env python3
"""Build a deterministic, machine-readable snapshot of a repository."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from feature_map import build_feature_map

VERSION = "0.2"
OUTPUT_DIR = ".groundwork"

IGNORE_DIRS = {".git", ".groundwork", "node_modules", "vendor", "dist", "build", ".next", ".nuxt", "coverage", "target", "__pycache__", ".venv", "venv"}
EXTENSIONS = {".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript", ".java": "Java", ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".php": "PHP", ".cs": "C#", ".swift": "Swift", ".kt": "Kotlin", ".kts": "Kotlin", ".sql": "SQL", ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell", ".css": "CSS", ".scss": "SCSS", ".html": "HTML", ".vue": "Vue"}
MANIFESTS = {"package.json": "Node.js package manifest", "pnpm-lock.yaml": "pnpm lockfile", "yarn.lock": "Yarn lockfile", "package-lock.json": "npm lockfile", "bun.lock": "Bun lockfile", "bun.lockb": "Bun lockfile", "pyproject.toml": "Python project manifest", "requirements.txt": "Python dependency manifest", "Pipfile": "Pipenv dependency manifest", "go.mod": "Go module manifest", "Cargo.toml": "Rust package manifest", "Gemfile": "Ruby dependency manifest", "pom.xml": "Maven project manifest", "build.gradle": "Gradle build manifest", "build.gradle.kts": "Gradle Kotlin build manifest"}
IMPORT_PATTERNS = {
    "Python": [re.compile(r"^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))", re.M)],
    "JavaScript": [re.compile(r"(?:import\s+(?:[^'\"]+\s+from\s+)?|require\()\s*['\"]([^'\"]+)['\"]")],
    "TypeScript": [re.compile(r"(?:import\s+(?:[^'\"]+\s+from\s+)?|require\()\s*['\"]([^'\"]+)['\"]")],
}


def run_git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=True)
    return result.stdout.strip()


def find_root(path: Path) -> Path:
    try:
        return Path(run_git(path, "rev-parse", "--show-toplevel"))
    except (subprocess.CalledProcessError, FileNotFoundError):
        return path.resolve()


def rel_files(root: Path) -> list[str]:
    try:
        files = run_git(root, "ls-files", "-z").split("\0")
        return sorted(f for f in files if f)
    except (subprocess.CalledProcessError, FileNotFoundError):
        found: list[str] = []
        for base, dirs, names in os.walk(root):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for name in names:
                found.append(Path(base, name).relative_to(root).as_posix())
        return sorted(found)


def language_for(path: str) -> str | None:
    return EXTENSIONS.get(Path(path).suffix.lower())


def purpose_for(path: str) -> str:
    name, lower = Path(path).name, path.lower()
    if name in MANIFESTS: return MANIFESTS[name]
    if name.lower().startswith("readme"): return "Project documentation and usage guide"
    if name.lower() in {"license", "license.md", "license.txt"}: return "Project license"
    if "/test" in lower or lower.startswith("test/") or lower.startswith("tests/"): return "Test source"
    if "/docs/" in f"/{lower}/" or lower.startswith("docs/"): return "Project documentation"
    if "/scripts/" in f"/{lower}/" or lower.startswith("scripts/"): return "Project automation script"
    lang = language_for(path)
    return f"{lang} source file" if lang else "Repository file"


def package_managers(files: Iterable[str]) -> list[str]:
    names = {Path(f).name for f in files}
    managers: list[str] = []
    if "pnpm-lock.yaml" in names: managers.append("pnpm")
    elif "yarn.lock" in names: managers.append("yarn")
    elif "bun.lock" in names or "bun.lockb" in names: managers.append("bun")
    elif "package-lock.json" in names: managers.append("npm")
    if {"pyproject.toml", "requirements.txt", "Pipfile"} & names: managers.append("python")
    if "go.mod" in names: managers.append("go")
    if "Cargo.toml" in names: managers.append("cargo")
    if "Gemfile" in names: managers.append("bundler")
    return managers


def detect_frameworks(root: Path, files: list[str]) -> list[str]:
    found: list[str] = []
    package = root / "package.json"
    if package.exists():
        try:
            data = json.loads(package.read_text(encoding="utf-8"))
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            checks = {"next": "Next.js", "react": "React", "vue": "Vue", "@angular/core": "Angular", "express": "Express", "fastify": "Fastify", "nestjs": "NestJS", "@nestjs/core": "NestJS"}
            found.extend(label for dep, label in checks.items() if dep in deps)
        except (OSError, json.JSONDecodeError): pass
    names = {Path(f).name for f in files}
    if "manage.py" in names: found.append("Django")
    if "requirements.txt" in names:
        try:
            text = (root / "requirements.txt").read_text(encoding="utf-8").lower()
            if "fastapi" in text: found.append("FastAPI")
            if "flask" in text: found.append("Flask")
        except OSError: pass
    return sorted(set(found))


def resolve_import(root: Path, source: str, target: str, language: str) -> str | None:
    if language in {"JavaScript", "TypeScript"} and target.startswith("."):
        base = (Path(source).parent / target).as_posix()
        candidates = [base] + [base + ext for ext in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".json")]
        candidates += [f"{base}/index{ext}" for ext in (".ts", ".tsx", ".js", ".jsx")]
    elif language == "Python" and not target.startswith("."):
        base = target.replace(".", "/")
        candidates = [base + ".py", base + "/__init__.py"]
    elif language == "Python" and target.startswith("."):
        dots = len(target) - len(target.lstrip("."))
        module = target[dots:].replace(".", "/")
        base = Path(source).parent
        for _ in range(max(dots - 1, 0)): base = base.parent
        candidates = [(base / module).as_posix() + ".py", (base / module / "__init__.py").as_posix()]
    else: return None
    for candidate in candidates:
        p = root / candidate
        try:
            if p.is_file(): return p.relative_to(root).as_posix()
        except ValueError: continue
    return None


def build_dependency_graph(root: Path, files: list[str]) -> dict:
    file_set, edges = set(files), []
    for source in files:
        language = language_for(source)
        if language not in IMPORT_PATTERNS: continue
        try: text = (root / source).read_text(encoding="utf-8", errors="ignore")
        except OSError: continue
        for pattern in IMPORT_PATTERNS[language]:
            for match in pattern.finditer(text):
                target = next((g for g in match.groups() if g), None)
                resolved = resolve_import(root, source, target, language) if target else None
                if resolved and resolved in file_set and resolved != source:
                    edges.append({"from": source, "to": resolved, "type": "import"})
    unique = {(e["from"], e["to"], e["type"]): e for e in edges}
    return {"nodes": [{"path": f, "language": language_for(f)} for f in files], "edges": sorted(unique.values(), key=lambda e: (e["from"], e["to"]))}


def analyze(root: Path) -> dict[str, dict]:
    files = rel_files(root)
    languages = Counter(language_for(f) for f in files if language_for(f))
    try:
        git = {"is_repository": True, "head": run_git(root, "rev-parse", "HEAD"), "branch": run_git(root, "symbolic-ref", "--short", "HEAD")}
    except (subprocess.CalledProcessError, FileNotFoundError):
        git = {"is_repository": False, "head": None, "branch": None}
    generated_at = datetime.now(timezone.utc).isoformat()
    project = {"schema_version": VERSION, "generated_at": generated_at, "root": str(root), "git": git, "file_count": len(files), "languages": dict(sorted(languages.items())), "package_managers": package_managers(files), "frameworks": detect_frameworks(root, files), "manifests": sorted(f for f in files if Path(f).name in MANIFESTS)}
    repo_map = {"schema_version": VERSION, "generated_at": generated_at, "files": [{"path": f, "purpose": purpose_for(f), "language": language_for(f)} for f in files]}
    graph = build_dependency_graph(root, files)
    feature_map = build_feature_map(root, repo_map)
    return {"project": project, "repo_map": repo_map, "dependency_graph": graph, "feature_map": feature_map}


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze a repository into .groundwork intelligence artifacts.")
    parser.add_argument("path", nargs="?", default=".", help="Repository path (default: current directory)")
    parser.add_argument("--stdout", action="store_true", help="Print the project snapshot instead of writing files")
    args = parser.parse_args()
    root = find_root(Path(args.path).resolve())
    result = analyze(root)
    if args.stdout:
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    out = root / OUTPUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    for name, data in result.items():
        (out / f"{name.replace('_', '-')}.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"GroundWork analyzed {root}")
    print(f"  Files: {result['project']['file_count']}")
    print(f"  Languages: {', '.join(result['project']['languages']) or 'none detected'}")
    print(f"  Frameworks: {', '.join(result['project']['frameworks']) or 'none detected'}")
    print(f"  Dependencies: {len(result['dependency_graph']['edges'])}")
    print(f"  Requirements: {len(result['feature_map']['requirements'])}")
    print(f"  Output: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
