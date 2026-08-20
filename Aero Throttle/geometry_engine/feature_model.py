"""Engine-neutral data model for deterministically generated CAD features."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


Vector3 = tuple[float, float, float]


@dataclass(frozen=True)
class Feature:
    feature_id: str
    position: Vector3
    orientation: Vector3 = (0.0, 0.0, 0.0)
    dimensions: Mapping[str, float] = field(default_factory=dict)
    classification: str = ""
    profile_level: int | None = None
    height: float | None = None
    feature_type: str = ""

    def __post_init__(self) -> None:
        if not self.feature_id:
            raise ValueError("feature_id must not be empty")
        if len(self.position) != 3 or len(self.orientation) != 3:
            raise ValueError("position and orientation must each contain three values")
        if any(value <= 0 for value in self.dimensions.values()):
            raise ValueError("feature dimensions must be positive")
