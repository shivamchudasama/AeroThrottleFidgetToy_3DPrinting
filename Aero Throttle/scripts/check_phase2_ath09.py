"""Objective ATH_09 mesh, PETG flexure, fit, and rest-pose validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import trimesh

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from geometry_engine.aero_throttle import AeroThrottleParameters, phase1_components, phase2_ath09


def main() -> int:
    p = AeroThrottleParameters(material="PETG")
    p.validate()
    stem = "ATH_09_DUAL_TRIGGER"
    stl_path = PROJECT_ROOT / "output/stl" / f"{stem}.stl"
    step_path = PROJECT_ROOT / "output/step" / f"{stem}.step"
    if not stl_path.is_file() or not step_path.is_file():
        raise RuntimeError("ATH_09 STL and STEP exports are both required")
    mesh = trimesh.load_mesh(stl_path, process=True)
    if not mesh.is_watertight or mesh.body_count != 1 or mesh.volume <= 0:
        raise RuntimeError(f"Invalid ATH_09 solid: watertight={mesh.is_watertight}, bodies={mesh.body_count}, volume={mesh.volume}")
    tolerance = 2 * p.eps
    expected_min = (46.00, -24.00, -p.trigger_shoe_half_width)
    expected_max = (62.00, 0.00, p.trigger_shoe_half_width)
    if any(abs(actual - expected) > tolerance for actual, expected in zip(mesh.bounds[0], expected_min)):
        raise RuntimeError(f"ATH_09 minimum bounds differ from the controlled trigger envelope: {mesh.bounds[0]} != {expected_min}")
    if any(abs(actual - expected) > tolerance for actual, expected in zip(mesh.bounds[1], expected_max)):
        raise RuntimeError(f"ATH_09 maximum bounds differ from the controlled trigger envelope: {mesh.bounds[1]} != {expected_max}")
    if abs(p.trigger_socket_nominal_d - p.trigger_socket_d) > tolerance:
        raise RuntimeError("ATH_09 trunnion/socket fit is not derived from FC-PIVOT")
    if p.trigger_stage1_stress_mpa > p.sigma_allow_cyclic_mpa or p.trigger_stage2_stress_mpa > p.sigma_allow_cyclic_mpa:
        raise RuntimeError("ATH_09 PETG flexure sizing exceeds the cyclic-stress allowable")
    if abs(p.trigger_stage1_force_computed_n - p.trigger_stage1_force_n) / p.trigger_stage1_force_n > 0.15:
        raise RuntimeError("ATH_09 stage-1 force is outside the V-174 acceptance band")
    if abs(p.trigger_break_force_computed_n - p.trigger_break_force_n) / p.trigger_break_force_n > 0.15:
        raise RuntimeError("ATH_09 stage-2 break force is outside the V-174 acceptance band")
    if abs(p.trigger_tooth_r - (p.trigger_break_force_n - p.trigger_stage1_force_n) * p.trigger_contact_r / p.trigger_stage2_tangential_force_n) > tolerance:
        raise RuntimeError("ATH_09 tooth radius must remain a force-derived dimension")
    if not (0 < p.trigger_stage1_deg < p.trigger_travel_deg < p.trigger_overtravel_deg_total):
        raise RuntimeError("ATH_09 travel staging does not close at 0, stage-1, full, and over-travel poses")
    grip = phase1_components(AeroThrottleParameters())["ATH_02"]
    trigger = phase2_ath09(p)
    rest_intersection = grip.intersect(trigger).val().Volume()
    if rest_intersection > p.eps ** 3:
        raise RuntimeError(f"ATH_09 rest-pose intersection with ATH_02: {rest_intersection} mm^3")
    report = {
        "component": stem,
        "geometry": {"watertight": True, "body_count": 1, "volume_mm3": float(mesh.volume)},
        "bounds_mm": {"minimum": [float(value) for value in mesh.bounds[0]], "maximum": [float(value) for value in mesh.bounds[1]]},
        "pivot_fit": {
            "trunnion_d_mm": p.trigger_trunnion_d,
            "socket_d_mm": p.trigger_socket_nominal_d,
            "clearance_per_side_mm": p.fit_clearance_pivot,
        },
        "stage_1": {
            "developed_length_mm": p.trigger_stage1_len,
            "width_mm": p.trigger_stage1_width_active,
            "thickness_mm": p.trigger_stage1_thick_active,
            "force_n": p.trigger_stage1_force_computed_n,
            "target_force_n": p.trigger_stage1_force_n,
            "cyclic_stress_mpa": p.trigger_stage1_stress_mpa,
        },
        "stage_2": {
            "length_mm": p.trigger_stage2_len,
            "width_mm": p.trigger_stage2_width_active,
            "thickness_mm": p.trigger_stage2_thick_active,
            "normal_force_n": p.trigger_stage2_normal_force_n,
            "tangential_force_n": p.trigger_stage2_tangential_force_n,
            "derived_tooth_radius_mm": p.trigger_tooth_r,
            "break_force_n": p.trigger_break_force_computed_n,
            "target_break_force_n": p.trigger_break_force_n,
            "cyclic_stress_mpa": p.trigger_stage2_stress_mpa,
        },
        "motion_samples_deg": [0.0, p.trigger_stage1_deg, p.trigger_travel_deg, p.trigger_overtravel_deg_total],
        "rest_pose_intersection_volume_mm3": {"ATH_02": rest_intersection},
    }
    (PROJECT_ROOT / "output/reports/phase2-ath09-validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("PHASE 2 ATH_09 VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
