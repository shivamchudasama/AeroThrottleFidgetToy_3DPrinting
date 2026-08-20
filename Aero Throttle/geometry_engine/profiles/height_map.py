"""Height-map placeholder for profile-based geometry."""

from __future__ import annotations


def constant_height(value: float):
    if value <= 0:
        raise ValueError("height must be positive")
    return lambda _x, _y: value
