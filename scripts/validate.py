"""Check every agent folder has the files and fields it needs. Exits non-zero on any problem."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
REQUIRED = ["kind", "name", "summary", "category", "license", "pricing", "agent", "maintainer"]


def check(folder: Path) -> list[str]:
    rel = folder.relative_to(ROOT)
    problems = []
    if not folder.name.startswith("_") and not SLUG_RE.match(folder.name):
        problems.append(f"{rel}: folder name must be lowercase letters, digits and hyphens")
    if not (folder / "README.md").is_file():
        problems.append(f"{rel}: missing README.md")
    manifest = folder / "agent.yaml"
    if not manifest.is_file():
        return problems + [f"{rel}: missing agent.yaml"]
    try:
        data = yaml.safe_load(manifest.read_text())
    except yaml.YAMLError as exc:
        return problems + [f"{rel}/agent.yaml: not valid YAML ({exc})"]
    if not isinstance(data, dict):
        return problems + [f"{rel}/agent.yaml: must be a mapping"]
    for key in REQUIRED:
        if key not in data:
            problems.append(f"{rel}/agent.yaml: missing '{key}'")
    if data.get("kind") != "agent":
        problems.append(f"{rel}/agent.yaml: kind must be 'agent'")
    if (data.get("pricing") or {}).get("education", {}).get("price") != "free":
        problems.append(f"{rel}/agent.yaml: agents must be free for education")
    if "safety" in data:
        problems.append(f"{rel}/agent.yaml: don't add a 'safety' section; reviewers set it")
    if not (data.get("agent") or {}).get("data_collected"):
        problems.append(f"{rel}/agent.yaml: agent.data_collected must say what is collected (or 'none')")
    return problems


def main() -> int:
    folders = sorted(p for p in (ROOT / "agents").iterdir() if p.is_dir() and not p.name.startswith("_"))
    problems = [p for f in folders for p in check(f)]
    problems += check_template()
    for p in problems:
        print(p)
    print(f"{len(folders)} agents checked, {len(problems)} problem(s)")
    return 1 if problems else 0


def check_template() -> list[str]:
    return check(ROOT / "agents" / "_template") if (ROOT / "agents" / "_template").is_dir() else []


if __name__ == "__main__":
    sys.exit(main())
