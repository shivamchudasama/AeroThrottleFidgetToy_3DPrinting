"""Objective Phase 1 validation for parameter chains and generated root solids."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import trimesh

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from geometry_engine.aero_throttle import AeroThrottleParameters


def main() -> int:
    p = AeroThrottleParameters()
    p.validate()
    expected = ("ATH_01", "ATH_02", "ATH_10_A", "ATH_10_B")
    report: dict[str, object] = {"parameters": "PASS", "parts": {}}
    for part_id in expected:
        path = PROJECT_ROOT / "output/stl" / f"{part_id}.stl"
        if not path.is_file():
            raise RuntimeError(f"Missing Phase 1 STL: {path}")
        # STL stores each triangle independently; processing welds the exact shared
        # vertices before the watertight/component topology test.
        mesh = trimesh.load_mesh(path, process=True)
        if not mesh.is_watertight or mesh.body_count != 1 or mesh.volume <= 0:
            raise RuntimeError(f"Invalid Phase 1 solid {part_id}: watertight={mesh.is_watertight}, bodies={mesh.body_count}, volume={mesh.volume}")
        report["parts"][part_id] = {"watertight": True, "body_count": 1, "volume_mm3": float(mesh.volume)}
    output = PROJECT_ROOT / "output/reports/phase1-validation.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("PHASE 1 VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
