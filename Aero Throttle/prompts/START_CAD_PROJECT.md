# Claude Start Prompt - Phase 1: Design Specification

You are the design architect for a new parametric 3D CAD project.

PROJECT:
Aero-Throttle — HOTAS Flight Controller Parametric Fidget Toy (Prototype 01)

OBJECTIVE:
Design and manufacture a 100% 3D-printable, zero-fastener, zero-metal-spring, zero-adhesive mechanical fidget device inspired by modern fighter jet HOTAS (Hands On Throttle And Stick) avionics cockpit controls. The assembly consists of 10 modular snap-fit components housing 6+ distinct tactile fidget mechanisms powered completely by integral compliant mechanisms (cantilever leaf springs, 3D serpentine flexures, bi-stable over-center cams, and acoustic ratchet pawls).

REFERENCE:
- Design PRD & Specifications: `Aero Throttle/idea/Aero Throttle CAD Design Specification.md` (Version 2.0)
- Design Concept & Portfolio: `Aero Throttle/idea/Fidget Toy Prototypes Portfolio.md` (Prototype 1)
- Visual Renders & Showcase:
  - Hero & Exploded Technical CAD Showcase: `C:/Users/chuda/.gemini/antigravity-ide/brain/293b7304-2725-4fe3-8bf9-53c688c7c8d4/aero_throttle_hero_1787163721644.jpg`
  - Original Concept Sketch: `C:/Users/chuda/.gemini/antigravity-ide/brain/5324f30b-bc16-4635-a890-31f0949b9622/prototype1_aero_throttle_1787157922526.jpg`
- Component Breakdown (10 Modular 3D-Printed Parts):
  1. `ATH_01_UPPER_CHASSIS`: Olive Drab Green Upper Avionics Body with top spherical gimbal socket, side dovetail throttle rail with afterburner ramp, forward-lower trim wheel cavity with integral ratchet pawl, and 4x bottom snap hooks.
  2. `ATH_02_LOWER_GRIP_SHELL`: Matte Black Ergonomic Handle with 108° rake angle, 3 anatomical finger grooves, 10 tactical ribs, trigger trunnion sockets, and stage-2 break stop bar.
  3. `ATH_03_FRONT_BEZEL_FACEPLATE`: Matte Black Rectangular Faceplate with central square button guide, top hinge stanchions, bi-stable cam leaf spring, and rear locking snap barbs.
  4. `ATH_04_MISSILE_SAFETY_GUARD`: Vibrant Red or Matte Black Flip-Up Protective Hood with integral snap hinge pins and dual-flat over-center cam.
  5. `ATH_05_FIRE_BUTTON_PLUNGER`: Vibrant Red 10.5mm Square Button Head with debossed "FIRE" text, retaining flange, and integrated 3D continuous S-curve serpentine spring.
  6. `ATH_06_4WAY_HAT_SWITCH`: Matte Black Stepped Pyramidal Thumb Cap with ⌀7.5mm hemisphere gimbal and 4-quadrant orthogonal star flexure spring arms.
  7. `ATH_07_ROTARY_TRIM_WHEEL`: Matte Black ⌀22.0mm Diamond Knurled Wheel with 20-tooth internal symmetric ratchet ring.
  8. `ATH_08_THROTTLE_SLIDER`: Matte Black Dovetail Slide Carriage with ribbed thumb tab and cantilever leaf spring with ⌀2.4mm rounded detent follower.
  9. `ATH_09_DUAL_TRIGGER`: Matte Black Ergonomic Index Trigger with ⌀3.8mm pivot trunnion, Stage-1 soft take-up flexure beam, and Stage-2 crisp break tooth.
  10. `ATH_10_ALIGNMENT_KEYS`: Matte Black Dual Shear-Locking Alignment Dowels (Qty 2).

TARGET MANUFACTURING METHOD:
FDM / FFF 3D Printing (100% Support-Free, single/multi-material bed layouts)

TARGET MATERIAL:
PLA / PLA+ (primary for high-stiffness spring return and acoustic clicks) or PETG / ABS / ASA (for high fatigue life)

TARGET SIZE:
Length (X): 86.0 mm
Height (Y): 72.0 mm
Width / Thickness (Z): 26.5 mm
Total Mass Target: ~58 grams (at 25% Gyroid infill in PLA+/PETG)

PRIMARY DESIGN REQUIREMENTS:
1. Zero-Hardware Compliant Assembly: 100% 3D printed with zero metal springs, screws, pins, bearings, or adhesives. All retention via integral snap-fit hooks, alignment keys, and captive trunnions.
2. 6+ Distinct High-Tactility Mechanisms:
   - Linear Throttle Slider: 28.0 mm total stroke along 45° dovetail track (0–23.8 mm smooth glide @ 0.8 N; 23.8–28.0 mm afterburner gate break requiring +3.5 N force).
   - 4-Way Tactile Hat Switch: ±14.0° omnidirectional deflection with 4-quadrant star flexure springs for cardinal tactile snaps and immediate 2.8 N auto-centering return.
   - Forward-Lower Rotary Trim Wheel: ⌀22.0 mm diamond-knurled rotor with internal 20-tooth ratchet and cantilever pawl delivering 48 dBA bi-directional clicks.
   - Flip-Up Missile Safety Guard: Bi-stable over-center cam with positive spring detents at 0° (closed) and 90° (open vertical).
   - Rectangular Fire Button: 10.5 mm square plunger with 3.5 mm travel stroke powered by an integrated continuous S-curve serpentine spring (3.2 N return).
   - Dual-Stage Index Trigger: 15.0° rotational pull with Stage-1 soft pre-travel (3.0 mm @ 1.6 N) and Stage-2 crisp mechanical break (5.2 N snap).
3. Authentic HOTAS Ergonomics & Aesthetics: Two-tone military color scheme (Olive Drab Green & Matte Black), 108° handle rake angle, palm swell, finger grooves, and tactical debossed markings.
4. 100% Support-Free Printability (DFAM): All overhangs ≤ 45° from vertical, all horizontal holes feature teardrop or chamfered bridging, and all parts have dedicated flat build-plate reference faces.

GEOMETRIC CONSTRAINTS:
1. Chassis Interlock Seam: Continuous 0.80 mm tongue-and-groove alignment lip with 0.15 mm clearance and 4x cantilever snap hooks (3.5 mm width, 1.2 mm barb) + 2x alignment keys (4.0 × 4.0 × 8.0 mm).
2. Dovetail Rail Geometry: 38.0 mm length, 7.0 mm slot width, 45° undercut angle; afterburner detent ramp at 85% stroke (32.3 mm) with 1.10 mm peak lift, 30° incline ramp, and 65° crisp drop-off.
3. Pivot Trunnions & Sockets:
   - Trigger pivot trunnion: ⌀3.8 mm shaft in ⌀4.0 mm frame socket (+0.20 mm diametral running clearance).
   - Trim wheel pivot trunnion: ⌀5.0 mm chassis post in ⌀5.5 mm wheel bore (+0.50 mm diametral running clearance).
   - Missile guard hinge: Dual ⌀2.35 mm snap pins into ⌀2.50 mm stanchion holes (+0.15 mm clearance).
   - Hat switch gimbal: ⌀7.5 mm hemisphere in ⌀8.0 mm spherical cradle (+0.50 mm clearance).
4. Stress Concentration Prevention: Internal fillets minimum R0.60 mm on all structural corners and spring roots.
5. First-Layer Compensation: 0.60 mm × 45° chamfers on all build-plate contact edges to eliminate elephant's foot.

MANUFACTURING CONSTRAINTS:
1. Minimum wall: 2.40 mm for exterior load-bearing walls (6 solid perimeters at 0.40 mm nozzle width); 1.80–2.00 mm for internal partitions.
2. Minimum feature: 0.80 mm for positive structural features; 0.50 mm depth for debossed text ("FIRE", directional arrows).
3. Clearances (Diametral / Planar):
   - Sliding Fit (Dynamic): +0.20 mm gap per side (0.40 mm total diametral).
   - Rotary Running Fit: +0.25 mm gap per side (0.50 mm total diametral).
   - Snap-Fit Interlocking: +0.15 mm clearance with 0.80 mm retention undercut.
   - Static Snug Fit / Alignment: +0.10 mm clearance.
   - Compliant Spring Preload: -0.40 mm to -0.75 mm interference.
4. Maximum unsupported overhang: 45.0 degrees from vertical (100% support-free design).
5. Print Orientation / Layer Alignment: Spring flexures (trigger beam, throttle detent leaf, fire button serpentine coil, star spring arms) oriented parallel to the XY build plane to ensure tensile/bending forces do not stress inter-layer bonds.

PARAMETRIC REQUIREMENTS:
The following must be user-adjustable via named variables in `src/parameters.scad`:
- Global Tolerances: `fit_clearance_sliding` (0.20 mm), `fit_clearance_rotary` (0.25 mm), `fit_clearance_snap` (0.15 mm).
- Chassis Geometry: `chassis_wall_thick` (2.40 mm), `chassis_length` (82.0 mm), `chassis_width` (26.5 mm), `chassis_height` (36.0 mm).
- Ergonomics: `grip_rake_angle` (108.0 deg), `finger_groove_depth` (2.20 mm), `palm_swell_width` (28.0 mm).
- Throttle Slider: `throttle_stroke` (28.0 mm), `afterburner_pos_ratio` (0.85), `afterburner_ramp_angle` (30.0 deg), `afterburner_lift` (1.10 mm).
- Trim Wheel: `trim_wheel_od` (22.0 mm), `ratchet_teeth_count` (20), `ratchet_tooth_depth` (1.10 mm), `pawl_thickness` (1.05 mm).
- Hat Switch: `hat_deflection_deg` (14.0 deg), `hat_cap_od` (17.5 mm), `hat_spring_arm_thick` (0.85 mm), `hat_spring_arm_len` (8.0 mm).
- Fire Button: `fire_btn_size` (10.5 mm), `fire_btn_travel` (3.50 mm), `serpentine_beam_w` (1.10 mm), `serpentine_beam_t` (1.40 mm).
- Dual Trigger: `trigger_travel_deg` (15.0 deg), `trigger_stage1_thick` (0.75 mm), `trigger_stage2_thick` (1.35 mm).
- Printability: `bed_chamfer` (0.60 mm), `internal_fillet_radius` (0.60 mm).

OUTPUT:
- Parametric OpenSCAD source (`src/main.scad`, `src/parameters.scad`, `src/geometry.scad`, and modular part modules in `src/components/`).
- Master Assembly AP242 `.STEP` and high-resolution manifold `.3MF` / `.STL` meshes (chordal deviation ≤ 0.01 mm).
- Automated test and verification scripts (`tests/` & `scripts/validate.py`).

YOUR TASK:

Do NOT write implementation code yet.

Instead:

1. Decompose the design into its 10 individual components and master assembly hierarchy.
2. Identify all explicit constraints (dimensions, fits, clearances, strokes, forces).
3. Identify hidden constraints (elastic deformation limits, inter-part interference during motion, print orientation fatigue, snap hook deflection stress, elephant's foot relief).
4. Define the coordinate system (Global Origin, X=Length/Slide axis, Y=Height/Crown axis, Z=Width/Lateral axis).
5. Define the parametric architecture (parameters.scad hierarchy, derived dimensions, tolerance tables).
6. Determine the geometry-generation algorithm for each component and compliant mechanism.
7. Identify potential geometric failure modes (non-manifold intersections, thin-wall slicing collapse, spring plastic deformation, snap-hook breakage during assembly).
8. Define validation tests.
9. Produce DESIGN_SPEC.md.
10. Produce PARAMETERS.md.
11. Produce design/ALGORITHM.md.

Do not invent missing dimensions.

Clearly mark assumptions as ASSUMPTION.

Clearly mark unresolved questions as OPEN QUESTION.

The result should be sufficiently precise that another engineer can implement it without making design decisions.
