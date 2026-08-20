# Changelog

## Unreleased

### Phase 1 structural-root implementation

- Changed files: CadQuery parameter model, Phase 1 geometry kernel, ATH_01/ATH_02/ATH_10 generators, Phase 1 exporter and validator.
- Reason for change: implement the first incomplete phase using the approved CadQuery/OCCT authority.
- Expected effect: deterministic, global-Y-up structural-root solids with material metadata and machine-readable derived parameters.
- Validation performed: STL/STEP export, watertight/single-body mesh validation, parameter-chain assertions, Python bytecode compilation, and preview inspection.
- Remaining issues: ATH_03 through ATH_09, PETG flexure re-solves, full export pipeline, and objective full-assembly validators remain Phase 2–4 scope.

---
