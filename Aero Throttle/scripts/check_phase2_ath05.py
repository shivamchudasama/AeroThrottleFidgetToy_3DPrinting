"""Objective ATH_05 mesh, stack, and PETG serpentine validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import trimesh

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from geometry_engine.aero_throttle import AeroThrottleParameters, phase1_components, phase2_ath03, phase2_ath05


def main() -> int:
    p = AeroThrottleParameters(material="PETG")
    p.validate()
    stl_path = PROJECT_ROOT / "output/stl/ATH_05_FIRE_BUTTON_PLUNGER.stl"
    step_path = PROJECT_ROOT / "output/step/ATH_05_FIRE_BUTTON_PLUNGER.step"
    if not stl_path.is_file() or not step_path.is_file():
        raise RuntimeError("ATH_05 STL and STEP exports are both required")
    mesh = trimesh.load_mesh(stl_path, process=True)
    if not mesh.is_watertight or mesh.body_count != 1 or mesh.volume <= 0:
        raise RuntimeError(f"Invalid ATH_05 solid: watertight={mesh.is_watertight}, bodies={mesh.body_count}, volume={mesh.volume}")
    tolerance = 2 * p.eps
    expected_min = (p.serpentine_anchor_rear_x, p.bezel_center_y - p.fire_btn_flange / 2, -p.fire_btn_flange / 2)
    expected_max = (p.btn_head_front_x, p.bezel_center_y + p.fire_btn_flange / 2, p.fire_btn_flange / 2)
    if any(abs(actual - expected) > tolerance for actual, expected in zip(mesh.bounds[0], expected_min)):
        raise RuntimeError(f"ATH_05 minimum bounds differ from datum-derived dimensions: {mesh.bounds[0]} != {expected_min}")
    if any(abs(actual - expected) > tolerance for actual, expected in zip(mesh.bounds[1], expected_max)):
        raise RuntimeError(f"ATH_05 maximum bounds differ from datum-derived dimensions: {mesh.bounds[1]} != {expected_max}")
    if p.serpentine_work_h - p.serpentine_solid_h < p.fire_btn_stop_reserve:
        raise RuntimeError("ATH_05 hard stop does not retain the required spring-solid reserve")
    if p.serpentine_stress_mpa > p.sigma_allow_cyclic_mpa:
        raise RuntimeError("ATH_05 PETG serpentine exceeds its cyclic-stress allowable")
    if not 2.70 <= p.serpentine_force_n <= 3.70:
        raise RuntimeError("ATH_05 return force is outside the V-171 acceptance band")
    chassis = phase1_components(AeroThrottleParameters())["ATH_01"]
    bezel = phase2_ath03(p)
    button = phase2_ath05(p)
    chassis_intersection = chassis.intersect(button).val().Volume()
    bezel_intersection = bezel.intersect(button).val().Volume()
    if chassis_intersection > p.eps ** 3 or bezel_intersection > p.eps ** 3:
        raise RuntimeError(f"ATH_05 assembled interference: ATH_01={chassis_intersection}, ATH_03={bezel_intersection} mm^3")
    report = {
        "component": "ATH_05_FIRE_BUTTON_PLUNGER",
        "geometry": {"watertight": True, "body_count": 1, "volume_mm3": float(mesh.volume)},
        "bounds_mm": {"minimum": [float(value) for value in mesh.bounds[0]], "maximum": [float(value) for value in mesh.bounds[1]]},
        "axial_stack": {
            "anchor_rear_x_mm": p.serpentine_anchor_rear_x,
            "flange_rear_x_mm": p.btn_flange_rear_x,
            "head_front_x_mm": p.btn_head_front_x,
            "snout_cavity_rear_x_mm": p.snout_cavity_rear_x,
        },
        "serpentine": {
            "material": "PETG", "loops": p.serpentine_loops,
            "force_at_3_5_mm_n": p.serpentine_force_n,
            "stiffness_n_per_mm": p.serpentine_stiffness_n_per_mm,
            "cyclic_stress_mpa": p.serpentine_stress_mpa,
            "cyclic_allowable_mpa": p.sigma_allow_cyclic_mpa,
            "solid_reserve_mm": p.serpentine_work_h - p.serpentine_solid_h,
            "cavity_clearance_per_side_mm": p.serpentine_clearance_z,
        },
        "assembled_intersection_volume_mm3": {"ATH_01": chassis_intersection, "ATH_03": bezel_intersection},
    }
    (PROJECT_ROOT / "output/reports/phase2-ath05-validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("PHASE 2 ATH_05 VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
