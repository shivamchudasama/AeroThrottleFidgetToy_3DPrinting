"""Deterministic placement patterns."""

from __future__ import annotations


def linear_positions(count: int, spacing: float, origin: float = 0.0) -> list[float]:
    if count < 1:
        raise ValueError("count must be at least one")
    if spacing <= 0:
        raise ValueError("spacing must be positive")
    return [origin + index * spacing for index in range(count)]
