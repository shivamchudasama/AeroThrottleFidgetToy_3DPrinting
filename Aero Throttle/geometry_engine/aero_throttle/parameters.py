"""Normative Phase 1 parameters and derived relationships in the Y-up frame."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import asin, atan, cos, degrees, pi, radians, sin, sqrt, tan
from typing import Any


@dataclass(frozen=True)
class AeroThrottleParameters:
    """Single-source dimensions for the structural-root build sequence.

    Coordinates are design coordinates: X forward, Y up, Z mechanism flank.
    Values originate in PARAMETERS.md; derived values are properties below.
    """

    material: str = "PLA_PLUS"
    handedness: int = 1
    chord_tolerance: float = 0.01
    eps: float = 0.01
    wall_exterior: float = 2.40
    wall_internal: float = 1.80
    feature_min: float = 0.80
    gap_print_min: float = 0.40
    internal_fillet_radius: float = 0.60
    bed_chamfer: float = 0.60
    fit_clearance_snap: float = 0.15
    fit_clearance_static: float = 0.10
    fit_clearance_sliding: float = 0.20
    fit_clearance_pivot: float = 0.10
    fit_clearance_rotary: float = 0.25
    hole_comp: float = 0.10
    mu_pla: float = 0.30
    chassis_length: float = 82.00
    chassis_height: float = 36.00
    chassis_width: float = 26.50
    grip_drop: float = 30.00
    hat_cap_protrusion: float = 6.00
    bezel_protrusion: float = 2.00
    guard_hood_h: float = 4.50
    guard_recess_depth: float = 2.50
    crown_chamfer: float = 3.00
    front_lower_chamfer: float = 12.00
    collar_w: float = 18.00
    collar_h: float = 20.00
    bezel_depth: float = 12.00
    bezel_center_y: float = 22.00
    snout_cavity_rear_x: float = 66.00
    snout_spring_cavity_y: float = 11.90
    snout_spring_cavity_z: float = 6.20
    collar_cavity_y: float = 16.40
    collar_cavity_z: float = 14.40
    rail_start_x: float = 3.00
    rail_center_y: float = 22.00
    throttle_carriage_len: float = 15.00
    throttle_stroke: float = 28.00
    rail_end_clear: float = 0.50
    dovetail_mouth_w: float = 7.00
    dovetail_base_w: float = 10.50
    dovetail_angle_deg: float = 45.00
    rail_channel_depth: float = 7.40
    rail_channel_h: float = 12.50
    tab_recess: float = 0.40
    throttle_tab_len: float = 12.00
    throttle_tab_h: float = 8.00
    tab_ridge_count: int = 4
    tab_ridge_r: float = 0.50
    afterburner_pos_ratio: float = 0.85
    afterburner_lift: float = 1.10
    afterburner_ramp_angle_deg: float = 30.00
    afterburner_drop_angle_deg: float = 65.00
    throttle_glide_force_n: float = 0.80
    throttle_break_force_n: float = 4.30
    throttle_leaf_len: float = 28.41
    throttle_leaf_width: float = 4.00
    throttle_leaf_thick: float = 2.63
    throttle_leaf_fold_r: float = 2.60
    throttle_leaf_arms: int = 2
    carriage_plate_t: float = 4.80
    detent_follower_r: float = 1.20
    throttle_detent_preload: float = 0.45
    # PETG re-solve: retaining the approved developed length and fold topology,
    # then increasing bending thickness and reducing width restores the 4.30 N
    # break target while preserving cyclic and sustained stress margins.
    throttle_leaf_width_petg: float = 3.55
    throttle_leaf_thick_petg: float = 3.20
    carriage_plate_t_petg: float = 5.20
    trim_wheel_center_x: float = 61.00
    trim_wheel_od: float = 22.00
    trim_rim_proud: float = 2.20
    trim_wheel_width: float = 6.80
    trim_pocket_clear_r: float = 1.00
    trim_pocket_clear_z: float = 0.60
    trim_post_d: float = 5.00
    trim_snap_head_d: float = 6.20
    trim_snap_head_t: float = 1.30
    trim_snap_slot_w: float = 0.80
    trim_snap_slot_len: float = 7.00
    trim_window_len: float = 16.00
    trim_window_clear_z: float = 0.60
    knurl_facets: int = 32
    knurl_depth: float = 0.70
    knurl_helix_deg: float = 45.00
    ratchet_teeth_count: int = 20
    ratchet_pitch_r: float = 7.00
    ratchet_tooth_depth: float = 1.10
    ratchet_torque_nmm: float = 12.00
    pawl_len: float = 17.70
    pawl_width: float = 3.60
    pawl_thickness: float = 1.05
    pawl_preload: float = 0.40
    pawl_fold_r: float = 1.20
    seam_tongue_thick: float = 1.20
    seam_tongue_height: float = 0.80
    snap_hook_len: float = 15.00
    snap_hook_w: float = 3.50
    snap_hook_t: float = 1.60
    snap_barb_depth: float = 1.20
    snap_hook_stations_x: tuple[float, float] = (12.00, 46.00)
    snap_hook_z: float = 9.50
    key_side: float = 4.00
    key_len: float = 8.00
    key_chamfer: float = 0.60
    key_waist_proud: float = 0.30
    key_waist_width: float = 1.00
    key_stations_x: tuple[float, float] = (30.00, 58.00)
    grip_rake_angle_deg: float = 108.00
    grip_root_x: float = 30.00
    grip_root_depth: float = 26.00
    grip_butt_depth: float = 24.00
    palm_swell_width: float = 26.10
    finger_groove_count: int = 3
    finger_groove_depth: float = 2.20
    finger_groove_r: float = 11.00
    finger_groove_pitch: float = 12.00
    grip_groove_start_ratio: float = 0.22
    rib_count: int = 10
    rib_width: float = 1.20
    rib_depth: float = 0.80
    rib_pitch: float = 2.20
    trigger_pivot_x: float = 58.00
    trigger_pivot_y: float = -4.00
    trigger_trunnion_d: float = 3.80
    trigger_socket_d: float = 4.00
    trigger_trunnion_len: float = 7.60
    trigger_cradle_mouth_w: float = 3.40
    trigger_cradle_wall_len: float = 7.50
    trigger_shoe_r: float = 16.00
    trigger_contact_r: float = 18.00
    trigger_travel_deg: float = 15.00
    trigger_stage1_travel: float = 3.00
    trigger_stage1_len: float = 21.20
    trigger_stage1_width: float = 14.60
    trigger_stage1_thick: float = 0.75
    trigger_stage1_force_n: float = 1.60
    trigger_stage2_len: float = 12.20
    trigger_stage2_width: float = 6.00
    trigger_stage2_thick: float = 1.35
    trigger_stage2_deflect: float = 0.55
    trigger_gate_angle_deg: float = 45.00
    trigger_break_force_n: float = 5.20
    trigger_overtravel_deg: float = 0.60
    # PETG re-solve.  Stage 1 holds its developed length, uses the full 22 MPa
    # cyclic-stress allowance, and tunes its width to the 1.60 N target.  The
    # stage-2 tooth grows only in its stress-sensitive thickness; its width is
    # then retuned so the derived tooth radius remains at the 9.46 mm design
    # station while delivering the required break force.
    trigger_stage1_thick_petg: float = 1.09863111111111
    trigger_stage1_width_petg: float = 7.66444349274416
    trigger_stage2_thick_petg: float = 1.50
    trigger_stage2_width_petg: float = 7.22
    trigger_shoe_half_width: float = 7.25
    trigger_shoe_section_t: float = 4.00
    trigger_spur_len: float = 6.00
    trigger_rib_depth: float = 0.30
    trigger_rib_pitch: float = 1.60
    bezel_w: float = 22.00
    bezel_h: float = 24.00
    bezel_chamfer: float = 1.50
    bezel_barb_len: float = 11.60
    bezel_barb_w: float = 2.80
    bezel_barb_t: float = 1.40
    snap_undercut: float = 0.80
    latch_pocket_w: float = 3.50
    latch_pocket_h: float = 1.80
    guard_hood_w: float = 15.00
    guard_hood_l: float = 19.00
    guard_wall: float = 1.60
    guard_recess_h: float = 20.00
    guard_recess_w: float = 16.00
    guard_pin_d: float = 2.35
    guard_pin_len: float = 3.00
    guard_open_deg: float = 90.00
    guard_overtravel_deg: float = 100.00
    guard_cam_lobe: float = 0.80
    guard_cam_base_r: float = 3.20
    guard_cam_leaf_len: float = 12.00
    guard_cam_leaf_w: float = 6.00
    guard_cam_leaf_t: float = 0.90
    guard_hood_chamfer: float = 0.60
    guard_pin_lead_angle_deg: float = 30.00
    guard_pin_lead_radial: float = 0.35
    guard_cam_flat_half_deg: float = 8.00
    guard_cam_crest_deg: float = 45.00
    guard_cam_crest_half_deg: float = 2.00
    guard_cam_segments: int = 36
    guard_stop_x: float = 1.60
    guard_stop_y: float = 1.60
    guard_stop_z: float = 4.00
    guard_lift_tab_x: float = 4.00
    guard_lift_tab_y: float = 8.00
    guard_lift_tab_z: float = 2.00
    fire_btn_size: float = 10.50
    fire_btn_head_t: float = 3.60
    fire_btn_proud: float = 3.00
    fire_btn_travel: float = 3.50
    fire_btn_flange: float = 12.50
    fire_btn_flange_t: float = 1.20
    fire_btn_force_n: float = 3.20
    fire_btn_deboss_depth: float = 0.50
    fire_btn_deboss_stroke: float = 1.20
    fire_btn_deboss_cap_h: float = 6.00
    fire_btn_stop_boss_x: float = 1.80
    fire_btn_stop_boss_y: float = 1.80
    serpentine_loops: int = 6
    serpentine_loop_r: float = 5.00
    serpentine_beam_w: float = 1.10
    serpentine_beam_t: float = 4.80
    serpentine_free_h: float = 13.50
    fire_btn_stop_reserve: float = 1.00
    serpentine_beam_w_petg: float = 0.92
    serpentine_beam_t_petg: float = 5.40
    serpentine_loop_dev_len_petg: float = 12.10
    # ATH_06 is PETG.  The two-level arm layout is the approved resolution of
    # the four-arm, 150-degree planar-overlap conflict: opposite arms share a
    # plane and the two planes are separated by the printable-gap minimum.
    hat_center_x: float = 46.00
    hat_cap_od: float = 17.50
    hat_cap_h: float = 11.50
    hat_ball_d: float = 7.50
    hat_deflection_deg: float = 14.00
    hat_arm_r: float = 7.00
    hat_spring_arm_count: int = 4
    hat_arm_sweep_deg: float = 150.00
    hat_arm_mean_r: float = 6.50
    hat_spring_arm_width: float = 4.00
    hat_spring_arm_thick: float = 0.85
    hat_spring_arm_width_petg: float = 2.35
    hat_spring_arm_thick_petg: float = 1.20
    hat_detent_nose_r: float = 1.00
    hat_detent_depth: float = 0.60
    hat_detent_flank_deg: float = 40.00
    hat_force_n: float = 2.80
    hat_recess_relief_deg: float = 16.00
    hat_recess_clearance_r: float = 0.50
    hat_retention_lip_r: float = 8.00
    hat_retention_lip_undercut: float = 1.20
    hat_bayonet_gap_deg: float = 40.00
    guard_hinge_slot_w: float = 2.10
    guard_stanchion_len: float = 9.00
    guard_stanchion_t: float = 3.20

    @property
    def flank_z(self) -> float: return self.chassis_width / 2
    @property
    def seam_x_max(self) -> float: return self.chassis_length - self.front_lower_chamfer
    @property
    def overall_length(self) -> float: return self.chassis_length + self.bezel_protrusion + self.guard_hood_h - self.guard_recess_depth
    @property
    def overall_height(self) -> float: return self.hat_cap_protrusion + self.chassis_height + self.grip_drop
    @property
    def deck_y(self) -> float: return self.chassis_height
    @property
    def hat_base_y(self) -> float: return self.deck_y - (self.hat_cap_h - self.hat_cap_protrusion)
    @property
    def hat_ball_r(self) -> float: return self.hat_ball_d / 2
    @property
    def hat_ball_bottom_y(self) -> float: return self.hat_base_y - self.hat_ball_r
    @property
    def hat_cradle_d(self) -> float: return self.hat_ball_d + 2 * self.fit_clearance_rotary
    @property
    def hat_recess_d(self) -> float: return self.hat_cap_od + 2 * self.hat_recess_clearance_r
    @property
    def hat_recess_depth(self) -> float: return self.hat_cap_h - self.hat_cap_protrusion
    @property
    def hat_spring_arm_len(self) -> float: return self.hat_arm_mean_r * radians(self.hat_arm_sweep_deg)
    @property
    def hat_spring_arm_width_active(self) -> float:
        return self.hat_spring_arm_width_petg if self.material == "PETG" else self.hat_spring_arm_width
    @property
    def hat_spring_arm_thick_active(self) -> float:
        return self.hat_spring_arm_thick_petg if self.material == "PETG" else self.hat_spring_arm_thick
    @property
    def hat_lower_arm_y(self) -> float: return self.hat_ball_bottom_y
    @property
    def hat_upper_arm_y(self) -> float:
        return self.hat_lower_arm_y + self.hat_spring_arm_thick_active + self.gap_print_min
    @property
    def hat_tip_deflect(self) -> float: return self.hat_arm_r * sin(radians(self.hat_deflection_deg))
    @property
    def hat_arm_stiffness_n_per_mm(self) -> float:
        inertia = self.hat_spring_arm_width_active * self.hat_spring_arm_thick_active ** 3 / 12
        return 3 * self.e_flex_mpa * inertia / self.hat_spring_arm_len ** 3
    @property
    def hat_force_computed_n(self) -> float:
        return self.hat_spring_arm_count * self.hat_arm_stiffness_n_per_mm * self.hat_tip_deflect
    @property
    def hat_stress_mpa(self) -> float:
        return 3 * self.e_flex_mpa * self.hat_tip_deflect * self.hat_spring_arm_thick_active / (2 * self.hat_spring_arm_len ** 2)
    @property
    def hat_rim_drop(self) -> float: return (self.hat_cap_od / 2) * sin(radians(self.hat_deflection_deg))
    @property
    def hat_arm_outer_r(self) -> float: return self.hat_arm_mean_r + self.hat_spring_arm_width_active / 2
    @property
    def trim_wheel_center_y(self) -> float: return self.trim_wheel_od / 2 - self.trim_rim_proud
    @property
    def trim_pocket_d(self) -> float: return self.trim_wheel_od + 2 * self.trim_pocket_clear_r
    @property
    def trim_pocket_x0(self) -> float: return self.trim_wheel_center_x - self.trim_pocket_d / 2
    @property
    def trim_pocket_depth(self) -> float: return self.trim_wheel_width + 2 * self.trim_pocket_clear_z
    @property
    def trim_pocket_floor_z(self) -> float: return self.flank_z - self.trim_pocket_depth
    @property
    def trim_post_len(self) -> float: return self.trim_pocket_depth - self.trim_pocket_clear_z
    @property
    def trim_bore_d(self) -> float: return self.trim_post_d + 2 * self.fit_clearance_rotary
    @property
    def trim_wheel_mid_z(self) -> float: return self.trim_pocket_floor_z + self.trim_pocket_clear_z + self.trim_wheel_width / 2
    @property
    def trim_wheel_min_z(self) -> float: return self.trim_wheel_mid_z - self.trim_wheel_width / 2
    @property
    def trim_wheel_max_z(self) -> float: return self.trim_wheel_mid_z + self.trim_wheel_width / 2
    @property
    def trim_counterbore_d(self) -> float: return self.trim_snap_head_d + self.fit_clearance_snap
    @property
    def trim_counterbore_depth(self) -> float: return self.trim_snap_head_t + self.hole_comp
    @property
    def trim_ratchet_cut_depth(self) -> float: return self.trim_wheel_width - self.wall_internal
    @property
    def ratchet_tooth_pitch(self) -> float: return 2 * pi * self.ratchet_pitch_r / self.ratchet_teeth_count
    @property
    def ratchet_incl_angle_deg(self) -> float: return 2 * degrees(atan(self.ratchet_tooth_pitch / (2 * self.ratchet_tooth_depth)))
    @property
    def ratchet_tip_r(self) -> float: return self.ratchet_pitch_r - self.ratchet_tooth_depth / 2
    @property
    def ratchet_root_r(self) -> float: return self.ratchet_pitch_r + self.ratchet_tooth_depth / 2
    @property
    def ratchet_web(self) -> float: return self.ratchet_tip_r - self.trim_bore_d / 2
    @property
    def ratchet_ramp_factor(self) -> float:
        flank = radians(self.ratchet_incl_angle_deg / 2)
        return (tan(flank) + self.mu_pla) / (1 - self.mu_pla * tan(flank))
    @property
    def pawl_deflect(self) -> float: return self.pawl_preload + self.ratchet_tooth_depth
    @property
    def pawl_stiffness_n_per_mm(self) -> float:
        inertia = self.pawl_width * self.pawl_thickness ** 3 / 12
        return 3 * self.e_flex_mpa * inertia / self.pawl_len ** 3
    @property
    def pawl_force_n(self) -> float: return self.pawl_stiffness_n_per_mm * self.pawl_deflect
    @property
    def pawl_torque_nmm(self) -> float: return self.pawl_force_n * self.ratchet_ramp_factor * self.ratchet_pitch_r
    @property
    def pawl_stress_mpa(self) -> float:
        return 3 * self.e_flex_mpa * self.pawl_deflect * self.pawl_thickness / (2 * self.pawl_len ** 2)
    @property
    def pawl_rest_stress_mpa(self) -> float:
        return 3 * self.e_flex_mpa * self.pawl_preload * self.pawl_thickness / (2 * self.pawl_len ** 2)
    @property
    def pawl_snap_strain(self) -> float:
        return 3 * ((self.trim_snap_head_d - self.trim_bore_d) / 2) * self.trim_snap_head_t / (2 * self.trim_snap_slot_len ** 2)
    @property
    def trim_safe_snap_hook_station_x(self) -> float:
        return self.trim_pocket_x0 - self.wall_internal - self.snap_hook_len / 2
    @property
    def pawl_root_y(self) -> float: return self.trim_wheel_center_y + self.pawl_len
    @property
    def pawl_tip_x(self) -> float: return self.trim_wheel_center_x + self.ratchet_pitch_r
    @property
    def pawl_leaf_top_z(self) -> float: return self.trim_wheel_min_z - self.eps
    @property
    def pawl_leaf_center_z(self) -> float: return self.pawl_leaf_top_z - self.pawl_thickness / 2
    @property
    def pawl_nose_d(self) -> float: return self.feature_min
    @property
    def pawl_nose_h(self) -> float: return self.pawl_preload
    @property
    def knurl_line_count(self) -> int: return self.knurl_facets // 2
    @property
    def knurl_line_pitch(self) -> float: return 2 * pi * (self.trim_wheel_od / 2) / self.knurl_line_count
    @property
    def knurl_groove_w(self) -> float: return self.knurl_line_pitch / 3
    @property
    def collar_depth(self) -> float: return self.bezel_depth - self.bezel_protrusion
    @property
    def rail_len(self) -> float: return self.throttle_carriage_len + self.throttle_stroke + 2 * self.rail_end_clear
    @property
    def rail_end_x(self) -> float: return self.rail_start_x + self.rail_len
    @property
    def dovetail_depth(self) -> float: return (self.dovetail_base_w - self.dovetail_mouth_w) / (2 * tan(radians(self.dovetail_angle_deg)))
    @property
    def channel_floor_z(self) -> float: return self.flank_z - self.rail_channel_depth
    @property
    def dovetail_floor_z(self) -> float: return self.channel_floor_z - self.dovetail_depth
    @property
    def throttle_tenon_base_w(self) -> float: return self.dovetail_base_w - 2 * self.fit_clearance_sliding
    @property
    def throttle_tenon_mouth_w(self) -> float: return self.dovetail_mouth_w - 2 * self.fit_clearance_sliding
    @property
    def throttle_leaf_width_active(self) -> float:
        return self.throttle_leaf_width_petg if self.material == "PETG" else self.throttle_leaf_width
    @property
    def throttle_leaf_thick_active(self) -> float:
        return self.throttle_leaf_thick_petg if self.material == "PETG" else self.throttle_leaf_thick
    @property
    def throttle_carriage_plate_t_active(self) -> float:
        return self.carriage_plate_t_petg if self.material == "PETG" else self.carriage_plate_t
    @property
    def throttle_leaf_arm_len(self) -> float:
        return (self.throttle_leaf_len - (self.throttle_leaf_arms - 1) * pi * self.throttle_leaf_fold_r) / self.throttle_leaf_arms
    @property
    def throttle_leaf_env_x_active(self) -> float:
        return self.throttle_leaf_arm_len + self.throttle_leaf_fold_r + self.throttle_leaf_width_active / 2
    @property
    def throttle_leaf_env_y_active(self) -> float:
        return (self.throttle_leaf_arms - 1) * 2 * self.throttle_leaf_fold_r + self.throttle_leaf_width_active
    @property
    def throttle_leaf_tip_offset_nominal(self) -> float:
        return self.throttle_leaf_arm_len + self.throttle_leaf_fold_r + self.throttle_leaf_width / 2
    @property
    def throttle_leaf_placement_offset(self) -> float:
        return self.throttle_leaf_tip_offset_nominal - self.throttle_leaf_env_x_active
    @property
    def throttle_follower_home_x(self) -> float:
        return self.rail_end_clear + self.throttle_leaf_tip_offset_nominal
    @property
    def afterburner_travel(self) -> float: return self.throttle_stroke * self.afterburner_pos_ratio
    @property
    def ramp_apex_x(self) -> float: return self.throttle_follower_home_x + self.afterburner_travel
    @property
    def ramp_run_up(self) -> float: return self.afterburner_lift / tan(radians(self.afterburner_ramp_angle_deg))
    @property
    def ramp_drop_off(self) -> float: return self.afterburner_lift / tan(radians(self.afterburner_drop_angle_deg))
    @property
    def ramp_footprint(self) -> float: return self.ramp_run_up + self.ramp_drop_off
    @property
    def throttle_leaf_deflect(self) -> float: return self.throttle_detent_preload + self.afterburner_lift
    @property
    def throttle_ramp_factor(self) -> float:
        angle = radians(self.afterburner_ramp_angle_deg)
        return (tan(angle) + self.mu_pla) / (1 - self.mu_pla * tan(angle))
    @property
    def throttle_leaf_stiffness_n_per_mm(self) -> float:
        inertia = self.throttle_leaf_width_active * self.throttle_leaf_thick_active ** 3 / 12
        return 3 * self.e_flex_mpa * inertia / self.throttle_leaf_len ** 3
    @property
    def throttle_leaf_normal_force_n(self) -> float: return self.throttle_leaf_stiffness_n_per_mm * self.throttle_leaf_deflect
    @property
    def throttle_break_force_computed_n(self) -> float: return self.throttle_leaf_normal_force_n * self.throttle_ramp_factor
    @property
    def throttle_leaf_stress_mpa(self) -> float:
        return 3 * self.e_flex_mpa * self.throttle_leaf_deflect * self.throttle_leaf_thick_active / (2 * self.throttle_leaf_len ** 2)
    @property
    def throttle_leaf_rest_stress_mpa(self) -> float:
        return 3 * self.e_flex_mpa * self.throttle_detent_preload * self.throttle_leaf_thick_active / (2 * self.throttle_leaf_len ** 2)
    @property
    def throttle_tab_h_z(self) -> float:
        return self.rail_channel_depth - self.throttle_carriage_plate_t_active - self.tab_recess
    @property
    def throttle_guide_ratio(self) -> float: return self.throttle_carriage_len / self.dovetail_base_w
    @property
    def key_socket_side(self) -> float: return self.key_side + 2 * self.fit_clearance_static
    @property
    def key_socket_depth(self) -> float: return self.key_len / 2 + self.fit_clearance_static
    @property
    def seam_groove_w(self) -> float: return self.seam_tongue_thick + 2 * self.fit_clearance_snap
    @property
    def seam_groove_d(self) -> float: return self.seam_tongue_height + self.fit_clearance_snap
    @property
    def snap_pocket_w(self) -> float: return self.snap_hook_w + 2 * self.fit_clearance_snap
    @property
    def grip_axial_len(self) -> float: return self.grip_drop / sin(radians(self.grip_rake_angle_deg))
    @property
    def grip_butt_x(self) -> float: return self.grip_root_x + self.grip_drop / tan(radians(self.grip_rake_angle_deg))
    @property
    def grip_x_min(self) -> float: return self.grip_butt_x - self.grip_butt_depth / 2 * sin(radians(self.grip_rake_angle_deg))
    @property
    def grip_groove_start(self) -> float: return self.grip_groove_start_ratio * self.grip_axial_len
    @property
    def e_flex_mpa(self) -> float: return 2000.0 if self.material == "PETG" else 3300.0
    @property
    def sigma_allow_cyclic_mpa(self) -> float: return 22.0 if self.material == "PETG" else 25.0
    @property
    def sigma_allow_sustained_mpa(self) -> float: return 6.0 if self.material == "PETG" else 8.0
    @property
    def strain_assembly_max(self) -> float: return 0.025 if self.material == "PETG" else 0.015
    @property
    def bezel_front_x(self) -> float: return self.chassis_length + self.bezel_protrusion
    @property
    def bezel_rear_x(self) -> float: return self.bezel_front_x - self.bezel_depth
    @property
    def bezel_cavity_w(self) -> float: return self.collar_w + 2 * self.fit_clearance_static
    @property
    def bezel_cavity_h(self) -> float: return self.collar_h + 2 * self.fit_clearance_static
    @property
    def fire_btn_bore(self) -> float: return self.fire_btn_size + 2 * self.fit_clearance_sliding
    @property
    def btn_shoulder_pocket(self) -> float: return self.fire_btn_bore + 2 * self.bezel_chamfer
    @property
    def recess_floor_x(self) -> float: return self.bezel_front_x - self.guard_recess_depth
    @property
    def btn_head_front_x(self) -> float: return self.recess_floor_x + self.fire_btn_proud
    @property
    def btn_head_rear_x(self) -> float: return self.btn_head_front_x - self.fire_btn_head_t
    @property
    def btn_flange_rear_x(self) -> float: return self.btn_head_rear_x - self.fire_btn_flange_t
    @property
    def serpentine_anchor_rear_x(self) -> float: return self.btn_flange_rear_x - self.serpentine_free_h
    @property
    def serpentine_anchor_front_x(self) -> float: return self.serpentine_anchor_rear_x + self.fire_btn_flange_t
    @property
    def serpentine_beam_w_active(self) -> float:
        return self.serpentine_beam_w_petg if self.material == "PETG" else self.serpentine_beam_w
    @property
    def serpentine_beam_t_active(self) -> float:
        return self.serpentine_beam_t_petg if self.material == "PETG" else self.serpentine_beam_t
    @property
    def serpentine_loop_dev_len(self) -> float:
        return self.serpentine_loop_dev_len_petg if self.material == "PETG" else pi * self.serpentine_loop_r
    @property
    def serpentine_pitch(self) -> float: return self.serpentine_free_h / self.serpentine_loops
    @property
    def serpentine_gap(self) -> float: return self.serpentine_pitch - self.serpentine_beam_w_active
    @property
    def serpentine_solid_h(self) -> float: return self.serpentine_loops * self.serpentine_beam_w_active + 2 * self.fire_btn_flange_t
    @property
    def serpentine_work_h(self) -> float: return self.serpentine_free_h - self.fire_btn_travel
    @property
    def serpentine_stiffness_n_per_mm(self) -> float:
        return self.e_flex_mpa * self.serpentine_beam_t_active * self.serpentine_beam_w_active ** 3 / (self.serpentine_loops * self.serpentine_loop_dev_len ** 3)
    @property
    def serpentine_force_n(self) -> float: return self.serpentine_stiffness_n_per_mm * self.fire_btn_travel
    @property
    def serpentine_stress_mpa(self) -> float:
        return 3 * self.e_flex_mpa * self.fire_btn_travel * self.serpentine_beam_w_active / (self.serpentine_loops * self.serpentine_loop_dev_len ** 2)
    @property
    def serpentine_clearance_z(self) -> float: return (self.snout_spring_cavity_z - self.serpentine_beam_t_active) / 2
    @property
    def guard_hinge_x(self) -> float: return self.bezel_front_x - 1.00
    @property
    def guard_hinge_y(self) -> float: return self.bezel_center_y + self.bezel_h / 2 - 2.00
    @property
    def guard_closed_x(self) -> float: return self.bezel_front_x - self.guard_recess_depth + self.guard_hood_h
    @property
    def guard_hood_min_x(self) -> float: return self.guard_closed_x - self.guard_hood_h
    @property
    def guard_hood_min_y(self) -> float: return self.guard_hinge_y - self.guard_hood_l
    @property
    def guard_hood_center_x(self) -> float: return (self.guard_hood_min_x + self.guard_closed_x) / 2
    @property
    def guard_hood_center_y(self) -> float: return (self.guard_hood_min_y + self.guard_hinge_y) / 2
    @property
    def guard_lift_tab_center_y(self) -> float: return self.guard_hood_min_y + self.guard_lift_tab_y / 4
    @property
    def guard_inner_clear(self) -> float: return self.guard_hood_h - self.guard_wall - self.gap_print_min
    @property
    def guard_pin_axis_z(self) -> float: return self.guard_hood_w / 2 + self.guard_pin_len / 2
    @property
    def guard_pin_outer_z(self) -> float: return self.guard_hood_w / 2 + self.guard_pin_len
    @property
    def guard_hinge_notch_depth(self) -> float: return self.fit_clearance_pivot + self.eps
    @property
    def guard_hinge_notch_center_z(self) -> float: return self.guard_hood_w / 2 - self.fit_clearance_pivot / 2 + self.eps / 2
    @property
    def guard_pin_lead_len(self) -> float: return self.guard_pin_lead_radial / tan(radians(self.guard_pin_lead_angle_deg))
    @property
    def guard_cam_flat_contact_y(self) -> float: return self.guard_hinge_y - self.guard_cam_base_r
    @property
    def guard_cam_leaf_clear_y(self) -> float: return self.guard_cam_flat_contact_y - self.guard_cam_lobe
    @property
    def guard_cam_leaf_center_y(self) -> float: return self.guard_cam_leaf_clear_y - self.guard_cam_leaf_t / 2
    @property
    def bezel_barb_z_offset(self) -> float: return self.guard_cam_leaf_w / 2 + self.bezel_barb_w / 2 + self.fit_clearance_static
    @property
    def guard_pin_hole_d(self) -> float: return self.guard_pin_d + 2 * self.fit_clearance_pivot
    @property
    def cam_leaf_deflection(self) -> float: return self.guard_cam_lobe
    @property
    def cam_leaf_stiffness_n_per_mm(self) -> float:
        return self.e_flex_mpa * self.guard_cam_leaf_w * self.guard_cam_leaf_t ** 3 / (4 * self.guard_cam_leaf_len ** 3)
    @property
    def cam_leaf_force_n(self) -> float: return self.cam_leaf_stiffness_n_per_mm * self.cam_leaf_deflection
    @property
    def cam_leaf_stress_mpa(self) -> float:
        return 3 * self.e_flex_mpa * self.cam_leaf_deflection * self.guard_cam_leaf_t / (2 * self.guard_cam_leaf_len ** 2)
    @property
    def cam_leaf_rest_stress_mpa(self) -> float: return 0.0
    @property
    def bezel_barb_strain(self) -> float:
        return 3 * (self.snap_undercut + self.fit_clearance_snap) * self.bezel_barb_t / (2 * self.bezel_barb_len ** 2)

    @property
    def trigger_stage1_thick_active(self) -> float:
        return self.trigger_stage1_thick_petg if self.material == "PETG" else self.trigger_stage1_thick

    @property
    def trigger_stage1_width_active(self) -> float:
        return self.trigger_stage1_width_petg if self.material == "PETG" else self.trigger_stage1_width

    @property
    def trigger_stage2_thick_active(self) -> float:
        return self.trigger_stage2_thick_petg if self.material == "PETG" else self.trigger_stage2_thick

    @property
    def trigger_stage2_width_active(self) -> float:
        return self.trigger_stage2_width_petg if self.material == "PETG" else self.trigger_stage2_width

    @property
    def trigger_stage1_deg(self) -> float:
        return degrees(asin(self.trigger_stage1_travel / self.trigger_contact_r))

    @property
    def trigger_stage1_stiffness_n_per_mm(self) -> float:
        inertia = self.trigger_stage1_width_active * self.trigger_stage1_thick_active ** 3 / 12
        return 3 * self.e_flex_mpa * inertia / self.trigger_stage1_len ** 3

    @property
    def trigger_stage1_force_computed_n(self) -> float:
        return self.trigger_stage1_stiffness_n_per_mm * self.trigger_stage1_travel

    @property
    def trigger_stage1_stress_mpa(self) -> float:
        return 3 * self.e_flex_mpa * self.trigger_stage1_travel * self.trigger_stage1_thick_active / (2 * self.trigger_stage1_len ** 2)

    @property
    def trigger_stage2_stiffness_n_per_mm(self) -> float:
        inertia = self.trigger_stage2_width_active * self.trigger_stage2_thick_active ** 3 / 12
        return 3 * self.e_flex_mpa * inertia / self.trigger_stage2_len ** 3

    @property
    def trigger_stage2_normal_force_n(self) -> float:
        return self.trigger_stage2_stiffness_n_per_mm * self.trigger_stage2_deflect

    @property
    def trigger_gate_ramp_factor(self) -> float:
        gate = radians(self.trigger_gate_angle_deg)
        return (tan(gate) + self.mu_pla) / (1 - self.mu_pla * tan(gate))

    @property
    def trigger_stage2_tangential_force_n(self) -> float:
        return self.trigger_stage2_normal_force_n * self.trigger_gate_ramp_factor

    @property
    def trigger_tooth_r(self) -> float:
        return (self.trigger_break_force_n - self.trigger_stage1_force_n) * self.trigger_contact_r / self.trigger_stage2_tangential_force_n

    @property
    def trigger_break_force_computed_n(self) -> float:
        return self.trigger_stage1_force_computed_n + self.trigger_stage2_tangential_force_n * self.trigger_tooth_r / self.trigger_contact_r

    @property
    def trigger_stage2_stress_mpa(self) -> float:
        return 3 * self.e_flex_mpa * self.trigger_stage2_deflect * self.trigger_stage2_thick_active / (2 * self.trigger_stage2_len ** 2)

    @property
    def trigger_overtravel_deg_total(self) -> float:
        return self.trigger_travel_deg + self.trigger_overtravel_deg

    @property
    def trigger_socket_nominal_d(self) -> float:
        return self.trigger_trunnion_d + 2 * self.fit_clearance_pivot

    def validate(self) -> None:
        """Phase 1 subset of ASSERT-01..23 that is owned by these parts."""
        checks = {
            "ASSERT-01 X dimensional chain": abs(self.overall_length - 86.00) < 1e-6,
            "ASSERT-02 Y dimensional chain": abs(self.overall_height - 72.00) < 1e-6,
            "ASSERT-03 grip width budget": self.palm_swell_width <= self.chassis_width,
            "ASSERT-04 rail/pocket wall": self.rail_end_x + self.wall_internal <= self.trim_wheel_center_x - self.trim_pocket_d / 2,
            "ASSERT-11 afterburner ramp footprint": self.ramp_footprint < self.throttle_stroke * (1 - self.afterburner_pos_ratio),
            "ASSERT-12 throttle guide ratio": self.throttle_guide_ratio >= 1.40,
            "ASSERT-21 throttle follower stays on rail": self.throttle_follower_home_x + self.throttle_stroke <= self.rail_len,
            "ASSERT-22 folded throttle leaf fits carriage": self.throttle_leaf_env_x_active <= self.throttle_carriage_len and self.throttle_leaf_env_y_active <= self.dovetail_base_w,
            "ASSERT-23 folded throttle arms separate": 2 * self.throttle_leaf_fold_r - self.throttle_leaf_width_active >= self.gap_print_min,
            "ASSERT-43 throttle tab positive thickness": self.throttle_tab_h_z >= self.feature_min,
            "ASSERT-44 PETG throttle cyclic stress": self.material != "PETG" or self.throttle_leaf_stress_mpa <= self.sigma_allow_cyclic_mpa,
            "ASSERT-45 PETG throttle preload stress": self.material != "PETG" or self.throttle_leaf_rest_stress_mpa <= self.sigma_allow_sustained_mpa,
            "ASSERT-46 PETG throttle break force": self.material != "PETG" or abs(self.throttle_break_force_computed_n - self.throttle_break_force_n) / self.throttle_break_force_n <= 0.15,
            "ASSERT-05 ratchet web": self.ratchet_web >= self.feature_min,
            "ASSERT-16 flexure minimum": self.pawl_thickness >= 0.75,
            "ASSERT-17 wall minima": self.wall_exterior >= 2.40 and self.wall_internal >= 1.60,
            "ASSERT-19 seam stations": all(station < self.seam_x_max for station in self.snap_hook_stations_x + self.key_stations_x),
            "ASSERT-20 trim rim protrusion": abs(self.trim_wheel_center_y - self.trim_wheel_od / 2 + self.trim_rim_proud) < 1e-6,
            "ASSERT-G2 positive fold length": self.pawl_len > 0,
            "ASSERT-34 trim counterbore clears snap head": self.trim_counterbore_d > self.trim_snap_head_d,
            "ASSERT-35 trim ratchet web depth": abs(self.trim_wheel_width - self.trim_ratchet_cut_depth - self.wall_internal) < 1e-6,
            "ASSERT-36 trim snap strain": self.pawl_snap_strain <= self.strain_assembly_max,
            "ASSERT-37 PLA ratchet cyclic stress": self.material != "PLA_PLUS" or self.pawl_stress_mpa <= self.sigma_allow_cyclic_mpa,
            "ASSERT-38 PLA ratchet preload stress": self.material != "PLA_PLUS" or self.pawl_rest_stress_mpa <= self.sigma_allow_sustained_mpa,
            "ASSERT-39 PLA ratchet torque": self.material != "PLA_PLUS" or abs(self.pawl_torque_nmm - self.ratchet_torque_nmm) / self.ratchet_torque_nmm <= 0.05,
            "ASSERT-40 trim-safe seam hook": self.trim_safe_snap_hook_station_x + self.snap_hook_len / 2 + self.wall_internal <= self.trim_pocket_x0,
            "ASSERT-41 pawl fits below wheel": self.pawl_leaf_top_z < self.trim_wheel_min_z,
            "ASSERT-42 pawl root reaches top deck": self.pawl_root_y < self.deck_y,
            "ASSERT-07 guard clearance": self.guard_hood_h - self.guard_wall - self.gap_print_min >= 0,
            "ASSERT-06 fire-button solid-height reserve": self.serpentine_work_h - self.serpentine_solid_h >= self.fire_btn_stop_reserve,
            "ASSERT-08 serpentine inter-loop clearance": self.serpentine_gap >= self.fire_btn_travel / self.serpentine_loops + self.gap_print_min,
            "ASSERT-10 fire-button spring cavity clearance": self.serpentine_clearance_z >= self.fit_clearance_sliding,
            "ASSERT-27 fire-button PETG cyclic stress": self.material != "PETG" or self.serpentine_stress_mpa <= self.sigma_allow_cyclic_mpa,
            "ASSERT-28 fire-button PETG return-force band": self.material != "PETG" or 2.70 <= self.serpentine_force_n <= 3.70,
            "ASSERT-29 fire-button axial stack": abs(self.serpentine_anchor_rear_x - (self.snout_cavity_rear_x + 0.20)) < 1e-6,
            "ASSERT-15 bezel barb strain": self.bezel_barb_strain <= self.strain_assembly_max,
            "ASSERT-24 guard cam leaf stress": self.cam_leaf_stress_mpa <= self.sigma_allow_cyclic_mpa,
            "ASSERT-25 guard lead-in geometry": 0 < self.guard_pin_lead_len < self.guard_pin_len,
            "ASSERT-26 guard cam shape": self.guard_cam_flat_half_deg < self.guard_cam_crest_deg < self.guard_open_deg - self.guard_cam_flat_half_deg,
            "ASSERT-09 hat recess relief": self.hat_recess_relief_deg >= self.hat_deflection_deg + 2,
            "ASSERT-30 hat arm fits cap": max(self.hat_arm_outer_r, self.hat_arm_r + self.hat_detent_nose_r) <= self.hat_cap_od / 2,
            "ASSERT-31 hat arm planes separate": self.hat_upper_arm_y >= self.hat_lower_arm_y + self.hat_spring_arm_thick_active + self.gap_print_min,
            "ASSERT-32 hat cyclic stress": self.hat_stress_mpa <= self.sigma_allow_cyclic_mpa,
            "ASSERT-33 hat force target": abs(self.hat_force_computed_n - self.hat_force_n) / self.hat_force_n <= 0.15,
            "ASSERT-47 trigger pivot fit": abs(self.trigger_socket_nominal_d - self.trigger_socket_d) < 1e-6,
            "ASSERT-48 trigger stage-1 stress": self.material != "PETG" or self.trigger_stage1_stress_mpa <= self.sigma_allow_cyclic_mpa,
            "ASSERT-49 trigger stage-1 force": self.material != "PETG" or abs(self.trigger_stage1_force_computed_n - self.trigger_stage1_force_n) / self.trigger_stage1_force_n <= 0.15,
            "ASSERT-50 trigger stage-2 stress": self.material != "PETG" or self.trigger_stage2_stress_mpa <= self.sigma_allow_cyclic_mpa,
            "ASSERT-51 trigger break force": self.material != "PETG" or abs(self.trigger_break_force_computed_n - self.trigger_break_force_n) / self.trigger_break_force_n <= 0.15,
            "ASSERT-52 trigger flexure minima": self.trigger_stage1_thick_active >= 0.75 and self.trigger_stage2_thick_active >= 0.75,
        }
        if self.material not in {"PLA_PLUS", "PETG"} or self.handedness not in (-1, 1):
            raise ValueError("material must be PLA_PLUS or PETG and handedness must be -1 or +1")
        failures = [name for name, passed in checks.items() if not passed]
        if failures:
            raise ValueError("; ".join(failures))

    def report(self) -> dict[str, Any]:
        self.validate()
        return {**asdict(self), "derived": {
            "overall_length": self.overall_length, "overall_height": self.overall_height,
            "overall_width": self.chassis_width, "flank_z": self.flank_z,
            "seam_x_max": self.seam_x_max, "rail_len": self.rail_len,
            "throttle_tenon_base_w": self.throttle_tenon_base_w,
            "throttle_tenon_mouth_w": self.throttle_tenon_mouth_w,
            "throttle_leaf_width_active": self.throttle_leaf_width_active,
            "throttle_leaf_thick_active": self.throttle_leaf_thick_active,
            "throttle_carriage_plate_t_active": self.throttle_carriage_plate_t_active,
            "throttle_leaf_arm_len": self.throttle_leaf_arm_len,
            "throttle_leaf_env_x_active": self.throttle_leaf_env_x_active,
            "throttle_leaf_env_y_active": self.throttle_leaf_env_y_active,
            "throttle_follower_home_x": self.throttle_follower_home_x,
            "ramp_apex_x": self.ramp_apex_x, "ramp_footprint": self.ramp_footprint,
            "throttle_leaf_deflect": self.throttle_leaf_deflect,
            "throttle_leaf_stiffness_n_per_mm": self.throttle_leaf_stiffness_n_per_mm,
            "throttle_break_force_computed_n": self.throttle_break_force_computed_n,
            "throttle_leaf_stress_mpa": self.throttle_leaf_stress_mpa,
            "throttle_leaf_rest_stress_mpa": self.throttle_leaf_rest_stress_mpa,
            "throttle_tab_h_z": self.throttle_tab_h_z,
            "throttle_guide_ratio": self.throttle_guide_ratio,
            "trim_pocket_floor_z": self.trim_pocket_floor_z,
            "trim_bore_d": self.trim_bore_d, "trim_wheel_mid_z": self.trim_wheel_mid_z,
            "trim_pocket_x0": self.trim_pocket_x0, "trim_safe_snap_hook_station_x": self.trim_safe_snap_hook_station_x,
            "trim_counterbore_d": self.trim_counterbore_d, "trim_counterbore_depth": self.trim_counterbore_depth,
            "ratchet_tooth_pitch": self.ratchet_tooth_pitch, "ratchet_incl_angle_deg": self.ratchet_incl_angle_deg,
            "ratchet_tip_r": self.ratchet_tip_r, "ratchet_root_r": self.ratchet_root_r,
            "ratchet_web": self.ratchet_web, "pawl_stiffness_n_per_mm": self.pawl_stiffness_n_per_mm,
            "pawl_force_n": self.pawl_force_n, "pawl_torque_nmm": self.pawl_torque_nmm,
            "pawl_stress_mpa": self.pawl_stress_mpa, "pawl_rest_stress_mpa": self.pawl_rest_stress_mpa,
            "pawl_snap_strain": self.pawl_snap_strain,
            "pawl_root_y": self.pawl_root_y, "pawl_tip_x": self.pawl_tip_x,
            "pawl_leaf_top_z": self.pawl_leaf_top_z, "pawl_nose_d": self.pawl_nose_d,
            "grip_axial_len": self.grip_axial_len, "grip_butt_x": self.grip_butt_x,
            "bezel_front_x": self.bezel_front_x, "bezel_rear_x": self.bezel_rear_x,
            "bezel_cavity_w": self.bezel_cavity_w, "bezel_cavity_h": self.bezel_cavity_h,
            "fire_btn_bore": self.fire_btn_bore, "btn_shoulder_pocket": self.btn_shoulder_pocket,
            "recess_floor_x": self.recess_floor_x, "btn_head_front_x": self.btn_head_front_x,
            "btn_head_rear_x": self.btn_head_rear_x, "btn_flange_rear_x": self.btn_flange_rear_x,
            "serpentine_anchor_rear_x": self.serpentine_anchor_rear_x,
            "serpentine_anchor_front_x": self.serpentine_anchor_front_x,
            "serpentine_beam_w_active": self.serpentine_beam_w_active,
            "serpentine_beam_t_active": self.serpentine_beam_t_active,
            "serpentine_loop_dev_len": self.serpentine_loop_dev_len,
            "serpentine_pitch": self.serpentine_pitch, "serpentine_gap": self.serpentine_gap,
            "serpentine_solid_h": self.serpentine_solid_h, "serpentine_work_h": self.serpentine_work_h,
            "serpentine_stiffness_n_per_mm": self.serpentine_stiffness_n_per_mm,
            "serpentine_force_n": self.serpentine_force_n,
            "serpentine_stress_mpa": self.serpentine_stress_mpa,
            "serpentine_clearance_z": self.serpentine_clearance_z,
            "guard_hinge_x": self.guard_hinge_x, "guard_hinge_y": self.guard_hinge_y,
            "guard_closed_x": self.guard_closed_x, "guard_hood_min_x": self.guard_hood_min_x,
            "guard_hood_min_y": self.guard_hood_min_y, "guard_inner_clear": self.guard_inner_clear,
            "guard_lift_tab_center_y": self.guard_lift_tab_center_y,
            "guard_pin_axis_z": self.guard_pin_axis_z, "guard_pin_outer_z": self.guard_pin_outer_z,
            "guard_hinge_notch_depth": self.guard_hinge_notch_depth,
            "guard_cam_flat_contact_y": self.guard_cam_flat_contact_y,
            "guard_cam_leaf_clear_y": self.guard_cam_leaf_clear_y,
            "guard_cam_leaf_center_y": self.guard_cam_leaf_center_y,
            "bezel_barb_z_offset": self.bezel_barb_z_offset,
            "guard_pin_hole_d": self.guard_pin_hole_d,
            "cam_leaf_stiffness_n_per_mm": self.cam_leaf_stiffness_n_per_mm,
            "cam_leaf_force_n": self.cam_leaf_force_n,
            "cam_leaf_stress_mpa": self.cam_leaf_stress_mpa,
            "cam_leaf_rest_stress_mpa": self.cam_leaf_rest_stress_mpa,
            "bezel_barb_strain": self.bezel_barb_strain,
            "deck_y": self.deck_y, "hat_base_y": self.hat_base_y,
            "hat_ball_bottom_y": self.hat_ball_bottom_y, "hat_cradle_d": self.hat_cradle_d,
            "hat_recess_d": self.hat_recess_d, "hat_recess_depth": self.hat_recess_depth,
            "hat_spring_arm_len": self.hat_spring_arm_len,
            "hat_spring_arm_width_active": self.hat_spring_arm_width_active,
            "hat_spring_arm_thick_active": self.hat_spring_arm_thick_active,
            "hat_lower_arm_y": self.hat_lower_arm_y, "hat_upper_arm_y": self.hat_upper_arm_y,
            "hat_tip_deflect": self.hat_tip_deflect,
            "hat_arm_stiffness_n_per_mm": self.hat_arm_stiffness_n_per_mm,
            "hat_force_computed_n": self.hat_force_computed_n,
            "hat_stress_mpa": self.hat_stress_mpa, "hat_rim_drop": self.hat_rim_drop,
            "hat_arm_outer_r": self.hat_arm_outer_r,
            "trigger_socket_nominal_d": self.trigger_socket_nominal_d,
            "trigger_stage1_deg": self.trigger_stage1_deg,
            "trigger_stage1_width_active": self.trigger_stage1_width_active,
            "trigger_stage1_thick_active": self.trigger_stage1_thick_active,
            "trigger_stage1_stiffness_n_per_mm": self.trigger_stage1_stiffness_n_per_mm,
            "trigger_stage1_force_computed_n": self.trigger_stage1_force_computed_n,
            "trigger_stage1_stress_mpa": self.trigger_stage1_stress_mpa,
            "trigger_stage2_width_active": self.trigger_stage2_width_active,
            "trigger_stage2_thick_active": self.trigger_stage2_thick_active,
            "trigger_stage2_stiffness_n_per_mm": self.trigger_stage2_stiffness_n_per_mm,
            "trigger_stage2_normal_force_n": self.trigger_stage2_normal_force_n,
            "trigger_stage2_tangential_force_n": self.trigger_stage2_tangential_force_n,
            "trigger_stage2_stress_mpa": self.trigger_stage2_stress_mpa,
            "trigger_tooth_r": self.trigger_tooth_r,
            "trigger_break_force_computed_n": self.trigger_break_force_computed_n,
            "trigger_overtravel_deg_total": self.trigger_overtravel_deg_total,
        }}
