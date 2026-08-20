"""Coordinate helpers for reusable geometry generation."""

from __future__ import annotations


def translate(point: tuple[float, float, float], offset: tuple[float, float, float]) -> tuple[float, float, float]:
    return tuple(a + b for a, b in zip(point, offset))
