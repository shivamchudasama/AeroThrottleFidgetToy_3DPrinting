"""Boundary-profile placeholder for a reusable design family."""

from __future__ import annotations


def rectangular_boundary(width: float, depth: float) -> tuple[tuple[float, float], ...]:
    if width <= 0 or depth <= 0:
        raise ValueError("boundary dimensions must be positive")
    return ((0.0, 0.0), (width, 0.0), (width, depth), (0.0, depth))
