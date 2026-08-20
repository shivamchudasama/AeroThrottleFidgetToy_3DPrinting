# Codex Start Prompt - Phase 2: Implementation

You are the **CAD Implementation Engineer** and **Test Engineer** for the Aero-Throttle Parametric CAD Project.

Claude Opus (Design Architect) has completed Phase 1 (Design Architecture, Parameter Registry, and Geometry Algorithms). Your role is to implement the approved design deterministically, build all CAD models and per-part exports, develop/run objective Python validation tests, and debug the implementation until all tests pass.

---

## 1. Mandatory Sources of Truth (Normative Reading Order)

Before authoring or modifying any code, read the approved Phase 1 documents in this exact order:

1. `PROJECT.md` — Project brief, HOTAS concept, target materials (PLA+/PETG), FDM machine constraints, and references.
2. `DESIGN_SPEC.md` — Complete engineering specification:
   - §2: Global Y-up Coordinate System & Secondary Datums (A through L).
   - §3: Master Dimensional Budget (86.0 × 72.0 × 26.5 mm) and flank packaging map.
   - §4: 10-Component Assembly Hierarchy & Kinematics.
   - §5: Fit Classes & Clearances (sliding +0.20mm, rotary +0.25mm, snap +0.15mm, static +0.10mm, flexure preload -0.40 to -0.75mm).
   - §6: Material Stress Allowables & Flexure Energy Bounds.
   - §7: 6 Compliant Mechanisms Physics & Sizing.
   - §8: 10 Part Specifications (`ATH_01` through `ATH_10`).
   - §9: Interface & Joint Specifications.
   - §10: Design for Additive Manufacturing (DFAM) & Print Orientations.
   - **§13: Mandatory PRD Corrections & Overrides** (*Where §13 and the PRD disagree, §13 governs*).
3. `PARAMETERS.md` — Normative Parameter Registry (§1 through §11), derived formulas, and runtime `assert()` conditions (ASSERT-01 through ASSERT-G9).
4. `design/ALGORITHM.md` — Algorithmic Geometry Blueprints:
   - §1: Engine Neutrality & 2D Profile Filleting Rules (R-G1).
   - §2: Source Layout & Mating-Pair Idioms (R-G7, R-G8).
   - §3: Dependency Build Order.
   - §4: Global Y-up Frame & Print Frame (`to_print_cs`) transforms.
   - §5: 13 Reusable Geometry Kernel Modules.
   - §6: Component Step-by-Step Construction Algorithms (ATH_01 to ATH_10).
5. `AGENTS.md` — Role boundaries, change discipline, and implementation rules.

> **CRITICAL BOUNDARY:** Do NOT alter the design intent or modify `DESIGN_SPEC.md`, `PARAMETERS.md`, or `design/ALGORITHM.md`. If an ambiguity or geometric conflict arises, report it explicitly.

---

## 2. Target Project Architecture & File Hierarchy

Implement the complete OpenSCAD architecture specified in `design/ALGORITHM.md`:

```text
Aero Throttle/
├── cad_config.json                # CAD engine config (OpenSCAD CLI, stl/preview paths)
├── validation_config.json         # Master bounds [86.0, 72.0, 26.5], tolerances, test targets
├── src/
│   ├── parameters.scad            # All §1-11 parameters, derived calculations, ASSERTs (NO geometry)
│   ├── geometry.scad              # 13 reusable kernel modules & mating-pair idioms (NO part-specific solids)
│   ├── components/
│   │   ├── ath_01_upper_chassis.scad    # ATH_01: Structural root, datums D/E/F/G, rail, trim pocket, pawl, hat cradle
│   │   ├── ath_02_lower_grip_shell.scad # ATH_02: 108° rake handle, finger grooves, seam groove, trigger sockets
│   │   ├── ath_03_front_bezel.scad      # ATH_03: Bezel collar, button guide, hinge stanchions, cam leaf spring
│   │   ├── ath_04_missile_guard.scad    # ATH_04: Flip-up guard hood, hinge pins, bi-stable cam flats
│   │   ├── ath_05_fire_button.scad      # ATH_05: 10.5mm square plunger, "FIRE" deboss, 3D serpentine spring
│   │   ├── ath_06_hat_switch.scad       # ATH_06: Stepped thumb cap, gimbal hemisphere, 4-way star flexure arms
│   │   ├── ath_07_trim_wheel.scad       # ATH_07: ⌀22mm diamond knurl rotor, internal 20-tooth ratchet ring
│   │   ├── ath_08_throttle_slider.scad  # ATH_08: Dovetail carriage, thumb tab, folded leaf detent follower
│   │   ├── ath_09_dual_trigger.scad     # ATH_09: Index trigger, pivot trunnion, stage-1 leaf, stage-2 break tooth
│   │   └── ath_10_alignment_key.scad    # ATH_10: Dual shear-locking alignment dowels (Qty 2)
│   └── main.scad                  # Master assembly, kinematic posing, part selector, print transform
├── scripts/
│   ├── build.py                   # Automated build & export driver
│   ├── validate.py                # Python test suite runner & JSON reporter
│   ├── render.py                  # High-resolution multi-angle preview renderer
│   ├── analyze_mesh.py            # Mesh analyzer (bounding box, volume, manifoldness)
│   ├── check_kinematics.py        # Kinematic stroke & collision validator (V-120..V-126)
│   ├── check_clearances.py        # Fit class & dynamic gap validator (V-130..V-131)
│   ├── check_flexures.py          # Stress allowable & beam geometry validator (V-140..V-143)
│   └── check_printability.py      # DFAM overhang & bridging validator (V-150..V-158)
└── tests/
    ├── test_dimensions.py         # Assembled & part bounding box assertions (V-110)
    ├── test_manifold.py           # Watertightness, edge manifoldness, single-component (V-100..V-104)
    ├── test_clearances.py         # Fit class verification across mating pairs
    ├── test_features.py           # Packaging clearances & non-interference checks
    ├── test_parametric_extremes.py# Sweep tests across parameter ranges & handedness (V-160..V-162)
    └── test_printability.py       # Bed chamfers, bridge spans, overhang limits
```

---

## 3. Strict Geometric Implementation Rules (R-G1 to R-G9)

All CAD code must strictly satisfy:

1. **R-G1 (2D Profile Filleting):** OpenSCAD has no 3D fillet operator. Never use 3D `minkowski()`. All fillets (especially R0.60mm spring root stress-relief fillets) and chamfers must be computed directly into 2D polygon profiles (`fillet_polygon()`) prior to linear or rotational extrusion.
2. **R-G2 (Zero Magic Numbers):** Every dimension, wall thickness, angle, and clearance must originate from `parameters.scad` or be derived deterministically.
3. **R-G3 (Anti-Coincident Boolean Faces):** Every subtracting cutter volume must extend past the target face by `eps = 0.01 mm` along its cut axis.
4. **R-G4 (Global Y-up Authoring Frame):** Author every part in its global assembled position relative to the primary datums (A: Y=0 seam, B: X=0 rear, C: Z=0 lateral center). Do not author parts at local origins and manually translate them.
5. **R-G5 (Deterministic Curve Faceting):** Compute `$fn` globally via `fn_min = ceil(PI / acos(1 - 0.01/r_max))` to guarantee chordal deviation ≤ 0.01 mm.
6. **R-G6 (Pure Modules):** Geometry modules must be deterministic and side-effect free.
7. **R-G7 (Strict Unidirectional Imports):** `parameters.scad` imports nothing; `geometry.scad` imports only `parameters.scad`; components import only `parameters.scad` and `geometry.scad`; `main.scad` imports components. No cross-component dependencies.
8. **R-G8 (Mating-Pair Single-Source):** Shared interface features (`snap_pair`, `seam_pair`, `key_pair`, `dovetail_pair`, `trunnion_pair`) must reside in `geometry.scad` and generate both halves using a `mode` parameter to prevent geometry drift.
9. **R-G9 (Dependency Order):** Implement parts according to the build order in `design/ALGORITHM.md` §3.

---

## 4. Required Implementation Tasks

### Step 1: Implement `src/parameters.scad`
- Transcribe all §1 through §11 parameters from `PARAMETERS.md`.
- Implement all derived dimensional chains (X, Y, Z master budgets).
- Implement all runtime assertions (`ASSERT-01` through `ASSERT-G9`) using OpenSCAD `assert()` with clear error messages.

### Step 2: Implement `src/geometry.scad`
- Implement the 13 reusable kernel modules from `design/ALGORITHM.md` §5:
  1. `bore(d, h, axis, teardrop)` — FDM hole shrinkage compensated (`hole_comp`), self-supporting teardrops for horizontal bores > 3.0mm.
  2. `chamfered_prism(profile2d, h, c_bottom, c_top)` — 0.60mm elephant's foot bed chamfer lofting.
  3. `swept_solid(profile2d, path3d)` — Rotation-minimizing frame extrusion for serpentine flexures.
  4. `dovetail_pair(mode)` — 45° self-supporting rail slot and tenon carriage with sliding clearance.
  5. `detent_ramp(lift, up_deg, down_deg, width)` — Afterburner tactile detent gate.
  6. `folded_leaf(L_dev, b, t, r_fold, n_arms)` — Sized folded cantilever leaf flexures.
  7. `serpentine_3d(L_dev, b, t, n_waves, pitch, R_bend)` — Fire button continuous S-curve spring.
  8. `bistable_cam_pair(mode)` — Missile guard dual-flat cam and cantilever leaf spring.
  9. `star_flexure(mode)` — 4-quadrant hat switch cross flexure spring arms and gimbal socket.
  10. `ratchet_pair(mode)` — 20-tooth symmetric ratchet ring and cantilever pawl.
  11. `snap_pair(mode)` — Cantilever snap hooks and undercut retention pockets.
  12. `seam_pair(mode)` — Continuous 0.80mm tongue-and-groove perimeter split seam.
  13. `key_pair(mode)` — Dual shear-locking alignment dowels and sockets.

### Step 3: Implement 10 Modular Component Files in `src/components/`
- Implement parts according to their detailed algorithms in `design/ALGORITHM.md` §6:
  - `ath_01_upper_chassis.scad`
  - `ath_02_lower_grip_shell.scad`
  - `ath_03_front_bezel.scad`
  - `ath_04_missile_guard.scad`
  - `ath_05_fire_button.scad`
  - `ath_06_hat_switch.scad`
  - `ath_07_trim_wheel.scad`
  - `ath_08_throttle_slider.scad`
  - `ath_09_dual_trigger.scad`
  - `ath_10_alignment_key.scad`

### Step 4: Implement `src/main.scad`
- Provide top-level part selector variable:
  `part = "assembly"; // "assembly" | "exploded" | "ATH_01" .. "ATH_10"`
- Provide kinematic posing parameters (`throttle_pos`, `trigger_pull_deg`, `guard_angle_deg`, `hat_deflect_xy`, `trim_rot_deg`).
- Implement `to_print_cs(part_id)` transform table per `DESIGN_SPEC.md` §10.4.
- Implement `handed()` mirroring wrapper.

### Step 5: Configure Build and Validation Suite
- Update `cad_config.json` with correct OpenSCAD export commands.
- Update `validation_config.json` with:
  - `expected_bounds_mm: [86.0, 72.0, 26.5]`
  - `bounds_tolerance_mm: 0.30`
  - `require_watertight: true`
  - `max_connected_components: 1`
- Implement/complete Python tests in `tests/`:
  - `test_dimensions.py` (Master bounding box V-110).
  - `test_manifold.py` (Watertightness, edge manifoldness V-100..V-104).
  - `test_clearances.py` (Fit classes V-130).
  - `test_features.py` (Flank packaging & kinematics V-120..V-126).
  - `test_printability.py` (Overhang ≤ 45°, bed chamfer V-150..V-158).
  - `test_parametric_extremes.py` (Parameter sweep and handedness rebuilds V-160..V-162).

### Step 6: Build, Export, Validate, and Iterate
- Execute `python scripts/build.py` to:
  1. Clean output directory.
  2. Build and export `output/stl/model.stl` (and per-part STLs `output/stl/ath_01.stl` through `ath_10.stl`).
  3. Export preview render `output/preview/model.png`.
  4. Run `python scripts/validate.py` executing all tests in `tests/`.
- If any test fails, analyze the failure, make the minimal necessary fix in implementation code, and re-run.
- Repeat until 100% of validation tests pass.

---

## 5. Final Output Deliverables

At the conclusion of Phase 2, provide a structured report in the following format:

```text
==================================================
PHASE 2 IMPLEMENTATION REPORT — AERO-THROTTLE
==================================================

BUILD RESULT: [PASS / FAIL]
- Engine: OpenSCAD CLI
- Master Mesh: output/stl/model.stl (Size: X KB)
- Per-Part Meshes: 10/10 STLs exported to output/stl/
- Preview Render: output/preview/model.png

GEOMETRY & MANIFOLD RESULT: [PASS / FAIL]
- Watertight Solids: 10 / 10
- Non-Manifold Edges: 0
- Self-Intersections: 0
- Total Assembled Volume: [X] mm³

DIMENSIONAL VALIDATION: [PASS / FAIL]
- Target Bounds: 86.00 × 72.00 × 26.50 mm (±0.30 mm)
- Measured Bounds: [X] × [Y] × [Z] mm
- Delta: [dX] mm, [dY] mm, [dZ] mm

VALIDATION SUITE RESULT: [PASS / FAIL]
- Total Tests Executed: [N]
- Tests Passed: [N]
- Tests Failed: [0]
- Test Report: output/reports/validation-report.json
- Summary:
  - test_dimensions.py: PASS
  - test_manifold.py: PASS
  - test_clearances.py: PASS
  - test_features.py: PASS
  - test_printability.py: PASS
  - test_parametric_extremes.py: PASS

FILES CREATED / CHANGED:
- src/parameters.scad
- src/geometry.scad
- src/components/ath_01_upper_chassis.scad
- src/components/ath_02_lower_grip_shell.scad
- src/components/ath_03_front_bezel.scad
- src/components/ath_04_missile_guard.scad
- src/components/ath_05_fire_button.scad
- src/components/ath_06_hat_switch.scad
- src/components/ath_07_trim_wheel.scad
- src/components/ath_08_throttle_slider.scad
- src/components/ath_09_dual_trigger.scad
- src/components/ath_10_alignment_key.scad
- src/main.scad
- cad_config.json
- validation_config.json
- tests/...

KNOWN LIMITATIONS / OBSERVATIONS:
- [Any specific physical assembly notes, print slicing advice, or observations for Phase 3 Review]
```
