# Feature Data Model

Use `geometry_engine.feature_model.Feature` for feature-heavy or recurring design families. Every generated feature should record:

- `feature_id`
- `position`
- `orientation`
- `dimensions`
- `classification`
- `profile_level`
- `height`
- `feature_type`

Keep feature data separate from CAD-engine calls so geometry can be regenerated, inspected, and tested deterministically.
