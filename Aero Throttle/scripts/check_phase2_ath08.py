"""Objective ATH_08 mesh, PETG leaf, rail-fit, and travel validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import trimesh

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from geometry_engine.aero_throttle import AeroThrottleParameters, phase1_components, phase2_ath08


def _translated(shape, distance_x: float):
    return shape.translate((distance_x, 0, 0))


def main() -> int:
    p = AeroThrottleParameters(material="PETG")
    p.validate()
    stl_path = PROJECT_ROOT / "output/stl/ATH_08_THROTTLE_SLIDER.stl"
    step_path = PROJECT_ROOT / "output/step/ATH_08_THROTTLE_SLIDER.step"
    if not stl_path.is_file() or not step_path.is_file():
        raise RuntimeError("ATH_08 STL and STEP exports are both required")
    mesh = trimesh.load_mesh(stl_path, process=True)
    if not mesh.is_watertight or mesh.body_count != 1 or mesh.volume <= 0:
        raise RuntimeError(f"Invalid ATH_08 solid: watertight={mesh.is_watertight}, bodies={mesh.body_count}, volume={mesh.volume}")
    tolerance = 2 * p.eps
    expected_min = (p.rail_start_x + p.rail_end_clear, p.rail_center_y - p.dovetail_base_w / 2, p.dovetail_floor_z)
    expected_max = (p.rail_start_x + p.rail_end_clear + p.throttle_carriage_len, p.rail_center_y + p.dovetail_base_w / 2, p.flank_z - p.tab_recess)
    if any(abs(actual - expected) > tolerance for actual, expected in zip(mesh.bounds[0], expected_min)):
        raise RuntimeError(f"ATH_08 minimum bounds differ from the datum-G placement: {mesh.bounds[0]} != {expected_min}")
    if any(abs(actual - expected) > tolerance for actual, expected in zip(mesh.bounds[1], expected_max)):
        raise RuntimeError(f"ATH_08 maximum bounds differ from the controlled envelope: {mesh.bounds[1]} != {expected_max}")
    if abs(p.throttle_tenon_base_w - (p.dovetail_base_w - 2 * p.fit_clearance_sliding)) > tolerance or abs(p.throttle_tenon_mouth_w - (p.dovetail_mouth_w - 2 * p.fit_clearance_sliding)) > tolerance:
        raise RuntimeError("ATH_08 dovetail clearance is not derived from FC-SLIDE")
    if abs(p.rail_len - (p.throttle_carriage_len + p.throttle_stroke + 2 * p.rail_end_clear)) > tolerance:
        raise RuntimeError("ATH_08 rail/travel closure is not preserved")
    if p.throttle_follower_home_x + p.throttle_stroke > p.rail_len + tolerance:
        raise RuntimeError("ATH_08 follower leaves the rail at full stroke")
    if p.ramp_footprint >= p.throttle_stroke * (1 - p.afterburner_pos_ratio):
        raise RuntimeError("ATH_08 ramp does not fit its afterburner over-travel")
    if p.throttle_leaf_stress_mpa > p.sigma_allow_cyclic_mpa or p.throttle_leaf_rest_stress_mpa > p.sigma_allow_sustained_mpa:
        raise RuntimeError("ATH_08 PETG detent leaf exceeds its stress allowable")
    if abs(p.throttle_break_force_computed_n - p.throttle_break_force_n) / p.throttle_break_force_n > 0.15:
        raise RuntimeError("ATH_08 afterburner force is outside the V-170 acceptance band")
    if p.throttle_guide_ratio < 1.40:
        raise RuntimeError("ATH_08 guide ratio is below the anti-binding minimum")
    chassis = phase1_components(AeroThrottleParameters())['ATH_01']
    slider = phase2_ath08(p)
    intersections = {}
    for label, distance in (("home", 0.0), ("mid", p.throttle_stroke / 2), ("full", p.throttle_stroke)):
        volume = chassis.intersect(_translated(slider, distance)).val().Volume()
        intersections[label] = volume
        if volume > p.eps ** 3:
            raise RuntimeError(f"ATH_08 {label}-pose intersection with ATH_01: {volume} mm^3")
    report = {
        "component": "ATH_08_THROTTLE_SLIDER",
        "geometry": {"watertight": True, "body_count": 1, "volume_mm3": float(mesh.volume)},
        "bounds_mm": {"minimum": [float(value) for value in mesh.bounds[0]], "maximum": [float(value) for value in mesh.bounds[1]]},
        "sliding_fit": {
            "slot_base_w_mm": p.dovetail_base_w,
            "slot_mouth_w_mm": p.dovetail_mouth_w,
            "tenon_base_w_mm": p.throttle_tenon_base_w,
            "tenon_mouth_w_mm": p.throttle_tenon_mouth_w,
            "clearance_per_side_mm": p.fit_clearance_sliding,
        },
        "afterburner": {
            "follower_home_rail_local_x_mm": p.throttle_follower_home_x,
            "ramp_apex_rail_local_x_mm": p.ramp_apex_x,
            "ramp_run_up_mm": p.ramp_run_up,
            "ramp_drop_off_mm": p.ramp_drop_off,
            "break_force_n": p.throttle_break_force_computed_n,
            "target_force_n": p.throttle_break_force_n,
            "cyclic_stress_mpa": p.throttle_leaf_stress_mpa,
            "rest_stress_mpa": p.throttle_leaf_rest_stress_mpa,
            "cyclic_allowable_mpa": p.sigma_allow_cyclic_mpa,
            "sustained_allowable_mpa": p.sigma_allow_sustained_mpa,
        },
        "travel": {"stroke_mm": p.throttle_stroke, "rail_len_mm": p.rail_len, "guide_ratio": p.throttle_guide_ratio},
        "assembled_intersection_volume_mm3": {"ATH_01": intersections},
    }
    (PROJECT_ROOT / "output/reports/phase2-ath08-validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("PHASE 2 ATH_08 VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
