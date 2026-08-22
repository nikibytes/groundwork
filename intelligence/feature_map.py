#!/usr/bin/env python3
"""Map PRD requirements to repository files and tests using deterministic signals.

The mapper is intentionally conservative: it extracts requirement headings and text
from docs/prd.md, then ranks files/tests by shared tokens and path/domain signals.
It does not claim semantic understanding that a parser cannot establish.
"""

from __future__ import annotations

import re
from pathlib import Path

STOPWORDS = {
    "about", "after", "also", "allow", "allows", "and", "are", "as", "at", "be",
    "can", "for", "from", "has", "have", "into", "is", "it", "must", "of", "on",
    "or", "should", "that", "the", "their", "then", "this", "to", "use", "users",
    "using", "when", "with", "will", "within", "without", "you", "your", "shall",
    "able", "app", "application", "feature", "system", "requirement",
}


def tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z][a-z0-9]{2,}", text.lower())
    return {w for w in words if w not in STOPWORDS}


def extract_requirements(prd: str) -> list[dict]:
    requirements: list[dict] = []
    current: dict | None = None
    for line_no, line in enumerate(prd.splitlines(), 1):
        heading = re.match(r"^#{2,4}\s+(.+?)\s*$", line)
        if heading:
            if current:
                requirements.append(current)
            title = heading.group(1).strip()
            current = {
                "id": f"PRD-{len(requirements) + 1:03d}",
                "title": title,
                "text": title,
                "source_line": line_no,
            }
        elif current and line.strip():
            current["text"] += " " + re.sub(r"[`*_]", "", line.strip())
    if current:
        requirements.append(current)

    # If the PRD has no section headings, treat non-empty bullet/list items as requirements.
    if not requirements:
        for line_no, line in enumerate(prd.splitlines(), 1):
            match = re.match(r"^\s*(?:[-*]|\d+[.)])\s+(.+)$", line)
            if match:
                text = match.group(1).strip()
                requirements.append({
                    "id": f"PRD-{len(requirements) + 1:03d}",
                    "title": text,
                    "text": text,
                    "source_line": line_no,
                })
    return requirements


def score_requirement(requirement: dict, path: str) -> int:
    req_tokens = tokens(requirement["text"])
    path_tokens = tokens(Path(path).stem.replace("_", " ").replace("-", " ") + " " + path)
    overlap = req_tokens & path_tokens
    score = len(overlap) * 10

    # Stronger signal when a whole requirement token appears in a directory/file name.
    path_lower = path.lower()
    for token in req_tokens:
        if token in path_lower:
            score += 3
    return score


def rank_files(requirement: dict, files: list[dict], limit: int = 8) -> list[dict]:
    ranked = []
    for item in files:
        path = item["path"]
        score = score_requirement(requirement, path)
        if score:
            ranked.append({
                "path": path,
                "score": score,
                "language": item.get("language"),
                "purpose": item.get("purpose"),
            })
    return sorted(ranked, key=lambda x: (-x["score"], x["path"]))[:limit]


def build_feature_map(root: Path, repo_map: dict) -> dict:
    prd_path = root / "docs" / "prd.md"
    if not prd_path.is_file():
        return {
            "schema_version": "0.1",
            "source": None,
            "requirements": [],
            "unavailable_reason": "docs/prd.md not found",
        }

    prd = prd_path.read_text(encoding="utf-8", errors="ignore")
    files = repo_map.get("files", [])
    requirements = extract_requirements(prd)
    mapped = []
    for requirement in requirements:
        candidates = rank_files(requirement, files)
        implementation = [x for x in candidates if not re.search(r"(^|/)(test|tests|spec|specs)(/|$)|(_test|\.test|\.spec)", x["path"], re.I)]
        tests = [x for x in candidates if x not in implementation and re.search(r"(^|/)(test|tests|spec|specs)(/|$)|(_test|\.test|\.spec)", x["path"], re.I)]
        mapped.append({
            "id": requirement["id"],
            "title": requirement["title"],
            "source": {"path": "docs/prd.md", "line": requirement["source_line"]},
            "implementation_files": implementation,
            "test_files": tests,
            "status": "mapped" if implementation else "unmapped",
        })

    return {
        "schema_version": "0.1",
        "source": "docs/prd.md",
        "requirements": mapped,
    }
