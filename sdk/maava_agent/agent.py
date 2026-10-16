"""An agent is a written brief plus a gateway to run it on."""
from __future__ import annotations

from pathlib import Path

from .client import Gateway


class Agent:
    """Wraps ``instructions`` (the brief) and runs requests on a gateway.

    Start with ``Agent.from_folder(...)``, which reads ``instructions.md`` from an agent folder.
    """

    def __init__(self, instructions: str, gateway: Gateway | None = None, agent_id: str = "main"):
        if not instructions.strip():
            raise ValueError("an agent needs instructions")
        self.instructions = instructions
        self.gateway = gateway or Gateway()
        self.agent_id = agent_id

    @classmethod
    def from_folder(cls, folder: str | Path, **kwargs) -> "Agent":
        return cls((Path(folder) / "instructions.md").read_text(), **kwargs)

    def run(self, request: str, *, session: str | None = None) -> str:
        return self.gateway.chat(request, system=self.instructions, agent=self.agent_id, session=session)
