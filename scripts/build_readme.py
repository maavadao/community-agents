"""Write the table of agents into README.md, between the agents:start and agents:end markers.

    python scripts/build_readme.py           # update README.md
    python scripts/build_readme.py --check   # exit non-zero if README.md is out of date
"""
from __future__ import annotations

import re
import sys

import yaml

from agents import ROOT, agents

START, END = "<!-- agents:start -->", "<!-- agents:end -->"


def table() -> str:
    rows = ["| Agent | What it does | Maintainer |", "| --- | --- | --- |"]
    for a in agents():
        data = yaml.safe_load((a.path / "agent.yaml").read_text())
        m = data.get("maintainer") or {}
        who = f"[{m['name']}](https://github.com/{m['github']})" if m.get("github") else m.get("name", "")
        summary = str(data.get("summary", "")).replace("|", "\\|")
        rows.append(f"| [**{data['name']}**]({a.repo}) | {summary} | {who} |")
    return "\n".join(rows)


def main(args: list[str]) -> int:
    readme = ROOT / "README.md"
    text = readme.read_text()
    new = re.sub(
        re.escape(START) + r".*?" + re.escape(END),
        lambda _: f"{START}\n{table()}\n{END}",
        text,
        flags=re.S,
    )
    if "--check" in args:
        if new != text:
            print("README.md's table of agents is out of date; run python scripts/build_readme.py")
            return 1
        return 0
    readme.write_text(new)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
