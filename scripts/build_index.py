"""Build dist/index.json from every agent's agent.yaml.

The shape matches marketplace-registry's index, so the website reads both the same way.
"""
from __future__ import annotations

import datetime as dt
import json

import yaml

from agents import ROOT, agents, git


def added_date(slug: str) -> str:
    """The date the agent first appeared in this index (as a folder, before agents had their own repos)."""
    out = git("log", "--diff-filter=A", "--format=%as", "--", f"agents/{slug}").split()
    return out[-1] if out else dt.date.today().isoformat()


def main() -> None:
    listings = []
    for a in agents():
        data = yaml.safe_load((a.path / "agent.yaml").read_text())
        data["slug"] = a.slug
        data.setdefault("links", {})["repository"] = a.repo
        data.setdefault("added", added_date(a.slug))
        if isinstance(data["added"], dt.date):
            data["added"] = data["added"].isoformat()
        data["commit"] = git("rev-parse", "HEAD", cwd=a.path)
        data["updated"] = git("log", "-1", "--format=%as", cwd=a.path)
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
