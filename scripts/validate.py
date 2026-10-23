"""Check every agent has the files and fields it needs. Exits non-zero on any problem.

    python scripts/validate.py                      # every agent and the template
    python scripts/validate.py agents/law-agent     # only these folders
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from agents import ROOT, agents

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# Keep in step with the categories in marketplace-registry's schema/listing.schema.json.
CATEGORIES = [
    "agents", "llm-apps", "coding", "local-llms", "chat", "image", "video", "speech", "documents", "search",
    "vector-databases", "ml-platforms", "robotics", "browser-automation", "no-code", "learning", "mcp-servers",
    "education", "other",
]
REQUIRED = ["kind", "name", "summary", "category", "license", "pricing", "agent", "maintainer"]


def check(folder: Path) -> list[str]:
    rel = folder.relative_to(ROOT)
    problems = []
    if folder.parent.name == "agents" and not SLUG_RE.match(folder.name):
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
    if data.get("category") not in CATEGORIES:
        problems.append(f"{rel}/agent.yaml: category must be one of {', '.join(CATEGORIES)}")
    if data.get("kind") != "agent":
        problems.append(f"{rel}/agent.yaml: kind must be 'agent'")
    if (data.get("pricing") or {}).get("education", {}).get("price") != "free":
        problems.append(f"{rel}/agent.yaml: agents must be free for education")
    if "safety" in data:
        problems.append(f"{rel}/agent.yaml: don't add a 'safety' section; reviewers set it")
    entry = (data.get("agent") or {}).get("entrypoint")
    if entry:
        path = folder / entry
        if not path.is_file():
            problems.append(f"{rel}/agent.yaml: entrypoint '{entry}' does not exist")
        else:
            try:
                compile(path.read_text(), str(path), "exec")
            except SyntaxError as exc:
                problems.append(f"{rel}/{entry}: syntax error ({exc.msg}, line {exc.lineno})")
        if not (folder / "requirements.txt").is_file():
            problems.append(f"{rel}: agents with code need a requirements.txt")
    for secret in folder.rglob(".env*"):
        if secret.name != ".env.example":
            problems.append(f"{secret.relative_to(ROOT)}: don't commit .env files; use .env.example")
    if not (data.get("agent") or {}).get("data_collected"):
        problems.append(f"{rel}/agent.yaml: agent.data_collected must say what is collected (or 'none')")
    return problems


def check_index() -> list[str]:
    """agents/ holds only submodules, and every submodule is checked out."""
    problems = []
    slugs = {a.slug for a in agents()}
    for p in sorted((ROOT / "agents").iterdir()):
        if p.is_dir() and p.name not in slugs:
            problems.append(f"agents/{p.name}: agents live in their own repo; add it as a submodule (see CONTRIBUTING.md)")
    for a in agents():
        if not (a.path / ".git").exists():
            problems.append(f"agents/{a.slug}: submodule not checked out; run git submodule update --init")
    return problems


def main(args: list[str]) -> int:
    if args:
        folders = [ROOT / a for a in args]
        problems = []
    else:
        folders = [a.path for a in agents() if (a.path / ".git").exists()] + [ROOT / "template"]
        problems = check_index()
    problems += [p for f in folders for p in check(f)]
    for p in problems:
        print(p)
    print(f"{len(folders)} folder(s) checked, {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
