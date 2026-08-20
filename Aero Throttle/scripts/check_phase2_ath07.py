"""Objective ATH_07 mesh, fit-chain, ratchet, and chassis-interface validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import trimesh

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from geometry_engine.aero_throttle import AeroThrottleParameters, phase1_components, phase2_ath07


def main() -> int:
    p = AeroThrottleParameters(material="PLA_PLUS")
    p.validate()
    stl_path = PROJECT_ROOT / "output/stl/ATH_07_ROTARY_TRIM_WHEEL.stl"
    step_path = PROJECT_ROOT / "output/step/ATH_07_ROTARY_TRIM_WHEEL.step"
    if not stl_path.is_file() or not step_path.is_file():
        raise RuntimeError("ATH_07 STL and STEP exports are both required")
    mesh = trimesh.load_mesh(stl_path, process=True)
    if not mesh.is_watertight or mesh.body_count != 1 or mesh.volume <= 0:
        raise RuntimeError(f"Invalid ATH_07 solid: watertight={mesh.is_watertight}, bodies={mesh.body_count}, volume={mesh.volume}")
    tolerance = 2 * p.eps
    expected_min = (p.trim_wheel_center_x - p.trim_wheel_od / 2, p.trim_wheel_center_y - p.trim_wheel_od / 2, p.trim_wheel_min_z)
    expected_max = (p.trim_wheel_center_x + p.trim_wheel_od / 2, p.trim_wheel_center_y + p.trim_wheel_od / 2, p.trim_wheel_max_z)
    if any(abs(actual - expected) > tolerance for actual, expected in zip(mesh.bounds[0], expected_min)):
        raise RuntimeError(f"ATH_07 minimum bounds differ from datum-derived dimensions: {mesh.bounds[0]} != {expected_min}")
    if any(abs(actual - expected) > tolerance for actual, expected in zip(mesh.bounds[1], expected_max)):
        raise RuntimeError(f"ATH_07 maximum bounds differ from datum-derived dimensions: {mesh.bounds[1]} != {expected_max}")
    if abs(p.trim_bore_d - p.trim_post_d - 2 * p.fit_clearance_rotary) > tolerance:
        raise RuntimeError("ATH_07 bore/post nominal clearance is not derived from FC-ROTARY")
    if abs(p.trim_pocket_d - p.trim_wheel_od - 2 * p.trim_pocket_clear_r) > tolerance:
        raise RuntimeError("ATH_07 radial pocket clearance is not derived from its named parameter")
    if abs(p.trim_pocket_depth - p.trim_wheel_width - 2 * p.trim_pocket_clear_z) > tolerance:
        raise RuntimeError("ATH_07 axial pocket clearance is not derived from its named parameter")
    if p.ratchet_teeth_count != 20 or abs(p.ratchet_incl_angle_deg - 90.0) > 0.05:
        raise RuntimeError("ATH_07 ratchet must retain 20 symmetric 90-degree teeth")
    if p.ratchet_web < p.feature_min - tolerance or p.trim_wheel_width - p.trim_ratchet_cut_depth < p.wall_internal - tolerance:
        raise RuntimeError("ATH_07 ratchet web or hub web is below its required minimum")
    if p.pawl_stress_mpa > p.sigma_allow_cyclic_mpa or p.pawl_rest_stress_mpa > p.sigma_allow_sustained_mpa:
        raise RuntimeError("ATH_07's PLA pawl sizing exceeds its stress allowable")
    if abs(p.pawl_torque_nmm - p.ratchet_torque_nmm) / p.ratchet_torque_nmm > 0.05:
        raise RuntimeError("ATH_07 pawl sizing does not meet the ratchet torque target")
    chassis = phase1_components(AeroThrottleParameters())["ATH_01"]
    wheel = phase2_ath07(p)
    intersection_volume = chassis.intersect(wheel).val().Volume()
    if intersection_volume > p.eps ** 3:
        raise RuntimeError(f"ATH_07 rest-pose intersection with ATH_01: {intersection_volume} mm^3")
    report = {
        "component": "ATH_07_ROTARY_TRIM_WHEEL",
        "geometry": {"watertight": True, "body_count": 1, "volume_mm3": float(mesh.volume)},
        "bounds_mm": {"minimum": [float(value) for value in mesh.bounds[0]], "maximum": [float(value) for value in mesh.bounds[1]]},
        "rotary_fit": {
            "post_d_mm": p.trim_post_d,
            "nominal_bore_d_mm": p.trim_bore_d,
            "manufacturing_bore_d_mm": p.trim_bore_d + p.hole_comp,
            "clearance_per_side_mm": p.fit_clearance_rotary,
            "pocket_radial_clearance_mm": p.trim_pocket_clear_r,
            "pocket_axial_clearance_mm": p.trim_pocket_clear_z,
        },
        "ratchet": {
            "teeth": p.ratchet_teeth_count,
            "pitch_radius_mm": p.ratchet_pitch_r,
            "tooth_depth_mm": p.ratchet_tooth_depth,
            "included_angle_deg": p.ratchet_incl_angle_deg,
            "hub_web_mm": p.wall_internal,
            "web_to_bore_mm": p.ratchet_web,
            "pawl_torque_nmm": p.pawl_torque_nmm,
            "target_torque_nmm": p.ratchet_torque_nmm,
            "pawl_cyclic_stress_mpa": p.pawl_stress_mpa,
            "pawl_rest_stress_mpa": p.pawl_rest_stress_mpa,
        },
        "chassis_redesign": {
            "trim_pocket_axis": "Z (datum K)",
            "post_carrier": "top-deck-connected structural spine",
            "pawl_topology": "under-wheel vertical PLA cantilever with valley-engaging nose",
            "pawl_length_mm": p.pawl_len,
            "pawl_cross_section_mm": [p.pawl_width, p.pawl_thickness],
            "pawl_nose_d_mm": p.pawl_nose_d,
            "rear_mechanism_flank_hook_station_x_mm": p.trim_safe_snap_hook_station_x,
            "hook_to_pocket_wall_mm": p.wall_internal,
        },
        "assembled_intersection_volume_mm3": {"ATH_01": intersection_volume},
    }
    (PROJECT_ROOT / "output/reports/phase2-ath07-validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("PHASE 2 ATH_07 VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
