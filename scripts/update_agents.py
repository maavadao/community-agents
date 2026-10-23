"""Move every agent submodule to the latest commit on its repo's default branch.

An agent whose latest commit fails validation stays on the commit it was on, so one broken
agent never holds the others back. Writes a commit message to the path given as the first
argument (nothing is written when no agent changed). Run daily by .github/workflows/update-agents.yml.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from agents import ROOT, agents, git
from validate import check


def main(args: list[str]) -> int:
    moved, held = [], []
    for a in agents():
        old = git("rev-parse", "HEAD", cwd=a.path)
        subprocess.run(["git", "submodule", "update", "--remote", "--checkout", f"agents/{a.slug}"], cwd=ROOT, check=True)
        new = git("rev-parse", "HEAD", cwd=a.path)
        if new == old:
            continue
        problems = check(a.path)
        if problems:
            git("checkout", "-q", old, cwd=a.path)
            held.append(f"- {a.slug}: kept at {old[:7]}; {new[:7]} fails validation:")
            held += [f"  - {p}" for p in problems]
            continue
        git("add", f"agents/{a.slug}")
        moved.append(f"- {a.slug}: {old[:7]} -> {new[:7]}")

    for line in moved + held:
        print(line)
    if not moved:
        print("No agent moved")
        return 0
    body = "\n".join(moved + ([""] + held if held else []))
    Path(args[0]).write_text(f"Update agents to their latest commits\n\n{body}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
