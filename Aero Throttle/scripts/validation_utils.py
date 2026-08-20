"""Shared utilities for independent CAD validation tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "validation_config.json"


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.is_file():
        raise RuntimeError(f"Missing validation configuration: {CONFIG_PATH}")
    with CONFIG_PATH.open(encoding="utf-8") as config_file:
        config = json.load(config_file)
    if not isinstance(config, dict):
        raise RuntimeError("validation_config.json must contain a JSON object")
    return config


def project_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def require_mesh(test_case: Any, mesh_path: str | Path | None = None) -> Any:
    config = load_config()
    selected_path = mesh_path or config.get("mesh_path")
    if not selected_path:
        test_case.skipTest("No mesh_path is configured in validation_config.json")

    path = project_path(selected_path)
    if not path.is_file():
        test_case.skipTest(f"Mesh has not been exported yet: {path}")

    try:
        import trimesh
    except ImportError:
        test_case.skipTest("Install requirements.txt to enable mesh validation")

    mesh = trimesh.load_mesh(path, process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))
    if not isinstance(mesh, trimesh.Trimesh):
        raise RuntimeError(f"Unsupported mesh type loaded from {path}: {type(mesh)!r}")
    return mesh


def assert_mesh_basics(test_case: Any, mesh: Any, label: str = "mesh") -> None:
    test_case.assertGreater(len(mesh.vertices), 0, f"{label} has no vertices")
    test_case.assertGreater(len(mesh.faces), 0, f"{label} has no faces")
    test_case.assertTrue(mesh.vertices.size > 0, f"{label} has no vertex data")
    test_case.assertTrue(mesh.faces.size > 0, f"{label} has no face data")
    test_case.assertTrue(bool(mesh.is_winding_consistent), f"{label} has inconsistent face winding")


def run_check_command(test_case: Any, check_name: str) -> None:
    config = load_config()
    check = config.get("project_checks", {}).get(check_name, {})
    command = check.get("command", []) if isinstance(check, dict) else []
    required = bool(check.get("required", False)) if isinstance(check, dict) else False

    if not command:
        if required:
            test_case.fail(
                f"Required project check '{check_name}' has no command in validation_config.json"
            )
        test_case.skipTest(f"No project-specific '{check_name}' check is configured")

    if not isinstance(command, list) or not all(isinstance(item, str) for item in command):
        test_case.fail(f"project_checks.{check_name}.command must be a list of strings")

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    message = (result.stdout + result.stderr).strip()
    test_case.assertEqual(result.returncode, 0, f"{check_name} check failed:\n{message}")


def run_sweep_command(sweep: dict[str, Any]) -> None:
    command = sweep.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(item, str) for item in command):
        raise RuntimeError("Every parametric sweep needs a non-empty command list")
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        raise RuntimeError(f"Sweep '{sweep.get('name', '<unnamed>')}' build failed:\n{output}")
