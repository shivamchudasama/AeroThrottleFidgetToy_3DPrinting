"""CAD-engine configuration and command helpers."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "cad_config.json"


def load_cad_config() -> dict[str, Any]:
    with CONFIG_PATH.open(encoding="utf-8") as config_file:
        config = json.load(config_file)
    if not isinstance(config, dict):
        raise RuntimeError("cad_config.json must contain a JSON object")
    return config


def project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def export_path(config: dict[str, Any], name: str) -> Path:
    value = config.get("exports", {}).get(name)
    if not value:
        raise RuntimeError(f"cad_config.json is missing exports.{name}")
    return project_path(value)


def command_for(config: dict[str, Any], name: str) -> list[str]:
    command = config.get("commands", {}).get(name, [])
    if not command:
        return []
    if not isinstance(command, list) or not all(isinstance(part, str) for part in command):
        raise RuntimeError(f"commands.{name} must be a list of strings")
    exports = config.get("exports", {})
    context = {
        "project_root": str(PROJECT_ROOT),
        "source": str(project_path(config.get("source", "src/main.scad"))),
        "stl_path": str(project_path(exports.get("stl", "output/stl/model.stl"))),
        "step_path": str(project_path(exports.get("step", "output/step/model.step"))),
        "preview_path": str(project_path(exports.get("preview", "output/preview/model.png"))),
    }
    return [part.format(**context) for part in command]


def run_command(command: list[str], label: str) -> None:
    if not command:
        raise RuntimeError(f"No command configured for {label}")
    result = subprocess.run(command, cwd=PROJECT_ROOT, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"{label} failed with exit code {result.returncode}")
