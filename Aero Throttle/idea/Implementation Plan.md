# Implementation Plan: Align Aero-Throttle CAD Specification with Original HOTAS Proposal

Re-align the Aero-Throttle CAD design specifications and technical renders with the original concept sketch and mechanism proposal in [`Fidget Toy Prototypes Portfolio.md`](file:///d:/3D%20Printing/Fidget%20Fuse/Fidget%20Toy%20Prototypes%20Portfolio.md).

## Discrepancy Analysis

The previous iteration in `Aero Throttle CAD Specification.md` and `Aero_Throttle_CAD_Design_Specification.md` deviated substantially from the approved concept in [`prototype1_aero_throttle_1787157922526.jpg`](file:///C:/Users/chuda/.gemini/antigravity-ide/brain/5324f30b-bc16-4635-a890-31f0949b9622/prototype1_aero_throttle_1787157922526.jpg):

| Feature / Component | Original Proposal Concept | Previous CAD Spec Deviation | Required Correction |
| :--- | :--- | :--- | :--- |
| **Chassis Architecture** | Two-tone modular split: **Upper Olive Drab Chassis** + **Lower Matte Black Grip Frame** + **Front Bezel Module** | Vertical clamshell split (Left Shell + Right Shell) | Redesign around Upper Chassis + Lower Grip Frame + Front Bezel snap-fit interlocking structure. |
| **Front Bezel & Missile Switch** | **Rectangular/faceted front faceplate** with rectangular flip-up missile guard and rectangular red fire button | Cylindrical $\varnothing 26\text{ mm}$ round snout (looked like a camera lens) with round button | Rectangular beveled avionics front faceplate with square/rectangular flip guard and tactile rectangular push button. |
| **Side Rotary Trim Wheel** | **Forward-lower side position** (embedded in lower forward flank of upper body, right above trigger guard) | Mistakenly moved to the **rear exhaust position** | Relocate trim wheel to the front-lower side quadrant as specified in the original sketch. |
| **Linear Throttle Slider** | Upper-mid side track with raised bezel and tactile slider tab | Generic side slider | Parametrically define the side-flank dovetail slide track with compliant $85\%$ afterburner detent gate. |
| **4-Way Hat Switch** | Crown-mounted stepped pyramidal 4-way switch on the top deck | Centered flat top puck | Top-deck mounted ergonomic 4-way hat switch with 4-directional compliant star-spring base. |
| **Dual-Stage Trigger** | Underside index-finger tactical trigger with bottom spur | Generic lower trigger | Ergonomic curved trigger with dual-stage flexure (light take-up then sharp mechanical break). |

---

## Proposed Changes

### 1. Visual Asset Generation
Generate updated, high-fidelity visual assets faithful to the original sketch:
- **Hero Render:** High-detail 3D product render showing the assembled Aero-Throttle in two-tone Olive Drab & Matte Black, with the front rectangular missile guard, forward-side knurled trim wheel, top 4-way hat switch, side linear throttle slider, and dual-stage index trigger.
- **Exploded Technical View:** Clear 3D exploded diagram showing all 10 snap-fit printed components aligned to the assembly axes.

### 2. CAD Specification Documents Update
Update both specification files to maintain full synchronization:
#### [MODIFY] [`Aero Throttle CAD Specification.md`](file:///d:/3D%20Printing/Fidget%20Fuse/Aero%20Throttle%20CAD%20Specification.md)
#### [MODIFY] [`Aero_Throttle_CAD_Design_Specification.md`](file:///d:/3D%20Printing/Fidget%20Fuse/Aero_Throttle_CAD_Design_Specification.md)

Key updates in both documents:
- Embed the new faithful visual renders.
- Revise the component taxonomy to match the 3-module architecture:
  1. `ATH_01_UPPER_CHASSIS` (Olive Drab Green Upper Body)
  2. `ATH_02_LOWER_GRIP_FRAME` (Matte Black Ergonomic Lower Handle)
  3. `ATH_03_FRONT_BEZEL_FRAME` (Matte Black Rectangular Faceplate)
  4. `ATH_04_MISSILE_GUARD` (Matte Red / Black Bi-Stable Flip Cover)
  5. `ATH_05_FIRE_BUTTON` (Vibrant Red Rectangular Tactile Plunger with S-Curve Spring)
  6. `ATH_06_4WAY_HAT_SWITCH` (Matte Black Stepped 4-Way Thumb Hat Switch)
  7. `ATH_07_ROTARY_TRIM_WHEEL` (Matte Black Diamond Knurled Front-Side Wheel)
  8. `ATH_08_TRIM_RATCHET_PAWL` (Compliant Acoustic Ratchet Spring)
  9. `ATH_09_THROTTLE_SLIDER` (Linear Slider Tab with Dovetail Carriage & Afterburner Gate)
  10. `ATH_10_DUAL_TRIGGER` (Dual-Stage Index Finger Trigger)
- Update all parametric dimensions, DFAM tolerances, kinematics joints, slicing orientations, and assembly sequences.

---

## Verification Plan

### Manual & Visual Verification
1. Compare new renders side-by-side with [`prototype1_aero_throttle_1787157922526.jpg`](file:///C:/Users/chuda/.gemini/antigravity-ide/brain/5324f30b-bc16-4635-a890-31f0949b9622/prototype1_aero_throttle_1787157922526.jpg) to ensure 100% aesthetic and component placement accuracy.
2. Confirm both `Aero Throttle CAD Specification.md` and `Aero_Throttle_CAD_Design_Specification.md` contain accurate references, clear markdown formatting, Mermaid diagrams, and consistent engineering numbers.
