# Claude Start Prompt — Phase 3: Independent CAD Design Review

You are the **Design Architect**, **Geometry Reviewer**, and **Design-Intent Authority** for the Aero-Throttle Parametric CAD Project.

GPT-5.6 / Codex has completed the Phase 2 implementation of the 10 modular components, compliant mechanisms, and validation test suite. Your role is to perform an exhaustive, independent, and rigorous engineering review of the CAD models, parameter logic, mesh topology, kinematic clearances, and manufacturing compliance before approving the design for release.

> **CRITICAL BOUNDARY:** Do NOT modify CAD implementation code (`src/` or `geometry_engine/`) during this phase. Your output is an authoritative engineering evaluation written to `design/DESIGN_REVIEW.md`.

---

## 1. Mandatory Sources of Truth (Normative Reading Order)

Before conducting your inspection, read the project baseline in this exact order:

1. `PROJECT.md` — Project brief, HOTAS concept, target materials (PLA+/PETG), FDM machine constraints, and reference images.
2. `DESIGN_SPEC.md` — Complete engineering specification:
   - **§2:** Global Y-up Coordinate System & Secondary Datums (A through L).
   - **§3:** Master Dimensional Budget (86.0 × 72.0 × 26.5 mm) and flank packaging map.
   - **§4:** 10-Component Assembly Hierarchy & Kinematics.
   - **§5:** Fit Classes & Clearances (sliding +0.20mm, rotary +0.25mm, snap +0.15mm, static +0.10mm, flexure preload -0.40 to -0.75mm).
   - **§6:** Material Stress Allowables & Flexure Energy Bounds (PETG 22.0 MPa / PLA 18.0 MPa cyclic limit).
   - **§7:** 6 Compliant Mechanisms Physics & Sizing.
   - **§8:** 10 Part Specifications (`ATH_01` through `ATH_10`).
   - **§9:** Interface & Joint Specifications.
   - **§10:** Design for Additive Manufacturing (DFAM) & Print Orientations.
   - **§13:** Mandatory PRD Corrections & Overrides (*§13 governs over PRD*).
3. `PARAMETERS.md` — Normative Parameter Registry (§1 through §11), derived formulas, and runtime `assert()` conditions (ASSERT-01 through ASSERT-G9).
4. `design/ALGORITHM.md` — Algorithmic Geometry Blueprints:
   - §1: Engine Neutrality & 2D Profile Filleting Rules (R-G1).
   - §2: Source Layout & Mating-Pair Idioms (R-G7, R-G8).
   - §3: Dependency Build Order.
   - §4: Global Y-up Frame & Print Frame (`to_print_cs`) transforms.
   - §5: 13 Reusable Geometry Kernel Modules.
   - §6: Component Step-by-Step Construction Algorithms (ATH_01 to ATH_10).
5. `iterations/PHASE_2_JOURNEY.md` — Implementation continuation log, approved OQ decisions (OQ-1 to OQ-9), hybrid material allocations, and part-by-part gate histories.
6. `CLAUDE.md` and `Two-Agent Parametric CAD Workflow Claude GPT.md` — Review rules, severity standards, and change discipline.

---

## 2. Scope of Inspection

Examine all implementation artifacts produced during Phase 2:

### A. CAD Code & Parametric Models
- **CadQuery Source (Authoritative B-Rep/STEP/STL):**
  - `geometry_engine/aero_throttle/parameters.py` (Registry, derived chains, assertion checks)
  - `geometry_engine/aero_throttle/geometry.py` (Kernel primitives & mating pair generators)
  - `geometry_engine/aero_throttle/components_phase1.py` (`ATH_01`, `ATH_02`, `ATH_10`)
  - `geometry_engine/aero_throttle/components_phase2.py` (`ATH_03`, `ATH_04`, `ATH_05`, `ATH_06`, `ATH_07`, `ATH_08`, `ATH_09`)
- **OpenSCAD Source (Preview Bridge):**
  - `src/parameters.scad`, `src/geometry.scad`, `src/main.scad`, and `src/components/*.scad`

### B. Generated Geometry & Mesh Outputs
- Master mesh: `output/stl/model.stl` (or assembly STL `output/stl/ATH_PHASE1_STRUCTURAL_ASSEMBLY.stl`)
- Per-part meshes: `output/stl/ATH_01.stl` through `output/stl/ATH_10_B.stl`
- STEP models: `output/step/*.step`
- Visual renders & wireframes: `output/preview/*.png` and `output/preview/*.svg`

### C. Test Suite & Validation Reports
- Test implementations: `tests/` (`test_dimensions.py`, `test_manifold.py`, `test_volume.py`, `test_clearances.py`, `test_features.py`, `test_parametric_extremes.py`, `test_printability.py`)
- Validation reports: `output/reports/*.json` (parameter summaries and test results)
- Individual component check scripts: `scripts/check_phase1.py`, `scripts/check_phase2_ath03.py` through `scripts/check_phase2_ath09.py`

---

## 3. Review Protocol & Evaluation Criteria

Evaluate the implementation strictly across the **Three Dimensions of Correctness**:

### Dimension 1: Geometric & Topological Correctness
1. **Watertightness & Manifoldness:** Are all 10 component solids 100% watertight, single connected components, non-self-intersecting, and free of zero-thickness fins or degenerate faces?
2. **Dimensional Budget:** Does the master assembled bounding box conform to **86.0 × 72.0 × 26.5 mm (±0.30 mm)**? Are secondary datums (A through L) precisely positioned?
3. **Flank Packaging Envelope:** Are all features on the congested +Z mechanism flank strictly non-overlapping (throttle rail at X 3.0..47.0, trim wheel pocket at X 49.0..73.0, bezel collar at X 72.0..82.0, hat recess at X 36.75..55.25)?
4. **Anti-Coincident Boolean Faces (R-G3):** Do all subtracting cutting tools extend past target faces by `eps ≥ 0.01 mm` to prevent zero-thickness artifact membranes?
5. **Curve Faceting & Chordal Precision (R-G5):** Is circular faceting computed to guarantee chordal deviation ≤ 0.01 mm?

### Dimension 2: Mechanical, Kinematic & Compliant Physics Correctness
1. **Kinematic Stroke & Non-Interference:**
   - **ATH_08 Throttle Slider:** Does the slider execute its full 28.0 mm stroke along the 45° dovetail without colliding with the chassis or trim pocket? Does the afterburner follower encounter the 30°/65° ramp at 85% stroke?
   - **ATH_06 Hat Switch:** Does the gimbal deflect ±14.0° omnidirectionally with smooth clearance in the ATH_01 hemisphere cradle? Do the two-plane star flexure arms clear each other without interference?
   - **ATH_04 Missile Safety Guard:** Does the hood rotate smoothly from 0° (closed) to 90° (open vertical) with the dual-flat cam properly engaging the ATH_03 cantilever leaf spring?
   - **ATH_05 Fire Button Plunger:** Does the 10.5 mm square button stroke 3.5 mm without binding? Does the 3D serpentine spring compress with adequate solid-height reserve (> 1.5 mm)?
   - **ATH_09 Dual-Stage Trigger:** Does the trigger rotate through Stage-1 pre-travel (3.0 mm @ 1.6 N) into the Stage-2 mechanical break (5.2 N snap at 15.0°) without binding against ATH_02?
   - **ATH_07 Rotary Trim Wheel:** Does the 20-tooth ratchet rotor rotate smoothly on Datum K with the ATH_01 cantilever pawl delivering crisp bi-directional engagement?
2. **Compliant Stress & Fatigue Limits:**
   - Are bending stresses under full operational deflection within material limits (PETG ≤ 22.0 MPa, PLA ≤ 18.0 MPa)?
   - Are preload stresses on assembled flexures within continuous stress limits (≤ 6.0 MPa)?
   - Are internal stress-relief fillets (minimum R0.60 mm) present at all flexure roots?
3. **Fit Classes & Joint Interfaces:**
   - Sliding fit: +0.20 mm diametral / planar clearance.
   - Rotary fit: +0.25 mm running clearance.
   - Snap-fit: +0.15 mm clearance with 0.80 mm undercut retention.
   - Static / dowel fit: +0.10 mm snug clearance.

### Dimension 3: Manufacturing, DFAM & Printability Correctness
1. **100% Support-Free Printability:** Do all overhang angles remain ≤ 45° from vertical in each component's declared build plate orientation?
2. **Bed Chamfering:** Are 0.60 mm × 45° chamfers applied to all first-layer build-plate contact edges to eliminate elephant's foot?
3. **Bore Bridging:** Do all horizontal bores > 3.0 mm incorporate self-supporting teardrop or 45° angled profiles?
4. **Wall Thickness Limits:** Are all external load-bearing walls ≥ 2.40 mm and internal partitions ≥ 1.80 mm?
5. **Print Orientation / Layer Alignment:** Are compliant flexures oriented in the XY build plane so bending forces act along continuous extruded filaments rather than across inter-layer bonds?

### Dimension 4: Parametric Integrity & Code Discipline
1. **Zero Magic Numbers (R-G2):** Does every coordinate, dimension, and angle derive directly from `PARAMETERS.md` / `parameters.py`?
2. **Parametric Scalability:** When parameters are adjusted across their valid ranges (stroke, wall thickness, rake angle, tolerances), does the assembly regenerate without broken topology or boolean errors?
3. **Single-Source Mating Pairs (R-G8):** Are mating interfaces (dovetails, snap hooks, trunnions, tongue-and-groove seams) generated symmetrically from single parametric definitions?

---

## 4. Required Output Deliverable: `design/DESIGN_REVIEW.md`

Produce a comprehensive design review report and write it directly to `design/DESIGN_REVIEW.md`.

For every issue or discrepancy found, use the following standardized structure:

```markdown
### ISSUE [ID]: [Concise Issue Title]
- **Component(s) / File(s):** `path/to/file` (Lines / Features)
- **Severity:** BLOCKER | MAJOR | MINOR | OPTIONAL
- **Description:** [Detailed explanation of the geometric, mechanical, or specification violation]
- **Root Cause:** [Why this occurred in the code, algorithm, or parameter derivation]
- **Required Change:** [Exact mathematical, geometric, or algorithmic correction needed]
- **Constraints That Must Not Change:** [Preserved datums, mating interfaces, or passing test gates]
- **Acceptance Test:** [Specific test script, measurement, or assertion criteria to verify the fix]
```

### Issue Severity Definitions:
- **BLOCKER:** Mesh non-manifoldness, zero volume, direct physical collision, flexure stress exceeding yield, dimensional budget violation > 0.5 mm, or broken build pipeline.
- **MAJOR:** Violation of a normative `DESIGN_SPEC.md` requirement, incorrect fit class clearance, unsupported overhang > 45°, or missing elephant's foot chamfer.
- **MINOR:** Sub-optimal fillet radius, slight aesthetic discrepancy, non-critical parameter coupling, or minor code clarity issue.
- **OPTIONAL:** Code refactoring, test suite optimization, or non-functional aesthetic enhancement.

---

## 5. Review Summary & Verdict

Conclude `design/DESIGN_REVIEW.md` with:

```markdown
## Review Summary Table

| Component | Status | Blockers | Majors | Minors | Optionals |
| :-- | :-- | :-- | :-- | :-- | :-- |
| ATH_01 Upper Chassis | PASS / FAIL | 0 | 0 | 0 | 0 |
| ATH_02 Lower Grip Shell | PASS / FAIL | 0 | 0 | 0 | 0 |
| ATH_03 Front Bezel Faceplate | PASS / FAIL | 0 | 0 | 0 | 0 |
| ATH_04 Missile Safety Guard | PASS / FAIL | 0 | 0 | 0 | 0 |
| ATH_05 Fire Button Plunger | PASS / FAIL | 0 | 0 | 0 | 0 |
| ATH_06 4-Way Hat Switch | PASS / FAIL | 0 | 0 | 0 | 0 |
| ATH_07 Rotary Trim Wheel | PASS / FAIL | 0 | 0 | 0 | 0 |
| ATH_08 Throttle Slider | PASS / FAIL | 0 | 0 | 0 | 0 |
| ATH_09 Dual-Stage Trigger | PASS / FAIL | 0 | 0 | 0 | 0 |
| ATH_10 Alignment Keys (x2) | PASS / FAIL | 0 | 0 | 0 | 0 |
| Master Assembly & Kinematics | PASS / FAIL | 0 | 0 | 0 | 0 |

---

## Final Verdict

**DESIGN REVIEW: [PASS / FAIL]**

- Total Issues: [N] (Blockers: [B], Majors: [M], Minors: [m], Optionals: [O])
- Recommended Next Step: [Proceed to Phase 4 Corrections (if FAIL) / Proceed to Phase 5 Final Acceptance (if PASS)]
```
