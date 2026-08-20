"""OpenSCAD export command builder."""

from __future__ import annotations

from pathlib import Path


def stl_command(source: Path, output: Path) -> list[str]:
    return ["openscad", "-o", str(output), str(source)]
