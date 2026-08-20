"""CadQuery export command builder; adapt the script arguments to the project."""

from __future__ import annotations

from pathlib import Path


def script_command(source: Path) -> list[str]:
    return ["python", str(source)]
