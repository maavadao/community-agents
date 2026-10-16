"""Entry point: runs the agent's instructions.md on a maava gateway."""
from __future__ import annotations

from pathlib import Path

from maava_agent import Agent

agent = Agent.from_folder(Path(__file__).resolve().parent.parent)


def run(request: str) -> str:
    return agent.run(request)


if __name__ == "__main__":
    import sys

    print(run(" ".join(sys.argv[1:])))
