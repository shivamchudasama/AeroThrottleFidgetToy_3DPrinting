# GEOMETRY GENERATION ALGORITHMS — Aero-Throttle (Prototype 01)

**Document status:** Phase 1 — Design Architecture. No implementation code is released here; this document specifies *how* the implementation agent must build each solid.
**Normative inputs:** `DESIGN_SPEC.md` (what to build), `PARAMETERS.md` (from what values).
**Audience:** the CAD implementation engineer (see `AGENTS.md`).

> Read `DESIGN_SPEC.md` §13 first. Five of the six mechanisms in the PRD are re-sized; building from PRD numbers produces parts that yield on first use.

---

## 1. Engine Contract

### 1.1 Engine neutrality
This document is written against an abstract solid-modelling API so it survives the answer to **OQ-9** (OpenSCAD vs CadQuery/OCCT). Every algorithm uses only these operations:

| Abstract op | OpenSCAD | CadQuery / OCCT |
| :-- | :-- | :-- |
| `box(l,w,h)` | `cube` | `Workplane.box` |
| `cyl(d,h)` | `cylinder` | `Workplane.circle().extrude()` |
| `sphere(d)` | `sphere` | `Workplane.sphere` |
| `extrude(profile2d, h)` | `linear_extrude` | `.extrude()` |
| `revolve(profile2d, deg)` | `rotate_extrude` | `.revolve()` |
| `sweep(profile2d, path3d)` | **not available** — see 1.2 | `.sweep()` |
| `fillet(edges, r)` | **not available** — see 1.2 | `.fillet()` |
| `chamfer(edges, c)` | **not available** — see 1.2 | `.chamfer()` |
| `union / difference / intersect` | `union / difference / intersection` | `.union / .cut / .intersect` |
| `hull(a,b)` | `hull` | `.union().convexHull()` |
| `mirror(axis)` | `mirror` | `.mirror` |

### 1.2 The three OpenSCAD gaps and their workarounds
OpenSCAD has no sweep, no fillet and no chamfer operator. Every compliant mechanism in this design needs all three (R0.60 spring roots are load-bearing — see F-01/F-07).

| Gap | Workaround if OpenSCAD is retained | Cost |
| :-- | :-- | :-- |
| `sweep` | `hull()` chain over N transformed copies of the profile; N ≥ 24 per 90° of path | Facet count explodes; chordal error must be checked against V-104 |
| `fillet` at a concave edge | `difference()` with a `hull()` of two cylinders, or `minkowski()` on the 2D profile before extrusion | `minkowski` is O(n²) and routinely non-manifold on non-convex inputs — **forbidden here**, use the 2D-profile fillet in 1.3 |
| `chamfer` | Model it into the 2D profile before extrusion | Free, but only works for prismatic geometry |

**Consequence:** all fillets and chamfers in this design are built **into 2D profiles before extrusion or revolution**, never applied to a finished 3D solid. This is a hard rule (R-G1) — it is what makes the model manifold by construction (F-07) and it is engine-independent.

### 1.3 Profile-level fillet (R-G1)
```
function fillet_polygon(points, r_map):
    # points: ordered 2D polyline; r_map: radius per vertex (0 = sharp)
    for each interior vertex v with radius r > 0:
        a, b = the two adjacent edge directions (unit vectors, pointing away from v)
        half  = angle_between(a, b) / 2
        setback = r / tan(half)
        assert setback < min(len(edge_a), len(edge_b)) / 2      # ASSERT-G1
        p1 = v + a*setback ;  p2 = v + b*setback
        centre = v + normalize(a + b) * (r / sin(half))
        replace v with an arc from p1 to p2 about centre, at fn_curve/4 segments per 90 deg
    return closed polygon
```
Every structural or spring profile passes through this function with `r = internal_fillet_radius` at each concave vertex before extrusion. V-154 checks the result.

### 1.4 Determinism rules (R-G2 … R-G6)
* **R-G2** No random, no time, no floating literals outside `parameters.scad`. Every number in a geometry module is a named parameter or an expression over them.
* **R-G3** Boolean operands must never share a coincident face. Every subtracting solid is grown by `eps = 0.01` along its cut axis (a single named constant). Coincident faces are the dominant source of non-manifold output (F-07).
* **R-G4** No solid is positioned by a literal coordinate. Positions come from the datum expressions in `DESIGN_SPEC.md` §2.4.
* **R-G5** `fn_curve` is set once, globally, and derived so chordal deviation ≤ 0.01 mm at the largest curved radius: `fn_min = ceil(PI / acos(1 - 0.01/r_max))`.
* **R-G6** Every module is a pure function of parameters — calling it twice yields identical geometry.

---

## 2. Source Layout and Module Hierarchy

```
src/
  parameters.scad        # §1-11 of PARAMETERS.md; all derived values; all ASSERTs. NO geometry.
  geometry.scad          # the reusable kernel of §5 below. NO part-specific geometry.
  components/
    ath_01_upper_chassis.scad
    ath_02_lower_grip_shell.scad
    ath_03_front_bezel.scad
    ath_04_missile_guard.scad
    ath_05_fire_button.scad
    ath_06_hat_switch.scad
    ath_07_trim_wheel.scad
    ath_08_throttle_slider.scad
    ath_09_dual_trigger.scad
    ath_10_alignment_key.scad
  main.scad              # assembly, posing, part selection, print-orientation transform
scripts/
  build.py               # drives per-part export
  check_kinematics.py    # V-120..V-126   (new)
  check_clearances.py    # V-130..V-131   (new)
  check_flexures.py      # V-140..V-143   (new)
  check_printability.py  # V-150..V-158   (new)
```

**Dependency rule (R-G7):** `parameters.scad` imports nothing. `geometry.scad` imports only `parameters.scad`. Each component imports only those two. `main.scad` imports components. There are **no** cross-component imports — if two parts share a feature (the seam, the snap pair), that feature lives in `geometry.scad` and both parts call it with opposite `mode` arguments. This is what guarantees a snap hook and its pocket can never drift apart.

### 2.1 The mating-pair idiom (R-G8)
Every interface in `DESIGN_SPEC.md` §9 is generated by **one** module that emits either half:

```
module snap_pair(mode)      // mode = "hook" | "pocket"
module seam_pair(mode)      // mode = "tongue" | "groove"
module key_pair(mode)       // mode = "key" | "socket"
module dovetail_pair(mode)  // mode = "slot" | "tenon"
module trunnion_pair(mode)  // mode = "shaft" | "socket"
```
The clearance is applied **inside** the module, from the named fit class, exactly once. A part never adds its own clearance. V-131 scans for violations.

### 2.2 Part selection and output modes
`main.scad` exposes one variable, `part`, taking `"assembly"`, `"exploded"`, or a part id (`"ATH_01"` …). `build.py` iterates the ten ids for export and uses `"assembly"` for preview renders. Motion posing (§7) applies only when `part == "assembly"`.

---

## 3. Build Order

Parts are generated in dependency order so that any feature shared across the seam is authored once, by its owner, before its consumer needs it.

```
 1. parameters.scad         evaluate all derived values; run all ASSERTs; abort on failure
 2. geometry.scad           kernel modules (§5); no side effects
 3. ATH_01 upper chassis    owns: datums D/E/F/G, rail, trim pocket + pawl, hat cradle,
                            collar, seam tongue, hooks, key sockets
 4. ATH_10 alignment key    trivial; needed by 01 and 02 socket generation
 5. ATH_02 lower grip shell consumes: seam groove, hook pockets, key sockets, trim relief
 6. ATH_03 front bezel      consumes: collar cavity, latch barbs
 7. ATH_04 missile guard    consumes: hinge slot, cam leaf contact
 8. ATH_05 fire button      consumes: bore, shoulder, snout cavity depth
 9. ATH_06 hat switch       consumes: cradle, detent pockets, retention lip
10. ATH_07 trim wheel       consumes: post, snap head, pawl engagement radius
11. ATH_08 throttle slider  consumes: dovetail, channel floor, ramp
12. ATH_09 dual trigger     consumes: cradle sockets, stop bar, leaf anchor
13. main.scad assembly      pose, colour, bounding-box assertions
```

**Rule R-G9:** a part later in this list may read parameters owned by an earlier part but may never redefine them.

---

## 4. Coordinate Handling

### 4.1 Authoring frame
Every part is authored **in the global Y-up design frame** (`DESIGN_SPEC.md` §2.2). No part is authored at its own origin and then moved — the part *is* its position. This makes interference checking trivial (all ten solids are already in assembly coordinates) and eliminates the commonest error class in multi-part CAD: a transform applied to one half of a mating pair and not the other.

### 4.2 Print frame
Export applies one transform per part, from the `print_orient` table (`DESIGN_SPEC.md` §10.4):

```
module to_print_cs(part_id):
    rot = PRINT_ORIENT[part_id].rotation      # e.g. [90, 0, 0]
    rotate(rot) children();
    then translate so that min(print_z) == 0  # computed, not typed
```
`build.py` calls this only for export; preview and validation of the assembly run in the design frame. V-158 verifies each flexure's bending-plane normal is parallel to `print_z` after the transform.

### 4.3 Handedness
```
module handed() { if (handedness == 1) children(); else mirror([0,0,1]) children(); }
```
Applied once, at the top of `main.scad`, wrapping the entire assembly. Never applied per-part (that would mirror text and threads independently). V-162 rebuilds with `handedness = -1`.

---

## 5. Geometry Kernel (`src/geometry.scad`)

Thirteen reusable generators. Every part is assembled from these; a part module that draws primitive geometry directly is a defect.

### 5.1 `bore(d, h, axis, teardrop)` — the only way a round hole is made
```
d_eff = d + hole_comp                       # FDM shrink comp, applied here and nowhere else
if teardrop and axis is horizontal in print CS and d > 3.00:
    profile = union(circle(d_eff/2),
                    triangle apex at +print_z, half-angle 45 deg, tangent to the circle)
else:
    profile = circle(d_eff/2)
extrude(profile, h + 2*eps) translated by -eps along axis      # R-G3
```
Satisfies P-10/V-156 by construction.

### 5.2 `chamfered_prism(profile2d, h, c_bottom, c_top)`
Chamfers are produced by lofting the profile to an offset copy, not by cutting:
```
lower = offset(profile2d, -c_bottom)
upper = offset(profile2d, -c_top)
solid = hull(extrude(lower, eps) at z=0, extrude(profile2d, eps) at z=c_bottom)
      + extrude(profile2d, h - c_bottom - c_top) at z=c_bottom
      + hull(extrude(profile2d, eps) at z=h-c_top, extrude(upper, eps) at z=h)
```
Used for every build-plate contact face with `c_bottom = bed_chamfer` (P-9/V-155).

### 5.3 `swept_solid(profile2d, path3d, twist_fn)`
```
n = max(24, ceil(path_length / 0.5))            # 0.5 mm max segment, R-G5
for i in 0 .. n-2:
    hull( place(profile2d, path[i],   frame(path,i)),
          place(profile2d, path[i+1], frame(path,i+1)) )
```
`frame()` is a rotation-minimising frame (parallel transport), **not** a Frenet frame — Frenet frames flip at inflection points and produce self-intersecting sweeps (F-07). Used by the grip body, all curved flexures, and the fold arcs.

### 5.4 `dovetail_pair(mode)` — throttle rail and tenon
```
flare  = (dovetail_base_w - dovetail_mouth_w)/2
depth  = flare / tan(dovetail_angle_deg)
slot_profile  = trapezoid(base = dovetail_base_w, top = dovetail_mouth_w, height = depth)
tenon_profile = offset(slot_profile, -fit_clearance_sliding)     # clearance applied ONCE
if mode == "slot":  extrude(fillet_polygon(slot_profile,  r=internal_fillet_radius), rail_len)
if mode == "tenon": extrude(fillet_polygon(tenon_profile, r=internal_fillet_radius), throttle_carriage_len)
```
The 45° flanks are self-supporting in the chassis print orientation (flank is a vertical wall) — P-1 holds without a check.

### 5.5 `detent_ramp(lift, up_deg, down_deg, width)` — the afterburner gate
A piecewise 2D profile extruded across the channel:
```
run_up   = lift / tan(up_deg)
drop_off = lift / tan(down_deg)
pts = [ (0,0), (run_up, lift), (run_up + drop_off, 0) ]
profile = fillet_polygon(pts, r=[0, detent_follower_r*0.5, 0])   # crest radius < follower radius
assert run_up + drop_off < throttle_stroke*(1 - afterburner_pos_ratio)   # ASSERT-11
extrude(profile, width) placed at ramp_apex_x - run_up
```
The crest fillet must be **smaller** than `detent_follower_r`, otherwise the follower rides the crest flat and the break becomes mushy (F-09 analogue).

### 5.6 `folded_leaf(L_dev, b, t, r_fold, n_arms)` — the general folded flexure
This is the single most important kernel module: three mechanisms use it (throttle detent leaf, trim pawl, trigger stage-1 leaf). It converts a **required developed length** into a shape that fits a bounded envelope.

```
arm_len   = (L_dev - (n_arms - 1) * PI * r_fold) / n_arms
assert arm_len > 0                                                    # ASSERT-G2
spacing   = 2 * r_fold                                                # arm centreline pitch
env_x     = arm_len + r_fold + b/2
env_y     = (n_arms - 1) * spacing + b
env_z     = t
assert env_x <= envelope.x and env_y <= envelope.y                    # ASSERT-G3
assert spacing - b >= gap_print_min                                   # arms must not fuse
path = []
for i in 0 .. n_arms-1:
    y = i * spacing
    path += straight segment along +/-x at y, length arm_len          # alternating direction
    if i < n_arms-1: path += semicircular arc of radius r_fold to y + spacing
leaf = swept_solid(rounded_rect(b, t, r=t/2), path)
root = fillet_polygon at the anchor, r = internal_fillet_radius       # R-M1 stress riser
```
**Stiffness model (A-10):** the folded leaf is treated as a straight cantilever of length `L_dev`, with a fold-compliance factor `kappa = 1.00`, valid to about ±15 %. `b` is the designated force-tuning knob because force is linear in `b` while stress is independent of it (R-M4). V-170/V-174 retune `b` after the first article.

**Sizing solve (this is how L_dev, b and t are obtained — none of them is chosen by eye):**
```
given k_req  = F_target / delta
      sigma_allow, E, delta, and the envelope
solve   t / L^2      = 2*sigma_allow / (3*E*delta)        # stress at the limit
        b * t^3/L^3  = 4*k_req / E                        # stiffness at the target
=>      L = ( (4*k_req/E) / (b * (2*sigma_allow/(3*E*delta))^3) )^(1/3)   for a chosen b
then    choose n_arms = smallest integer such that env_x <= envelope.x
```
Both equations are equalities: the design always sits exactly on the stress limit, because any spare stress margin is wasted force capacity (§6.2 energy bound).

### 5.7 `arc_serpentine(n_loops, r_mean, w, t, free_h)` — the fire-button spring
```
pitch = free_h / n_loops
assert pitch - w >= fire_btn_travel/n_loops + gap_print_min           # ASSERT-08
path = []
for i in 0 .. n_loops-1:
    centre = (i*pitch + pitch/2, 0)
    dir    = (i even) ? +1 : -1
    path += semicircle of radius r_mean about centre, sweeping in direction dir
spring = swept_solid(rect(w, t), path)          # w in-plane (bending), t out-of-plane (force)
cap the two ends with the anchor plate and the flange
```
Arcs, not straight segments: developed length `PI*r_mean` per half-loop is what keeps stress at 25.7 MPa instead of 59 MPa (D-06). `t` is the force knob, `r_mean` the stress knob.

### 5.8 `spiral_arm(sweep_deg, r_mean, b, t)` — the hat star spring
```
L_dev = r_mean * sweep_deg * PI/180
path  = polar arc, constant radius r_mean, from theta_0 to theta_0 + sweep_deg, at y = arm_plane_y
arm   = swept_solid(rect(b, t), path)           # b radial, t vertical (bending)
tip   = sphere(2*detent_nose_r) at r = hat_arm_r, blended into the arm end
root  = fillet_polygon(r = internal_fillet_radius) where the arm meets the cap boss
instantiate hat_spring_arm_count copies at 360/count spacing
```
The four arms must **not** intersect: `assert sweep_deg < 360/count + 90` for a nested spiral, or offset alternate arms in Y. At the default 150° sweep with 4 arms the spirals nest at different radii — verify with V-102.

### 5.9 `internal_ratchet(n_teeth, pitch_r, depth)` — the trim wheel ring
```
tooth_pitch = 2*PI*pitch_r / n_teeth
incl_angle  = 2*atan(tooth_pitch / (2*depth))              # derived, = 90 deg (D-05)
assert pitch_r - depth/2 - trim_bore_d/2 >= feature_min     # ASSERT-05 web check
tooth = fillet_polygon(isoceles triangle(base=tooth_pitch, height=depth),
                       r=[0.15, 0.15, 0.15])                # tip and root relief
ring  = difference(cyl(2*(pitch_r+depth/2)), cyl(2*(pitch_r-depth/2)))
teeth = for i in 0..n_teeth-1: rotate(i*360/n_teeth) place tooth pointing inward at pitch_r
ratchet = ring - teeth
```
Symmetric teeth: bi-directional clicking is a requirement, and a 90° symmetric tooth is far less prone to skipping than the PRD's 60° form.

### 5.10 `diamond_knurl(od, width, n_facets, depth, helix_deg)`
```
cutter = extrude(triangle(base=2*depth*tan(helix_deg), height=depth), width*1.5)
for i in 0..n_facets-1:
    rotate(i*360/n_facets) about the wheel axis, twisted +helix_deg -> subtract
    rotate(i*360/n_facets) about the wheel axis, twisted -helix_deg -> subtract
```
Facet pitch `PI*od/n_facets = 2.16 mm` at the defaults — comfortably above the 0.4 mm nozzle (P-5). Knurl is cut **after** the ratchet ring so the two never interact.

### 5.11 `snap_pair(mode, lead_deg, return_deg)` — hooks, barbs, mushroom heads
```
L_min = sqrt(3*y*t / (2*strain_assembly_max))
assert L >= L_min                                            # ASSERT-15 / R-M3
hook  = extrude(fillet_polygon(beam profile, r=internal_fillet_radius), b)
      + barb wedge: lead-in face at lead_deg, return face at return_deg
pocket = offset(hook envelope, +fit_clearance_snap) + retention ledge of snap_undercut
```
`return_deg = 0` for permanent joints (bezel barbs, trim head, button flange), `45` for serviceable ones. The `L_min` assertion is what catches F-04 — two features in this design failed it at their first-guess lengths.

### 5.12 `seam_pair(mode)` — tongue and groove around a non-convex perimeter
```
perimeter = 2D outline of the chassis at Y=0, clipped to X <= seam_x_max,
            with the trim window subtracted                 # the seam is NOT a closed rectangle
tongue = extrude(offset(perimeter, -wall_exterior + seam_tongue_thick/2) as a ribbon
                 of width seam_tongue_thick, height seam_tongue_height)
         with a 45 deg lead-in of seam_lead_in on the free edge
groove = extrude(same ribbon, offset outward by fit_clearance_snap,
                 width seam_groove_w, depth seam_groove_d)
```
The perimeter is **interrupted** by the trim wheel window (§8.1 feature 14). The tongue must terminate with a filleted end face on each side of the window, not run through it — a tongue crossing a hole is the classic non-manifold generator here.

### 5.13 `deboss(text_or_shape, depth, face)`
```
cut = extrude(shape, depth + eps) oriented normal to face, sunk depth into the solid
assert depth >= deboss_depth and stroke_width >= feature_min      # P-5, P-6
```
Applied to "FIRE" on ATH_05, the four directional arrows on ATH_06, and the throttle scale ticks. Debossed (never embossed) so no feature can be knocked off in handling.

---

## 6. Per-Part Generation Algorithms

Each part is built as: **outer envelope → structural subtractions → mating features → compliant features → printability treatment.** Compliant features are added last so their fillet roots are never clipped by a later boolean (F-07).

### 6.1 ATH_01_UPPER_CHASSIS
```
 1  profile_xy = chassis outline in XY: rect(chassis_length, chassis_height)
                 - crown chamfers (crown_chamfer, 45 deg, both top corners)
                 - front-lower chamfer from (chassis_length, front_lower_chamfer) to
                   (chassis_length - front_lower_chamfer, 0)
 2  shell = extrude(fillet_polygon(profile_xy), chassis_width) centred on Z=0
 3  cavity = offset(profile_xy, -wall_exterior) extruded (chassis_width - 2*wall_exterior),
             open at Y=0;  shell -= cavity
 4  collar: add box(collar_w, collar_h, collar_depth) at (collar_x0, bezel_center_y, 0)
            - internal cavity: X[snout_cavity_rear_x, collar_x0] section 11.90 x 6.20
                               X[collar_x0, chassis_front_x] section 16.40 x 14.40
            - latch pockets via snap_pair("pocket") x2
 5  hat cradle: subtract sphere(hat_cradle_d) at L
                subtract cyl(hat_recess_d, hat_recess_depth) from datum E
                subtract cone relief at hat_recess_relief_deg from the recess floor
                subtract 4x detent pockets at hat_arm_r, 90 deg apart
                add retention lip: ring at r=8.00, 1.20 undercut, 4x 40 deg bayonet gaps
 6  throttle rail: subtract channel box(rail_len, dovetail_base_w + 4, rail_channel_depth)
                   from flank F at rail_center_y
                   subtract dovetail_pair("slot") at the channel floor
                   add detent_ramp() on the channel floor at ramp_apex_x
                   add rear lead-in chamfer and forward hard stop
 7  trim pocket:  subtract cyl(trim_pocket_d, trim_pocket_depth) on axis K from flank F
                  subtract trim window through datum A (16.00 x 8.00 at X=61)
                  add snap post: cyl(trim_post_d, trim_post_len) + mushroom head
                                 + 4 relief slots of trim_snap_slot_w
 8  ratchet pawl: folded_leaf(pawl_len, pawl_width, pawl_thickness, r_fold=1.20, n_arms=2)
                  anchored on the pocket's forward wall, tip nose at r = ratchet_pitch_r
                  with pawl_preload interference
 9  seam:        seam_pair("tongue") around the clipped perimeter
10  snaps:       snap_pair("hook", 30, 45) x4 at snap_hook_stations_x, +/-snap_hook_z
11  keys:        subtract key_pair("socket") x2 at key_stations_x
12  printability: bed chamfer on the whole Y=0 perimeter via chamfered_prism
```
**Ordering trap:** step 7's window and step 9's tongue interact. Generate the tongue from a perimeter that already has the window subtracted (§5.12), never subtract the window from a finished tongue.

### 6.2 ATH_02_LOWER_GRIP_SHELL
```
 1  tray = extrude(chassis profile clipped to X <= seam_x_max, chassis_width),
           Y from 0 down to grip root; hollowed to wall_exterior
 2  grip = swept_solid(section, path along grip_axis_dir from (grip_root_x,0) for grip_axial_len)
           section morphs root (grip_root_depth x chassis_width) -> butt (grip_butt_depth x 25.0)
           with palm swell peaking at 60 % of axial length, width palm_swell_width
           assert palm_swell_width <= chassis_width                       # ASSERT-03
 3  body = hull-blend(tray, grip) with internal_fillet_radius at the junction
 4  finger grooves: subtract 3x cyl(finger_groove_r) swept across the grip front,
                    depth finger_groove_depth, pitch finger_groove_pitch
 5  traction ribs: subtract 10x rib_width x rib_depth grooves at rib_pitch
 6  trigger cradle: trunnion_pair("socket") x2 on axis J, with cradle mouth
                    trigger_cradle_mouth_w and spring walls trigger_cradle_wall_len
 7  stop bar + over-travel shelf + stage-1 leaf anchor pad (14.60 wide)
 8  seam_pair("groove"); snap_pair("pocket") x4; key_pair("socket") x2
 9  trim relief pocket (grip_relief_len x grip_relief_w x grip_relief_depth) at X=61
10  bed chamfer on the Y=0 perimeter (this is the build face, printed rim-down)
```

### 6.3 ATH_03_FRONT_BEZEL_FACEPLATE
```
 1  body = chamfered_prism(rect(bezel_w, bezel_h), bezel_depth, c=bezel_chamfer)
 2  subtract rear collar cavity (bezel_cavity_w x bezel_cavity_h x collar_depth)
 3  subtract guide bore: square fire_btn_bore through, with 0.60 x 45 lead-in
 4  add retaining shoulder: 1.50 ledge -> rear pocket btn_shoulder_pocket
 5  subtract guard recess (16.00 x 20.00 x guard_recess_depth) in the front face
 6  add hinge stanchions x2: guard_stanchion_len x guard_stanchion_t, bore guard_pin_hole_d,
     with a radial snap-entry slot guard_hinge_slot_w opening forward
 7  add bi-stable cam leaf: straight cantilever guard_cam_leaf_len x _w x _t,
     root filleted, free end bearing on the guard cam at guard_cam_base_r
 8  add snap_pair("hook", 30, 0) x2  -> permanent barbs, bezel_barb_len long
 9  bed chamfer on the front face (build face)
```

### 6.4 ATH_04_MISSILE_SAFETY_GUARD
```
 1  hood = chamfered_prism(rect(guard_hood_w, guard_hood_l), guard_hood_h) hollowed to guard_wall
 2  add hinge bosses + pins: cyl(guard_pin_d, guard_pin_len) outward, 30 deg lead-in
 3  add cam: revolve a dual-flat profile about the hinge axis --
     r(theta) = guard_cam_base_r                      for theta in [-8, +8]      (flat A, 0 deg rest)
              = guard_cam_base_r + guard_cam_lobe     for theta near 45 deg      (crest)
              = guard_cam_base_r                      for theta in [82, 98]      (flat B, 90 deg rest)
     blended with fillet_polygon so dr/dtheta is continuous (a step here is a broken leaf)
 4  add over-travel stop face at guard_overtravel_deg
 5  add lift tab
```
Both rest positions must be **energy minima with the leaf undeflected**; the only deflection in the cycle is at the crest. Verify `sigma(crest) <= sigma_allow_cyclic` and `sigma(rest) == 0` (R-M2 satisfied by construction).

### 6.5 ATH_05_FIRE_BUTTON_PLUNGER
```
 1  head = chamfered_prism(square(fire_btn_size), fire_btn_head_t, c=0.80)
 2  deboss("FIRE", deboss_depth) on the head front face
 3  flange = box(fire_btn_flange, fire_btn_flange, fire_btn_flange_t) behind the head
 4  hard-stop bosses x2 on the flange rear, height set so contact occurs at fire_btn_travel
     assert serpentine_work_h - serpentine_solid_h >= fire_btn_stop_reserve   # ASSERT-06
 5  spring = arc_serpentine(serpentine_loops, serpentine_loop_r,
                            serpentine_beam_w, serpentine_beam_t, serpentine_free_h)
 6  anchor plate at the rear, seating on snout_cavity_rear_x
 7  union all; fillet every root at internal_fillet_radius
```

### 6.6 ATH_06_4WAY_HAT_SWITCH
```
 1  cap = stepped pyramid: 3 stacked chamfered_prism discs, hat_cap_od base -> crown,
         total height hat_cap_h, all side walls <= overhang_max_deg from vertical
 2  deboss 4 arrows + 8 radial ribs
 3  ball = sphere(hat_ball_d) at L, unioned to the cap underside via a filleted neck
 4  arms = spiral_arm(hat_arm_sweep_deg, hat_arm_mean_r,
                      hat_spring_arm_width, hat_spring_arm_thick) x hat_spring_arm_count
 5  arm tips: R1.00 detent noses at hat_arm_r
 6  bayonet lugs on the arm roots
 7  assert hat_rim_drop < recess relief at hat_recess_relief_deg                # ASSERT-09
```

### 6.7 ATH_07_ROTARY_TRIM_WHEEL
```
 1  rotor = cyl(trim_wheel_od, trim_wheel_width)
 2  diamond_knurl(...) subtracted from the OD
 3  bore(trim_bore_d, trim_wheel_width) on the axis
 4  counterbore trim_snap_head_d + fit_clearance_snap, depth trim_snap_head_t + 0.10, on +Z
 5  internal_ratchet(ratchet_teeth_count, ratchet_pitch_r, ratchet_tooth_depth)
    subtracted from the -Z face, leaving the hub web (wall_internal) on +Z
 6  bed chamfer on the -Z face (build face)
```

### 6.8 ATH_08_THROTTLE_SLIDER
```
 1  tenon = dovetail_pair("tenon"), length throttle_carriage_len
 2  plate = box(throttle_carriage_len, dovetail_base_w, carriage_plate_t) above the tenon
 3  tab   = chamfered_prism(rect(throttle_tab_len, throttle_tab_h), tab_h_z)
            with tab_ridge_count ridges of tab_ridge_r; outer face at flank_z - tab_recess
 4  leaf  = folded_leaf(throttle_leaf_len, throttle_leaf_width, throttle_leaf_thick,
                        throttle_leaf_fold_r, throttle_leaf_arms)
            pocketed into the plate, anchored at the carriage front,
            follower nose (detent_follower_r) at the free tip
 5  anti-lift lugs x2 at both ends of the tenon
 6  assert guide_ratio >= 1.40                                                # ASSERT-12
```

### 6.9 ATH_09_DUAL_TRIGGER
```
 1  shoe = swept_solid(rib-textured section, arc of trigger_shoe_r) hanging from J
 2  trunnion = trunnion_pair("shaft"), trigger_trunnion_d x trigger_trunnion_len on axis J
 3  stage-1 leaf = folded_leaf(trigger_stage1_len, trigger_stage1_width,
                               trigger_stage1_thick, r_fold=2.00, n_arms=2)
                   curved to follow the grip's inner front wall
 4  stage-2 tooth = cantilever trigger_stage2_len x _width x _thick at trigger_tooth_r from J,
                    gate face at trigger_gate_angle_deg
 5  over-travel face at trigger_travel_deg + trigger_overtravel_deg
 6  retention spur; all roots filleted
```

### 6.10 ATH_10_ALIGNMENT_KEYS
```
key = chamfered_prism(square(key_side), key_len, c_bottom=key_chamfer, c_top=key_chamfer)
    + waist rib 0.30 x 1.00 at mid-length
```

---

## 7. Assembly, Posing and Motion

### 7.1 Pose parameters
`main.scad` exposes one normalised pose variable per DOF, all defaulting to 0 (rest):

| Variable | Range | Maps to |
| :-- | :-- | :-- |
| `pose_throttle` | 0 … 1 | translate `+X * pose * throttle_stroke` |
| `pose_hat_x`, `pose_hat_z` | −1 … +1 | rotate about L by `pose * hat_deflection_deg` |
| `pose_trim_deg` | 0 … 360 | rotate about K |
| `pose_guard` | 0 … 1 | rotate about the bezel hinge by `pose * guard_overtravel_deg` |
| `pose_button` | 0 … 1 | translate `−X * pose * fire_btn_travel` |
| `pose_trigger` | 0 … 1 | rotate about J by `pose * trigger_travel_deg` |
| `explode` | 0 … 1 | translate each part along its assembly vector by `pose * 25 mm` |

Posing is a **transform on the finished solid only**. No part's geometry may depend on a pose variable — a pose that changes geometry would let a check pass at one pose and fail at another for reasons the model hides.

### 7.2 Motion-envelope generation (feeds V-120 … V-126)
```
for each moving part p with DOF set D:
    envelope[p] = union over the sample grid of D of pose(p, sample)
    samples: end points + midpoint of every DOF; diagonals for the 2-DOF hat
for each pair (a, b) of parts that are not joined:
    assert intersection_volume(envelope[a], envelope[b]) == 0
for each pair that is joined by a running fit:
    assert min_distance(a, b) >= its fit class - 0.03
```
Sample counts are fixed by `DESIGN_SPEC.md` §12.3 (3 positions per translational DOF, 4 rotational + 2 diagonals for the hat, 4 for the trigger). `check_kinematics.py` writes a JSON of every measured minimum so a regression shows *which* clearance moved.

### 7.3 Exploded view
Assembly vectors follow the assembly sequence (`DESIGN_SPEC.md` §4.3), so the exploded render is a picture of the build order: ATH_02 along −Y, ATH_03/04/05 along +X, ATH_06 along +Y, ATH_07/08 along +Z, ATH_09 along −Y, keys along −Y. This makes the render a review artefact for `design/VISUAL_REVIEW.md`, not decoration.

---

## 8. Export Pipeline

### 8.1 Per-part export
```
for part_id in ATH_01 .. ATH_10:
    solid = component(part_id)                      # design frame
    solid = to_print_cs(part_id, solid)             # §4.2
    export STL  -> output/stl/{part_id}.stl
    export 3MF  -> output/3mf/{part_id}.3mf         (with the colour from §10.5)
    export STEP -> output/step/{part_id}.step       (see 8.3)
export assembly -> output/stl/ATH_MASTER_ASSEMBLY.stl (design frame, for review only)
export colour-tagged multi-object 3MF -> output/3mf/ATH_MASTER.3mf
```

### 8.2 Tessellation
`fn_curve` is derived from the chordal target, not chosen: `fn_min = ceil(PI / acos(1 - chord_tol/r_max))` with `chord_tol = 0.01` and `r_max = trim_wheel_od/2 = 11.0` gives `fn_min = 74`; the default 96 clears it. Angular tolerance ≤ 1.0° and max edge ≤ 2.0 mm are then satisfied for every radius in the model (V-104). `preview_mode` must be false for any exported build — `build.py` asserts this.

### 8.3 STEP (OQ-9)
`cad_config.json.commands.step_export` is empty and OpenSCAD cannot emit STEP. Until OQ-9 is answered, `build.py` must **fail loudly** on the STEP target rather than silently skipping it. Two resolutions:
* **(a)** Drop the AP242 requirement; ship STL + 3MF. Cheapest, loses PMI and the master assembly deliverable.
* **(b)** Make CadQuery/OCCT the geometry of record (`geometry_engine/exporters/cadquery.py` already exists in this repo) and keep OpenSCAD for fast preview only. **Recommended** — every compliant mechanism needs true fillets at its spring roots (§1.2, F-01/F-07), which OpenSCAD cannot produce without `minkowski`, and `minkowski` is forbidden here.

This is the one decision that must be made **before** any implementation code is written, because it determines the kernel API in §5.

### 8.4 Mass check
```
mass_g = mesh_volume_mm3 * rho_eff_g_mm3          # rho_eff already folds in 25 % gyroid
assert abs(mass_g - mass_target_g) / mass_target_g <= 0.10        # V-176
```

---

## 9. Validation Hooks

Each check script reads the exported meshes plus a machine-readable dump of the derived parameters, so the tests never re-implement the design maths.

```
build.py --dump-parameters -> output/reports/parameters.json
```
This file is the contract between the model and the tests. It carries every derived value from `PARAMETERS.md` §12, every computed stiffness/stress, and the datum stations.

| Script | Reads | Emits | Covers |
| :-- | :-- | :-- | :-- |
| `check_kinematics.py` | 10 STLs + parameters.json | per-pair min distances | V-120 … V-126 |
| `check_clearances.py` | 10 STLs + parameters.json | per-interface measured gap vs §9 table | V-130, V-131 |
| `check_flexures.py` | parameters.json only | sigma/strain per flexure vs allowables | V-140 … V-143 |
| `check_printability.py` | 10 STLs in print CS | overhang, wall, gap, bridge, chamfer report | V-150 … V-158 |

`validation_config.json` must then be filled in — it is currently all-null, so `test_dimensions`, `test_volume` and `test_manifold` all **skip**, and `scripts/validate.py` reports `INCOMPLETE`, not `PASS`. Minimum wiring:
```json
"expected_bounds_mm": [86.0, 72.0, 26.5],
"bounds_tolerance_mm": 0.30,
"require_watertight": true,
"max_connected_components": 1,
"project_checks": {
  "clearances":        {"required": true, "command": ["python","scripts/check_clearances.py"]},
  "features":          {"required": true, "command": ["python","scripts/check_kinematics.py"]},
  "self_intersections":{"required": true, "command": ["python","scripts/check_printability.py","--self-intersect"]}
}
```
Per `AGENTS.md`, none of these thresholds may be relaxed to make a build pass. If a threshold is wrong, the argument for changing it goes in `design/DESIGN_REVIEW.md` first.

---

## 10. Iteration Protocol

### 10.1 The tuning loop
Three parameters are **expected** to change after the first physical article, and only these three:

| Knob | Mechanism | Retuned by | Why it is the right knob |
| :-- | :-- | :-- | :-- |
| `serpentine_beam_t` | fire button | V-171 | force ∝ t, stress independent of t (R-M4) |
| `throttle_leaf_width` | afterburner detent | V-170 | force ∝ b, stress independent of b |
| `trigger_stage1_width` / `trigger_tooth_r` | trigger | V-174 | width sets stage 1, tooth radius sets the break |

Retuning any *length* or *thickness* instead changes stress and invalidates the fatigue case — that is a redesign, not a tune, and it must go back through §7 of `DESIGN_SPEC.md`.

### 10.2 Change discipline (per `CLAUDE.md`)
Every iteration reports: files changed, parameters changed, expected effect, validation performed, remaining issues. One subsystem per iteration. A build that compiles is not a result.

### 10.3 Definition of ready for Phase 2
Implementation may begin when, and only when:
1. **OQ-9 is answered** (§8.3) — determines the kernel API.
2. **OQ-1, OQ-4, OQ-6 are answered** — they change the rail, the seam and the material geometry respectively.
3. `validation_config.json` is populated (§9).
4. `.gitattributes` routes `*.stl`, `*.3mf`, `*.step` to Git LFS — the repo has no commits yet, so this must land **before** the first mesh is committed or those blobs are permanent.

---

## 11. Glossary of Symbols

| Symbol | Meaning |
| :-- | :-- |
| `L`, `L_dev` | beam length; developed (arc/fold) length |
| `b` | beam width — the **force** knob (stress-neutral) |
| `t` | beam thickness in the bending direction — the **stress** knob |
| `d`, `delta` | deflection |
| `k` | stiffness, N/mm |
| `sigma` | max bending stress, MPa |
| `kappa` | fold/curvature compliance factor (A-10, default 1.00) |
| `mu` | friction coefficient |
| datums A/B/C | seam plane, chassis rear face, symmetry plane |
| datums D…L | derived feature datums, `DESIGN_SPEC.md` §2.4 |
| FC-* | fit classes, `DESIGN_SPEC.md` §5 |
| R-M*, R-P*, R-G* | mechanical, printability and geometry rules |
| V-*** | validation tests, `DESIGN_SPEC.md` §12 |
| D-**, A-**, OQ-* | deviations, assumptions, open questions |
