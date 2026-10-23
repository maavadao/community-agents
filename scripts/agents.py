"""The agents in this index: one git submodule per agent under agents/, each its own repo."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Agent:
    slug: str
    path: Path
    repo: str  # https://github.com/<owner>/<repo>, no .git


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def agents() -> list[Agent]:
    """Every submodule under agents/, sorted by folder name."""
    if not (ROOT / ".gitmodules").is_file():
        return []
    paths = git("config", "-f", ".gitmodules", "--get-regexp", r"^submodule\..*\.path$").splitlines()
    found = []
    for line in paths:
        key, path = line.split(maxsplit=1)
        if not path.startswith("agents/"):
            continue
        name = key[len("submodule."):-len(".path")]
        url = git("config", "-f", ".gitmodules", f"submodule.{name}.url").removesuffix(".git")
        found.append(Agent(slug=path.removeprefix("agents/"), path=ROOT / path, repo=url))
    return sorted(found, key=lambda a: a.slug)
