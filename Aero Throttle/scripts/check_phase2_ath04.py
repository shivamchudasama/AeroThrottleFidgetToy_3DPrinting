"""Objective ATH_04 mesh, hinge, and PETG cam-interface validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import trimesh

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from geometry_engine.aero_throttle import AeroThrottleParameters, phase2_ath03, phase2_ath04


def _assert_bounds(actual: object, expected: tuple[float, float, float], tolerance: float, label: str) -> None:
    if any(abs(value - reference) > tolerance for value, reference in zip(actual, expected)):
        raise RuntimeError(f"{label} differs from datum-derived dimensions: {actual} != {expected}")


def main() -> int:
    parameters = AeroThrottleParameters(material="PETG")
    parameters.validate()
    stl_path = PROJECT_ROOT / "output/stl/ATH_04_MISSILE_SAFETY_GUARD.stl"
    step_path = PROJECT_ROOT / "output/step/ATH_04_MISSILE_SAFETY_GUARD.step"
    if not stl_path.is_file() or not step_path.is_file():
        raise RuntimeError("ATH_04 STL and STEP exports are both required")
    mesh = trimesh.load_mesh(stl_path, process=True)
    if not mesh.is_watertight or mesh.body_count != 1 or mesh.volume <= 0:
        raise RuntimeError(f"Invalid ATH_04 solid: watertight={mesh.is_watertight}, bodies={mesh.body_count}, volume={mesh.volume}")
    tolerance = 2 * parameters.eps
    # The user-approved hood bounding-box exemption permits the cam to extend
    # forward of the hood's X minimum and the pins beyond its Z limits.
    if not parameters.guard_hinge_x - parameters.guard_cam_base_r - parameters.guard_cam_lobe - tolerance <= mesh.bounds[0][0] < parameters.guard_hood_min_x - tolerance:
        raise RuntimeError(f"ATH_04 cam extension is outside its approved envelope: {mesh.bounds[0][0]}")
    _assert_bounds(mesh.bounds[0][1:], (parameters.guard_hood_min_y - parameters.guard_lift_tab_y / 4, -parameters.guard_pin_outer_z), tolerance, "ATH_04 minimum Y/Z bounds")
    _assert_bounds(mesh.bounds[1], (parameters.guard_closed_x, parameters.guard_hinge_y + parameters.guard_stop_y, parameters.guard_pin_outer_z), tolerance, "ATH_04 maximum bounds")
    if parameters.cam_leaf_stress_mpa > parameters.sigma_allow_cyclic_mpa:
        raise RuntimeError("ATH_04 cam interface exceeds the PETG cyclic-stress allowable")
    if parameters.cam_leaf_rest_stress_mpa != 0:
        raise RuntimeError("ATH_04 cam flats must leave the ATH_03 leaf undeflected at rest")
    contact_volume = phase2_ath03(parameters).intersect(phase2_ath04(parameters)).val().Volume()
    if contact_volume > parameters.eps ** 3:
        raise RuntimeError(f"ATH_03 and closed ATH_04 overlap by {contact_volume} mm^3")
    report = {
        "component": "ATH_04_MISSILE_SAFETY_GUARD",
        "geometry": {"watertight": True, "body_count": 1, "volume_mm3": float(mesh.volume)},
        "bounds_mm": {"minimum": [float(value) for value in mesh.bounds[0]], "maximum": [float(value) for value in mesh.bounds[1]]},
        "hinge": {
            "axis": [parameters.guard_hinge_x, parameters.guard_hinge_y, 0],
            "pin_axis_z_mm": [-parameters.guard_pin_axis_z, parameters.guard_pin_axis_z],
            "pin_outer_z_mm": [-parameters.guard_pin_outer_z, parameters.guard_pin_outer_z],
            "hood_bbox_excludes_pins": True,
            "hood_bbox_excludes_cam": True,
        },
        "cam_interface": {
            "material": "PETG",
            "crest_deflection_mm": parameters.cam_leaf_deflection,
            "crest_stress_mpa": parameters.cam_leaf_stress_mpa,
            "cyclic_allowable_mpa": parameters.sigma_allow_cyclic_mpa,
            "rest_stress_mpa": parameters.cam_leaf_rest_stress_mpa,
            "closed_pose_intersection_volume_mm3": contact_volume,
        },
    }
    (PROJECT_ROOT / "output/reports/phase2-ath04-validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("PHASE 2 ATH_04 VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
