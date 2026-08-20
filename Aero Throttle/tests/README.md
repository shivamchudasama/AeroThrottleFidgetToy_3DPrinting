# Validation Suite

Run the complete validation suite from the project root:

```text
python scripts/validate.py
```

Configure `validation_config.json` before treating the result as release evidence. The default configuration deliberately has no expected dimensions or volume, and refers to `output/stl/model.stl`.

## Test ownership

- `test_dimensions.py`: bounding box and placement.
- `test_volume.py`: non-zero and configured volume limits.
- `test_manifold.py`: mesh validity, watertightness, components, and an optional self-intersection command.
- `test_clearances.py`: project-specific clearance and manufacturability command.
- `test_features.py`: project-specific feature, spacing, symmetry, and mating-geometry command.
- `test_parametric_extremes.py`: rebuilds configured parameter sweeps and validates every exported mesh.

`trimesh` is required for mesh-based checks. Install the project dependencies with:

```text
python -m pip install -r requirements.txt
```

## Project-specific checks

Generic STL analysis cannot reliably infer a design's intended features, clearances, or all self-intersections. Configure each required check under `project_checks` with a command that exits 0 only when the stated constraint passes. Commands run from the project root. For example:

```json
"clearances": {
  "required": true,
  "command": ["python", "scripts/check_clearances.py"]
}
```

## Parameter sweeps

Each `parametric_sweeps` item needs a `name`, a build `command`, and the generated `mesh_path`. It may also set `expected_bounds_mm`, `min_volume_mm3`, and `max_volume_mm3`. The sweep test rejects missing, non-watertight, empty, or out-of-range meshes.
