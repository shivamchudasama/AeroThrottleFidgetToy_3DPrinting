"""Objective ATH_06 mesh, PETG star-spring, and chassis-interface validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import trimesh

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from geometry_engine.aero_throttle import AeroThrottleParameters, phase1_components, phase2_ath06


def main() -> int:
    p = AeroThrottleParameters(material="PETG")
    p.validate()
    stl_path = PROJECT_ROOT / "output/stl/ATH_06_4WAY_HAT_SWITCH.stl"
    step_path = PROJECT_ROOT / "output/step/ATH_06_4WAY_HAT_SWITCH.step"
    if not stl_path.is_file() or not step_path.is_file():
        raise RuntimeError("ATH_06 STL and STEP exports are both required")
    mesh = trimesh.load_mesh(stl_path, process=True)
    if not mesh.is_watertight or mesh.body_count != 1 or mesh.volume <= 0:
        raise RuntimeError(f"Invalid ATH_06 solid: watertight={mesh.is_watertight}, bodies={mesh.body_count}, volume={mesh.volume}")
    tolerance = 2 * p.eps
    expected_min = (p.hat_center_x - p.hat_cap_od / 2, p.hat_ball_bottom_y, -p.hat_cap_od / 2)
    expected_max = (p.hat_center_x + p.hat_cap_od / 2, p.deck_y + p.hat_cap_protrusion, p.hat_cap_od / 2)
    if any(abs(actual - expected) > tolerance for actual, expected in zip(mesh.bounds[0], expected_min)):
        raise RuntimeError(f"ATH_06 minimum bounds differ from datum-derived dimensions: {mesh.bounds[0]} != {expected_min}")
    if any(abs(actual - expected) > tolerance for actual, expected in zip(mesh.bounds[1], expected_max)):
        raise RuntimeError(f"ATH_06 maximum bounds differ from datum-derived dimensions: {mesh.bounds[1]} != {expected_max}")
    if p.hat_stress_mpa > p.sigma_allow_cyclic_mpa:
        raise RuntimeError("ATH_06 PETG star spring exceeds cyclic-stress allowable")
    if abs(p.hat_force_computed_n - p.hat_force_n) / p.hat_force_n > 0.15:
        raise RuntimeError("ATH_06 self-centring force is outside the V-143 acceptance band")
    if p.hat_upper_arm_y - (p.hat_lower_arm_y + p.hat_spring_arm_thick_active) < p.gap_print_min - p.eps:
        raise RuntimeError("ATH_06 arm planes do not retain the printable minimum separation")
    if p.hat_cradle_d - p.hat_ball_d != 2 * p.fit_clearance_rotary:
        raise RuntimeError("ATH_06 gimbal clearance is not derived from FC-ROTARY")
    chassis = phase1_components(AeroThrottleParameters())["ATH_01"]
    hat = phase2_ath06(p)
    intersection_volume = chassis.intersect(hat).val().Volume()
    if intersection_volume > p.eps ** 3:
        raise RuntimeError(f"ATH_06 rest-pose intersection with ATH_01: {intersection_volume} mm^3")
    report = {
        "component": "ATH_06_4WAY_HAT_SWITCH",
        "geometry": {"watertight": True, "body_count": 1, "volume_mm3": float(mesh.volume)},
        "bounds_mm": {"minimum": [float(value) for value in mesh.bounds[0]], "maximum": [float(value) for value in mesh.bounds[1]]},
        "star_spring": {
            "material": "PETG", "topology": "two-level alternating star",
            "arm_planes_y_mm": [p.hat_lower_arm_y, p.hat_upper_arm_y],
            "inter_plane_gap_mm": p.gap_print_min,
            "force_at_14_deg_n": p.hat_force_computed_n,
            "target_force_n": p.hat_force_n,
            "cyclic_stress_mpa": p.hat_stress_mpa,
            "cyclic_allowable_mpa": p.sigma_allow_cyclic_mpa,
            "rest_stress_mpa": 0.0,
        },
        "gimbal": {"ball_d_mm": p.hat_ball_d, "cradle_d_mm": p.hat_cradle_d, "clearance_per_side_mm": p.fit_clearance_rotary},
        "assembled_intersection_volume_mm3": {"ATH_01": intersection_volume},
    }
    (PROJECT_ROOT / "output/reports/phase2-ath06-validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("PHASE 2 ATH_06 VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
