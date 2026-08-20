# DESIGN REVIEW — Aero-Throttle (Prototype 01), Phase 3

**Reviewer:** Design Architect / Geometry Reviewer (Claude Opus)
**Date:** 2026-08-20
**Scope:** Independent engineering review of the Phase 2 implementation (`geometry_engine/aero_throttle/`, `scripts/`, `tests/`, `output/`) against `PROJECT.md`, `DESIGN_SPEC.md`, `PARAMETERS.md`, `design/ALGORITHM.md`, and the approved decisions in `iterations/PHASE_2_JOURNEY.md`.
**Boundary observed:** no implementation code was modified. This document is the sole deliverable.

---

## 0. Executive Summary

**DESIGN REVIEW: FAIL.**

The Phase 2 build is solid on the axes it measured: all ten solids export watertight, single-body and positive-volume in both STL and STEP; the assembled bounding box measures **86.000 × 72.000 × 26.500 mm — exactly on target (V-110 PASS)**; nothing protrudes past `±chassis_width/2` (V-112 PASS); and tessellation holds chordal deviation to ≤ 0.0029 mm against the 0.010 mm target.

Almost everything the Phase 2 gates *did not* measure has failed.

Independent measurement in the assembled rest pose and across the declared motion envelopes found **nine part-pair interferences totalling 663 mm³**, of which the Phase 2 check scripts detected **none**. Five of the six compliant mechanisms cannot execute their specified motion: the trigger jams against its own grip shell 21.9 mm³ deep before stage 1 completes; the hat switch bottoms after 0.40 mm of its required 1.694 mm tip travel; the missile guard drives 20.7 mm³ into the bezel at 90°; the trim ratchet is kinematically locked (an axially-deflecting pawl against radially-escaping teeth); and the fire-button spring runs at **56.6 MPa against a 22.0 MPa allowable** — it yields on the first press. The front bezel cannot be assembled onto the chassis at all (450.9 mm³ of solid-on-solid interference), because the chassis snout was never necked down to its collar.

Underneath the geometry failures sit three systemic causes that must be fixed before any part is re-cut:

1. **No fillets and no bed chamfers exist anywhere in the model.** `internal_fillet_radius` is never used as a radius and `.fillet()` is never called. Every flexure root, in a design that deliberately sits *exactly on* its stress allowable (§6.2 energy bound), is a sharp square corner. P-8, P-9, V-154, V-155, F-01, F-07 and F-12 are all unmitigated.
2. **The validation suite is inert.** `output/reports/validation-report.json` reports `status: INCOMPLETE`, `tests_run: 11, passed: 0, skipped: 11`. `check_kinematics.py`, `check_clearances.py`, `check_flexures.py` and `check_printability.py` — the four scripts that own V-120 … V-158 — do not exist. `validation_config.json` is still the all-null template and still points at `output/stl/model.stl`, which is never produced. The per-part `check_phase2_*.py` gates that *were* written test rest pose only and re-evaluate the analytic formulas rather than the geometry; in the one case where they do sample motion (ATH_08) they sample 0/50/100 % instead of the V-123-specified 0 / 23.8 / 28.0 mm, missing the only station where the detent acts.
3. **The released documents no longer describe the released geometry.** Four flexures were re-solved for PETG by changing *thickness* — the stress knob that `ALGORITHM.md` §10.1 explicitly forbids retuning without going back through `DESIGN_SPEC.md` §7 — and neither `DESIGN_SPEC.md` nor `PARAMETERS.md` was updated. 56 parameters exist in `parameters.py` that are absent from the §1–11 registry; 14 registry parameters (including `overhang_max_deg`, `bridge_max`, `flexure_min`, `fn_curve`, `deboss_depth`) are absent from the implementation; and several §12 derived values are typed in as literals.

Eleven defects are rooted in the normative documents themselves and cannot be fixed by the implementation agent alone. They are listed in §5 and are my responsibility to correct before Phase 4 begins.

**Recommended next step: Phase 4 Corrections**, executed in the sequence given in §7.

---

## 1. Evidence Base

Every numeric claim below was produced by re-running the implementation in the project's own `.venv-cad` (CadQuery 2.8.0 / OCCT, trimesh 5.0.0) and measuring — not by reading the existing reports.

| Measurement | Method | Result |
| :-- | :-- | :-- |
| Mesh integrity, 10 parts + assembly | `trimesh`, `process=True` | all watertight, 1 body, volume > 0, 0 degenerate facets |
| Assembly bounding box | OCCT union of all ten solids | 86.000 × 72.000 × 26.500 mm |
| Rest-pose interference | OCCT `intersect()`, all 55 part pairs | 9 non-zero pairs, 663.0 mm³ total |
| Motion-envelope interference | OCCT, poses per §12.3 | throttle 0/14/23.8/28 mm; trigger 0/9.594/15.0/15.6°; guard 0/45/90/100°; button 0/3.5 mm; hat ±14° in X and Z |
| Minimum running clearance | `BRepExtrema_DistShapeShape` | 8 mating pairs |
| Overhang audit | facet normals in the §10.4 build orientations | 10 parts |
| Chordal deviation | vertex angular pitch on r = 11.0 and r = 9.25 arcs | 0.0023 / 0.0029 mm |
| Serpentine developed length | OCCT wire length on the as-built path | 64.557 mm total, 7.542 mm per active leg |
| Registry coverage | field/property diff vs `PARAMETERS.md` §1–11 | 14 missing, 56 undeclared |

### 1.1 Measured rest-pose interference (mm³)

| Pair | Volume | Region (design CS) |
| :-- | --: | :-- |
| ATH_01 ∩ ATH_03 | **450.86** | X[72.0, 82.0] Y[10.0, 34.0] Z[±11.0] |
| ATH_02 ∩ ATH_07 | **96.10** | X[54.4, 67.6] Y[−2.2, 0.0] Z[5.85, 12.65] |
| ATH_01 ∩ ATH_04 | **37.77** | X[79.78, 82.0] Y[13.1, 32.7] Z[±10.47] |
| ATH_09 ∩ ATH_10_B | **31.15** | X[56.0, 60.3] Y[−4.0, 0.0] Z[±2.3] |
| ATH_04 ∩ ATH_05 | **7.21** | hood inner ceiling vs button head |
| ATH_01 ∩ ATH_10_A / _B | 4.20 / 4.20 | seam tongue rib at Y[0, 0.8] |
| ATH_02 ∩ ATH_10_B / _A | 4.16 / 1.46 | waist rib vs the 4.20 socket |

### 1.2 Measured motion-envelope interference (mm³)

| Mechanism | Pose | Interference | Verdict |
| :-- | :-- | --: | :-- |
| ATH_08 throttle | 14.0 mm / 28.0 mm | 0.00 / 0.00 | free |
| ATH_08 throttle | 23.8 mm (afterburner) | 3.39 (intended detent) | force target missed — M-03 |
| ATH_09 trigger | 9.594° / 15.0° / 15.6° | **21.85 / 42.67 / 44.42** | jams |
| ATH_04 guard | 45° / 90° / 100° | **10.03 / 20.71 / 25.74** | cannot open |
| ATH_05 button | 3.50 mm | 0.00 | free |
| ATH_06 hat | ±14° X, ±14° Z | **34.24 / 45.99 / 37.16 / 40.07** | cannot deflect |

### 1.3 Measured minimum clearances at rest (mm)

| Pair | Measured | Required (§9) | Verdict |
| :-- | --: | :-- | :-- |
| ATH_01 – ATH_08 | 0.1005 | FC-SLIDE 0.20/side (I-01) | FAIL |
| ATH_01 – ATH_07 | 0.0100 | 0.60/side (I-07) | FAIL |
| ATH_02 – ATH_09 | 0.0427 | FC-PIVOT 0.10/side (I-13) | FAIL |
| ATH_03 – ATH_05 | 0.1000 | FC-SLIDE 0.20/side (I-17) | FAIL |

### 1.4 Measured overhang in the §10.4 declared build orientations

| Part | Area > 45° from vertical | % of surface | Worst facet |
| :-- | --: | --: | --: |
| ATH_01 | 2327.9 mm² | 11.62 % | 90.0° |
| ATH_02 | 284.6 mm² | 3.67 % | 90.0° |
| ATH_03 | 151.9 mm² | 5.92 % | 90.0° |
| ATH_04 | 131.8 mm² | 11.48 % | 90.0° |
| ATH_05 | 389.4 mm² | **28.06 %** | 90.0° |
| ATH_06 | 348.9 mm² | 21.59 % | 90.0° |
| ATH_07 | 56.4 mm² | 2.79 % | 90.0° |
| ATH_08 | 132.0 mm² | 11.07 % | 90.0° |
| ATH_09 | 135.7 mm² | 11.02 % | 90.0° |
| ATH_10 | 5.2 mm² | 2.99 % | 90.0° |

### 1.5 What passes

For the record, these criteria were independently verified and **pass**:

* V-100 / V-101 / V-103 — ten watertight, single-body, positive-volume solids.
* V-110 — assembly bbox 86.000 × 72.000 × 26.500 mm, error < 0.001 mm against a ±0.30 mm band.
* V-111 — the X, Y and Z chains close exactly (ASSERT-01, -02 evaluate to 86.000 / 72.000).
* V-112 — max |Z| over all parts = 13.250 mm.
* V-104 (chordal part) — 0.0023 mm at r = 11.0, 0.0029 mm at r = 9.25 against a 0.010 mm limit.
* ASSERT-04, -05, -12, -20, -21, -22, -23 — flank packaging, ratchet web, guide ratio, rim protrusion, follower travel and folded-leaf envelope all hold at the defaults.
* `.gitattributes` routes `*.stl`, `*.3mf`, `*.step` to Git LFS, and it landed before any binary was committed (`ALGORITHM.md` §10.3 item 4).

---

## 2. BLOCKER Issues

### ISSUE B-01: Chassis snout is never necked to the collar; the bezel cannot be assembled
- **Component(s) / File(s):** `geometry_engine/aero_throttle/components_phase1.py:213-222` (`ath_01_upper_chassis`, collar block); `components_phase2.py:74-90` (`ath_03_front_bezel_faceplate`)
- **Severity:** BLOCKER
- **Description:** ATH_03 and ATH_01 overlap by **450.86 mm³** over X[72.0, 82.0], Y[10.0, 34.0], Z[±11.0]. The bezel's 22.0 × 24.0 outer shell has an 18.20 × 20.20 rear cavity, so its rear 10 mm is a closed ring of wall 1.90 mm thick. That ring is driven straight into the chassis, which is still full section (26.5 mm wide, Y 12…33 solid) right up to X = 82.0. Two further lumps of 7.84 mm³ each are the bezel barbs colliding with chassis material at X[76.05, 79.55] because ATH_01 has no latch pockets (see M-02), and 12.96 mm³ is the cam-leaf anchor at X[72.0, 73.2].
- **Root Cause:** `DESIGN_SPEC.md` §8.1 feature 4 calls the collar a "male boss" occupying X[72.0, 82.0] but never states the complementary requirement — that the surrounding chassis nose must be *removed* over the same X band so the boss stands alone. The implementation read the feature literally and added `collar = box(collar_depth, collar_h, collar_w)` at X[72, 82], which lands entirely inside the existing chassis solid and is therefore a no-op union.
- **Required Change:** Over X ∈ [`bezel_rear_x`, `chassis_front_x`], subtract everything outside the collar section from ATH_01 — cut the chassis profile down to `collar_w` (Z) × `collar_h` (Y) centred on (`bezel_center_y`, 0), leaving a `collar_depth` = 10.00 mm boss. Retain the collar's internal cavity chain (`collar_cavity_y/z`, `snout_spring_cavity_y/z`) unchanged. Add a 45° lead-in on the boss's leading edges.
- **Constraints That Must Not Change:** `chassis_front_x` = 82.00 (datum D); `bezel_rear_x` = 72.00; `bezel_cavity_w/h` = collar + 2·FC-STATIC; the X chain closing on 86.000 (ASSERT-01).
- **Acceptance Test:** `ATH_01.intersect(ATH_03).Volume() == 0`, and `BRepExtrema` min distance between the collar faces and the bezel cavity faces = 0.100 ± 0.03 mm on all four faces (I-08).

### ISSUE B-02: The missile guard cannot rotate to its open detent
- **Component(s) / File(s):** `components_phase2.py:373-418` (`ath_04_missile_safety_guard`, hood and `stop`); `parameters.py:562-566` (`guard_hinge_y`)
- **Severity:** BLOCKER
- **Description:** Rotating ATH_04 about the hinge datum (83.0, 32.0) drives the hood into the bezel body: **10.03 mm³ at 45°, 20.71 mm³ at 90°, 25.74 mm³ at 100°**, over X[81.4, 84.0], Y[32.0, 34.0], Z[±7.39]. Separately, the over-travel `stop` block sits at X[84.0, 85.6], Y[32.0, 33.6] — its rear face is *coincident with the bezel front face at 0°*, so the feature §8.4 feature 4 specifies as a 100° hard stop is already in contact at the closed rest position (measured ATH_03–ATH_04 minimum distance = 0.0000 mm).
- **Root Cause:** `guard_hinge_y` = `bezel_center_y + bezel_h/2 − 2.00` = 32.00 leaves only 2.00 mm of bezel above the hinge axis, while the hood is 4.50 mm thick and sweeps through that band. The hinge station was set by an inherited offset rather than solved from the hood's swept envelope, and no swept-envelope check exists anywhere in the pipeline.
- **Required Change:** Solve the hinge station from the sweep. Either raise the hinge above the bezel's top face by at least `guard_hood_h` and extend the stanchions accordingly, or relieve the bezel's upper-front corner over the swept arc for theta in [0°, `guard_overtravel_deg`]. Re-place the over-travel stop so first contact occurs at exactly `guard_overtravel_deg` = 100°.
- **Constraints That Must Not Change:** `guard_closed_x` = 86.00 (X chain); the D2.35/D2.55 FC-PIVOT hinge pair (I-15); both cam flats undeflected at 0° and 90° (R-M2).
- **Acceptance Test:** `check_kinematics.py` V-126 sweeps 0/45/90/100° with `intersection_volume == 0` at 0/45/90, and first contact detected at 100.0 ± 0.2°.

### ISSUE B-03: The closed guard interferes with the fire-button head
- **Component(s) / File(s):** `parameters.py:215` (`fire_btn_proud`), `parameters.py:571` (`guard_inner_clear`), `parameters.py:707` (ASSERT-07)
- **Severity:** BLOCKER
- **Description:** ATH_04 ∩ ATH_05 = **7.21 mm³** at rest. The hood's inner ceiling sits at X = `guard_hood_min_x` + (`guard_hood_h` − `guard_wall`) = 81.50 + 2.90 = **84.40**, while the button head's front face is at `btn_head_front_x` = **84.50** — a 0.10 mm hard interference with no margin at all against the 0.40 mm printable gap. The guard cannot close; if forced, it holds the button spring permanently pre-compressed, violating R-M2.
- **Root Cause:** `PARAMETERS.md` §6 declares the constraint `fire_btn_proud < guard_hood_h − guard_wall` = 2.90 and then sets `fire_btn_proud` = 3.00 — the default violates its own declared bound. The implementation reproduced both faithfully. ASSERT-07 was then re-expressed in `parameters.py` as `guard_hood_h − guard_wall − gap_print_min >= 0`, which is satisfied by any hood thicker than its wall and no longer guards the condition it was written for.
- **Required Change:** Set `fire_btn_proud` = 2.50 and derive it as `guard_hood_h − guard_wall − gap_print_min` rather than typing it. Restore ASSERT-07 to a form that guards the real condition: `fire_btn_proud + gap_print_min <= guard_hood_h - guard_wall`.
- **Constraints That Must Not Change:** `guard_hood_h` = 4.50 and `guard_recess_depth` = 2.50 (both are X-chain terms; changing either breaks ASSERT-01); `fire_btn_travel` = 3.50.
- **Acceptance Test:** `ATH_04.intersect(ATH_05).Volume() == 0` at 0° with minimum distance ≥ 0.40 mm; the restored ASSERT-07 passes; ASSERT-01 still evaluates to 86.000.

### ISSUE B-04: The trim-wheel relief pocket in ATH_02 is cut at the wrong Z station
- **Component(s) / File(s):** `components_phase1.py:288-289` (`ath_02_lower_grip_shell`, `relief`)
- **Severity:** BLOCKER
- **Description:** ATH_02 ∩ ATH_07 = **96.10 mm³** over X[54.4, 67.6], Y[−2.2, 0.0], Z[5.85, 12.65]. The relief pocket is built centred on **Z = 0**, the lateral symmetry plane. The wheel it is meant to clear lives at Z[5.85, 12.65]. The pocket therefore misses the wheel entirely and the 2.20 mm of exposed rim ploughs into the solid grip tray.
- **Root Cause:** The pocket's Z centre was defaulted to 0 instead of `trim_wheel_mid_z` = 9.25, and its X and Z sizes were re-derived locally instead of taken from the §12.8 chain. No check script compares ATH_02 against ATH_07; the pair is untested.
- **Required Change:** Centre the relief on (`trim_wheel_center_x`, 0, `trim_wheel_mid_z`) and size it from §12.8: `grip_relief_len` = 17.00 (X), `grip_relief_w` = 9.00 (Z), `grip_relief_depth` = 3.00 (Y).
- **Constraints That Must Not Change:** `trim_wheel_center_y` = 8.80 derived from `trim_rim_proud` (ASSERT-20); ATH_02 must remain a single connected solid.
- **Acceptance Test:** `ATH_02.intersect(ATH_07).Volume() == 0`; minimum distance ATH_02–ATH_07 ≥ 0.50 mm all round (I-20).

### ISSUE B-05: The trim ratchet is kinematically locked and cannot click in either direction
- **Component(s) / File(s):** `components_phase1.py:112-140` (`_trim_post_and_pawl_carrier`, `pawl_leaf` and `pawl_nose`); `components_phase2.py:597-620` (`_ratchet_tooth_cuts`)
- **Severity:** BLOCKER
- **Description:** The ratchet teeth are Z-prismatic triangular pockets: every tooth flank is a surface parallel to the wheel axis, so its normal lies entirely in the XY plane and can only push the pawl **radially**. The implemented pawl is a vertical cantilever 3.60 (X) × 17.70 (Y) × 1.05 (Z) whose only compliant direction is **Z (axial)**; radially it presents its 3.60 mm dimension and is roughly 40× stiffer. A D0.80 × 0.40 nose sitting in a 9°-wide valley at r = 7.00 therefore has no escape path — rotation drives it into a wall it cannot ride over. The mechanism jams, or shears the nose off.
- **Root Cause:** `ALGORITHM.md` §6.1 step 8 specifies the pawl as `folded_leaf(...)` anchored on the pocket's forward wall, tip engaging the ring at r = `ratchet_pitch_r` with `pawl_preload` of **radial** interference. The Phase 2 ATH_07 integration redesign replaced this with an under-wheel vertical cantilever and an axial nose, and re-purposed `pawl_preload` = 0.40 mm as the *height* of the nose rather than as radial interference. The analytic chain in `parameters.py` (`pawl_deflect` = 1.50 mm, k = 0.620 N/mm, torque = 12.09 N·mm, sigma = 24.88 MPa) still describes the original radial pawl and bears no relationship to the solid that is built.
- **Required Change:** Restore a radially-compliant pawl: anchored on the pocket's forward wall, bending in the design XY plane, developed length `pawl_len` = 17.70 mm, section `pawl_width` × `pawl_thickness` = 3.60 × 1.05 mm, tip nose reaching r = `ratchet_pitch_r` with `pawl_preload` = 0.40 mm of **radial** interference against `ratchet_tip_r`. Where the straight beam does not fit the pocket, fold it with `folded_leaf(L_dev, b, t, r_fold, n_arms)` — do not shorten it, because `pawl_len` is solved from the stress limit, not chosen.
- **Constraints That Must Not Change:** 20 teeth, `ratchet_tooth_depth` = 1.10, the derived 89.97° included angle, `ratchet_web` = 3.70 ≥ `feature_min` (ASSERT-05), `ratchet_pitch_r` = 7.00, and ATH_07's ring geometry.
- **Acceptance Test:** A new V-127 in `check_kinematics.py` rotates ATH_07 through one tooth pitch (18°) in 20 steps and asserts the pawl's required radial displacement never exceeds `ratchet_tooth_depth`; `check_flexures.py` re-derives k, F and sigma from the built beam's actual bending axis and reports torque = 12.0 ± 0.6 N·mm.

### ISSUE B-06: The trim snap post has no relief slots, so ATH_07 cannot be installed
- **Component(s) / File(s):** `components_phase1.py:141-152` (`_trim_post_and_pawl_carrier`, `post` and `head`); `parameters.py:98-99` (`trim_snap_slot_w`, `trim_snap_slot_len` — declared, never used in geometry)
- **Severity:** BLOCKER
- **Description:** The mushroom head is D6.20; the wheel bore is D5.50 nominal (D5.60 as cut, with `hole_comp`). Assembly step 1 requires the head to compress **0.30 mm per side** to pass the bore. The post is a solid D5.00 cylinder — the four `trim_snap_slot_w` = 0.80 mm relief slots that make that compression possible (§8.1 feature 13) are never cut. The `pawl_snap_strain` = 1.39 % assertion computes the strain of a finger that does not exist.
- **Root Cause:** `trim_snap_slot_w` and `trim_snap_slot_len` are referenced only inside the strain formula, never by any geometry call.
- **Required Change:** Cut four radial slots of width `trim_snap_slot_w` = 0.80 mm and length `trim_snap_slot_len` = 7.00 mm through post and head at 90° spacing, plus the 30° lead-in chamfer on the head. Generate head and bore from a single `snap_pair("mushroom")` module so the D6.20 / D5.50 relationship cannot drift.
- **Constraints That Must Not Change:** `trim_post_d` = 5.00; `trim_bore_d` = `trim_post_d` + 2·FC-ROTARY; `trim_snap_head_d` = 6.20; the 1.39 % assembly strain (ASSERT-36).
- **Acceptance Test:** The four slots measure 0.80 ± 0.02 mm; the post's minimum ligament at the slot root ≥ `feature_min`; `check_flexures.py` V-142 evaluates finger strain from the *built* slot length.

### ISSUE B-07: The trigger jams against ATH_02 before stage 1 completes
- **Component(s) / File(s):** `components_phase1.py:300-330` (`ath_02_lower_grip_shell`, `stop_bar` and `shelf`); `components_phase2.py:846-870` (`ath_09_dual_trigger`)
- **Severity:** BLOCKER
- **Description:** Rotating ATH_09 about datum J produces **21.85 mm³ of interference at 9.594°** (the end of stage-1 travel), **42.67 mm³ at 15.0°** and **44.42 mm³ at 15.6°**, in two distinct collisions:
  - X[54.7, 57.3] Y[−16.25, −14.45] Z[±3.0] — the stage-2 tooth passes *through* the stop bar instead of deflecting 0.55 mm and riding over it. At 15° essentially the whole 1.80 × 1.80 × 7.22 mm stop bar lies inside the tooth.
  - X[52.4, 55.6] Y[−22.36, −20.56] Z[±2.0] — the shoe is already 9.15 mm³ inside the over-travel shelf at 9.594°, so the shelf that should first be touched at 15.6° blocks the trigger from the start of its stroke.
- **Root Cause:** `stop_center_x/y` and `shelf_center_x/y` are placed by ad-hoc scalar multiples of `trigger_tooth_r` and `trigger_contact_r` (× 0.25, × 1.20, × 0.20, × 0.97) rather than solved from the tooth's and shoe's swept arcs. `check_phase2_ath09.py` tests the rest pose only; its `motion_samples_deg` field is written into the report without ever being evaluated.
- **Required Change:** Solve both features from the kinematics. The stop bar's gate face must lie on the tooth-tip arc of radius `trigger_tooth_r` = 9.455 mm about J, positioned so first contact occurs at `trigger_stage1_deg` = 9.594° and the interference measured normal to the 45° gate flank is exactly `trigger_stage2_deflect` = 0.55 mm. The over-travel shelf must lie on the shoe's arc of radius `trigger_contact_r` = 18.00 mm with first contact at `trigger_travel_deg + trigger_overtravel_deg` = 15.6°.
- **Constraints That Must Not Change:** datum J at (58.0, −4.0); `trigger_tooth_r` remaining solved from the 5.20 N break target; the FC-PIVOT D3.80/D4.00 pair; ATH_02 remaining one connected solid.
- **Acceptance Test:** `check_kinematics.py` V-124 sweeps 0 / 9.594 / 15.0 / 15.6°; interference is zero everywhere except at the gate, where penetration normal to the flank = 0.55 ± 0.03 mm; first shelf contact detected at 15.6 ± 0.1°.

### ISSUE B-08: The trigger cradle has no open-mouth snap entry, so ATH_09 cannot be installed
- **Component(s) / File(s):** `components_phase1.py:283-295`; `parameters.py:147` (`trigger_cradle_mouth_w`, declared but never used)
- **Severity:** BLOCKER
- **Description:** The cradle sockets are blind D4.00 bores in two solid 7.50 × 5.60 × 3.80 mm walls. Assembly step 7 requires the D3.80 trunnion to enter laterally through a 3.40 mm mouth that spreads each wall by 0.20 mm (§7.7, 1.07 % strain). The mouth does not exist, so the trunnion has no insertion path and the joint is unassemblable.
- **Root Cause:** `trigger_cradle_mouth_w` is defined in `parameters.py` and referenced by nothing.
- **Required Change:** Generate the cradle from a `trunnion_pair("socket")` module that emits the D4.00 bore *and* a `trigger_cradle_mouth_w` = 3.40 mm slot opening in the insertion direction, with a 30° lead-in, over the full `trigger_cradle_wall_len` = 7.50 mm spring-wall length.
- **Constraints That Must Not Change:** FC-PIVOT 0.10/side; `trigger_trunnion_len` = 7.60 mm; the 1.07 % cradle strain (§7.7).
- **Acceptance Test:** The mouth measures 3.40 ± 0.02 mm; `check_flexures.py` V-142 computes cradle-wall strain from the built wall and reports ≤ `strain_assembly_max`.

### ISSUE B-09: The hat switch bottoms after 0.40 mm of a required 1.694 mm tip travel
- **Component(s) / File(s):** `components_phase1.py:24-79` (`_hat_cradle`); `components_phase2.py:562-583` (`ath_06_4way_hat_switch`)
- **Severity:** BLOCKER
- **Description:** Tilting ATH_06 by ±14° produces **34.24 / 45.99 / 37.16 / 40.07 mm³** of interference with ATH_01 in the four cardinal directions. Three independent causes:
  - The chassis "detent pockets" are built as **raised pads** — `pad` cylinders unioned onto the support annulus at `support_top_y + gap_print_min/2` — not as pockets. The annulus top sits `gap_print_min` = 0.40 mm below the arm plane, so each arm has **0.40 mm of downward travel** before it lands on solid chassis. The required tip deflection is `hat_arm_r · sin(14°)` = **1.694 mm**. The hat reaches roughly 3.3° before bottoming.
  - `hat_recess_relief_deg` = 16.0° is used only inside ASSERT-09; **no conical relief is cut into the recess floor**. The cap rim descends `hat_rim_drop` = 2.117 mm at 14° onto a flat floor — precisely failure mode F-10. Measured interference lumps at Y[29.30, 30.50] confirm rim-on-floor contact.
  - `hat_detent_depth` = 0.60 and `hat_detent_flank_deg` = 40.0 are never used, so the arm-tip detent noses are buried inside the arm ribbon and there is no cardinal click at all.
- **Root Cause:** The detent interface was inverted (pad instead of pocket) when the ATH_06 support annulus was added, and the conical relief was dropped in the same change. `check_phase2_ath06.py` tests the rest pose only.
- **Required Change:** (a) Replace the four pads with four detent pockets of depth `hat_detent_depth` = 0.60 mm and flank `hat_detent_flank_deg` = 40°, centred at r = `hat_arm_r` = 7.00, 90° apart, sunk *into* the support annulus. (b) Cut the `hat_recess_relief_deg` = 16° conical relief into the recess floor from datum E. (c) Provide at least `hat_tip_deflect + hat_detent_depth + gap_print_min` = 2.69 mm of vertical free space below every arm tip over its full swept arc.
- **Constraints That Must Not Change:** datum L at (46.0, 30.5, 0); `hat_cap_od` = 17.50; the ±14° travel limit; the cap crown at Y = 42.0 (Y chain).
- **Acceptance Test:** `check_kinematics.py` V-122 sweeps 0°, ±14° in X and Z and both 45° diagonals with zero interference except the intended detent engagement of ≤ 0.60 mm; measured free travel below each arm tip ≥ 2.69 mm.

### ISSUE B-10: The fire-button serpentine runs at 56.6 MPa — 2.6× the PETG allowable
- **Component(s) / File(s):** `components_phase2.py:193-227` (`_fire_serpentine`); `parameters.py:232-234` (`serpentine_beam_w_petg`, `serpentine_beam_t_petg`, `serpentine_loop_dev_len_petg`)
- **Severity:** BLOCKER
- **Description:** The built spring is **not** the arc serpentine of D-06. Measured from the as-built wire: six straight legs of **7.542 mm** joined by five semicircular turns of radius **1.229 mm** (total centreline 64.557 mm). Under the fixed-guided model of §6.2 with the true active length L = 7.542 mm:

  `sigma = 3·E·d·w / (N·L²) = 3 · 2000 · 3.50 · 0.92 / (6 · 7.542²) =` **56.61 MPa**

  against `sigma_allow_cyclic` = 22.0 MPa, and above PETG's 50 MPa flexural strength. The spring yields on the first press. Even the most generous reading — leg plus full connecting arc, L = 11.403 mm — gives **24.76 MPa**, still over the allowable. The value `parameters.py` actually uses, `serpentine_loop_dev_len_petg = 12.10`, corresponds to **no measurable length in the model**; it is the only value that brings sigma to 21.99 MPa, i.e. 0.05 % under the 22.00 MPa assertion threshold.
- **Root Cause:** D-06 exists precisely because straight segments reach 59 MPa, and its fix was arcs of mean radius `serpentine_loop_r` = 5.00 buying `pi·R` = 15.708 mm of developed length per half-loop. The lateral re-fold adopted in Phase 2 kept the name `serpentine_loop_r` = 5.00 but used it only to set the transverse envelope, replaced the arcs with straight legs, and so reverted to exactly the topology D-06 rejected. The analytic length was then set by hand to a number that passes ASSERT-27.
- **Required Change:** Rebuild the spring so its active segments are true arcs of mean radius `serpentine_loop_r`, developed length `pi·serpentine_loop_r` per half-loop, per `ALGORITHM.md` §5.7. Delete `serpentine_loop_dev_len_petg`: the developed length must be **measured from the generated wire** (OCCT `Wire.Length()` per half-loop) and fed to the stress and stiffness formulas, so the analysis can never again describe a different spring from the one built. Re-solve `serpentine_beam_t` for the 3.20 N target after the geometry is fixed — depth is the force knob and is stress-neutral (R-M4).
- **Constraints That Must Not Change:** `fire_btn_travel` = 3.50; `serpentine_free_h` = 13.50 with the axial stack closing on `snout_cavity_rear_x` = 66.00 (ASSERT-29); the 1.00 mm solid-height reserve (ASSERT-06); the local spring bore section 11.90 × 6.20.
- **Acceptance Test:** `check_flexures.py` V-140 recomputes sigma from the measured wire length and reports ≤ 22.0 MPa with at least 5 % margin; the V-171 force band 2.70…3.70 N is still met; the measured half-loop length equals `pi·serpentine_loop_r` ± 0.05 mm.

### ISSUE B-11: The four chassis-to-grip snap hooks sit entirely above datum A and never engage
- **Component(s) / File(s):** `geometry.py:74-86` (`snap_feature`); `components_phase1.py:230-233`; `components_phase1.py:281-283`
- **Severity:** BLOCKER
- **Description:** The hook solid occupies **Y[0.00, 3.60]** — its measured volume below datum A is **0.000 mm³**. The catch pocket cut in ATH_02 occupies Y[−1.70, 1.40]. ATH_01 lives at Y ≥ 0 and ATH_02 at Y ≤ 0, so the hooks are re-added as internal ribs inside the chassis cavity and the pockets are holes in the grip tray that nothing enters. The primary retention joint of the whole assembly (§4.3 step 9, I-11) does not exist. The pocket is also offset `snap_hook_len/2` = 7.5 mm in X from the hook body (hook X[4.50, 19.50] against pocket X[17.60, 21.40]).
- **Root Cause:** `snap_feature` builds the beam with y-centre = `snap_hook_t/2`, i.e. upward from datum A, for both the hook and its pocket. The mating-pair idiom (R-G8) was implemented, but with the deflection direction pointing into the owning part rather than across the seam.
- **Required Change:** Reflect the hook about datum A so the beam hangs from ATH_01 into ATH_02's tray, with the barb protruding laterally (±Z) by `snap_barb_depth` = 1.20 mm into the catch ledge, a `snap_lead_angle_deg` = 30° lead-in and — per the approved OQ-4 decision that the seam is permanent — a `snap_return_angle_deg` = 0° return face. Derive the pocket station from the *barb's* position, not from `station_x + snap_hook_len/2`.
- **Constraints That Must Not Change:** `snap_hook_len` = 15.00 and `snap_hook_t` = 1.60 (they set the 1.44 % assembly strain, A-15 / ASSERT-15); `snap_pocket_w` = `snap_hook_w` + 2·FC-SNAP; four hooks on both flanks.
- **Acceptance Test:** ATH_01's hook volume at Y < 0 equals the full barb plus engagement length; `check_clearances.py` V-130 measures 0.15 ± 0.03 mm on the I-11 faces; a virtual assembly along −Y shows the barb clearing the ledge with `snap_undercut` = 0.80 mm of retention.

### ISSUE B-12: Alignment key station X = 58.0 collides with the trigger pivot
- **Component(s) / File(s):** `parameters.py:122` (`key_stations_x`), `parameters.py:141` (`trigger_pivot_x`); `PARAMETERS.md` §10 and §11; `DESIGN_SPEC.md` §8.2 features 5 and 11
- **Severity:** BLOCKER
- **Description:** ATH_10_B ∩ ATH_09 = **31.15 mm³** over X[56.0, 60.3], Y[−4.0, 0.0], Z[±2.3]. The second alignment key is centred at X = 58.0 spanning Y[−4.0, +4.0]; datum J — the trigger pivot axis — is the line (X = 58.0, Y = −4.0). The key passes straight through the trunnion.
- **Root Cause:** This is a **normative defect**, not an implementation error. `DESIGN_SPEC.md` §8.2 places key sockets at X = 30.0 and 58.0 (feature 11) and the trigger cradle on axis J at X = 58.0 (feature 5). The two features were written independently and never cross-checked. The implementation reproduced both correctly.
- **Required Change:** Move `key_stations_x[1]` clear of the trigger cradle envelope. The nearest station that stays inside the seam perimeter (`seam_x_max` = 70.00) while clearing both the cradle walls (X 54.25…61.75) and the trim window (X 53.0…69.0 at Z 5.85…12.65) is **X ≈ 66.0 on Z = 0**; the alternative is to return the key to X = 46.0 and re-space the hooks. Whichever is chosen, add an assertion that every key station is at least `key_socket_side/2 + trigger_cradle_wall_len/2 + wall_internal` from `trigger_pivot_x`.
- **Constraints That Must Not Change:** two keys straddling datum A; FC-STATIC 0.10/side; the keys must still react the Z shear couple of §8.10 (F-14, V-113), so they must remain well separated in X.
- **Acceptance Test:** `ATH_09.intersect(ATH_10_B).Volume() == 0`; the new key-to-pivot separation assertion passes; V-113 shear sizing is recomputed at the new stations.

### ISSUE B-13: Key sockets are absent from ATH_01, and the waist rib cannot enter either socket
- **Component(s) / File(s):** `geometry.py:64-72` (`key_feature`); `components_phase1.py:228-229`; `components_phase1.py:277-278`; `components_phase1.py:236-239` (`ath_10_alignment_key`)
- **Severity:** BLOCKER
- **Description:** The socket cutter occupies **Y[−4.10, 0.00]**. It is applied to both shells, but ATH_01 lives at Y ≥ 0, so it removes nothing: a probe of the volume where ATH_01's socket should be finds only 3.84 mm³ of the spurious seam rib (M-01), not a socket. The key's upper 4.00 mm therefore has no locating feature at all and F-14's shear path is broken. Separately, the key's waist rib measures `key_side + 2·key_waist_proud` = **4.60 mm** across while `key_socket_side` = **4.20 mm**, an 0.20 mm/side interference measured as 1.46 and 4.16 mm³ against ATH_02.
- **Root Cause:** One socket generator is used for both halves without reflecting it about datum A for the upper part. The waist rib was implemented exactly as `DESIGN_SPEC.md` §8.10 feature 3 describes it (0.30 proud, at mid-length), but a rib proud of the key body at mid-length cannot enter a socket unless a seam-plane relief exists, and §8.10 specifies none.
- **Required Change:** Emit `key_pair("socket")` twice with opposite Y sense — Y ∈ [0, `key_socket_depth`] for ATH_01 and Y ∈ [−`key_socket_depth`, 0] for ATH_02. Either delete the waist rib or add a matching `key_waist_width` + 2·FC-STATIC relief groove at the socket mouths in both shells. My recommendation is to delete it: it serves only as an assembly aid and costs a seam-plane feature in both shells.
- **Constraints That Must Not Change:** `key_socket_side` = `key_side` + 2·FC-STATIC; `key_socket_depth` = `key_len`/2 + FC-STATIC; the key straddling datum A 4.00 mm into each half.
- **Acceptance Test:** `ATH_01.intersect(ATH_10_*).Volume() == 0` and `ATH_02.intersect(ATH_10_*).Volume() == 0`; measured socket clearance 0.100 ± 0.03 mm on all four faces of both halves (I-12).

### ISSUE B-14: No stress-relief fillets exist anywhere in the model
- **Component(s) / File(s):** all of `geometry_engine/aero_throttle/`; `parameters.py:26` (`internal_fillet_radius`)
- **Severity:** BLOCKER
- **Description:** `.fillet()` is called **zero** times in the entire geometry engine. `internal_fillet_radius` = 0.60 appears three times: once as its own default, and twice inside `_cam_leaf` where it is used as a *length* (`2 * p.internal_fillet_radius` as an anchor width), never as a radius. Every flexure root in the design — throttle detent leaf, trim pawl, hat spiral arms, serpentine anchor, trigger stage-1 leaf and stage-2 tooth, bezel cam leaf, and all snap beams — is a sharp square inside corner. Because §6.2 sizes every one of these beams to sit **exactly on** `sigma_allow_cyclic` (the energy bound makes any stress margin wasted force capacity), a root stress-concentration factor of 2 to 3 puts every mechanism straight into first-cycle yield. P-8, V-154, F-01 and F-07 are all unmitigated.
- **Root Cause:** `ALGORITHM.md` §1.3 mandates profile-level filleting via `fillet_polygon(points, r_map)` before extrusion — rule R-G1, which is what makes the model manifold by construction. `fillet_polygon` was never implemented; part modules extrude raw polylines and union raw boxes.
- **Required Change:** Implement `fillet_polygon` per §1.3 including ASSERT-G1 (setback < half the shorter adjacent edge), and route every structural and spring profile through it with `r = internal_fillet_radius` at each concave vertex before extrusion. Where a root is formed by a boolean union of two boxes rather than by a profile, replace the union with a single filleted profile — do not post-fillet a finished solid.
- **Constraints That Must Not Change:** the developed length of every flexure (each is stress-solved); the watertight, single-body status of all ten exports.
- **Acceptance Test:** `check_printability.py` V-154 scans for internal corners sharper than R0.60 at any structural or spring root and reports zero; all ten meshes remain watertight and single-body.

### ISSUE B-15: All ten parts violate the 45° overhang rule in their declared build orientation
- **Component(s) / File(s):** all parts; `DESIGN_SPEC.md` §10.4; no `to_print_cs` implementation exists
- **Severity:** BLOCKER
- **Description:** Measured in the build orientations declared by §10.4, every part carries downward-facing geometry beyond 45° from vertical, with **90° (fully horizontal, unsupported) facets present in all ten** — see §1.4. ATH_05 is the worst at **28.06 %** of surface area: its spring legs run horizontally in the print frame, each supported at one end by the arc from the previous leg and free at the other, so they are cantilevered into air rather than bridged. `PROJECT.md`'s headline requirement is 100 % support-free printing and S-6 requires *zero* geometry exceeding the rule.
- **Root Cause:** No overhang constraint was applied during generation; `overhang_max_deg` and `bridge_max` do not exist in `parameters.py` at all; and `to_print_cs` / `print_orient` are unimplemented, so nothing in the pipeline has ever examined a part in its build frame.
- **Required Change:** (1) Implement the `print_orient` record and the `to_print_cs()` transform of §10.4 and §4.2, and apply it on export. (2) Add `overhang_max_deg` and `bridge_max` to the implementation registry. (3) Write `check_printability.py` V-150 and V-157 and iterate the geometry until zero facets exceed 45° with the build-plate face excluded: teardrop or chamfer-bridge every horizontal hole, add self-supporting 45° lead-ins under every horizontal ledge, and re-orient or re-shape the ATH_05 spring so each segment is either vertical or bridged over at most 12.0 mm.
- **Constraints That Must Not Change:** R-P1 — every flexure must still bend within the print XY plane (V-158). Note that for ATH_05 and ATH_08 these two requirements cannot both be met under the *currently declared* build faces; see S-05.
- **Acceptance Test:** `check_printability.py` V-150 reports zero violating facets per part; V-157 reports no unsupported bridge greater than 12.0 mm; V-158 confirms each flexure's bending plane.

### ISSUE B-16: The validation suite is inert — no normative test has ever executed
- **Component(s) / File(s):** `validation_config.json`; `tests/*.py`; `output/reports/validation-report.json`; the missing `scripts/check_kinematics.py`, `check_clearances.py`, `check_flexures.py`, `check_printability.py`
- **Severity:** BLOCKER
- **Description:** The current report reads `"status": "INCOMPLETE", "tests_run": 11, "passed": 0, "skipped": 11`. Every test skips: five because `mesh_path` points at `output/stl/model.stl`, which the CadQuery pipeline never produces; the rest because `expected_bounds_mm`, `expected_minimum_mm`, `min/max_volume_mm3`, `parametric_sweeps` and all three `project_checks` are still null or empty. `tests/test_printability.py` and `tests/test_geometry.py` are one-line docstring stubs. The four check scripts that own V-120 … V-158 do not exist. Consequently V-102, V-104, V-110 … V-113, V-120 … V-131, V-140 … V-143 and V-150 … V-162 have **never been evaluated**, and `RELEASE_CHECKLIST.md` cannot be satisfied.
- **Root Cause:** Phase 3 (exports, preview bridge, objective validators) is recorded as *Pending* in `PHASE_2_JOURNEY.md`. The interim per-part `check_phase2_*.py` scripts were then treated as the evidence base for gate decisions.
- **Required Change:** Populate `validation_config.json` exactly as `ALGORITHM.md` §9 prescribes (`expected_bounds_mm: [86.0, 72.0, 26.5]`, `bounds_tolerance_mm: 0.30`, all three `project_checks` with `required: true`), export the master assembly to the configured `mesh_path`, implement the four check scripts against `output/reports/parameters.json`, and implement `tests/test_printability.py`. Per `AGENTS.md`, no threshold may be relaxed to make a build pass.
- **Constraints That Must Not Change:** every numeric criterion in `DESIGN_SPEC.md` §12.
- **Acceptance Test:** `python scripts/validate.py` reports `status: PASS` with `skipped: 0`.

### ISSUE B-17: The documented build pipeline is disconnected from the implementation
- **Component(s) / File(s):** `cad_config.json`; `scripts/build.py`; `src/parameters.scad`, `src/geometry.scad`, `src/main.scad`
- **Severity:** BLOCKER
- **Description:** `WORKFLOW.md` names `python scripts/build.py` as "the evidence-producing command". It reads `cad_config.json`, which still declares `"engine": "openscad"`, `"source": "src/main.scad"` and an export target of `output/stl/model.stl`. All three `src/*.scad` files are **5-byte stubs** (BOM plus CRLF, no content) and `src/components/` does not exist. The command therefore produces nothing, while the ten real parts are built by nine separate ad-hoc `scripts/build_phase2_ath0*.py` entry points with no single driver. `build-report.json` is never produced, so `scripts/release_check.py` can never pass.
- **Root Cause:** OQ-9 moved geometry authority to CadQuery/OCCT; the configuration and the top-level driver were not migrated with it.
- **Required Change:** Repoint `cad_config.json` at the CadQuery engine; replace `scripts/build.py`'s OpenSCAD invocation with a driver that iterates the ten part ids, applies `to_print_cs`, exports STL, STEP and 3MF plus the master assembly, dumps `output/reports/parameters.json`, and writes `build-report.json`. Keep the `src/preview_phase2_*.scad` files as the preview bridge only. Delete or populate the three empty `src/*.scad` stubs so the repository no longer implies an OpenSCAD source of truth.
- **Constraints That Must Not Change:** CadQuery/OCCT remains the geometry of record (approved OQ-9); `preview_mode` must never be true for an export build.
- **Acceptance Test:** `python scripts/build.py` runs end to end and produces all ten STLs, ten STEPs, the colour-tagged 3MF, the master assembly mesh at the configured `mesh_path`, `parameters.json`, and `build-report.json` with `status: PASS`.

---

## 3. MAJOR Issues

### ISSUE M-01: The seam tongue is on the wrong side of datum A and is not a perimeter ribbon
- **Component(s) / File(s):** `geometry.py:50-62` (`seam_ribbon`); `components_phase1.py:226`; `components_phase1.py:272`
- **Severity:** MAJOR
- **Description:** The tongue solid occupies **Y[0.00, 0.80], Z[−0.60, +0.60]** — above datum A, inside ATH_01's own cavity — while ATH_02's groove is cut at **Y[−0.95, 0.00]**. They never meet, so interface I-10 does not exist. The tongue is also a single straight rib along Z = 0 for X ∈ [0, 70], not the continuous ribbon around the Y = 0 perimeter required by §8.1 feature 16. The spurious rib is what the alignment keys collide with (4.20 mm³ each). The trim-window interruption inside `seam_ribbon` is dead code: the cutter is placed at Z[5.25, 13.25] while the rib lives at Z[−0.60, 0.60], so it removes nothing.
- **Root Cause:** `y_center = depth/2` for the tongue mirrors the groove's `−depth/2` instead of matching it; and the perimeter offset logic of `ALGORITHM.md` §5.12 (offset the Y = 0 outline inward by `wall_exterior − seam_tongue_thick/2`, clip to `seam_x_max`, subtract the trim window) was replaced by a single box.
- **Required Change:** Implement `seam_pair(mode)` per §5.12: build the ribbon from the chassis outline at Y = 0 offset inward, clipped to `seam_x_max` = 70.00, with the trim window subtracted and filleted end faces on both sides of the window. Place the tongue at Y ∈ [−`seam_tongue_height`, 0] so it enters ATH_02's groove, and add the `seam_lead_in` = 0.40 mm × 45° lead-in on its free edge.
- **Constraints That Must Not Change:** `seam_groove_w` = `seam_tongue_thick` + 2·FC-SNAP; `seam_groove_d` = `seam_tongue_height` + FC-SNAP; the seam existing only where X ≤ `seam_x_max` (ASSERT-19).
- **Acceptance Test:** `check_clearances.py` V-130 measures 0.15 ± 0.03 mm on I-10 in both X and Z around the full perimeter; the tongue does not cross the trim window; ATH_01 remains watertight and single-body.

### ISSUE M-02: ATH_01 has no bezel latch pockets
- **Component(s) / File(s):** `components_phase1.py` (`ath_01_upper_chassis` — no latch-pocket cut exists); `parameters.py:185-186` (`latch_pocket_w`, `latch_pocket_h`)
- **Severity:** MAJOR
- **Description:** §8.1 feature 5 requires two 3.50 × 1.80 × 0.80 mm deep pockets on the collar's ±Y faces at X = 76.0 to receive ATH_03's permanent barbs (I-09). No such cut exists; `latch_pocket_w/h` are used only inside ATH_03's own barb undercut block. The barbs consequently have nothing to latch into and contribute 15.68 mm³ of the ATH_01/ATH_03 interference.
- **Root Cause:** The pocket half of the `snap_pair` was never emitted by ATH_01.
- **Required Change:** Cut both pockets from the same `snap_pair("pocket", lead=30, return=0)` call that generates ATH_03's barbs, at X = `collar_x0` + 4.00 on the collar's ±`collar_h`/2 faces, with FC-SNAP applied once inside the module.
- **Constraints That Must Not Change:** `bezel_barb_len` = 11.60 (it sets the 1.48 % assembly strain, D-12); `snap_undercut` = 0.80; the 0° permanent return face.
- **Acceptance Test:** V-130 measures 0.15 ± 0.03 mm on I-09; the barb's retention face overlaps the ledge by `snap_undercut` = 0.80 mm.

### ISSUE M-03: The throttle detent preload is not built, so the break force is 31 % low
- **Component(s) / File(s):** `components_phase2.py:679-717` (`_throttle_leaf`, `nose_base_z`); `parameters.py:79` (`throttle_detent_preload`)
- **Severity:** MAJOR
- **Description:** The follower nose bottom sits at `channel_floor_z + eps` = 5.86 mm with the leaf **undeflected** — measured rest clearance to the rail floor is 0.01 mm, so the built preload is **0.00 mm**, not the specified `throttle_detent_preload` = 0.45 mm (I-02 requires −0.45). Consequences: the 0.80 N glide force disappears (the carriage rattles), and at the ramp apex the leaf deflects only 1.10 mm instead of 1.55 mm, giving `F_break` = k · 1.10 · 1.0612 = **2.96 N** against a 4.30 N target — a −31 % error, well outside the ±15 % V-143 / V-170 band. The `throttle_leaf_rest_stress_mpa` = 5.35 MPa reported as evidence describes a preload the solid does not have.
- **Root Cause:** The leaf was placed at its free (undeflected) height rather than at `free_height − throttle_detent_preload`, so the rest interference against the rail floor is zero.
- **Required Change:** Lower the leaf's free tip by `throttle_detent_preload` = 0.45 mm relative to the channel floor, so that at rest the assembled leaf is pre-deflected 0.45 mm and the follower bears on the floor. Model the leaf in its *free* state in the part file and let the assembly interference represent the preload, exactly as I-02 defines it.
- **Constraints That Must Not Change:** `throttle_leaf_len` = 28.41 developed; the folded two-arm topology; `leaf_env_x` ≤ `throttle_carriage_len` (ASSERT-22); the ramp apex at rail-local 39.02.
- **Acceptance Test:** `check_clearances.py` measures −0.45 ± 0.03 mm of interference on I-02 at rest; `check_flexures.py` V-143 reports `F_break` = 4.30 ± 0.65 N and `sigma_rest` ≤ `sigma_allow_sustained`.

### ISSUE M-04: The trim pawl runs 0.010 mm from the rotating wheel face
- **Component(s) / File(s):** `parameters.py:388-390` (`pawl_leaf_top_z` = `trim_wheel_min_z − eps`)
- **Severity:** MAJOR
- **Description:** Measured minimum distance ATH_01–ATH_07 = **0.0100 mm**. I-07 specifies 0.60 mm per side between the pocket walls and the wheel faces. A 0.01 mm running clearance is below the printable-gap minimum, below every fit class, and guarantees the wheel seizes on the pawl carrier.
- **Root Cause:** The pawl leaf's top face was positioned with the boolean epsilon (`eps` = 0.01) as if it were a clearance. `eps` is an anti-coincidence allowance for boolean operations (R-G3); it is not a fit.
- **Required Change:** Position the pawl leaf so the gap to `trim_wheel_min_z` is `trim_pocket_clear_z` = 0.60 mm. Never use `eps` as a clearance term anywhere; add a static scan that flags any clearance expression containing `eps`.
- **Constraints That Must Not Change:** `trim_pocket_clear_z` = 0.60; `trim_wheel_mid_z` = 9.25; the pawl's engagement radius `ratchet_pitch_r` = 7.00.
- **Acceptance Test:** `BRepExtrema` ATH_01–ATH_07 ≥ 0.57 mm; V-131 static scan reports zero clearances not traceable to a named fit-class parameter.

### ISSUE M-05: The dovetail relief slot applies FC-STATIC to a sliding interface
- **Component(s) / File(s):** `components_phase2.py:659-666` (`_throttle_tenon` relief cut); `components_phase1.py:181-190` (`_afterburner_root`)
- **Severity:** MAJOR
- **Description:** The tenon is split by a central relief of `throttle_leaf_width + 2·fit_clearance_static` = 4.20 mm to clear ATH_01's 4.00 mm afterburner root web, giving 0.10 mm per side. That is FC-STATIC applied to a joint that slides 28 mm. Measured minimum ATH_01–ATH_08 distance is **0.1005 mm** against the FC-SLIDE 0.20 mm/side required by I-01. The relief also bisects the tenon over its full length, halving dovetail engagement, and the root web is a permanent obstruction in the middle of the slot.
- **Root Cause:** The afterburner ramp was placed on a raised central web instead of on the channel floor, forcing a full-length relief in the tenon; the relief then used the wrong fit class.
- **Required Change:** Return the ramp to the channel floor (`ALGORITHM.md` §5.5 `detent_ramp` extruded across the channel at `ramp_apex_x − ramp_run_up`) so the dovetail slot stays clear and the tenon needs no relief. If a central web is genuinely required, size its relief from `fit_clearance_sliding`, not `fit_clearance_static`.
- **Constraints That Must Not Change:** `dovetail_base_w` = 10.50, `dovetail_mouth_w` = 7.00, 45° flanks; the tenon derived once from the slot by `dovetail_pair(mode)`; `guide_ratio` ≥ 1.40.
- **Acceptance Test:** V-130 measures 0.20 ± 0.03 mm on all four I-01 flank faces at 0, 14 and 28 mm of stroke.

### ISSUE M-06: ATH_08's carriage plate leaves 0.475 mm side rails
- **Component(s) / File(s):** `components_phase2.py:730-737` (`plate` and `pocket`)
- **Severity:** MAJOR
- **Description:** The leaf pocket is `throttle_leaf_env_y_active + 2·gap_print_min` = 9.55 mm wide inside a `dovetail_base_w` = 10.50 mm plate, leaving side rails of **(10.50 − 9.55)/2 = 0.475 mm**. P-2/P-3/V-151 forbid any wall in the open interval (0, 0.80); at 0.475 mm with a 0.40 mm nozzle these rails are a single under-extruded perimeter and will collapse or delaminate (F-08).
- **Root Cause:** The PETG re-solve widened `throttle_leaf_env_y_active` to 8.75 mm without re-checking the plate's residual wall.
- **Required Change:** Either widen the plate to `throttle_leaf_env_y_active + 2·gap_print_min + 2·wall_internal` = 13.15 mm (which requires re-checking against `rail_channel_h` = 12.50 and the flank packaging map), or reduce `throttle_leaf_fold_r` / re-solve the leaf width so the envelope leaves at least `wall_internal` on each side. Add an assertion: `(dovetail_base_w − leaf_pocket_w)/2 >= wall_internal`.
- **Constraints That Must Not Change:** ASSERT-22 (`leaf_env_y` ≤ `dovetail_base_w`); ASSERT-23 (arm separation ≥ `gap_print_min`); the leaf's developed length.
- **Acceptance Test:** `check_printability.py` V-151 reports no wall in (0, 0.80) on ATH_08; the new assertion passes.

### ISSUE M-07: The trigger trunnion "chamfer" is a counterbore that leaves a 0.60 mm annular fin
- **Component(s) / File(s):** `components_phase2.py:855-868` (`end_relief`)
- **Severity:** MAJOR
- **Description:** `end_relief` subtracts a concentric D2.60 × 0.60 disc from each end of the D3.80 trunnion. That produces a 0.60 mm-deep cup at each end, bounded by a **0.60 mm-thick annular fin** — below `feature_min` = 0.80 and inside the V-151 forbidden band — instead of the 0.40 × 45° lead-in chamfer §8.9 feature 3 requires. The fin sits precisely at the bearing entry, where it is most likely to shear off during snap-in assembly.
- **Root Cause:** A chamfer was approximated by a subtractive concentric cylinder rather than by a conical cut, and `bed_chamfer` = 0.60 was used where the specified value is 0.40.
- **Required Change:** Replace the counterbore with a true 0.40 × 45° conical lead-in at each trunnion end (a `makeCone` cut, or a filleted profile revolved).
- **Constraints That Must Not Change:** `trigger_trunnion_d` = 3.80, `trigger_trunnion_len` = 7.60; FC-PIVOT 0.10/side.
- **Acceptance Test:** V-151 reports no feature below 0.80 mm on ATH_09; the trunnion end taper measures 45 ± 1° over 0.40 ± 0.02 mm.

### ISSUE M-08: The trigger cradle wall is 0.80 mm thick over the pivot bore
- **Component(s) / File(s):** `components_phase1.py:288-295` (`cradle_wall`)
- **Severity:** MAJOR
- **Description:** The wall is `trigger_trunnion_d + wall_internal` = 5.60 mm tall in Y with a D4.00 bore centred in it, leaving **0.80 mm** of material above and below the bore. `wall_internal` is 1.80 mm (P-3). This is the wall that must both carry the trigger's 5.20 N break reaction and spring open by 0.20 mm during assembly.
- **Root Cause:** The wall height was composed as `trunnion_d + wall_internal` (a single wall's worth of material shared between two sides) rather than `trigger_socket_d + 2·wall_internal`.
- **Required Change:** Size the cradle wall as `trigger_socket_d + 2·wall_internal` = 7.60 mm in Y, and re-check it against ATH_02's internal envelope and ATH_09's swept shoe.
- **Constraints That Must Not Change:** datum J; `trigger_cradle_wall_len` = 7.50 and `trigger_cradle_wall_t` = 2.00 (they set the 1.07 % assembly strain).
- **Acceptance Test:** V-151 reports ≥ 1.80 mm at every point of the cradle wall; the cradle-wall strain assertion still passes.

### ISSUE M-09: The bezel wall around the collar cavity is 1.90 mm
- **Component(s) / File(s):** `components_phase2.py:80-85`; `PARAMETERS.md` §6 (`bezel_w` 22.00, `bezel_h` 24.00 against `collar_w` 18.00, `collar_h` 20.00)
- **Severity:** MAJOR
- **Description:** `(bezel_w − bezel_cavity_w)/2 = (22.00 − 18.20)/2 =` **1.90 mm** in Z and the same in Y. `wall_exterior` is 2.40 mm (P-2, six perimeters at 0.40). The bezel is a load-bearing exterior shell that takes the guard's hinge reaction and the button's 3.20 N return, so this is a genuine structural shortfall, not a cosmetic one.
- **Root Cause:** `bezel_w`/`bezel_h` and `collar_w`/`collar_h` are independent inputs in `PARAMETERS.md` §4 and §6, with no assertion linking them.
- **Required Change:** Either raise `bezel_w`/`bezel_h` to `collar_* + 2·fit_clearance_static + 2·wall_exterior` = 23.00 / 25.00, or reduce the collar by 1.00 mm in each direction. Add an assertion `(bezel_w − bezel_cavity_w)/2 >= wall_exterior` and the same for Y.
- **Constraints That Must Not Change:** the bezel must stay inside the ±13.25 mm flank budget and inside the front-lower chamfer; `bezel_center_y` = 22.00 (D-14).
- **Acceptance Test:** V-151 reports ≥ 2.40 mm on all ATH_03 exterior walls; the new assertion passes; V-112 still holds.

### ISSUE M-10: The fire-button guide bore is only 2.00 mm long for a 10.50 mm head
- **Component(s) / File(s):** `components_phase2.py:86-99` (`guide_bore`, `shoulder_pocket`, `collar_cavity`)
- **Severity:** MAJOR
- **Description:** The 10.90 mm square guide bore is cut through the full bezel depth, but the 18.20 × 20.20 mm collar cavity then removes the bore's walls everywhere over X[72.0, 82.0]. Only the 2.00 mm band X[82.0, 84.0] actually guides the head — a length-to-width ratio of 0.19 against the 1.40 anti-binding minimum the same design applies to the throttle carriage (ASSERT-12). The button will cock and jam under any off-axis thumb load. The redundant `shoulder_pocket` cut lies entirely inside the collar cavity and does nothing.
- **Root Cause:** The collar cavity and the guide bore were authored as independent subtractions in the same X band, without checking which survives.
- **Required Change:** Restore a guiding length of at least 1.40 × `fire_btn_size` = 14.70 mm, or accept a shorter bore and add a second guide feature further back (a square guide collar inside ATH_01's snout cavity that engages the flange). Whichever is chosen, add an assertion `guide_length / fire_btn_size >= 1.40` mirroring ASSERT-12. Delete the redundant `shoulder_pocket` cut.
- **Constraints That Must Not Change:** `fire_btn_bore` = `fire_btn_size` + 2·FC-SLIDE (D-11); the flange bearing on the retaining shoulder at X = 82.0 (I-18); `fire_btn_travel` = 3.50.
- **Acceptance Test:** The new guide-ratio assertion passes; `check_kinematics.py` V-125 sweeps the button 0…3.50 mm with a 0.5° cock imposed and reports no binding contact.

### ISSUE M-11: The hat gimbal spherical socket is omitted, so the ball is unconstrained
- **Component(s) / File(s):** `components_phase1.py:74-78` (comment: "the optional spherical cup envelope above it is deliberately relieved")
- **Severity:** MAJOR
- **Description:** §8.1 feature 6 and interface I-03 require a D8.00 spherical socket at datum L to receive ATH_06's D7.50 hemisphere at FC-ROTARY. The implementation deliberately omits the cup and substitutes a flat support annulus. The gimbal therefore has no defined centre of rotation: the cap can translate as well as tilt, the ±14° limit is not geometrically enforced, and the 1.694 mm tip deflection the force model assumes is not kinematically guaranteed.
- **Root Cause:** The cup was found to occupy the same radial band as the spiral arm roots and was dropped rather than re-arranged.
- **Required Change:** Reinstate the spherical socket at datum L with `hat_cradle_d` = `hat_ball_d` + 2·FC-ROTARY = 8.00 mm, and move the arm roots radially outward (or raise the arm planes) so the two features no longer compete for the same band. If the cup genuinely cannot coexist with the arms, the gimbal must be re-architected and the change routed back through §7.4 — it cannot simply be deleted.
- **Constraints That Must Not Change:** datum L at (46.0, 30.5, 0); `hat_ball_d` = 7.50; FC-ROTARY 0.25/side.
- **Acceptance Test:** V-130 measures 0.25 ± 0.03 mm radial clearance on I-03; V-122 confirms the cap rotates about L with translation below 0.05 mm.

### ISSUE M-12: The hat force model assumes four active arms; the built topology gives at most two
- **Component(s) / File(s):** `parameters.py:307-311` (`hat_force_computed_n` = `hat_spring_arm_count` · k · delta); `components_phase2.py:577-580` (two-plane arm layout)
- **Severity:** MAJOR
- **Description:** The approved two-plane layout puts the 0°/180° arms in the lower plane and the 90°/270° arms in the upper. For a tilt about Z the 90° and 270° arms lie on the neutral axis and contribute almost nothing in bending; of the remaining pair, one is pressed into its detent and the other lifts away from the chassis, so it can only contribute through the bayonet lip. The reported 2.791 N therefore over-states the achievable self-centring force by roughly a factor of two to four, and the two planes give different lever arms about the ball centre, so the X and Z axes are not equally stiff.
- **Root Cause:** The force model was carried over unchanged from the single-plane four-arm design of §7.4 when the topology changed to two planes.
- **Required Change:** Re-derive the self-centring force for the built topology: count only the arms that bend for a given tilt axis, include each arm's actual lever arm from datum L, and state whether the lifting arm reacts through the retention lip. If the recomputed force falls outside 2.80 ± 0.42 N, retune `hat_spring_arm_width` (the stress-neutral force knob) — not the thickness.
- **Constraints That Must Not Change:** `hat_deflection_deg` = 14.0; `hat_arm_r` = 7.00; `sigma_hat` ≤ `sigma_allow_cyclic`; arm planes separated by at least `gap_print_min`.
- **Acceptance Test:** `check_flexures.py` V-143 reports the recomputed force within ±15 % of 2.80 N for tilts about both X and Z, and reports the X/Z stiffness ratio within ±10 %.

### ISSUE M-13: No build-plate chamfers exist on any part
- **Component(s) / File(s):** all parts; `parameters.py:27` (`bed_chamfer`, used only to cut the ATH_09 trunnion counterbore)
- **Severity:** MAJOR
- **Description:** P-9 and V-155 require a 0.60 × 45° chamfer on every build-plate contact edge, and it is the sole mitigation for F-12 (elephant's foot closing a running clearance). No part carries one. `bed_chamfer` appears in the geometry engine only inside `end_relief` in ATH_09, where it is misused (M-07). The seam plane, the rail, the dovetail and the trim pocket all have first-layer edges whose squish will close clearances that are only 0.10–0.25 mm wide by design.
- **Root Cause:** `chamfered_prism` (`ALGORITHM.md` §5.2) was never implemented; `bevelled_box` chamfers all twelve edges of a box uniformly and is used only for four cosmetic bodies.
- **Required Change:** Implement `chamfered_prism(profile2d, h, c_bottom, c_top)` per §5.2 and apply it with `c_bottom = bed_chamfer` to each part's declared build face, after `to_print_cs` is known (B-15).
- **Constraints That Must Not Change:** the declared build faces of §10.4; every mating dimension at full depth (the chamfer must not eat into a fit surface by more than `bed_chamfer`).
- **Acceptance Test:** `check_printability.py` V-155 confirms every build-plate contact edge carries a 0.60 ± 0.05 mm × 45° chamfer on all ten parts.

### ISSUE M-14: Print-CS transform, 3MF export, master assembly and mass check are all absent
- **Component(s) / File(s):** `scripts/build_phase*.py`; `DESIGN_SPEC.md` §10.4, §10.5; `ALGORITHM.md` §8.1, §8.4
- **Severity:** MAJOR
- **Description:** `to_print_cs` and `print_orient` do not exist, so all exports are in the design frame and V-150/V-158 cannot be evaluated. There is no `output/3mf/` directory and no colour-tagged multi-object 3MF, which the approved OQ-8 decision makes a deliverable. There is no ten-part master assembly export — `ATH_PHASE1_STRUCTURAL_ASSEMBLY` contains only ATH_01 and ATH_02. `rho_eff_g_mm3` and `mass_target_g` are absent from the implementation, so the V-176 mass check has never run.
- **Root Cause:** Phase 3 scope, still open.
- **Required Change:** Implement the §10.4 orientation table and the export pipeline of §8.1 (STL + STEP + 3MF per part, colour from §10.5, plus the master assembly), and add the §8.4 mass check with `rho_eff_g_mm3` and `mass_target_g` restored to the registry.
- **Constraints That Must Not Change:** colour is metadata only and must not change any dimension.
- **Acceptance Test:** Ten 3MFs plus one colour-tagged master 3MF exist; the master assembly mesh loads and measures 86.0 × 72.0 × 26.5 mm; V-176 reports mass within ±10 % of 58.0 g.

### ISSUE M-15: The grip body is a constant-section prism with none of its specified ergonomics
- **Component(s) / File(s):** `components_phase1.py:243-247, 291-296` (`ath_02_lower_grip_shell`)
- **Severity:** MAJOR
- **Description:** §8.2 feature 2 specifies a body swept along the rake axis `g`, morphing from 26.0 × 26.5 mm at the root to 24.0 × 25.0 mm at the butt with a palm swell peaking at 60 % of axial length. The implementation extrudes a four-point side profile a constant `palm_swell_width` = 26.10 mm in Z: no sweep, no taper, no swell. Feature 3's three R11.0 scallops are 2.20 × 1.20 mm rectangular notches (`finger_groove_r` is never used) and feature 4's ten traction ribs are absent entirely (`rib_count`, `rib_pitch`, `rib_depth` unused). The preview render confirms a flat wedge rather than a grip.
- **Root Cause:** `swept_solid` (`ALGORITHM.md` §5.3) was never implemented, so the grip fell back to a prism.
- **Required Change:** Implement `swept_solid(profile2d, path3d, twist_fn)` with a rotation-minimising frame per §5.3 and build the grip from it, including the root-to-butt section morph, the palm swell at 60 % of `grip_axial_len`, the R11.0 scallops at `finger_groove_pitch`, and the traction ribs.
- **Constraints That Must Not Change:** ASSERT-03 (`palm_swell_width` ≤ `chassis_width`); `grip_drop` = 30.00 (Y chain); `grip_rake_angle_deg` = 108.0; the butt at Y = −30.0.
- **Acceptance Test:** Measured section at 0 %, 60 % and 100 % of `grip_axial_len` matches §8.2 within ±0.20 mm; V-112 still holds; ATH_02 remains watertight and single-body.

### ISSUE M-16: The parameter registry and the implementation have diverged
- **Component(s) / File(s):** `parameters.py`; `PARAMETERS.md` §1–11 and §12
- **Severity:** MAJOR
- **Description:** A field-by-field diff finds **14 registry parameters absent from the implementation** — `bridge_max`, `deboss_depth`, `flexure_min`, `fn_curve`, `mass_target_g`, `overhang_max_deg`, `preview_mode`, `rho_eff_g_mm3`, `seam_lead_in`, `sigma_y_mpa`, `snap_hook_count`, `snap_lead_angle_deg`, `snap_return_angle_deg`, `trigger_cradle_wall_t` — and **56 parameters in the implementation that the registry never declares**. Several of the latter are §12 *derived* values typed in as literals: `rail_channel_h` = 12.50 (should be `dovetail_base_w + 2.00`), `trim_window_len` = 16.00 (should be the §12.8 chord expression), `trigger_socket_d` = 4.00 (should be `trunnion_d + 2·FC-PIVOT`, and is then asserted equal to its own derived twin), `collar_cavity_y/z` and `snout_spring_cavity_y/z` (the §8.5 cavity sections), and `serpentine_loop_dev_len_petg` = 12.10 (B-10). Part modules also contain bare literals (3.00, 6.30, 2.40, 4.60, 3.30, 6.50, 7.40, 10.00, 0.25, 1.40) in place of named parameters, violating R-G2 and making V-131's "zero literals" scan impossible to pass.
- **Root Cause:** Parameters were added to `parameters.py` as geometry needed them, without the corresponding registry update — a crossing of the ownership boundary in `OWNERSHIP.md`, since `PARAMETERS.md` is design-owned.
- **Required Change:** Reconcile in both directions: add the 14 missing parameters to the implementation and use them; raise a design change request for each of the 56 undeclared ones so they can be added to `PARAMETERS.md` §1–11 with units, defaults, valid ranges and derivations, or be replaced by an existing derived expression. Replace every §12 value that is currently typed with its formula. Replace every bare literal in the component modules with a named parameter.
- **Constraints That Must Not Change:** rule 1 of `PARAMETERS.md` — a value appears once, and if it can be computed it belongs in §12.
- **Acceptance Test:** The field diff reports zero missing and zero undeclared; V-131's static literal scan reports zero clearance literals in `geometry_engine/`.

### ISSUE M-17: Assertion coverage is incomplete and material-gated
- **Component(s) / File(s):** `parameters.py:675-733` (`validate`)
- **Severity:** MAJOR
- **Description:** `PARAMETERS.md` §13 defines ASSERT-01…23 as unconditional. In the implementation: ASSERT-13/14/15/18 (the blanket "every sigma / every sigma_rest / every strain / every force" checks) are not implemented as blanket checks at all, but as per-mechanism checks each gated on `material`. Because `validate()` runs against a single instance, a PLA_PLUS build silently skips every PETG stress check (ASSERT-44…51) and a PETG build silently skips every PLA check (ASSERT-37…39). No single invocation validates the hybrid assembly that is actually built. ASSERT-07 and ASSERT-10 were replaced with weaker predicates that no longer guard their stated conditions (see B-03). ASSERT-G1 and ASSERT-G3 are absent. ASSERT-16 checks only `pawl_thickness`, and ASSERT-17 checks `wall_internal >= 1.60` while `PARAMETERS.md` §2 sets the parameter to 1.80.
- **Root Cause:** The hybrid material allocation (OQ-6) introduced per-part materials, but the assertion block remained a single-material construct.
- **Required Change:** Evaluate the assertion block per part against that part's allocated material, and add an assembly-level `validate_all()` that runs every mechanism's checks with its own material. Restore ASSERT-07 and ASSERT-10 to their normative predicates. Implement ASSERT-G1 and ASSERT-G3 inside `fillet_polygon` and `folded_leaf`. Make ASSERT-16 iterate over every flexure thickness in the model.
- **Constraints That Must Not Change:** no threshold may be weakened (AGENTS.md).
- **Acceptance Test:** A single command validates all ten parts with their allocated materials and reports every ASSERT id as evaluated (not skipped).

### ISSUE M-18: The Phase 2 gates measure the wrong things, and the journey overstates what they proved
- **Component(s) / File(s):** `scripts/check_phase2_ath0*.py`; `iterations/PHASE_2_JOURNEY.md`
- **Severity:** MAJOR
- **Description:** Every per-part gate checks (a) mesh watertightness, (b) the part's own bounding box, (c) the *analytic* formulas in `parameters.py`, and (d) a rest-pose intersection against one or two named parts. None measures a clearance from the geometry, and only ATH_08 samples motion — at 0/50/100 % of stroke rather than the V-123-specified 0/23.8/28.0 mm, which is why the afterburner station has never been evaluated. Nine part pairs are never compared at all (ATH_02–ATH_07, ATH_04–ATH_05, ATH_09–ATH_10 among them), which is exactly where the largest interferences are. `PHASE_2_JOURNEY.md` nonetheless records for ATH_09 that the gate "confirmed … 0/9.594/15.0/15.6 degree pose stations"; the script writes those numbers into a JSON field and never evaluates them. Independent measurement finds 21.85 mm³ of interference at 9.594°.
- **Root Cause:** Interim gates were treated as acceptance evidence in the absence of the §12 validators.
- **Required Change:** Retire the per-part gates in favour of the four §12 check scripts (B-16), which must sweep every DOF at the §12.3 sample set and compare **all** part pairs. Correct the ATH_09 and ATH_07 entries in `PHASE_2_JOURNEY.md` so they state what was actually executed.
- **Constraints That Must Not Change:** the §12.3 sample sets are normative — 3 positions per translational DOF, 4 rotational plus 2 diagonals for the hat, 4 for the trigger.
- **Acceptance Test:** `check_kinematics.py` emits a JSON of measured minimum distances for all 55 pairs at every sampled pose, and the journey's claims match its output.

### ISSUE M-19: The 13-module geometry kernel was never built; parts draw primitives directly
- **Component(s) / File(s):** `geometry.py` (8 helpers); `ALGORITHM.md` §5
- **Severity:** MAJOR
- **Description:** §5 mandates thirteen reusable generators and states that "a part module that draws primitive geometry directly is a defect". Implemented: `bore_z` (partially — `hole_comp` is applied by `bore_z` but bypassed by the trigger socket, the trim pocket and the hat recess, which cut raw diameters), `seam_ribbon`, `key_feature`, `snap_feature`. Missing entirely: `fillet_polygon`, `chamfered_prism`, `swept_solid`, `dovetail_pair`, `detent_ramp`, `folded_leaf`, `arc_serpentine`, `spiral_arm`, `internal_ratchet`, `diamond_knurl`, `deboss`. Each of those is instead inlined in one part module, so the mating-pair guarantee of R-G8 — that a hook and its pocket cannot drift apart — does not hold. Six of the fifteen defects above are direct consequences (B-01, B-02, B-04, B-11, M-01, M-05).
- **Root Cause:** Parts were authored before the kernel.
- **Required Change:** Extract the eleven missing modules into `geometry.py` per §5, with every clearance applied once inside the module from its named fit class, and refactor the part modules to call them. This is the single change that prevents the mating-pair class of defect from recurring.
- **Constraints That Must Not Change:** R-G7 dependency rule (no cross-component imports); every existing passing dimension.
- **Acceptance Test:** No part module constructs a `box`/`cylinder` for a mating feature; V-131 reports every clearance traceable to a fit class; all ten parts still export watertight and single-body with unchanged bounding boxes.

### ISSUE M-20: PETG re-solves changed the stress knob without a design change request
- **Component(s) / File(s):** `parameters.py:81-83, 165-170, 232-234, 249-250`; `DESIGN_SPEC.md` §7; `PARAMETERS.md` §14
- **Severity:** MAJOR
- **Description:** Four flexures were re-solved for PETG by changing **thickness**, the stress knob: throttle leaf 2.63 → 3.20 mm, hat arm 0.85 → 1.20 mm, serpentine beam 1.10 → 0.92 mm, trigger stage-1 0.75 → 1.0986 mm and stage-2 1.35 → 1.50 mm. `ALGORITHM.md` §10.1 states plainly that retuning a length or thickness "changes stress and invalidates the fatigue case — that is a redesign, not a tune, and it must go back through §7 of `DESIGN_SPEC.md`". It did not. `DESIGN_SPEC.md` §7 and `PARAMETERS.md` §1–12 still carry the PLA+ geometry, so the two normative documents no longer describe the released parts, and `PARAMETERS.md` §14 (which says PETG is not a drop-in and that three of six widths do not fit) was never superseded. `trigger_stage1_thick_petg` = 1.09863111111111 and `trigger_stage1_width_petg` = 7.66444349274416 are unrounded solver outputs typed as constants rather than expressions.
- **Root Cause:** OQ-6 was answered "hybrid material authorised" without a follow-on design pass, and the re-solves were performed in the implementation layer.
- **Required Change:** Route each PETG re-solve back through §7 as a design change: publish the re-derived L, b, t, k, sigma and F for each mechanism in `DESIGN_SPEC.md` §7 and `PARAMETERS.md`, retire `PARAMETERS.md` §14's PLA-scaling table, and express the solved values as formulas (`t = f(sigma_allow, E, delta, L)`), not as 14-digit literals.
- **Constraints That Must Not Change:** the six force targets of §4.2; the PETG allowables 22.0 / 6.0 MPa; R-M4 (tune force with width, stress with length and thickness).
- **Acceptance Test:** For every flexure, the value in `parameters.py` equals the value published in `PARAMETERS.md` §12 to 1e-6, and each is produced by an expression rather than a literal.

### ISSUE M-21: The guard hood wall is 1.60 mm
- **Component(s) / File(s):** `parameters.py:191` (`guard_wall`); `PARAMETERS.md` §6
- **Severity:** MAJOR
- **Description:** `guard_wall` = 1.60 mm is an *exterior* wall on a hand-operated part, below both P-2 (2.40 mm exterior) and P-3 (1.80 mm internal partition). The implementation follows the parameter faithfully, so this is a specification defect surfaced by the build.
- **Root Cause:** §8.4 feature 1 states "wall 1.60" without reconciling it against §10.2.
- **Required Change:** Either raise `guard_wall` to 2.40 mm — which reduces `guard_inner_clear` to 2.10 mm and therefore requires `fire_btn_proud` ≤ 1.70 mm (interacts with B-03) — or add an explicit, justified exemption for ATH_04 in §10.2 on the grounds that the hood is a shell in compression, not a load-bearing wall. I recommend the exemption, stated in §10.2 with the reasoning, and a floor of 1.60 mm.
- **Constraints That Must Not Change:** `guard_hood_h` = 4.50 (X chain); the hood must still swallow the button head with clearance.
- **Acceptance Test:** V-151 either reports ≥ 2.40 mm on ATH_04 or matches the documented exemption value exactly.

### ISSUE M-22: The rail has no rear lead-in and no forward end stop
- **Component(s) / File(s):** `components_phase1.py:223-225` (`rail_channel`, `_throttle_dovetail_slot`); `DESIGN_SPEC.md` §8.1 feature 11
- **Severity:** MAJOR
- **Description:** Feature 11 requires a 0.60 × 45° lead-in at rail-local x = 0 and a forward hard stop at rail-local x = 43.50. Neither exists: the dovetail slot is extruded through the full `rail_len + 2·eps` with open ends, so the carriage can be pushed straight out of the *front* of the rail, past the ramp, and the 28.0 mm stroke has no mechanical limit. Measured ATH_01–ATH_08 minimum distance at full stroke is 0.0050 mm, i.e. the carriage is already touching something at the travel limit without a defined stop face.
- **Root Cause:** The `dovetail_pair` module (which owns the end features) was never implemented; the slot is a bare prism.
- **Required Change:** Terminate the dovetail slot at rail-local 43.50 with a full-height stop face, and add the 0.60 × 45° lead-in chamfer at the rear entry, both inside `dovetail_pair("slot")`.
- **Constraints That Must Not Change:** `rail_len` = `throttle_carriage_len + throttle_stroke + 2·rail_end_clear` = 44.00; travel = 28.00 exactly (ASSERT-21).
- **Acceptance Test:** `check_kinematics.py` V-123 reports first stop contact at 28.00 ± 0.05 mm of travel and no path out of the rail's forward end.

---

## 4. MINOR and OPTIONAL Issues

### ISSUE m-01: ATH_01 overshoots datum E by 0.005 mm
- **Component(s) / File(s):** `components_phase1.py:88-110` (`post_spine`, `pawl_mount` heights of `deck_y − y0 + eps`)
- **Severity:** MINOR
- **Description:** Measured ATH_01 max Y = **36.005 mm**. The trim post spine and pawl mount are extruded `+ eps` past `deck_y`, leaving two 0.005 mm nubs proud of the top deck. Datum E is no longer a flat plane, and the part's build face carries two sub-layer bumps.
- **Root Cause:** `eps` (an anti-coincidence allowance for subtractions, R-G3) applied to an *additive* solid, where it has no purpose.
- **Required Change:** Grow additive solids only toward the interior; reserve `eps` for cutting tools.
- **Constraints That Must Not Change:** `chassis_height` = 36.00 (Y chain).
- **Acceptance Test:** ATH_01 max Y = 36.000 ± 0.001 mm.

### ISSUE m-02: ATH_03 exceeds its declared bounding box by 0.60 mm in X
- **Component(s) / File(s):** `components_phase2.py:110-120` (`stanchion` at `guard_hinge_x` with `guard_stanchion_t` in X)
- **Severity:** MINOR
- **Description:** Measured ATH_03 X extent is [72.0, **84.60**] against the §8.3 declared X[72.0, 84.0]. The hinge stanchions are centred on `guard_hinge_x` = 83.0 with a 3.20 mm X thickness, so they stand 0.60 mm proud of the bezel front face. The assembly X chain still closes at 86.0 (the guard is foremost), so this is dimensional drift rather than an envelope breach.
- **Root Cause:** Stanchion thickness was applied symmetrically about the hinge axis rather than referenced to the bezel front face.
- **Required Change:** Either reference the stanchion's front face to `bezel_front_x` or update §8.3's declared bounding box to X[72.0, 84.60] with a stated reason.
- **Constraints That Must Not Change:** `guard_hinge_x` = 83.0; the D2.55 pivot bore axis.
- **Acceptance Test:** ATH_03's measured bbox matches its declared bbox within ±0.05 mm.

### ISSUE m-03: V-104's maximum-edge criterion is not met by any part
- **Component(s) / File(s):** all exported meshes; `DESIGN_SPEC.md` §12.1 V-104
- **Severity:** MINOR
- **Description:** V-104 requires "max edge ≤ 2.0 mm". Measured longest edges: ATH_01 77.2 mm, ATH_02 70.0 mm, ATH_09 18.9 mm, ATH_08 15.9 mm, ATH_05 13.6 mm. The chordal half of V-104 passes comfortably (0.0023–0.0029 mm against a 0.010 mm limit), so this is a criterion-versus-mesh mismatch, not a geometric error: the long edges belong to planar faces that need no subdivision.
- **Root Cause:** V-104 bundles a curvature criterion (chordal deviation) with a uniform tessellation criterion (max edge) that only matters for downstream tools requiring near-uniform triangles.
- **Required Change:** Either state the intent — restrict the max-edge criterion to facets on curved faces — or set a linear deflection in the exporter that subdivides planar faces. I recommend the former; a 77 mm planar triangle is exact and is not a defect.
- **Constraints That Must Not Change:** chordal deviation ≤ 0.01 mm.
- **Acceptance Test:** V-104 as restated passes for all ten parts.

### ISSUE m-04: The "FIRE" deboss reads rotated 90°
- **Component(s) / File(s):** `components_phase2.py:143-191` (`_fire_label`)
- **Severity:** MINOR
- **Description:** The four glyphs are laid out along design **Y** (the vertical axis) with their cap height along design Z, so the legend reads bottom-to-top rather than left-to-right on the button face. The preview render confirms it.
- **Root Cause:** The glyph advance and cap-height axes were transposed when the label was placed on the YZ face.
- **Required Change:** Advance the glyphs along Z with cap height along Y.
- **Constraints That Must Not Change:** `fire_btn_deboss_depth` = 0.50 ≥ `deboss_depth` (P-6); stroke width 1.20 ≥ `feature_min` (P-5); cap height 6.00.
- **Acceptance Test:** Visual inspection in `design/VISUAL_REVIEW.md`; the glyph bounding box measures 6.00 mm in Y and about 6.35 mm in Z.

### ISSUE m-05: `hole_comp` is applied inconsistently
- **Component(s) / File(s):** `geometry.py:44-46` (`bore_z`); `components_phase1.py:216, 297` (trim pocket, trigger socket); `components_phase1.py:26-33` (hat recess)
- **Severity:** MINOR
- **Description:** §5.2 requires `hole_comp` = 0.10 mm to be applied once, at the point of subtraction, by a single helper. `bore_z` does so and is used for the trim bore and counterbore and the guard pin holes. The trigger socket (D4.00), the trim pocket (D24.00) and the hat recess (D18.50) are cut with `cylinder_z`/`cylinder_y` at raw diameters, so those internal features will print undersize by roughly 0.10 mm — enough to consume half of FC-PIVOT on the trigger pivot.
- **Root Cause:** Two cylinder helpers exist; only one compensates.
- **Required Change:** Route every internal cylindrical subtraction through the compensating helper, and add a Y-axis and X-axis equivalent of `bore_z`.
- **Constraints That Must Not Change:** `hole_comp` must not be folded into the fit-class constants (§5.2).
- **Acceptance Test:** V-131's scan finds no raw-diameter internal cut; the trigger socket cutter measures 4.10 mm.

### ISSUE m-06: The retaining shoulder is derived from `bezel_chamfer`
- **Component(s) / File(s):** `parameters.py:534` (`btn_shoulder_pocket` = `fire_btn_bore + 2·bezel_chamfer`)
- **Severity:** MINOR
- **Description:** §12.3 defines `btn_shoulder_pocket` = `fire_btn_bore + 2 × 1.50`, where 1.50 is the shoulder *ledge width* (§8.3 feature 5). The implementation reuses `bezel_chamfer`, which is coincidentally also 1.50. The number is right today and will silently become wrong the moment the perimeter chamfer is retuned.
- **Root Cause:** A numeric coincidence was used as a derivation.
- **Required Change:** Introduce a named `btn_shoulder_ledge` = 1.50 parameter in `PARAMETERS.md` §6 and derive the pocket from it.
- **Constraints That Must Not Change:** `btn_shoulder_pocket` = 13.90 at the defaults.
- **Acceptance Test:** Changing `bezel_chamfer` leaves `btn_shoulder_pocket` unchanged.

### ISSUE m-07: Handedness is mirrored per part rather than once around the assembly
- **Component(s) / File(s):** `components_phase1.py:325-328`; every `phase2_ath0*` wrapper
- **Severity:** MINOR
- **Description:** `ALGORITHM.md` §4.3 requires `handed()` to wrap the entire assembly once and warns explicitly that per-part mirroring mirrors text and directional features independently. Each part instead applies its own `mirror("XY")`. The geometry is equivalent, but the "FIRE" legend and the four hat direction arrows come out mirror-imaged when `handedness = −1`.
- **Root Cause:** The mirror was placed in the part wrappers because no assembly module exists.
- **Required Change:** Apply the mirror once in the assembly driver; remove it from the part wrappers.
- **Constraints That Must Not Change:** V-162 must still rebuild and pass at `handedness = −1`.
- **Acceptance Test:** V-162 rebuilds the mirrored assembly with all tests passing and legible (non-mirrored) legends.

### ISSUE m-08: The +Z snap hooks are silently relocated, breaking station symmetry
- **Component(s) / File(s):** `geometry.py:76-79` (`if station_z > 0: station_x = min(station_x, p.trim_safe_snap_hook_station_x)`)
- **Severity:** MINOR
- **Description:** The mechanism-flank hook at X = 46.0 is silently moved to X = 39.70 while its −Z twin stays at 46.0. §8.1 feature 17 and §8.2 feature 10 specify both flanks at X = 12.0 and 46.0. The asymmetry biases the seam closing force toward −Z and is applied by a hidden `min()` inside a shared helper rather than declared as a parameter.
- **Root Cause:** A collision with the trim pocket was resolved locally instead of by re-specifying `snap_hook_stations_x`.
- **Required Change:** Either move both flanks' hooks to a common, declared station pair, or add an explicit `snap_hook_stations_x_flank` parameter to `PARAMETERS.md` §11 stating the asymmetry and its reason.
- **Constraints That Must Not Change:** ASSERT-19 (all hook stations < `seam_x_max`); ASSERT-40 (hook clear of the trim pocket by `wall_internal`).
- **Acceptance Test:** The hook stations in the built geometry match the declared registry values exactly.

### ISSUE m-09: ATH_10 exceeds its declared 4.00 mm cross-section
- **Component(s) / File(s):** `components_phase1.py:236-239`; `DESIGN_SPEC.md` §8.10
- **Severity:** MINOR
- **Description:** Measured key extents are 4.60 × 8.00 × 4.60 mm against the declared 4.00 × 8.00 × 4.00 mm, because the waist rib is 0.30 mm proud on all four faces. See B-13 for the functional consequence.
- **Root Cause:** §8.10 states both the 4.00 bounding box and the proud rib without reconciling them.
- **Required Change:** Resolve with B-13 — delete the rib, or restate the bounding box and add socket-mouth reliefs.
- **Constraints That Must Not Change:** `key_side` = 4.00; `key_len` = 8.00.
- **Acceptance Test:** ATH_10's measured bbox matches its declared bbox.

### ISSUE O-01: `CHANGELOG.md` does not record Phase 2
- **Severity:** OPTIONAL — the changelog still ends at the Phase 1 structural-root entry, while ATH_03…ATH_09 have since been implemented. Add the Phase 2 entry in the existing format (files changed, reason, expected effect, validation performed, remaining issues), per `CLAUDE.md`'s change-discipline rule.

### ISSUE O-02: Validation reports contain fields that look like executed checks but are not
- **Severity:** OPTIONAL — `phase2-ath09-validation.json` carries `"motion_samples_deg": [0.0, 9.594, 15.0, 15.6]` and `phase2-ath07-validation.json` carries a `chassis_redesign` block; neither is the output of a check. Rename such fields to make their descriptive status explicit, or delete them, so a reader cannot mistake a record for a result.

### ISSUE O-03: Dead code in `seam_ribbon`
- **Severity:** OPTIONAL — the trim-window cutter inside `seam_ribbon` is placed at Z[5.25, 13.25] while the ribbon lives at Z[−0.60, +0.60], so `rail.cut(window)` removes nothing. It will become live once M-01 restores the perimeter ribbon; until then it is misleading.

### ISSUE O-04: `_hat_arm` builds its detent stem with a negative height
- **Severity:** OPTIONAL — `stem_top_y − nose_top_y + eps` evaluates to −0.39 mm at the defaults, so `_cylinder_y_design` is called with a negative extrusion. OCCT tolerates it and the export is valid, but the intent is unclear and the feature is buried inside the arm ribbon. Resolve alongside B-09 when the detent noses are reinstated.

---

## 5. Defects in the Normative Documents (design-owned; my responsibility)

Eleven items cannot be fixed by the implementation agent because the specification itself is wrong or silent. I will correct these in `DESIGN_SPEC.md` and `PARAMETERS.md` before Phase 4 begins; they are listed here so the Phase 4 change request is unambiguous about what is authorised to move.

| ID | Document | Defect | Resolution I will apply |
| :-- | :-- | :-- | :-- |
| S-01 | `DESIGN_SPEC.md` §8.2 f.5/f.11, `PARAMETERS.md` §10/§11 | `key_stations_x[1]` = 58.0 is the same station as `trigger_pivot_x` = 58.0, and the key spans the pivot's Y. Geometrically impossible (B-12). | Move the key to X ≈ 66.0; add a key-to-pivot separation assertion. |
| S-02 | `PARAMETERS.md` §6 | `fire_btn_proud` = 3.00 violates its own declared bound `< guard_hood_h − guard_wall` = 2.90 and interferes with the closed hood (B-03). | Set to 2.50 and derive it. |
| S-03 | `DESIGN_SPEC.md` §8.1 f.4 | The snout collar is called a "male boss" at X[72, 82] but the required nose relief around it is never stated (B-01). | State the neck-down explicitly as a controlled feature. |
| S-04 | `DESIGN_SPEC.md` §8.8 | The part bounding box Z[5.00, 12.85] contradicts feature 1, which places the tenon at Z[4.10, 5.85]. The build measures Z[4.11, 12.85]. | Correct the bounding box to Z[4.10, 12.85]. |
| S-05 | `DESIGN_SPEC.md` §10.4 | The table is self-inconsistent: the declared rotations do not put the declared build faces on the plate (rot Y +90 maps design X to print −Z, so it cannot seat a Z-normal face), and for ATH_05 and ATH_08 the declared build face makes R-P1/V-158 unsatisfiable as worded. | Re-derive every row from its build face, state the rotation as a computed consequence, and restate V-158 as "the flexure's neutral axis lies in the print XY plane". |
| S-06 | `PARAMETERS.md` §6 | `bezel_barb_len` = 10.50 contradicts §7.7, §8.3 and D-12, which all specify 11.60. At 10.50 the assembly strain is 1.81 %, above the 1.5 % PLA limit. The implementation correctly used 11.60. | Correct §6 to 11.60. |
| S-07 | `DESIGN_SPEC.md` §13 | D-05 states the pawl becomes "17.70 dev × 5.50 wide" while §7.2 and §12.5 both solve 3.60. D-09 states stage 1 becomes "developed 21.00, width 14.50" while §7.5, §8.9 and §12.10 use 21.20 / 14.60. | Correct the D-05 and D-09 rows to match the solved values. |
| S-08 | `DESIGN_SPEC.md` §8.3, §8.4 vs §10.2 | `guard_wall` = 1.60 and the bezel's 1.90 mm collar wall are exterior walls below P-2's 2.40 mm (M-09, M-21). | Raise the bezel section; grant ATH_04 a documented, reasoned exemption with a 1.60 mm floor. |
| S-09 | `DESIGN_SPEC.md` §8.10 | A 4.00 mm bounding box and a 0.30 mm proud waist rib are declared together, and `key_socket_side` = 4.20 cannot accept the resulting 4.60 mm section (B-13, m-09). | Delete the waist rib. |
| S-10 | `DESIGN_SPEC.md` §15 OQ-3 | Still unanswered: no holding torque is specified for the guard's bi-stable cam, so `guard_cam_leaf_w` = 6.00 remains a free variable and the mechanism has no acceptance criterion. | Specify a holding torque, or formally accept 6.00 and defer to first-article tuning. |
| S-11 | `DESIGN_SPEC.md` §6/§7, `PARAMETERS.md` §14 | The hybrid PLA/PETG allocation approved under OQ-6 was never propagated into the normative documents; §14 still says PETG is not a drop-in and that three of six widths do not fit (M-20). | Publish the per-part material map and the PETG-solved geometry in §7; retire the §14 scaling table. |

---

## 6. Review Summary Table

Counts are of issues in which the component is named as affected; an issue spanning two parts is counted against both.

| Component | Status | Blockers | Majors | Minors | Optionals |
| :-- | :-- | :-- | :-- | :-- | :-- |
| ATH_01 Upper Chassis | FAIL | 8 | 8 | 3 | 1 |
| ATH_02 Lower Grip Shell | FAIL | 7 | 4 | 2 | 0 |
| ATH_03 Front Bezel Faceplate | FAIL | 4 | 4 | 2 | 0 |
| ATH_04 Missile Safety Guard | FAIL | 3 | 2 | 0 | 0 |
| ATH_05 Fire Button Plunger | FAIL | 4 | 3 | 1 | 0 |
| ATH_06 4-Way Hat Switch | FAIL | 3 | 4 | 0 | 1 |
| ATH_07 Rotary Trim Wheel | FAIL | 4 | 2 | 0 | 0 |
| ATH_08 Throttle Slider | FAIL | 2 | 6 | 0 | 0 |
| ATH_09 Dual-Stage Trigger | FAIL | 5 | 3 | 1 | 0 |
| ATH_10 Alignment Keys (x2) | FAIL | 3 | 1 | 1 | 0 |
| Master Assembly & Kinematics | FAIL | 4 | 7 | 2 | 2 |

Unique issue count: **17 BLOCKER, 22 MAJOR, 9 MINOR, 4 OPTIONAL**, plus **11 normative-document defects** (§5).

### 6.1 Success criteria (`DESIGN_SPEC.md` §1.2)

| # | Criterion | Verdict | Evidence |
| :-- | :-- | :-- | :-- |
| S-1 | Ten watertight, single-component, positive-volume solids | **PASS** | measured, all ten |
| S-2 | Assembly bbox 86.0 × 72.0 × 26.5 ±0.30 | **PASS** | 86.000 × 72.000 × 26.500 |
| S-3 | No static interference at any point of motion | **FAIL** | 9 rest-pose pairs, 663 mm³; 4 mechanisms interfere in motion |
| S-4 | Every dynamic clearance equals its fit class ±0.03 | **FAIL** | 4 of 4 measured pairs out of tolerance |
| S-5 | Every flexure within §6.3 allowables at max deflection | **FAIL** | serpentine 56.6 MPa vs 22.0; no root fillets anywhere |
| S-6 | Zero geometry beyond the 45° overhang rule | **FAIL** | all ten parts, worst facet 90° |
| S-7 | Every parameter rebuilds across its declared range | **NOT EVALUATED** | V-160/161/162 never run |
| S-8 | Six mechanisms deliver target force/travel | **FAIL** | throttle −31 %; hat model invalid; trim locked; trigger jams |

---

## 7. Recommended Phase 4 Correction Sequence

`CLAUDE.md` requires one subsystem per iteration. The order below is dependency-driven: each step unblocks the next, and every step ends with objective evidence rather than a successful build.

1. **Normative repair (design-owned, blocking).** Apply S-01 … S-11. Nothing in `geometry_engine/` should move until the specification is self-consistent, or the same defects will be re-implemented.
2. **Instrumentation before geometry (B-16, B-17, M-18).** Populate `validation_config.json`, write the four §12 check scripts, and repoint the build driver at CadQuery. Confirm they *reproduce* the nine interferences and the four clearance failures reported here. A correction loop without working validators is guesswork.
3. **Kernel extraction (B-14, M-13, M-19).** Implement `fillet_polygon`, `chamfered_prism`, `swept_solid`, `dovetail_pair`, `detent_ramp`, `folded_leaf`, `arc_serpentine`, `spiral_arm`, `internal_ratchet`, `diamond_knurl`, `deboss` and the true mating-pair modules. This alone resolves or de-risks six blockers and prevents the mating-pair defect class from recurring.
4. **Seam subsystem (B-11, B-13, M-01).** Hooks, tongue-and-groove and key sockets, all reflected correctly about datum A. Verify with a virtual −Y assembly sweep.
5. **Nose subsystem (B-01, B-02, B-03, M-02, M-09, M-10).** Chassis neck-down, latch pockets, hinge relocation, button proud height and guide length.
6. **Trim subsystem (B-04, B-05, B-06, M-04).** Relief pocket Z station, radial pawl, post relief slots.
7. **Trigger subsystem (B-07, B-08, M-07, M-08).** Stop bar and shelf solved from the swept arcs; cradle mouth; trunnion chamfer.
8. **Hat subsystem (B-09, M-11, M-12).** Detent pockets, conical relief, gimbal socket, re-derived force model.
9. **Throttle subsystem (M-03, M-05, M-06, M-22).** Preload, ramp back on the channel floor, plate wall thickness, end stop and lead-in.
10. **Fire-button spring (B-10, M-20).** True arc serpentine with the developed length measured from the wire, re-solved for PETG through §7.
11. **Printability pass (B-15, M-13, M-14).** Print-CS transform, overhang elimination, bed chamfers, 3MF and master-assembly exports, mass check.
12. **Parametric robustness (M-16, M-17).** Registry reconciliation, per-part assertion evaluation, then V-160/161/162 across every declared range and at `handedness = −1`.

---

## Final Verdict

**DESIGN REVIEW: FAIL**

- Total issues: **52** (Blockers: **17**, Majors: **22**, Minors: **9**, Optionals: **4**), plus **11** normative-document defects that must be corrected by the design authority first.
- Recommended Next Step: **Proceed to Phase 4 Corrections**, in the sequence given in §7. Phase 5 acceptance must not be attempted until `design/DESIGN_REVIEW.md` carries no unresolved BLOCKER or MAJOR and `python scripts/validate.py` reports `status: PASS` with zero skipped tests.
