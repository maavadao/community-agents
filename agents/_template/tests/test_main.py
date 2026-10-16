import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import main


def test_instructions_load():
    assert main.agent.instructions.strip()
