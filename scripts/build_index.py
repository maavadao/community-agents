"""Build dist/index.json from every agents/<name>/agent.yaml.

The shape matches marketplace-registry's index, so the website reads both the same way.
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REPO = "https://github.com/maavadao/maava-agents"


def added_date(folder: Path) -> str:
    """The date the agent's folder first appeared in git history."""
    out = subprocess.run(
        ["git", "log", "--diff-filter=A", "--format=%as", "--", str(folder)],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout.split()
    return out[-1] if out else dt.date.today().isoformat()


def main() -> None:
    listings = []
    for folder in sorted(p for p in (ROOT / "agents").iterdir() if p.is_dir() and not p.name.startswith("_")):
        data = yaml.safe_load((folder / "agent.yaml").read_text())
        data["slug"] = folder.name
        data.setdefault("links", {})["repository"] = f"{REPO}/tree/main/agents/{folder.name}"
        data.setdefault("added", added_date(folder))
        if isinstance(data["added"], dt.date):
            data["added"] = data["added"].isoformat()
        listings.append(data)

    out = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "counts": {"tools": 0, "agents": len(listings)},
        "listings": listings,
    }
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    (dist / "index.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(f"Wrote dist/index.json with {len(listings)} agent(s)")


if __name__ == "__main__":
    main()
