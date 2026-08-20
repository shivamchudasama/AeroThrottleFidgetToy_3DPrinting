"""ATH_03 Front Bezel Faceplate, authored in global Y-up design coordinates."""

from __future__ import annotations

from math import atan, cos, degrees, pi, radians, sin, sqrt, tan

import cadquery as cq

from .geometry import bevelled_box, box, bore_z, cylinder_y, cylinder_z, prism_xy, prism_yz
from .parameters import AeroThrottleParameters


def _bezel_barb(side: int, p: AeroThrottleParameters) -> cq.Workplane:
    """Permanent rear latch barb on one collar-facing Y flank.

    The beam is X-long and bends in Y during insertion.  Its 0 degree return
    face is represented by the square retention face of the undercut block.
    """
    y_outer = p.bezel_center_y + side * (p.collar_h / 2 + p.bezel_barb_t / 2)
    beam = box(
        p.bezel_barb_len,
        p.bezel_barb_t,
        p.bezel_barb_w,
        (p.bezel_rear_x + p.bezel_barb_len / 2, y_outer, side * p.bezel_barb_z_offset),
    )
    undercut_y = p.bezel_center_y + side * (p.collar_h / 2 - p.snap_undercut / 2)
    undercut = box(
        p.latch_pocket_w,
        p.snap_undercut,
        p.bezel_barb_w,
        (p.bezel_rear_x + p.bezel_barb_len / 2, undercut_y, side * p.bezel_barb_z_offset),
    )
    return beam.union(undercut)


def _cam_leaf(p: AeroThrottleParameters) -> cq.Workplane:
    """PETG bistable-cam leaf with a profile-level root-relief approximation.

    The beam spans from the rear bezel web toward datum K's guard hinge.  Its
    nominal contact is undeflected at either cam flat; the 0.80 mm lobe is the
    maximum working deflection used by the parameter analysis.
    """
    root_x = p.bezel_rear_x
    # The beam clears the complete lobe; its named minimum-feature follower
    # reaches the 0-degree flat without embedding the cam in the beam body.
    leaf_center_y = p.guard_cam_leaf_center_y
    leaf = box(
        p.guard_cam_leaf_len,
        p.guard_cam_leaf_t,
        p.guard_cam_leaf_w,
        (root_x + p.guard_cam_leaf_len / 2, leaf_center_y, 0),
    )
    # The anchor rises to the untouched upper bezel web.  It starts at the
    # leaf root, so the leaf remains a true 12 mm cantilever toward the hinge.
    anchor_top_y = p.bezel_center_y + p.bezel_cavity_h / 2
    anchor = box(
        2 * p.internal_fillet_radius,
        anchor_top_y - leaf_center_y + p.eps,
        p.guard_cam_leaf_w,
        (root_x + p.internal_fillet_radius, (anchor_top_y + leaf_center_y) / 2, 0),
    )
    follower = box(
        p.feature_min,
        p.guard_cam_lobe,
        p.guard_cam_leaf_w,
        (
            p.guard_hinge_x + p.feature_min / 2,
            (p.guard_cam_leaf_clear_y + p.guard_cam_flat_contact_y) / 2,
            0,
        ),
    )
    return leaf.union(follower).union(anchor)


def ath_03_front_bezel_faceplate(p: AeroThrottleParameters) -> cq.Workplane:
    """Build ATH_03 with the collar fit, guard interface, and button interface."""
    p.validate()
    body_center_x = (p.bezel_rear_x + p.bezel_front_x) / 2
    body = bevelled_box(p.bezel_depth, p.bezel_h, p.bezel_w, (body_center_x, p.bezel_center_y, 0), p.bezel_chamfer)

    collar_cavity = box(
        p.collar_depth + p.eps,
        p.bezel_cavity_h,
        p.bezel_cavity_w,
        (p.bezel_rear_x + p.collar_depth / 2 - p.eps / 2, p.bezel_center_y, 0),
    )
    guide_bore = box(
        p.bezel_depth + 2 * p.eps,
        p.fire_btn_bore,
        p.fire_btn_bore,
        (body_center_x, p.bezel_center_y, 0),
    )
    shoulder_pocket = box(
        p.collar_depth + 2 * p.eps,
        p.btn_shoulder_pocket,
        p.btn_shoulder_pocket,
        (p.bezel_rear_x + p.collar_depth / 2, p.bezel_center_y, 0),
    )
    guard_recess = box(
        p.guard_recess_depth + p.eps,
        p.guard_recess_h,
        p.guard_recess_w,
        (p.bezel_front_x - p.guard_recess_depth / 2 + p.eps / 2, p.bezel_center_y, 0),
    )
    # The cam projects behind the hood at the fixed hinge datum.  This local
    # pocket is cut from the bezel before the leaf is unioned back into it, so
    # the only rest-pose contact is the specified cam-flat/leaf-face tangent.
    cam_relief = _guard_cam(p)
    body = body.cut(collar_cavity).cut(guide_bore).cut(shoulder_pocket).cut(guard_recess).cut(cam_relief)

    stanchion_z = p.guard_hood_w / 2 + p.guard_pin_len / 2
    for side in (-1, 1):
        stanchion = box(
            p.guard_stanchion_t,
            p.guard_stanchion_len,
            p.guard_stanchion_t,
            (p.guard_hinge_x, p.guard_hinge_y - p.guard_stanchion_len / 2, side * stanchion_z),
        )
        pin_hole = bore_z(
            p.guard_pin_hole_d,
            p.guard_stanchion_t,
            (p.guard_hinge_x, p.guard_hinge_y, side * stanchion_z),
            p,
        )
        entry_slot = box(
            p.guard_stanchion_t + 2 * p.eps,
            p.guard_hinge_slot_w,
            p.guard_stanchion_t + 2 * p.eps,
            (p.guard_hinge_x, p.guard_hinge_y + p.guard_hinge_slot_w / 2, side * stanchion_z),
        )
        # Cut after the union: these bores must pass through any overlapping
        # faceplate material as well as their nominal stanchion ear.
        body = body.union(stanchion).cut(pin_hole).cut(entry_slot)

    body = body.union(_cam_leaf(p))
    for side in (-1, 1):
        body = body.union(_bezel_barb(side, p))
    return body


def phase2_ath03(p: AeroThrottleParameters | None = None) -> cq.Workplane:
    """Return ATH_03 using its approved PETG-specific material property set."""
    parameters = p or AeroThrottleParameters(material="PETG")
    if parameters.material != "PETG":
        raise ValueError("ATH_03 is allocated to PETG; use AeroThrottleParameters(material='PETG')")
    part = ath_03_front_bezel_faceplate(parameters)
    return part.mirror("XY") if parameters.handedness == -1 else part


def _fire_label(p: AeroThrottleParameters) -> cq.Workplane:
    """Condensed 6 mm-cap-height, 1.20 mm-stroke FIRE deboss cutter.

    The letters are deliberately constructed from deterministic strokes instead
    of relying on a host-font installation.  Their plane is YZ; the cutter is
    sunk from ATH_05's +X face.
    """
    x = p.btn_head_front_x - p.fire_btn_deboss_depth / 2
    stroke = p.fire_btn_deboss_stroke
    glyph_w = 1.40
    spacing = 0.25
    y0 = p.bezel_center_y - (4 * glyph_w + 3 * spacing) / 2
    z0 = -p.fire_btn_deboss_cap_h / 2

    def stroke_box(y: float, z: float, y_len: float, z_len: float) -> cq.Workplane:
        return box(p.fire_btn_deboss_depth + p.eps, y_len, z_len, (x, y, z))

    cutter: cq.Workplane | None = None
    for index, letter in enumerate("FIRE"):
        yc = y0 + glyph_w / 2 + index * (glyph_w + spacing)
        pieces = [stroke_box(yc - glyph_w / 2 + stroke / 2, 0, stroke, p.fire_btn_deboss_cap_h)]
        if letter in {"F", "E"}:
            pieces.extend([
                stroke_box(yc, z0 + p.fire_btn_deboss_cap_h - stroke / 2, glyph_w, stroke),
                stroke_box(yc - stroke / 8, 0, glyph_w * 0.85, stroke),
            ])
            if letter == "E":
                pieces.append(stroke_box(yc, z0 + stroke / 2, glyph_w, stroke))
        elif letter == "I":
            pieces = [stroke_box(yc, 0, stroke, p.fire_btn_deboss_cap_h)]
        elif letter == "R":
            pieces.extend([
                stroke_box(yc, z0 + p.fire_btn_deboss_cap_h - stroke / 2, glyph_w, stroke),
                stroke_box(yc, stroke / 2, glyph_w, stroke),
                stroke_box(yc + glyph_w / 2 - stroke / 2, p.fire_btn_deboss_cap_h / 4, stroke, p.fire_btn_deboss_cap_h / 2),
                stroke_box(yc + glyph_w / 4, -p.fire_btn_deboss_cap_h / 4, stroke, p.fire_btn_deboss_cap_h / 2),
            ])
        for piece in pieces:
            cutter = piece if cutter is None else cutter.union(piece)
    assert cutter is not None
    return cutter


def _fire_serpentine(p: AeroThrottleParameters) -> cq.Workplane:
    """Six laterally folded arc spans in the XY bending plane.

    This topology is the approved Phase-2 resolution of the conflicting axial
    stack: all spring material stays within the 11.10 mm transverse envelope,
    the spring joins the flange and rear anchor without entering the trim
    pocket, and Z is reserved solely for the PETG force-tuning depth.
    """
    beam = p.serpentine_beam_w_active
    x_first = p.serpentine_anchor_front_x
    # End one epsilon inside the flange so the swept path overlaps its rear
    # face, rather than relying on a coincident-face union.
    x_last = p.btn_flange_rear_x - p.eps
    track_pitch = (x_last - x_first) / (p.serpentine_loops - 1)
    turn_r = track_pitch / 2
    y_extent = p.serpentine_loop_r + beam / 2
    # Keep the folded spring below ATH_03's cam leaf by FC-STATIC while still
    # remaining inside ATH_01's local 11.90 mm spring bore.
    spring_center_y = min(
        p.bezel_center_y,
        p.guard_cam_leaf_center_y - p.guard_cam_leaf_t / 2 - p.fit_clearance_static - y_extent,
    )
    leg_end = y_extent - turn_r - beam / 2
    y_low = spring_center_y - leg_end
    y_high = spring_center_y + leg_end

    path = cq.Workplane("XY").moveTo(x_first, y_low)
    for index in range(p.serpentine_loops):
        y_end = y_high if index % 2 == 0 else y_low
        path = path.lineTo(x_first + index * track_pitch, y_end)
        if index < p.serpentine_loops - 1:
            y_mid = y_end + (turn_r if index % 2 == 0 else -turn_r)
            path = path.threePointArc((x_first + (index + 0.5) * track_pitch, y_mid), (x_first + (index + 1) * track_pitch, y_end))
    return path.wire().toPending().offset2D(beam / 2).extrude(p.serpentine_beam_t_active).translate((0, 0, -p.serpentine_beam_t_active / 2))


def ath_05_fire_button_plunger(p: AeroThrottleParameters) -> cq.Workplane:
    """Build ATH_05 from the ATH_03 guide/shoulder and ATH_01 snout datums."""
    p.validate()
    head = bevelled_box(
        p.fire_btn_head_t,
        p.fire_btn_size,
        p.fire_btn_size,
        ((p.btn_head_front_x + p.btn_head_rear_x) / 2, p.bezel_center_y, 0),
        0.80,
    ).cut(_fire_label(p))
    # The guard cam leaf crosses the upper-centre corner of the button guide.
    # This shallow, datum-derived relief avoids a rest-pose collision without
    # altering the controlled 10.50 mm guide contact faces.
    head_cam_relief = box(
        p.fire_btn_head_t + 2 * p.eps,
        p.bezel_center_y + p.fire_btn_size / 2 - (p.guard_cam_leaf_center_y - p.guard_cam_leaf_t / 2 - p.fit_clearance_static),
        p.guard_cam_leaf_w + 2 * p.fit_clearance_static,
        ((p.btn_head_front_x + p.btn_head_rear_x) / 2, (p.guard_cam_leaf_center_y - p.guard_cam_leaf_t / 2 - p.fit_clearance_static + p.bezel_center_y + p.fire_btn_size / 2) / 2, 0),
    )
    head = head.cut(head_cam_relief)
    flange = box(
        p.fire_btn_flange_t,
        p.fire_btn_flange,
        p.fire_btn_flange,
        ((p.btn_head_rear_x + p.btn_flange_rear_x) / 2, p.bezel_center_y, 0),
    )
    # ATH_03's PETG guard cam leaf occupies the upper-centre band of the rear
    # shoulder pocket.  Relieve only that band from the flange, enlarged by
    # FC-STATIC, so the remaining three-sided flange still retains the button.
    cam_leaf_relief = box(
        p.fire_btn_flange_t + 2 * p.eps,
        p.guard_cam_leaf_t + 2 * p.fit_clearance_static,
        p.guard_cam_leaf_w + 2 * p.fit_clearance_static,
        ((p.btn_head_rear_x + p.btn_flange_rear_x) / 2, p.guard_cam_leaf_center_y, 0),
    )
    flange = flange.cut(cam_leaf_relief)
    anchor = box(
        p.fire_btn_flange_t,
        p.fire_btn_flange,
        p.serpentine_beam_t_active,
        ((p.serpentine_anchor_rear_x + p.serpentine_anchor_front_x) / 2, p.bezel_center_y, 0),
    )
    stop_y = p.bezel_center_y - p.fire_btn_flange / 2 + p.fire_btn_stop_boss_y / 2
    stop_z = p.fire_btn_flange / 2 - p.fire_btn_stop_boss_y / 2
    stops = box(
        p.fire_btn_stop_boss_x,
        p.fire_btn_stop_boss_y,
        p.fire_btn_stop_boss_y,
        (p.btn_flange_rear_x - p.fire_btn_stop_boss_x / 2, stop_y, -stop_z),
    ).union(box(
        p.fire_btn_stop_boss_x,
        p.fire_btn_stop_boss_y,
        p.fire_btn_stop_boss_y,
        (p.btn_flange_rear_x - p.fire_btn_stop_boss_x / 2, stop_y, stop_z),
    ))
    return head.union(flange).union(stops).union(_fire_serpentine(p)).union(anchor)


def phase2_ath05(p: AeroThrottleParameters | None = None) -> cq.Workplane:
    """Return ATH_05 using the approved PETG-specific spring re-solve."""
    parameters = p or AeroThrottleParameters(material="PETG")
    if parameters.material != "PETG":
        raise ValueError("ATH_05 is allocated to PETG; use AeroThrottleParameters(material='PETG')")
    part = ath_05_fire_button_plunger(parameters)
    return part.mirror("XY") if parameters.handedness == -1 else part


def _guard_pin(side: int, p: AeroThrottleParameters) -> cq.Workplane:
    """Outward-facing hinge pin with a parameter-derived 30 degree lead-in."""
    radius = p.guard_pin_d / 2
    lead_radius = radius - p.guard_pin_lead_radial
    straight_len = p.guard_pin_len - p.guard_pin_lead_len
    pin = (
        cq.Workplane("XY")
        .circle(radius)
        .workplane(offset=straight_len)
        .circle(radius)
        .workplane(offset=p.guard_pin_lead_len)
        .circle(lead_radius)
        .loft(combine=True)
        .translate((p.guard_hinge_x, p.guard_hinge_y, p.guard_hood_w / 2 - p.eps))
    )
    # The root boss bridges the side-wall relief while the nominal pin keeps
    # its controlled 3.00 mm protruding length and its pivot-bore clearance.
    root = cylinder_z(
        p.guard_pin_d,
        p.guard_hinge_notch_depth,
        (
            p.guard_hinge_x,
            p.guard_hinge_y,
            p.guard_hood_w / 2 - p.guard_hinge_notch_depth / 2,
        ),
    )
    combined = pin.union(root)
    return combined if side > 0 else combined.mirror("XY")


def _guard_hinge_side_relief(side: int, p: AeroThrottleParameters) -> cq.Workplane:
    """Remove only the hood band that would overlap ATH_03's hinge ear."""
    return box(
        p.guard_stanchion_t + 2 * p.eps,
        p.guard_stanchion_len + 2 * p.eps,
        p.guard_hinge_notch_depth,
        (
            p.guard_hinge_x,
            p.guard_hinge_y - p.guard_stanchion_len / 2,
            side * p.guard_hinge_notch_center_z,
        ),
    )


def _guard_cam_radius(angle_deg: float, p: AeroThrottleParameters) -> float:
    """C1-continuous raised-cosine transition between the two cam flats."""
    start_deg = p.guard_cam_flat_half_deg
    end_deg = p.guard_open_deg - p.guard_cam_flat_half_deg
    if angle_deg <= start_deg or angle_deg >= end_deg:
        return p.guard_cam_base_r
    progress = (angle_deg - start_deg) / (end_deg - start_deg)
    return p.guard_cam_base_r + p.guard_cam_lobe * (0.5 - 0.5 * cos(2 * pi * progress))


def _guard_cam(p: AeroThrottleParameters) -> cq.Workplane:
    """The 0/90-degree dual-flat cam, extruded through the ATH_03 leaf width."""
    start_deg = -p.guard_cam_flat_half_deg
    end_deg = p.guard_open_deg + p.guard_cam_flat_half_deg
    points = [(p.guard_hinge_x, p.guard_hinge_y)]
    for index in range(p.guard_cam_segments + 1):
        angle_deg = start_deg + (end_deg - start_deg) * index / p.guard_cam_segments
        radius = _guard_cam_radius(angle_deg, p)
        angle_rad = radians(angle_deg)
        points.append((
            p.guard_hinge_x - radius * sin(angle_rad),
            p.guard_hinge_y - radius * cos(angle_rad),
        ))
    return prism_xy(points, p.guard_cam_leaf_w)


def ath_04_missile_safety_guard(p: AeroThrottleParameters) -> cq.Workplane:
    """Build ATH_04 in its closed pose about the ATH_03 hinge datum.

    The normative hood envelope is Z = +/-7.50 mm.  The approved bounding-box
    exemptions permit the serviceable hinge pins and dual-flat cam to extend
    beyond that hood envelope while preserving the specified mating geometry.
    """
    p.validate()
    outer = bevelled_box(
        p.guard_hood_h,
        p.guard_hood_l,
        p.guard_hood_w,
        (p.guard_hood_center_x, p.guard_hood_center_y, 0),
        p.guard_hood_chamfer,
    )
    inner = box(
        p.guard_hood_h - p.guard_wall + p.eps,
        p.guard_hood_l - 2 * p.guard_wall,
        p.guard_hood_w - 2 * p.guard_wall,
        (
            p.guard_hood_min_x + (p.guard_hood_h - p.guard_wall) / 2,
            p.guard_hood_center_y,
            0,
        ),
    )
    hood = outer.cut(inner)
    for side in (-1, 1):
        hood = hood.cut(_guard_hinge_side_relief(side, p))

    lift_tab = box(
        p.guard_lift_tab_z,
        p.guard_lift_tab_y,
        p.guard_lift_tab_x,
        (
            p.guard_closed_x - p.guard_lift_tab_z / 2,
            p.guard_lift_tab_center_y,
            0,
        ),
    )
    stop = box(
        p.guard_stop_x,
        p.guard_stop_y,
        p.guard_stop_z,
        (
            p.bezel_front_x + p.guard_stop_x / 2,
            p.guard_hinge_y + p.guard_stop_y / 2,
            0,
        ),
    )
    body = hood.union(lift_tab).union(stop).union(_guard_cam(p))
    for side in (-1, 1):
        body = body.union(_guard_pin(side, p))
    return body


def phase2_ath04(p: AeroThrottleParameters | None = None) -> cq.Workplane:
    """Return ATH_04 using its approved PETG-specific material property set."""
    parameters = p or AeroThrottleParameters(material="PETG")
    if parameters.material != "PETG":
        raise ValueError("ATH_04 is allocated to PETG; use AeroThrottleParameters(material='PETG')")
    part = ath_04_missile_safety_guard(parameters)
    return part.mirror("XY") if parameters.handedness == -1 else part


def _prism_xz(points: list[tuple[float, float]], y_base: float, y_height: float) -> cq.Workplane:
    """Extrude an XZ profile upward in design Y, without a local part frame."""
    return cq.Workplane("XZ").polyline(points).close().extrude(y_height).translate((0, y_base + y_height, 0))


def _cylinder_y_design(diameter: float, height: float, center: tuple[float, float, float]) -> cq.Workplane:
    """Y-axis cylinder centred in the global Y-up design frame."""
    return cylinder_y(diameter, height, (center[0], center[1] + height, center[2]))


def _cone_y_design(radius_bottom: float, radius_top: float, height: float, base: tuple[float, float, float]) -> cq.Workplane:
    """Closed Y-axis conical frustum, avoiding pole-degenerate sphere facets."""
    solid = cq.Solid.makeCone(radius_bottom, radius_top, height, cq.Vector(*base), cq.Vector(0, 1, 0))
    return cq.Workplane(obj=solid)


def _hat_gimbal_dome(p: AeroThrottleParameters) -> cq.Workplane:
    """Loft a pole-free approximation of the exposed lower ball hemisphere."""
    ring_count = 6
    bottom_y = p.hat_ball_bottom_y + p.eps
    rings = []
    for index in range(ring_count):
        y = bottom_y + (p.hat_base_y + p.eps - bottom_y) * index / (ring_count - 1)
        sphere_y = y - p.hat_base_y
        radius = max(p.feature_min / 2, sqrt(max(0.0, p.hat_ball_r ** 2 - sphere_y ** 2)))
        edge = cq.Edge.makeCircle(radius, cq.Vector(p.hat_center_x, y, 0), cq.Vector(0, 1, 0))
        rings.append(cq.Wire.assembleEdges([edge]))
    return cq.Workplane(obj=cq.Solid.makeLoft(rings, ruled=True))


def _hat_arm(tip_angle_deg: float, arm_y: float, p: AeroThrottleParameters) -> cq.Workplane:
    """One PETG spiral arm, its root column, bayonet lug, and detent nose.

    Each plane contains only an opposite pair.  A 150-degree ribbon therefore
    occupies disjoint angular intervals; placing the cardinally alternate pair
    on the other plane resolves the specification's otherwise planar overlap.
    """
    root_angle_deg = tip_angle_deg - p.hat_arm_sweep_deg
    outer_r = p.hat_arm_mean_r + p.hat_spring_arm_width_active / 2
    inner_r = p.hat_arm_mean_r - p.hat_spring_arm_width_active / 2
    segments = 30
    outer = []
    inner = []
    for index in range(segments + 1):
        angle = radians(root_angle_deg + p.hat_arm_sweep_deg * index / segments)
        outer.append((p.hat_center_x + outer_r * cos(angle), outer_r * sin(angle)))
        inner.append((p.hat_center_x + inner_r * cos(angle), inner_r * sin(angle)))
    arm = _prism_xz(outer + list(reversed(inner)), arm_y, p.hat_spring_arm_thick_active)

    root_angle = radians(root_angle_deg)
    root_x = p.hat_center_x + p.hat_arm_mean_r * cos(root_angle)
    root_z = p.hat_arm_mean_r * sin(root_angle)
    root_column = _cylinder_y_design(
        p.hat_spring_arm_width_active,
        p.hat_base_y - arm_y + p.eps,
        (root_x, arm_y + (p.hat_base_y - arm_y) / 2, root_z),
    )
    lug = box(
        3.00,
        p.hat_retention_lip_undercut,
        p.hat_spring_arm_width_active,
        (
            p.hat_center_x + 7.40,
            p.hat_base_y - p.hat_retention_lip_undercut - p.fit_clearance_snap - p.hat_retention_lip_undercut / 2,
            0,
        ),
    ).rotate((p.hat_center_x, 0, 0), (p.hat_center_x, 1, 0), root_angle_deg)

    tip_angle = radians(tip_angle_deg)
    tip_x = p.hat_center_x + p.hat_arm_r * cos(tip_angle)
    tip_z = p.hat_arm_r * sin(tip_angle)
    nose_base_y = p.hat_lower_arm_y
    nose_top_y = nose_base_y + p.hat_detent_nose_r
    nose = _cone_y_design(
        p.feature_min / 2,
        p.hat_detent_nose_r,
        p.hat_detent_nose_r,
        (tip_x, nose_base_y, tip_z),
    )
    stem_top_y = arm_y + p.hat_spring_arm_thick_active / 2
    stem = _cylinder_y_design(
        2 * p.hat_detent_nose_r,
        stem_top_y - nose_top_y + p.eps,
        (tip_x, (stem_top_y + nose_top_y - p.eps) / 2, tip_z),
    )
    return arm.union(root_column).union(lug).union(stem).union(nose)


def _hat_cap(p: AeroThrottleParameters) -> cq.Workplane:
    """Three deterministic cap steps with tactile ribs and directional debosses."""
    step_h = (p.hat_cap_h - 0.40) / 3
    step_overlap_h = step_h + p.eps
    diameters = (p.hat_cap_od, p.hat_cap_od - 3.00, p.hat_cap_od - 6.00)
    cap = _cylinder_y_design(diameters[0], step_overlap_h, (p.hat_center_x, p.hat_base_y + step_overlap_h / 2, 0))
    cap = cap.union(_cylinder_y_design(diameters[1], step_overlap_h, (p.hat_center_x, p.hat_base_y + step_h + step_overlap_h / 2, 0)))
    cap = cap.union(_cylinder_y_design(diameters[2], step_overlap_h, (p.hat_center_x, p.hat_base_y + 2 * step_h + step_overlap_h / 2, 0)))
    rib_y = p.hat_base_y + p.hat_cap_h - 0.20
    for angle_deg in range(0, 360, 45):
        rib = box(6.50, 0.40, 0.60, (p.hat_center_x + 3.25, rib_y, 0))
        cap = cap.union(rib.rotate((p.hat_center_x, 0, 0), (p.hat_center_x, 1, 0), angle_deg))
    for angle_deg in (0, 90, 180, 270):
        angle = radians(angle_deg)
        arrow = [
            (p.hat_center_x + 4.60, 0),
            (p.hat_center_x + 3.30, -0.80),
            (p.hat_center_x + 3.30, 0.80),
        ]
        cut = _prism_xz(arrow, p.hat_base_y + p.hat_cap_h - 0.50, 0.51)
        cap = cap.cut(cut.rotate((p.hat_center_x, 0, 0), (p.hat_center_x, 1, 0), angle_deg))
    return cap


def ath_06_4way_hat_switch(p: AeroThrottleParameters) -> cq.Workplane:
    """Build ATH_06 in its rest pose at datum L, using the approved PETG re-solve."""
    p.validate()
    cap = _hat_cap(p)
    ball = _hat_gimbal_dome(p)
    body = cap.union(ball)
    for tip_angle_deg, arm_y in ((0, p.hat_lower_arm_y), (180, p.hat_lower_arm_y), (90, p.hat_upper_arm_y), (270, p.hat_upper_arm_y)):
        body = body.union(_hat_arm(tip_angle_deg, arm_y, p))
    return body


def phase2_ath06(p: AeroThrottleParameters | None = None) -> cq.Workplane:
    """Return ATH_06 using its approved PETG two-level star-spring re-solve."""
    parameters = p or AeroThrottleParameters(material="PETG")
    if parameters.material != "PETG":
        raise ValueError("ATH_06 is allocated to PETG; use AeroThrottleParameters(material='PETG')")
    part = ath_06_4way_hat_switch(parameters)
    return part.mirror("XY") if parameters.handedness == -1 else part


def _trim_knurl_cuts(p: AeroThrottleParameters) -> cq.Workplane:
    """Crossed, 45-degree exterior-only groove family for the wheel knurl.

    Every pocket stops at the derived 0.70 mm rim depth.  The two local 45-degree
    cuts at every circumferential station form one diamond on the vertical rim,
    without cutting a continuous stripe through the rotor shell.
    """
    cut: cq.Workplane | None = None
    outer_r = p.trim_wheel_od / 2
    radial_cut = p.knurl_depth + 2 * p.eps
    radial_center = outer_r - p.knurl_depth / 2
    for index in range(p.knurl_line_count):
        angle = radians(360 * index / p.knurl_line_count)
        station = (p.trim_wheel_center_x + radial_center, p.trim_wheel_center_y, p.trim_wheel_mid_z)
        for sign in (-1, 1):
            pocket = box(radial_cut, p.knurl_line_pitch, p.knurl_groove_w, station)
            pocket = pocket.rotate(
                station,
                (station[0] + 1, station[1], station[2]),
                sign * p.knurl_helix_deg,
            ).rotate(
                (p.trim_wheel_center_x, p.trim_wheel_center_y, p.trim_wheel_mid_z),
                (p.trim_wheel_center_x, p.trim_wheel_center_y, p.trim_wheel_mid_z + 1),
                degrees(angle),
            )
            cut = pocket if cut is None else cut.union(pocket)
    if cut is None:
        raise ValueError("knurl_facets must produce at least one crossed groove")
    return cut


def _ratchet_tooth_cuts(p: AeroThrottleParameters) -> cq.Workplane:
    """Return 20 derived-angle triangular voids, open at the wheel's -Z face."""
    cut: cq.Workplane | None = None
    # Keep an epsilon-scale uncut land between neighbouring triangular cuts.
    # Coincident cutter bases otherwise produce a non-manifold annular seam.
    half_tooth_angle = radians(180 / p.ratchet_teeth_count) - atan(p.eps / p.ratchet_root_r)
    cut_height = p.trim_ratchet_cut_depth + p.eps
    for index in range(p.ratchet_teeth_count):
        center_angle = radians(360 * index / p.ratchet_teeth_count)
        points = [
            (
                p.trim_wheel_center_x + p.ratchet_tip_r * cos(center_angle),
                p.trim_wheel_center_y + p.ratchet_tip_r * sin(center_angle),
            ),
            (
                p.trim_wheel_center_x + p.ratchet_root_r * cos(center_angle - half_tooth_angle),
                p.trim_wheel_center_y + p.ratchet_root_r * sin(center_angle - half_tooth_angle),
            ),
            (
                p.trim_wheel_center_x + p.ratchet_root_r * cos(center_angle + half_tooth_angle),
                p.trim_wheel_center_y + p.ratchet_root_r * sin(center_angle + half_tooth_angle),
            ),
        ]
        tooth = prism_xy(points, cut_height, p.trim_wheel_min_z + cut_height / 2 - p.eps / 2)
        cut = tooth if cut is None else cut.union(tooth)
    if cut is None:
        raise ValueError("ratchet_teeth_count must be positive")
    return cut


def ath_07_rotary_trim_wheel(p: AeroThrottleParameters) -> cq.Workplane:
    """Build the PLA trim wheel at datum K in its assembled rest orientation."""
    p.validate()
    rotor = cylinder_z(
        p.trim_wheel_od,
        p.trim_wheel_width,
        (p.trim_wheel_center_x, p.trim_wheel_center_y, p.trim_wheel_mid_z),
    )
    rotor = rotor.cut(_trim_knurl_cuts(p))
    rotor = rotor.cut(bore_z(
        p.trim_bore_d,
        p.trim_wheel_width,
        (p.trim_wheel_center_x, p.trim_wheel_center_y, p.trim_wheel_mid_z),
        p,
    ))
    rotor = rotor.cut(bore_z(
        p.trim_counterbore_d,
        p.trim_counterbore_depth,
        (
            p.trim_wheel_center_x,
            p.trim_wheel_center_y,
            p.trim_wheel_max_z - p.trim_counterbore_depth / 2,
        ),
        p,
    ))
    return rotor.cut(_ratchet_tooth_cuts(p))


def phase2_ath07(p: AeroThrottleParameters | None = None) -> cq.Workplane:
    """Return ATH_07 using its approved matte-PLA material allocation."""
    parameters = p or AeroThrottleParameters(material="PLA_PLUS")
    if parameters.material != "PLA_PLUS":
        raise ValueError("ATH_07 is allocated to matte PLA; use AeroThrottleParameters(material='PLA_PLUS')")
    part = ath_07_rotary_trim_wheel(parameters)
    return part.mirror("XY") if parameters.handedness == -1 else part


def _throttle_tenon(p: AeroThrottleParameters, carriage_x0: float) -> cq.Workplane:
    """Male dovetail generated from the sole FC-SLIDE clearance application."""
    y0 = p.rail_center_y - p.throttle_tenon_base_w / 2
    y1 = p.rail_center_y + p.throttle_tenon_base_w / 2
    mouth_y0 = p.rail_center_y - p.throttle_tenon_mouth_w / 2
    mouth_y1 = p.rail_center_y + p.throttle_tenon_mouth_w / 2
    tenon = prism_yz([
        (y0, p.dovetail_floor_z + p.eps),
        (y1, p.dovetail_floor_z + p.eps),
        (mouth_y1, p.channel_floor_z + p.eps),
        (mouth_y0, p.channel_floor_z + p.eps),
    ], p.throttle_carriage_len, carriage_x0)
    return tenon.cut(box(
        p.throttle_carriage_len + 2 * p.eps,
        p.throttle_leaf_width + 2 * p.fit_clearance_static,
        p.dovetail_depth + 2 * p.eps,
        (carriage_x0 + p.throttle_carriage_len / 2, p.rail_center_y, (p.dovetail_floor_z + p.channel_floor_z) / 2),
    ))


def _throttle_leaf(p: AeroThrottleParameters, carriage_x0: float) -> cq.Workplane:
    """Two-arm PETG U leaf with its free fold at the derived follower station.

    The U is cut free from the plate on all non-root sides.  Its outer fold is
    deliberately kept at the nominal PLA-derived tip station so ATH_01's fixed
    afterburner ramp remains valid after PETG's cross-section re-solve.
    """
    arm_x0 = carriage_x0 + p.throttle_leaf_placement_offset
    arm_x1 = arm_x0 + p.throttle_leaf_arm_len
    half_spacing = p.throttle_leaf_fold_r
    leaf_z0 = p.channel_floor_z + p.throttle_carriage_plate_t_active - p.throttle_leaf_thick_active
    arm_low = box(p.throttle_leaf_arm_len, p.throttle_leaf_width_active, p.throttle_leaf_thick_active, (arm_x0 + p.throttle_leaf_arm_len / 2, p.rail_center_y - half_spacing, leaf_z0 + p.throttle_leaf_thick_active / 2))
    arm_high = box(p.throttle_leaf_arm_len, p.throttle_leaf_width_active, p.throttle_leaf_thick_active, (arm_x0 + p.throttle_leaf_arm_len / 2, p.rail_center_y + half_spacing, leaf_z0 + p.throttle_leaf_thick_active / 2))
    crossbar = box(p.throttle_leaf_width_active, p.throttle_leaf_env_y_active, p.throttle_leaf_thick_active, (arm_x1, p.rail_center_y, leaf_z0 + p.throttle_leaf_thick_active / 2))
    forward_tongue_len = p.throttle_leaf_fold_r + p.throttle_leaf_width_active / 2
    forward_tongue = box(forward_tongue_len, p.throttle_leaf_width_active, p.throttle_leaf_thick_active, (arm_x1 + forward_tongue_len / 2, p.rail_center_y, leaf_z0 + p.throttle_leaf_thick_active / 2))
    leaf = arm_low.union(arm_high).union(crossbar).union(forward_tongue)
    # The follower station is its forward tangency, retaining the specified
    # X=[3.50,18.50] carriage envelope despite the R1.20 hemispherical nose.
    follower_x = carriage_x0 + p.throttle_leaf_tip_offset_nominal - p.detent_follower_r
    nose_base_z = p.channel_floor_z + p.eps
    nose_top_z = nose_base_z + p.detent_follower_r
    stem_bottom = nose_top_z - p.eps
    stem_top = leaf_z0 + p.throttle_leaf_thick_active
    stem = box(
        p.detent_follower_r,
        p.throttle_leaf_width_active,
        stem_top - stem_bottom + p.eps,
        (follower_x, p.rail_center_y, (stem_top + stem_bottom) / 2),
    )
    # A truncated cone is a pole-free R1.20 nose pointing -Z.  Avoiding a
    # sphere's zero-area pole keeps the exported FDM mesh manifold.
    nose = cq.Workplane(obj=cq.Solid.makeCone(
        p.feature_min / 2,
        p.detent_follower_r,
        p.detent_follower_r,
        cq.Vector(follower_x, p.rail_center_y, nose_base_z),
        cq.Vector(0, 0, 1),
    ))
    return leaf.union(stem).union(nose)


def ath_08_throttle_slider(p: AeroThrottleParameters) -> cq.Workplane:
    """Build ATH_08 at rest on ATH_01 datum G using the PETG leaf re-solve."""
    p.validate()
    carriage_x0 = p.rail_start_x + p.rail_end_clear
    plate_z0 = p.channel_floor_z
    plate_top_z = plate_z0 + p.throttle_carriage_plate_t_active
    plate = box(
        p.throttle_carriage_len,
        p.dovetail_base_w,
        p.throttle_carriage_plate_t_active,
        (carriage_x0 + p.throttle_carriage_len / 2, p.rail_center_y, plate_z0 + p.throttle_carriage_plate_t_active / 2),
    )
    pocket = box(
        p.throttle_carriage_len - p.wall_internal,
        p.throttle_leaf_env_y_active + 2 * p.gap_print_min,
        p.throttle_carriage_plate_t_active + 2 * p.eps,
        (carriage_x0 + p.wall_internal + (p.throttle_carriage_len - p.wall_internal) / 2, p.rail_center_y, plate_z0 + p.throttle_carriage_plate_t_active / 2),
    )
    plate = plate.cut(pocket)
    tab_base_h = p.throttle_tab_h_z - p.tab_ridge_r
    tab = bevelled_box(
        p.throttle_tab_len,
        p.throttle_tab_h,
        tab_base_h,
        (carriage_x0 + p.throttle_carriage_len / 2, p.rail_center_y, plate_top_z + tab_base_h / 2),
        min(0.60, tab_base_h / 3),
    )
    for index in range(p.tab_ridge_count):
        ridge_x = carriage_x0 + (index + 1) * p.throttle_tab_len / (p.tab_ridge_count + 1)
        ridge = box(
            2 * p.tab_ridge_r,
            p.throttle_tab_h - 2 * p.tab_ridge_r,
            p.tab_ridge_r,
            (ridge_x, p.rail_center_y, p.flank_z - p.tab_recess - p.tab_ridge_r / 2),
        )
        tab = tab.union(ridge)
    anti_lift = box(
        1.00,
        p.throttle_tenon_mouth_w,
        p.feature_min,
        (carriage_x0 + 0.50, p.rail_center_y, p.channel_floor_z + p.feature_min / 2),
    ).union(box(
        1.00,
        p.throttle_tenon_mouth_w,
        p.feature_min,
        (carriage_x0 + p.throttle_carriage_len - 0.50, p.rail_center_y, p.channel_floor_z + p.feature_min / 2),
    ))
    return _throttle_tenon(p, carriage_x0).union(plate).union(tab).union(anti_lift).union(_throttle_leaf(p, carriage_x0)).combine(glue=True, clean=True)


def phase2_ath08(p: AeroThrottleParameters | None = None) -> cq.Workplane:
    """Return ATH_08 with its approved PETG-specific detent leaf geometry."""
    parameters = p or AeroThrottleParameters(material="PETG")
    if parameters.material != "PETG":
        raise ValueError("ATH_08 is allocated to PETG; use AeroThrottleParameters(material='PETG')")
    part = ath_08_throttle_slider(parameters)
    return part.mirror("XY") if parameters.handedness == -1 else part


def _strip_xy(points: list[tuple[float, float]], thickness: float, z_width: float) -> cq.Workplane:
    """Create a constant-section XY flexure strip about a deterministic wire."""
    path = cq.Workplane("XY").moveTo(*points[0])
    for point in points[1:]:
        path = path.lineTo(*point)
    return path.wire().toPending().offset2D(thickness / 2).extrude(z_width).translate((0, 0, -z_width / 2))


def _trigger_shoe(p: AeroThrottleParameters) -> cq.Workplane:
    """Finger saddle and 6 mm retention spur, rooted at datum J.

    The saddle is an explicit swept XY profile.  Its centreline terminates at
    the named 18 mm finger-contact radius, while the 4 mm section and the
    flared outer pads provide a tangible R16-class finger surface without
    changing the pivot or PETG spring interfaces.
    """
    pivot = (p.trigger_pivot_x, p.trigger_pivot_y)
    contact_dx = -0.5 * p.trigger_contact_r
    contact_dy = -sqrt(3) * p.trigger_contact_r / 2
    contact = (pivot[0] + contact_dx, pivot[1] + contact_dy)
    lower = (contact[0] - 1.0, contact[1] - 2.4)
    saddle = _strip_xy([pivot, contact, lower], p.trigger_shoe_section_t, 6.00)
    # Split upper pads reach the controlled Y=0 envelope outside ATH_02's
    # central stage-1 landing pad, and remain inside the cradle-wall throat.
    upper = box(4.00, 3.00, 2.20, (p.trigger_pivot_x + 2.00, p.trigger_pivot_y + 2.50, 2.70)).union(box(
        4.00,
        3.00,
        2.20,
        (p.trigger_pivot_x + 2.00, p.trigger_pivot_y + 2.50, -2.70),
    ))
    spur = box(2.40, p.trigger_spur_len, 2 * p.trigger_shoe_half_width, (lower[0] + 1.20, lower[1] + p.trigger_spur_len / 2 - 1.20, 0))
    # Four shallow transverse ribs provide the specified tactile texture.
    ribs: cq.Workplane | None = None
    for index in range(4):
        fraction = (index + 1) / 5
        x = pivot[0] + fraction * (contact[0] - pivot[0])
        y = pivot[1] + fraction * (contact[1] - pivot[1])
        rib = box(p.trigger_rib_depth, 1.20, 6.20, (x, y, 0))
        ribs = rib if ribs is None else ribs.union(rib)
    assert ribs is not None
    return saddle.union(upper).union(spur).union(ribs)


def _trigger_stage1_leaf(p: AeroThrottleParameters) -> cq.Workplane:
    """21.20 mm developed PETG return leaf ending just clear of ATH_02's pad."""
    # The 6.00 + pi*2.50 + 7.346 path is 21.20 mm developed length.  Its free
    # tip preserves an epsilon-free 0.05 mm assembly clearance to the ATH_02
    # anchor at rest; contact is produced only by trigger rotation.
    root = (p.trigger_pivot_x - 2.00, p.trigger_pivot_y - 4.00)
    turn_start = (p.trigger_pivot_x - 8.00, p.trigger_pivot_y - 4.00)
    turn_end = (p.trigger_pivot_x - 8.00, p.trigger_pivot_y + 1.00)
    tip = (p.trigger_pivot_x - 0.654, p.trigger_pivot_y + 1.00)
    path = cq.Workplane("XY").moveTo(*root).lineTo(*turn_start).threePointArc((p.trigger_pivot_x - 10.50, p.trigger_pivot_y - 1.50), turn_end).lineTo(*tip)
    return path.wire().toPending().offset2D(p.trigger_stage1_thick_active / 2).extrude(p.trigger_stage1_width_active).translate((0, 0, -p.trigger_stage1_width_active / 2))


def _trigger_stage2_tooth(p: AeroThrottleParameters) -> cq.Workplane:
    """PETG gate tooth with the derived tip radius and 45 degree gate loading."""
    pivot = (p.trigger_pivot_x, p.trigger_pivot_y)
    tip = (pivot[0] - 0.5 * p.trigger_tooth_r, pivot[1] - sqrt(3) * p.trigger_tooth_r / 2)
    root = (p.trigger_pivot_x - 7.30, p.trigger_pivot_y - 10.40)
    turn_start = (p.trigger_pivot_x - 9.70, p.trigger_pivot_y - 10.40)
    turn_end = (p.trigger_pivot_x - 9.70, p.trigger_pivot_y - 7.32)
    path = cq.Workplane("XY").moveTo(*root).lineTo(*turn_start).threePointArc((p.trigger_pivot_x - 11.24, p.trigger_pivot_y - 8.86), turn_end).lineTo(*tip)
    return path.wire().toPending().offset2D(p.trigger_stage2_thick_active / 2).extrude(p.trigger_stage2_width_active).translate((0, 0, -p.trigger_stage2_width_active / 2))


def ath_09_dual_trigger(p: AeroThrottleParameters) -> cq.Workplane:
    """Build ATH_09 about datum J from ATH_02's pivot, stop, and anchor interfaces."""
    p.validate()
    shoe = _trigger_shoe(p)
    trunnion = cylinder_z(
        p.trigger_trunnion_d,
        p.trigger_trunnion_len,
        (p.trigger_pivot_x, p.trigger_pivot_y, 0),
    )
    # The trunnion end bevel is constrained by the part's 0.40 mm print lead-in.
    end_relief = cylinder_z(
        p.trigger_trunnion_d - 2 * p.bed_chamfer,
        p.bed_chamfer,
        (p.trigger_pivot_x, p.trigger_pivot_y, p.trigger_trunnion_len / 2 - p.bed_chamfer / 2),
    ).union(cylinder_z(
        p.trigger_trunnion_d - 2 * p.bed_chamfer,
        p.bed_chamfer,
        (p.trigger_pivot_x, p.trigger_pivot_y, -p.trigger_trunnion_len / 2 + p.bed_chamfer / 2),
    ))
    trunnion = trunnion.cut(end_relief)
    part = shoe.union(trunnion).union(_trigger_stage1_leaf(p)).union(_trigger_stage2_tooth(p))
    return part.combine(glue=True, clean=True)


def phase2_ath09(p: AeroThrottleParameters | None = None) -> cq.Workplane:
    """Return ATH_09 using the approved PETG-specific force re-solve."""
    parameters = p or AeroThrottleParameters(material="PETG")
    if parameters.material != "PETG":
        raise ValueError("ATH_09 is allocated to PETG; use AeroThrottleParameters(material='PETG')")
    part = ath_09_dual_trigger(parameters)
    return part.mirror("XY") if parameters.handedness == -1 else part
