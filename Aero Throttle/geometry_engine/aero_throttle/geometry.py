"""CadQuery geometry kernel for Phase 1, authored in the global Y-up frame."""

from __future__ import annotations

import cadquery as cq

from .parameters import AeroThrottleParameters


def box(x: float, y: float, z: float, center: tuple[float, float, float]) -> cq.Workplane:
    """Create an axis-aligned design-frame box from explicit extents and centre."""
    return cq.Workplane("XY").box(x, y, z).translate(center)


def cylinder_z(diameter: float, height: float, center: tuple[float, float, float]) -> cq.Workplane:
    return cq.Workplane("XY").circle(diameter / 2).extrude(height).translate((center[0], center[1], center[2] - height / 2))


def cylinder_y(diameter: float, height: float, center: tuple[float, float, float]) -> cq.Workplane:
    return cq.Workplane("XZ").circle(diameter / 2).extrude(height).translate((center[0], center[1] - height / 2, center[2]))


def cylinder_x(diameter: float, height: float, center: tuple[float, float, float]) -> cq.Workplane:
    return cq.Workplane("YZ").circle(diameter / 2).extrude(height).translate((center[0] - height / 2, center[1], center[2]))


def prism_xy(points: list[tuple[float, float]], z_height: float, z_center: float = 0.0) -> cq.Workplane:
    return cq.Workplane("XY").polyline(points).close().extrude(z_height).translate((0, 0, z_center - z_height / 2))


def prism_yz(points: list[tuple[float, float]], x_length: float, x_start: float = 0.0) -> cq.Workplane:
    """Extrude an explicit YZ profile along +X in the global design frame."""
    return cq.Workplane("YZ").polyline(points).close().extrude(x_length).translate((x_start, 0, 0))


def prism_xz(points: list[tuple[float, float]], y_height: float, y_center: float = 0.0) -> cq.Workplane:
    """Extrude an explicit XZ profile along Y, correcting CadQuery's -Y normal."""
    return cq.Workplane("XZ").polyline(points).close().extrude(y_height).translate((0, y_center + y_height / 2, 0))


def bore_z(diameter: float, height: float, center: tuple[float, float, float], p: AeroThrottleParameters) -> cq.Workplane:
    """The single compensated circular-hole generator for Phase 1."""
    return cylinder_z(diameter + p.hole_comp, height + 2 * p.eps, center)


def bevelled_box(x: float, y: float, z: float, center: tuple[float, float, float], chamfer: float) -> cq.Workplane:
    """Axis-aligned box with the requested deterministic exterior edge chamfer."""
    return box(x, y, z, center).edges().chamfer(chamfer)


def seam_ribbon(mode: str, p: AeroThrottleParameters) -> cq.Workplane:
    """Single-source tongue/groove geometry, interrupted at the trim window."""
    if mode not in {"tongue", "groove"}:
        raise ValueError(f"Unsupported seam mode: {mode}")
    width = p.seam_tongue_thick if mode == "tongue" else p.seam_groove_w
    depth = p.seam_tongue_height if mode == "tongue" else p.seam_groove_d
    y_center = depth / 2 if mode == "tongue" else -depth / 2
    rail = box(p.seam_x_max, depth, width, (p.seam_x_max / 2, y_center, 0))
    window = box(
        p.trim_wheel_od,
        depth + 2 * p.eps,
        p.trim_wheel_width + 2 * p.trim_pocket_clear_z,
        (p.trim_wheel_center_x, y_center, p.trim_wheel_mid_z),
    )
    return rail.cut(window)


def key_feature(mode: str, station_x: float, p: AeroThrottleParameters) -> cq.Workplane:
    """Generate either the physical key or a socket with FC-STATIC applied once."""
    if mode == "key":
        return box(p.key_side, p.key_len, p.key_side, (station_x, 0, 0))
    if mode == "socket":
        return box(p.key_socket_side, p.key_socket_depth, p.key_socket_side, (station_x, -p.key_socket_depth / 2, 0))
    raise ValueError(f"Unsupported key mode: {mode}")


def snap_feature(mode: str, station_x: float, station_z: float, p: AeroThrottleParameters) -> cq.Workplane:
    """Mating hook/pocket pair; the pocket owns FC-SNAP clearance."""
    # The mechanism-flank rear hook is constrained by the trim pocket.  Move
    # only that hook to the derived safe station; its paired pocket shares this
    # helper, so the full 15 mm beam and FC-SNAP relationship are preserved.
    if station_z > 0:
        station_x = min(station_x, p.trim_safe_snap_hook_station_x)
    if mode == "hook":
        beam = box(p.snap_hook_len, p.snap_hook_t, p.snap_hook_w, (station_x, p.snap_hook_t / 2, station_z))
        barb = box(p.snap_barb_depth, p.snap_hook_t + p.snap_barb_depth, p.snap_hook_w, (station_x + p.snap_hook_len / 2 - p.snap_barb_depth / 2, p.snap_hook_t + p.snap_barb_depth / 2, station_z))
        return beam.union(barb)
    if mode == "pocket":
        return box(p.snap_pocket_w, p.snap_hook_t + p.snap_barb_depth + 2 * p.fit_clearance_snap, p.snap_hook_w + 2 * p.fit_clearance_snap, (station_x + p.snap_hook_len / 2, -p.fit_clearance_snap, station_z))
    raise ValueError(f"Unsupported snap mode: {mode}")
