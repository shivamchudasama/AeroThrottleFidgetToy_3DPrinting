"""Objective Phase 2 ATH_03 mesh and PETG cam-leaf validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import trimesh

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from geometry_engine.aero_throttle import AeroThrottleParameters


def main() -> int:
    parameters = AeroThrottleParameters(material="PETG")
    parameters.validate()
    stl_path = PROJECT_ROOT / "output/stl/ATH_03_FRONT_BEZEL_FACEPLATE.stl"
    step_path = PROJECT_ROOT / "output/step/ATH_03_FRONT_BEZEL_FACEPLATE.step"
    if not stl_path.is_file() or not step_path.is_file():
        raise RuntimeError("ATH_03 STL and STEP exports are both required")
    mesh = trimesh.load_mesh(stl_path, process=True)
    if not mesh.is_watertight or mesh.body_count != 1 or mesh.volume <= 0:
        raise RuntimeError(f"Invalid ATH_03 solid: watertight={mesh.is_watertight}, bodies={mesh.body_count}, volume={mesh.volume}")
    if parameters.cam_leaf_stress_mpa > parameters.sigma_allow_cyclic_mpa:
        raise RuntimeError("PETG guard cam leaf exceeds cyclic-stress allowable")
    if parameters.cam_leaf_rest_stress_mpa != 0:
        raise RuntimeError("Guard cam leaf must be undeflected at both detent flats")
    expected_min = (
        parameters.bezel_rear_x,
        parameters.bezel_center_y - parameters.bezel_h / 2,
        -parameters.bezel_w / 2,
    )
    expected_max = (
        max(parameters.bezel_front_x, parameters.guard_hinge_x + parameters.guard_stanchion_t / 2),
        parameters.bezel_center_y + parameters.bezel_h / 2,
        parameters.bezel_w / 2,
    )
    tolerance = 2 * parameters.eps
    if any(abs(actual - expected) > tolerance for actual, expected in zip(mesh.bounds[0], expected_min)):
        raise RuntimeError(f"ATH_03 minimum bounds differ from datum-derived dimensions: {mesh.bounds[0]} != {expected_min}")
    if any(abs(actual - expected) > tolerance for actual, expected in zip(mesh.bounds[1], expected_max)):
        raise RuntimeError(f"ATH_03 maximum bounds differ from datum-derived dimensions: {mesh.bounds[1]} != {expected_max}")
    report = {
        "component": "ATH_03_FRONT_BEZEL_FACEPLATE",
        "geometry": {"watertight": True, "body_count": 1, "volume_mm3": float(mesh.volume)},
        "bounds_mm": {"minimum": [float(value) for value in mesh.bounds[0]], "maximum": [float(value) for value in mesh.bounds[1]]},
        "cam_leaf": {
            "material": "PETG",
            "width_mm": parameters.guard_cam_leaf_w,
            "stiffness_n_per_mm": parameters.cam_leaf_stiffness_n_per_mm,
            "crest_force_n": parameters.cam_leaf_force_n,
            "crest_stress_mpa": parameters.cam_leaf_stress_mpa,
            "cyclic_allowable_mpa": parameters.sigma_allow_cyclic_mpa,
            "rest_stress_mpa": parameters.cam_leaf_rest_stress_mpa,
            "tuning": "first physical article",
        },
    }
    (PROJECT_ROOT / "output/reports/phase2-ath03-validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("PHASE 2 ATH_03 VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
