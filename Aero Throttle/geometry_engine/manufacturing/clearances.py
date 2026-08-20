"""Manufacturing clearance policy."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClearancePolicy:
    minimum_clearance_mm: float

    def __post_init__(self) -> None:
        if self.minimum_clearance_mm <= 0:
            raise ValueError("minimum_clearance_mm must be positive")
