"""Entry point for the agent. The interface below is a first draft and may change."""
from __future__ import annotations


def run(request: str) -> str:
    """Take what the user asked for and return the agent's answer."""
    raise NotImplementedError("Write your agent here.")


if __name__ == "__main__":
    import sys

    print(run(" ".join(sys.argv[1:])))
