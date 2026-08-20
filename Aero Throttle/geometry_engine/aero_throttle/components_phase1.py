"""ATH_01, ATH_10, and ATH_02 solids in dependency order."""

from __future__ import annotations

from math import cos, radians, sin

import cadquery as cq

from .geometry import box, bore_z, cylinder_y, cylinder_z, key_feature, prism_xy, prism_xz, prism_yz, seam_ribbon, snap_feature
from .parameters import AeroThrottleParameters


def _cylinder_y_design(diameter: float, height: float, center: tuple[float, float, float]) -> cq.Workplane:
    """Y-axis cylinder at its requested design-frame centre.

    CadQuery's XZ workplane normal points toward -Y, while the legacy kernel
    helper predates that convention.  Keep the correction local to the new
    hat interface so previously validated Phase 1 geometry is untouched.
    """
    return cylinder_y(diameter, height, (center[0], center[1] + height, center[2]))


def _hat_cradle(p: AeroThrottleParameters) -> tuple[cq.Workplane, cq.Workplane]:
    """Return the deck recess cutter and its FC-ROTARY support/lip interface."""
    recess = _cylinder_y_design(
        p.hat_recess_d,
        p.hat_recess_depth + p.eps,
        (p.hat_center_x, p.deck_y - p.hat_recess_depth / 2 + p.eps / 2, 0),
    )
    support_h = p.wall_exterior
    support_top_y = p.hat_ball_bottom_y - p.gap_print_min
    support_outer_r = p.flank_z - p.wall_exterior + p.eps
    support = _cylinder_y_design(
        2 * support_outer_r,
        support_h,
        (p.hat_center_x, support_top_y - support_h / 2, 0),
    ).cut(_cylinder_y_design(
        p.hat_cradle_d,
        support_h + 2 * p.eps,
        (p.hat_center_x, support_top_y - support_h / 2, 0),
    ))
    for tip_angle_deg in (0, 90, 180, 270):
        angle = radians(tip_angle_deg)
        pad = _cylinder_y_design(
            2 * p.hat_detent_nose_r,
            p.gap_print_min,
            (
                p.hat_center_x + p.hat_arm_r * cos(angle),
                support_top_y + p.gap_print_min / 2,
                p.hat_arm_r * sin(angle),
            ),
        )
        support = support.union(pad)

    lip_h = p.hat_retention_lip_undercut
    lip_outer = _cylinder_y_design(p.hat_recess_d, lip_h, (p.hat_center_x, p.hat_base_y - lip_h / 2, 0))
    lip_inner = _cylinder_y_design(2 * p.hat_retention_lip_r, lip_h + 2 * p.eps, (p.hat_center_x, p.hat_base_y - lip_h / 2, 0))
    lip = lip_outer.cut(lip_inner)
    gap_width = 2 * (p.hat_retention_lip_r + (p.hat_recess_d / 2 - p.hat_retention_lip_r) / 2) * sin(radians(p.hat_bayonet_gap_deg / 2))
    for angle_deg in (0, 90, 180, 270):
        gap = box(
            p.hat_recess_d / 2,
            lip_h + 2 * p.eps,
            gap_width,
            (p.hat_center_x + p.hat_recess_d / 4, p.hat_base_y - lip_h / 2, 0),
        ).rotate((p.hat_center_x, 0, 0), (p.hat_center_x, 1, 0), angle_deg)
        lip = lip.cut(gap)
    # Four outboard columns join the interrupted lip to the chassis-connected
    # lower annulus while remaining outside ATH_06's r=8.00 nose envelope.
    strut_y_h = p.hat_base_y - support_top_y
    for angle_deg in (45, 135, 225, 315):
        strut = box(
            1.80,
            strut_y_h,
            p.wall_internal,
            (p.hat_center_x + 10.00, support_top_y + strut_y_h / 2, 0),
        ).rotate((p.hat_center_x, 0, 0), (p.hat_center_x, 1, 0), angle_deg)
        support = support.union(strut)
    # The support annulus is the load-bearing FC-ROTARY cradle.  The optional
    # spherical cup envelope above it is deliberately relieved: it would
    # occupy the same radial band as ATH_06's compliant spiral roots.
    return recess, support.union(lip)


def _trim_post_and_pawl_carrier(p: AeroThrottleParameters) -> cq.Workplane:
    """Top-deck carrier for the datum-K post and its under-wheel PLA pawl.

    The corrected Z-axis pocket opens the previous post into the chassis void.
    A structural spine therefore carries the post to the top deck.  A second,
    wider root spine clamps a 17.70 mm vertical cantilever below ATH_07; its
    0.80 mm nose enters the rest-pose ratchet valley from the -Z opening.
    """
    support_bottom_z = p.trim_pocket_floor_z - p.wall_internal
    support_top_z = p.trim_pocket_floor_z + p.eps
    post_spine_y0 = p.trim_wheel_center_y - p.trim_post_d / 2
    post_spine = box(
        p.trim_post_d + 2 * p.wall_internal,
        p.deck_y - post_spine_y0 + p.eps,
        support_top_z - support_bottom_z,
        (
            p.trim_wheel_center_x,
            post_spine_y0 + (p.deck_y - post_spine_y0) / 2,
            (support_bottom_z + support_top_z) / 2,
        ),
    )
    pawl_mount_y0 = p.pawl_root_y - p.wall_internal
    pawl_mount_top_z = p.pawl_leaf_top_z
    pawl_mount = box(
        p.pawl_width + 2 * p.wall_internal,
        p.deck_y - pawl_mount_y0 + p.eps,
        pawl_mount_top_z - support_bottom_z,
        (
            p.pawl_tip_x,
            pawl_mount_y0 + (p.deck_y - pawl_mount_y0) / 2,
            (support_bottom_z + pawl_mount_top_z) / 2,
        ),
    )
    pawl_leaf = box(
        p.pawl_width,
        p.pawl_len + p.eps,
        p.pawl_thickness,
        (
            p.pawl_tip_x,
            p.trim_wheel_center_y + (p.pawl_len + p.eps) / 2,
            p.pawl_leaf_center_z,
        ),
    )
    pawl_nose = cylinder_z(
        p.pawl_nose_d,
        p.pawl_nose_h,
        (
            p.pawl_tip_x,
            p.trim_wheel_center_y,
            p.pawl_leaf_top_z + p.pawl_nose_h / 2,
        ),
    )
    post = cylinder_z(
        p.trim_post_d,
        p.trim_post_len + 2 * p.eps,
        (p.trim_wheel_center_x, p.trim_wheel_center_y, p.trim_pocket_floor_z + p.trim_post_len / 2 - p.eps),
    )
    head = cylinder_z(
        p.trim_snap_head_d,
        p.trim_snap_head_t,
        (p.trim_wheel_center_x, p.trim_wheel_center_y, p.trim_wheel_max_z - p.trim_snap_head_t / 2),
    )
    return post_spine.union(pawl_mount).union(pawl_leaf).union(pawl_nose).union(post).union(head)


def _throttle_dovetail_slot(p: AeroThrottleParameters) -> cq.Workplane:
    """Female rail dovetail; the matching tenon applies FC-SLIDE exactly once."""
    y0 = p.rail_center_y - p.dovetail_base_w / 2
    y1 = p.rail_center_y + p.dovetail_base_w / 2
    mouth_y0 = p.rail_center_y - p.dovetail_mouth_w / 2
    mouth_y1 = p.rail_center_y + p.dovetail_mouth_w / 2
    return prism_yz([
        (y0, p.dovetail_floor_z),
        (y1, p.dovetail_floor_z),
        (mouth_y1, p.channel_floor_z),
        (mouth_y0, p.channel_floor_z),
    ], p.rail_len + 2 * p.eps, p.rail_start_x - p.eps)


def _afterburner_ramp(p: AeroThrottleParameters) -> cq.Workplane:
    """Rail-floor ramp at the slider-derived local afterburner station."""
    x0 = p.rail_start_x + p.ramp_apex_x - p.ramp_run_up
    return prism_xz([
        (x0, p.channel_floor_z - 5 * p.eps),
        (x0 + p.ramp_run_up, p.channel_floor_z + p.afterburner_lift),
        (x0 + p.ramp_footprint, p.channel_floor_z - 5 * p.eps),
    ], p.throttle_leaf_width, p.rail_center_y)


def _throttle_rail_spine(p: AeroThrottleParameters) -> cq.Workplane:
    """Rear-anchored internal rail spine that carries the isolated ramp root."""
    return box(
        p.rail_end_x + p.wall_exterior,
        p.throttle_leaf_width,
        p.wall_internal + p.eps,
        ((p.rail_end_x + p.wall_exterior) / 2, p.rail_center_y, p.dovetail_floor_z - p.wall_internal / 2 + p.eps / 2),
    )


def _afterburner_root(p: AeroThrottleParameters) -> cq.Workplane:
    """Narrow central web from the rail spine to the ramp; ATH_08 keys around it."""
    x0 = p.rail_start_x + p.ramp_apex_x - p.ramp_run_up
    return box(
        p.ramp_footprint,
        p.throttle_leaf_width,
        p.channel_floor_z - p.dovetail_floor_z + 4 * p.eps,
        (x0 + p.ramp_footprint / 2, p.rail_center_y, (p.channel_floor_z + p.dovetail_floor_z) / 2),
    )


def ath_01_upper_chassis(p: AeroThrottleParameters) -> cq.Workplane:
    p.validate()
    outline = [(0, 0), (p.seam_x_max, 0), (p.chassis_length, p.front_lower_chamfer), (p.chassis_length, p.chassis_height - p.crown_chamfer), (p.chassis_length - p.crown_chamfer, p.chassis_height), (p.crown_chamfer, p.chassis_height), (0, p.chassis_height - p.crown_chamfer)]
    body = prism_xy(outline, p.chassis_width)
    cavity = box(p.chassis_length - 2 * p.wall_exterior, p.chassis_height - p.wall_exterior + p.eps, p.chassis_width - 2 * p.wall_exterior, ((p.chassis_length - 2 * p.wall_exterior) / 2 + p.wall_exterior, (p.chassis_height - p.wall_exterior) / 2, 0))
    body = body.cut(cavity)
    collar = box(p.collar_depth, p.collar_h, p.collar_w, (p.chassis_length - p.collar_depth / 2, p.bezel_center_y, 0))
    body = body.union(collar)
    deep_cavity_len = p.chassis_length - p.collar_depth - p.snout_cavity_rear_x
    deep_cavity = box(deep_cavity_len + 2 * p.eps, p.snout_spring_cavity_y, p.snout_spring_cavity_z, ((p.snout_cavity_rear_x + (p.chassis_length - p.collar_depth)) / 2, p.bezel_center_y, 0))
    collar_cavity = box(p.collar_depth + 2 * p.eps, p.collar_cavity_y, p.collar_cavity_z, (p.chassis_length - p.collar_depth / 2, p.bezel_center_y, 0))
    body = body.cut(deep_cavity).cut(collar_cavity)
    hat_recess, hat_interface = _hat_cradle(p)
    body = body.cut(hat_recess).union(hat_interface)
    rail_channel = box(p.rail_len, p.rail_channel_h, p.rail_channel_depth + p.eps, (p.rail_start_x + p.rail_len / 2, p.rail_center_y, (p.flank_z + p.channel_floor_z) / 2))
    body = body.union(_throttle_rail_spine(p)).cut(rail_channel).cut(_throttle_dovetail_slot(p))
    body = body.union(_afterburner_root(p)).union(_afterburner_ramp(p))
    # Datum K is parallel to Z: the trim pocket therefore uses the same Z-axis
    # cylinder as its wheel, post, bore, and ratchet-ring interfaces.
    trim_center = (p.trim_wheel_center_x, p.trim_wheel_center_y, p.trim_pocket_floor_z + p.trim_pocket_depth / 2)
    body = body.cut(cylinder_z(p.trim_pocket_d, p.trim_pocket_depth + 2 * p.eps, trim_center))
    # The trim exposure window is intentionally cut before the seam ribbon is added.
    trim_window = box(p.trim_window_len, p.wall_exterior + 2 * p.eps, p.trim_wheel_width + 2 * p.trim_window_clear_z, (p.trim_wheel_center_x, 0, p.trim_pocket_floor_z + p.trim_pocket_clear_z + p.trim_wheel_width / 2))
    body = body.cut(trim_window)
    body = body.union(_trim_post_and_pawl_carrier(p)).union(seam_ribbon("tongue", p))
    for station in p.key_stations_x:
        body = body.cut(key_feature("socket", station, p))
    for station in p.snap_hook_stations_x:
        for side in (-1, 1):
            body = body.union(snap_feature("hook", station, side * p.snap_hook_z, p))
    return body


def ath_10_alignment_key(p: AeroThrottleParameters, station_x: float) -> cq.Workplane:
    key = key_feature("key", station_x, p)
    waist = box(p.key_side + 2 * p.key_waist_proud, p.key_waist_width, p.key_side + 2 * p.key_waist_proud, (station_x, 0, 0))
    return key.union(waist)


def ath_02_lower_grip_shell(p: AeroThrottleParameters) -> cq.Workplane:
    p.validate()
    # A deterministic side profile gives the specified root, butt, drop, and X minimum.
    grip_profile = [(p.grip_x_min, -p.grip_drop), (p.grip_butt_x + p.grip_butt_depth / 2, -p.grip_drop), (p.grip_root_x + p.grip_root_depth / 2, 0), (p.grip_root_x - p.grip_root_depth / 2, 0)]
    grip = prism_xy(grip_profile, p.palm_swell_width)
    tray = box(p.seam_x_max, p.wall_exterior, p.chassis_width, (p.seam_x_max / 2, -p.wall_exterior / 2, 0))
    root_bridge = box(p.grip_root_depth, p.wall_exterior, p.chassis_width, (p.grip_root_x, -p.wall_exterior / 2, 0))
    body = grip.union(root_bridge).union(tray).cut(seam_ribbon("groove", p))
    for station in p.key_stations_x:
        body = body.cut(key_feature("socket", station, p))
    for station in p.snap_hook_stations_x:
        for side in (-1, 1):
            body = body.cut(snap_feature("pocket", station, side * p.snap_hook_z, p))
    relief = box(p.trim_wheel_od - 2 * p.trim_rim_proud + 1.00, p.trim_rim_proud + p.feature_min, p.trim_wheel_width + 2 * p.trim_pocket_clear_z + 1.00, (p.trim_wheel_center_x, -p.trim_rim_proud / 2, 0))
    body = body.cut(relief)
    # Finger grooves are shallow anterior notches, so they cannot sever the grip.
    for index in range(p.finger_groove_count):
        y = -(p.grip_groove_start + index * p.finger_groove_pitch / 2)
        cutter = box(p.finger_groove_depth, p.rib_width, p.palm_swell_width + 2 * p.eps, (p.grip_root_x + p.grip_root_depth / 2, y, 0))
        body = body.cut(cutter)
    socket_z = p.trigger_trunnion_len / 2
    # ATH_02 owns the trigger cradle: two open-mouth spring walls carry the
    # FC-PIVOT sockets while leaving the central Z band free for ATH_09's shoe.
    # The stop bar and shelf are connected back to the seam tray by a single
    # structural strut, so they are not floating helper solids.
    cradle_x = p.trigger_pivot_x
    cradle_y = p.trigger_pivot_y
    # The central throat is opened before the side walls are placed.  It keeps
    # the trigger's centre shoe clear of the seam tray while the root anchor is
    # restored below as its own ATH_02-owned landing pad.
    trigger_throat = box(
        p.trigger_cradle_wall_len + 2 * p.wall_internal,
        p.wall_exterior + 2 * p.eps,
        p.trigger_stage1_width_active + 2 * p.fit_clearance_pivot,
        (cradle_x, -p.wall_exterior / 2, 0),
    )
    body = body.cut(trigger_throat)
    cradle_wall_z = p.trigger_trunnion_len / 2 + p.trigger_trunnion_d / 2 + p.fit_clearance_pivot
    for side in (-1, 1):
        cradle_wall = box(
            p.trigger_cradle_wall_len,
            p.trigger_trunnion_d + p.wall_internal,
            p.trigger_trunnion_d,
            (cradle_x, cradle_y, side * cradle_wall_z),
        )
        body = body.union(cradle_wall)
    for side in (-1, 1):
        body = body.cut(cylinder_z(p.trigger_socket_d, p.trigger_cradle_wall_len + 2 * p.eps, (p.trigger_pivot_x, p.trigger_pivot_y, side * socket_z)))
    anchor = box(p.trigger_stage1_width, p.wall_internal, p.wall_internal, (p.trigger_pivot_x - p.wall_internal, -p.wall_exterior / 2, 0))
    # Preserve the leaf's left-hand landing while opening the centre/right
    # portion of the pad for ATH_09's upper saddle envelope.
    anchor = anchor.cut(box(6.30, p.wall_internal + 2 * p.eps, p.trigger_stage1_width_active + 2 * p.fit_clearance_pivot, (p.trigger_pivot_x + 2.40, -p.wall_exterior / 2, 0)))
    stop_center_x = p.trigger_pivot_x - p.trigger_tooth_r * 0.25
    stop_center_y = p.trigger_pivot_y - p.trigger_tooth_r * 1.20
    stop_bar = box(
        p.wall_internal,
        p.wall_internal,
        p.trigger_stage2_width_active,
        (stop_center_x, stop_center_y, 0),
    )
    rear_strut_x = p.trigger_pivot_x + p.trigger_cradle_wall_len - p.wall_internal / 2
    shelf_center_x = p.trigger_pivot_x - p.trigger_contact_r * 0.20
    shelf_center_y = p.trigger_pivot_y - p.trigger_contact_r * 0.97
    rear_strut = box(
        p.wall_internal,
        -shelf_center_y - p.wall_exterior / 2,
        p.wall_internal,
        (rear_strut_x, (shelf_center_y - p.wall_exterior) / 2, 0),
    )
    shelf = box(
        p.trigger_shoe_section_t,
        p.wall_internal,
        p.trigger_shoe_section_t,
        (shelf_center_x, shelf_center_y, 0),
    )
    stop_link = box(rear_strut_x - stop_center_x, p.wall_internal, p.wall_internal, ((rear_strut_x + stop_center_x) / 2, stop_center_y, 0))
    shelf_link = box(rear_strut_x - shelf_center_x, p.wall_internal, p.wall_internal, ((rear_strut_x + shelf_center_x) / 2, shelf_center_y, 0))
    # These two bridges reconnect the deliberately opened central throat to
    # ATH_02's uncut tray on its safe rear and left sides.  Both stations sit
    # outside ATH_09's rest envelope, preserving the running-fit clearance.
    rear_tray_bridge = box(p.wall_internal, p.wall_exterior, p.trigger_stage1_width_active + 2 * p.wall_internal, (rear_strut_x, -p.wall_exterior / 2, 0))
    anchor_tray_bridge = box(2 * p.wall_internal, p.wall_internal, p.wall_internal, (p.trigger_pivot_x - p.trigger_stage1_width / 2 - p.wall_internal / 2, -p.wall_exterior / 2, 0))
    return body.union(anchor).union(stop_bar).union(rear_strut).union(stop_link).union(shelf).union(shelf_link).union(rear_tray_bridge).union(anchor_tray_bridge)


def phase1_components(p: AeroThrottleParameters | None = None) -> dict[str, cq.Workplane]:
    parameters = p or AeroThrottleParameters()
    components = {
        "ATH_01": ath_01_upper_chassis(parameters),
        "ATH_02": ath_02_lower_grip_shell(parameters),
        "ATH_10_A": ath_10_alignment_key(parameters, parameters.key_stations_x[0]),
        "ATH_10_B": ath_10_alignment_key(parameters, parameters.key_stations_x[1]),
    }
    if parameters.handedness == -1:
        return {part_id: solid.mirror("XY") for part_id, solid in components.items()}
    return components
