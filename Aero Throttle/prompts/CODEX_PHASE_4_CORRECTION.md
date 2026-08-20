# Codex Start Prompt — Phase 4: Review Corrections

You are the CAD Implementation Engineer. Phase 3 is complete: `design/DESIGN_REVIEW.md`
returned **FAIL** with 17 BLOCKER, 22 MAJOR, 9 MINOR and 4 OPTIONAL issues, and the design
authority has since issued specification corrections. Your job is to resolve every BLOCKER
and MAJOR issue.

---

## 1. Read these first, in this order

1. `AGENTS.md` — your standing rules. They govern everything below.
2. `DESIGN_SPEC.md` **§16** — Phase 3 Specification Corrections. **This section outranks
   §§1–15 of the same document.** Two clauses in the original spec described geometry that
   cannot be built at any tolerance; §16 replaces them. Read §16 before §8.
3. `PARAMETERS.md` **§15** — the companion parameter corrections. **§15 supersedes §12, §13
   and §14.** §14 is retired outright; its PETG scaling table has been deleted so it cannot
   be mistaken for live values.
4. `design/DESIGN_REVIEW.md` — the full issue list, with measured evidence for each.
5. `PROJECT.md`, the rest of `DESIGN_SPEC.md`, the rest of `PARAMETERS.md`,
   `design/ALGORITHM.md`.

Values marked **[S-nn]** in `PARAMETERS.md` §§1–11 changed in this correction. Twenty-four
registry entries moved; do not carry any Phase 2 value forward from memory.

---

## 2. What changed in the specification, and why it matters to you

| Change | Effect on your work |
| :-- | :-- |
| §16.1 — `key_stations_x` = [20.0, 37.0] | The old X = 58.0 station was the same station as the trigger pivot. ATH_01 also gains two internal key-socket bulkheads. |
| §16.2 — `fire_btn_proud` = 2.50, derived | The whole fire-button axial stack moves. `snout_cavity_rear_x` is now 65.50. |
| §16.3 — chassis snout necked down to the collar | ATH_01's body now ends at X = 72.0; the collar is a free-standing boss over X[72, 82]. `front_lower_chamfer` = 2.00. `seam_x_max` keeps its value of 70.00 but changes derivation. |
| §16.6 — print orientation table re-derived | ATH_05 and ATH_08 have **new build faces**. R-P1 is now two tiers (R-P1a mandatory, R-P1b preferred), and three exemptions are recorded in §16.6.1. New rule R-P2 for cross-layer snaps. |
| §16.8 — `bezel_w` = 23.00, `bezel_h` = 25.00 | Restores the 2.40 mm exterior wall around the collar cavity. ATH_04's 1.60 mm hood wall is now an explicit, named exemption. |
| §16.9 — ATH_10 waist rib deleted | The key is a plain 4.00 × 8.00 × 4.00 mm prism with end chamfers. |
| §16.10 — OQ-3 closed | `guard_detent_torque_nmm` = 3.00; `guard_cam_leaf_w` is solved from it and still returns 6.00. |
| §16.11 — hybrid material map is normative | `material` is a **per-part** property, not a global switch. **Every `*_petg` duplicate parameter is void** — delete them. Each flexure now has exactly one material and one published solve. |

Four flexures were re-solved and their published values are in `PARAMETERS.md` §15.3,
§15.5, §15.6 and §15.7. Take the formulas, not the numbers: a solver output typed as a
14-digit constant is a defect (review M-20).

---

## 3. Work order — one subsystem per iteration

`CLAUDE.md` requires one subsystem per iteration. Follow this order; it is
dependency-driven, and steps 1 and 2 exist because a correction loop without working
validators is guesswork.

**Step 1 — Build pipeline (B-17).** Repoint `cad_config.json` at CadQuery. Replace
`scripts/build.py`'s OpenSCAD invocation with one driver that iterates the ten part ids,
applies `to_print_cs`, exports STL + STEP + 3MF plus the master assembly, dumps
`output/reports/parameters.json`, and writes `build-report.json`. Delete or populate the
three empty `src/*.scad` stubs. Keep `src/preview_phase2_*.scad` as the preview bridge.

**Step 2 — Validators (B-16, M-18).** Populate `validation_config.json` per
`design/ALGORITHM.md` §9. Write `scripts/check_kinematics.py`, `check_clearances.py`,
`check_flexures.py`, `check_printability.py`. Implement `tests/test_printability.py`.

> **Gate on step 2:** before touching any geometry, your new validators must **reproduce**
> the nine rest-pose interferences, the four out-of-tolerance clearances, and the
> ten-part overhang failures listed in `design/DESIGN_REVIEW.md` §1.1–§1.4. If they report
> clean, the validators are wrong, not the model. Do not proceed until they fail correctly.

**Step 3 — Geometry kernel (B-14, M-13, M-19).** Implement the eleven missing kernel
modules of `ALGORITHM.md` §5: `fillet_polygon` (with ASSERT-G1), `chamfered_prism`,
`swept_solid`, `dovetail_pair`, `detent_ramp`, `folded_leaf` (with ASSERT-G3),
`arc_serpentine`, `spiral_arm`, `internal_ratchet`, `diamond_knurl`, `deboss`. Refactor the
part modules onto them, with each clearance applied **once inside the module** from its
named fit class. This step alone resolves or de-risks six blockers and is what stops the
mating-pair defect class from recurring.

**Step 4 — Seam subsystem** (B-11, B-13, M-01) — hooks, tongue-and-groove and key sockets,
all reflected correctly about datum A; ATH_01 key bulkheads per §16.1.
**Step 5 — Nose subsystem** (B-01, B-02, B-03, M-02, M-09, M-10) — neck-down, latch
pockets, hinge relocation, button stack, guide length.
**Step 6 — Trim subsystem** (B-04, B-05, B-06, M-04) — relief pocket Z station, radial
pawl, post relief slots.
**Step 7 — Trigger subsystem** (B-07, B-08, M-07, M-08) — stop bar and shelf solved from
the swept arcs, cradle mouth, trunnion chamfer.
**Step 8 — Hat subsystem** (B-09, M-11, M-12) — detent pockets, conical relief, gimbal
socket, two-active-arm force model.
**Step 9 — Throttle subsystem** (M-03, M-05, M-06, M-22) — preload, ramp back on the
channel floor, plate wall thickness, end stop and lead-in.
**Step 10 — Fire-button spring** (B-10) — true arc serpentine, developed length measured
from the wire.
**Step 11 — Printability** (B-15, M-13, M-14) — print-CS transform, overhang elimination,
bed chamfers, 3MF and master-assembly exports, mass check.
**Step 12 — Parametric integrity** (M-16, M-17) — registry reconciliation, per-part
assertion evaluation, then V-160 / V-161 / V-162.

---

## 4. For each issue

1. Locate the responsible implementation.
2. Identify the root cause — the review states one for every issue; confirm or correct it.
3. Make the minimum change that fixes that root cause.
4. Preserve all previously passing behaviour. The list of what currently passes is in
   `design/DESIGN_REVIEW.md` §1.5; treat it as a regression baseline.
5. Rebuild, run the full validation suite, regenerate the preview, inspect it.
6. Confirm the issue's stated **Acceptance Test** passes. Quote the measured number.

---

## 5. Hard rules

- **Never modify a validation threshold to make a build pass.** If a threshold is wrong,
  say why in your report and leave it failing. `AGENTS.md` and `ALGORITHM.md` §9 both bind
  you here. Note in particular that the Phase 2 constant `serpentine_loop_dev_len_petg =
  12.10` existed only to land a stress assertion 0.05 % under its limit; do not repeat that
  pattern anywhere.
- **Never invent a parameter.** 56 parameters currently exist in `parameters.py` that
  `PARAMETERS.md` §§1–11 never declares, and 14 declared ones are missing from the code
  (review M-16). Reconcile in both directions. If you need a value the registry does not
  have, stop and report it as an ambiguity — do not add it silently.
- **Never edit `DESIGN_SPEC.md`, `PARAMETERS.md` or `design/`.** They are design-owned
  (`OWNERSHIP.md`). If a correction cannot be implemented as specified, stop and report it.
- **`eps` is not a clearance.** It is the anti-coincidence allowance of R-G3. Assertion
  ASSERT-35 forbids any clearance expression containing it (review M-04).
- **Rename your ad-hoc assertions.** The implementation's ASSERT-24 … ASSERT-52 collide with
  the numbering in `PARAMETERS.md` §13/§15. Move them to an `ASSERT-Inn` namespace;
  `ASSERT-nn` is reserved for the design documents.

---

## 6. Known open item — do not let it block you

**OQ-10** (`DESIGN_SPEC.md` §16.12) is unanswered: the four seam snap hooks bend across
layers and fail the new R-P2 derated strain limit at 1.44 % against 0.90 %. The project
owner must choose between three resolutions.

For Phase 4, build **option (3)** — the hooks as currently dimensioned (15.00 × 3.50 ×
1.60) — so that B-11's actual defect, hooks sitting on the wrong side of datum A, is fixed
independently of the strain question. Leave ASSERT-33 in place and **let it fail**, and
report it as a known limitation. Do not resize the hooks to silence it.

---

## 7. Scope

Address every **BLOCKER** and **MAJOR**. Address MINOR and OPTIONAL issues only where they
fall out of a change you are already making. Do not address anything that would change
design intent.

---

## 8. Report at completion

```
BUILD:         PASS/FAIL
GEOMETRY:      PASS/FAIL
DIMENSIONS:    PASS/FAIL
PRINTABILITY:  PASS/FAIL
PROJECT TESTS: PASS/FAIL
```

Then list, per `AGENTS.md` and `CLAUDE.md` change discipline:

- files changed
- parameters changed
- tests executed, with the measured numbers for each acceptance test
- issue-by-issue disposition: every BLOCKER and MAJOR id marked resolved, or explained
- remaining known limitations

Update `CHANGELOG.md` with a Phase 4 entry in the existing format (changed files, reason,
expected effect, validation performed, remaining issues) — the Phase 2 entry is still
missing and should be added at the same time (review O-01).

Update `iterations/PHASE_2_JOURNEY.md` so its claims match what your scripts actually
execute. Two current entries do not: the ATH_09 gate is recorded as having "confirmed
0/9.594/15.0/15.6 degree pose stations", and the ATH_07 gate as having validated the pawl,
when neither check evaluates those things (review M-18).

A successful build is not a result. Stop only when the objective validators pass, or when a
remaining blocker is backed by measured evidence.
