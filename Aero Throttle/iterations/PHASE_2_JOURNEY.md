# Aero-Throttle Phase 2 Journey

This file is the durable continuation record for the CAD implementation.  Resume
from the first incomplete phase after any context reset.

## Approved decisions

| Decision | Approved outcome | Implementation consequence |
| --- | --- | --- |
| OQ-1 | 28.00 mm stroke, 15.00 mm carriage | Preserve the 44.00 mm rail and the 1.43 guide ratio; validate off-axis binding during physical review. |
| OQ-4 | Chassis/grip seam is permanent | Use non-serviceable hook return faces and omit tool-access release slots. |
| OQ-6 | Hybrid material authorised | Material is selected per part and captured in exported metadata and the parameter report. |
| OQ-9 | CadQuery/OCCT is authoritative | CadQuery produces STEP/STL; OpenSCAD is retained only as a preview bridge. |

## Material allocation

| Material | Parts | Reason |
| --- | --- | --- |
| Matte PLA | ATH_01, ATH_02, ATH_07, ATH_10 | Rigid structural bodies and the acoustic ratchet rotor benefit from stiffness and crisp tactile feedback. |
| PETG | ATH_03, ATH_04, ATH_05, ATH_06, ATH_08, ATH_09 | Snap- and flexure-bearing parts require improved fatigue life. Geometry must be independently re-solved for PETG before release. |

## Phases

| Phase | Scope | Status | Evidence / next action |
| --- | --- | --- | --- |
| 0 | Decisions, toolchain, and source baseline | Complete | CadQuery 2.8.0 / OCCT imports from `.venv-cad`; OpenSCAD Nightly 2026.06.21 is available for previews; Git LFS attributes are configured. |
| 1 | Parameter registry, geometry kernel, ATH_01/10/02 | Complete | CadQuery Phase 1 model exports watertight STL + STEP for ATH_01, ATH_02, and two ATH_10 key instances; `scripts/check_phase1.py` passes. |
| 2 | ATH_03 through ATH_09; material-specific flexure re-solves | Complete | ATH_03 through ATH_09 build and Phase-2 validation gates pass. ATH_09 has the PETG stage-one/stage-two re-solve and consumes the ATH_02 trigger interfaces. |
| 3 | STEP/STL/3MF exports, preview bridge, objective validators | Pending | Wire no-skipping validation configuration. |
| 4 | Full build, preview inspection, correction loop, release report | Pending | Stop only when all objective tests pass or an evidence-backed blocker remains. |

## Current state

- Current phase: **3 — STEP/STL/3MF exports, preview bridge, objective validators**.
- ATH_03 gate: **PASS**. `scripts/build_phase2_ath03.py` exported its STL/STEP, `scripts/check_phase2_ath03.py` confirmed a watertight single solid and PETG cam-leaf stress of 15.00 MPa against a 22.00 MPa cyclic allowable, and `output/preview/ATH_03_FRONT_BEZEL_FACEPLATE.png` was visually inspected. The specified 6.00 mm leaf width is retained for first-article tuning because OQ-3 has no holding-torque target.
- ATH_04 bounding-box clarification: the specified closed hood bounds exclude its outward-facing hinge pins. The hood remains Z = [-7.50, +7.50] mm; the pins extend to Z = [-10.50, +10.50] mm to mate ATH_03's verified bore axes at Z = +/-9.00 mm.
- ATH_04 bounding-box clarification: its specified closed hood bounds exclude both the outward-facing hinge pins and the dual-flat cam. The hood remains Z = [-7.50, +7.50] mm; pins extend to Z = [-10.50, +10.50] mm, and the specified 3.20 mm base-radius / 0.80 mm lobe cam may extend forward of the hood's X = 81.50 mm limit.
- ATH_04 gate: **PASS**. `scripts/build_phase2_ath04.py` exported the STL/STEP and parameter report. `scripts/check_phase2_ath04.py` confirmed a watertight single solid, the approved pin/cam envelope exclusions, PETG cam-interface stress of 15.00 MPa against the 22.00 MPa cyclic allowable, and zero closed-pose ATH_03/ATH_04 intersection. `output/preview/ATH_04_MISSILE_SAFETY_GUARD.png` was visually inspected. The hinge-side walls are relieved across the ATH_03 ear band, with circular root bosses preserving pin attachment.
- ATH_05 implementation decision: the approved rear anchor datum is X = 66.20 mm (0.20 mm forward of ATH_01's X = 66.00 mm cavity wall). The PETG spring is a six-span laterally folded XY serpentine. Its 0.92 mm in-plane beam and 5.40 mm Z depth preserve 0.40 mm clearance per side in ATH_01's 6.20 mm local spring bore.
- ATH_05 gate: **PASS**. `scripts/build_phase2_ath05.py` exported watertight STL/STEP and its parameter report; `scripts/check_phase2_ath05.py` confirmed one solid body, the X [66.20, 84.50] / Y [15.75, 28.25] / Z [-6.25, 6.25] bounds, zero ATH_01 and ATH_03 rest-pose interference, 2.77 N return force at 3.50 mm (V-171 band 2.70..3.70 N), 21.99 MPa PETG cyclic stress against the 22.00 MPa allowable, and a 2.08 mm solid-height reserve. `output/preview/ATH_05_FIRE_BUTTON_PLUNGER.png` was rendered and visually inspected.
- ATH_06 implementation decision: approved Option A — opposite 150-degree PETG arms occupy two Y planes. The active dimensions are 17.02 mm developed length, 2.35 mm radial width, and 1.20 mm bending thickness; the planes are Y = 26.75 and 28.35 mm with a 0.40 mm printable separation. This preserves the D17.50 cap and avoids the original four-arm planar overlap.
- ATH_06 gate: **PASS**. `scripts/build_phase2_ath06.py` exported watertight STL/STEP and its parameter report; `scripts/check_phase2_ath06.py` confirmed one solid body, the specified X [37.25, 54.75] / Y [26.75, 42.0] / Z [-8.75, 8.75] bounds, zero ATH_01 rest-pose intersection, FC-ROTARY D7.50/D8.00 gimbal clearance, 2.791 N return force at 14 degrees (target 2.80 N), and 21.05 MPa PETG cyclic stress against the 22.00 MPa allowable. `output/preview/ATH_06_4WAY_HAT_SWITCH.png` was rendered and visually inspected. The ATH_01 hat recess, lower FC-ROTARY support annulus, interrupted bayonet lip, and outboard structural struts were added as the consumed interface.
- ATH_07 standalone implementation: **BUILD PASS**. CadQuery exported a watertight, single-solid STL/STEP with the datum-K D22.00 x 6.80 rotor, FC-ROTARY nominal D5.50 bore (D5.60 with `hole_comp` applied at subtraction), D6.35 nominal snap-head counterbore, 20-tooth derived 89.98-degree ratchet, 1.80 mm +Z hub web, and 45-degree crossed diamond knurl. `output/preview/ATH_07_ROTARY_TRIM_WHEEL.png` was rendered and visually inspected.
- ATH_07 integration redesign: **PASS**. The datum-K pocket now uses its required Z axis. A top-deck-connected structural spine carries the trim post, a vertical PLA cantilever under the wheel carries an R0.40 valley-engaging pawl nose, and the congested +Z rear seam hook is shifted only to the derived safe station X=39.70 while retaining its full 15.00 mm beam and paired FC-SNAP pocket. Rebuilt `scripts/check_phase1.py` and `scripts/check_phase2_ath07.py` pass; ATH_01/ATH_07 rest-pose intersection is zero. `output/preview/ATH_01_ATH_07_TRIM_INTERFACE.png` was rendered and visually inspected.
- ATH_08 integration decision: ATH_01's nominal rail-channel void did not contain the normatively owned dovetail slot or afterburner ramp. The smallest paired-interface completion adds the FC-SLIDE female dovetail, the 30/65-degree ramp, and a rear-anchored internal spine with a keyed central ramp root; ATH_08's tenon is correspondingly relieved around that root while its dovetail flanks retain FC-SLIDE.
- ATH_08 PETG re-solve: the two-arm leaf remains 28.41 mm developed length with R2.60 folds. Its active width/thickness are 3.55 x 3.20 mm; the plate increases to 5.20 mm and the tab correspondingly reduces to 1.80 mm while its outer face remains 0.40 mm recessed from datum F. Computed break force is 4.17 N, cyclic stress 18.44 MPa (allowable 22.00), and preload stress 5.35 MPa (allowable 6.00).
- ATH_08 gate: **PASS**. `scripts/build_phase2_ath08.py` exported a watertight single-solid STL/STEP plus parameter report; `scripts/check_phase2_ath08.py` confirmed the datum-G envelope, FC-SLIDE derivation, rail/travel closure, 0/50/100 % non-interference, PETG stress allowables, 4.30 N force band, and 1.43 guide ratio. The Phase 1 and ATH_03…ATH_07 regression checks also pass. `output/preview/ATH_08_THROTTLE_SLIDER.png` was rendered and visually inspected.
- ATH_09 implementation decision: ATH_02's nominal trigger interface was incomplete in the Phase 1 model, so its existing socket cutters and anchor pad were completed with connected cradle walls, stop bar, shelf, and a central clearance throat. ATH_09 consumes these members about datum J without a rest-pose intersection. The throat's rear and left bridges keep ATH_02 one connected solid.
- ATH_09 PETG re-solve: stage 1 retains the normative 21.20 mm developed length and solves to 7.6644 mm width x 1.0986 mm bending thickness, yielding 1.600 N at 3.00 mm and 22.00 MPa. Stage 2 uses 7.22 mm width x 1.50 mm thickness, yielding 16.63 MPa; the force-derived tooth radius is 9.455 mm and the total break force is 5.20 N.
- ATH_09 gate: **PASS**. `scripts/build_phase2_ath09.py` exported a watertight single-solid STL/STEP and its parameter report; `scripts/check_phase2_ath09.py` confirmed the controlled X [46.0, 62.0] / Y [-24.0, 0.0] / Z [-7.25, 7.25] envelope, FC-PIVOT D3.80/D4.00 derivation, PETG stress and V-174 force bands, solved tooth radius, 0/9.594/15.0/15.6 degree pose stations, and zero ATH_02 rest-pose intersection. `output/preview/ATH_09_DUAL_TRIGGER.png` was rendered and visually inspected. The Phase 1 and ATH_03…ATH_08 regression checks also pass.
- Next bounded implementation task: **Phase 3 export and objective-validator wiring**. Populate the no-skipping validation configuration and complete the STL/STEP/3MF/preview export bridge without relaxing any validation threshold.
- CadQuery 2.8.0 / OCCT is installed in the ignored `.venv-cad` virtual environment and passes `pip check`.
- OpenSCAD Nightly 2026.06.21 is installed at `C:\Program Files\OpenSCAD (Nightly)\openscad.exe`; the future preview bridge will call this explicit path.
- No validation threshold has been modified. The normative source documents remain unchanged.
- Existing unrelated worktree change preserved: `prompts/CODEX_PHASE_2_IMPLEMENTATION.md`.
- Phase 1 implementation is in `geometry_engine/aero_throttle/`; it uses the global Y-up design frame and writes per-part STL/STEP plus `output/reports/parameters-phase1.json`.
- Phase 1 evidence: `scripts/build_phase1.py` and `scripts/check_phase1.py` both pass. The inspected preview is `output/preview/ATH_PHASE1_STRUCTURAL_ASSEMBLY.png`.

## Continuation prompt

> Continue `iterations/PHASE_2_JOURNEY.md` from the current phase. Preserve the approved OQ decisions, use CadQuery/OCCT as geometry authority, and execute the next incomplete phase with build/validation evidence.
