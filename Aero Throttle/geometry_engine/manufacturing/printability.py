"""Printability policy used by project-specific validation checks."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PrintabilityPolicy:
    minimum_wall_mm: float
    minimum_feature_mm: float
    maximum_unsupported_overhang_degrees: float
