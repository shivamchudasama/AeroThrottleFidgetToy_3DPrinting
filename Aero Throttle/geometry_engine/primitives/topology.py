"""Topology policy definitions shared by geometry generators and tests."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TopologyPolicy:
    require_watertight: bool = True
    max_connected_components: int = 1
