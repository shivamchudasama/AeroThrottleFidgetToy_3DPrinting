"""Feature catalog keyed by deterministic feature ID."""

from __future__ import annotations

from geometry_engine.feature_model import Feature


def index_by_id(features: list[Feature]) -> dict[str, Feature]:
    indexed = {feature.feature_id: feature for feature in features}
    if len(indexed) != len(features):
        raise ValueError("feature IDs must be unique")
    return indexed
