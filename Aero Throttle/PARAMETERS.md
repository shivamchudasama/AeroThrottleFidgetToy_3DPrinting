# PARAMETER DEFINITIONS — Aero-Throttle (Prototype 01)

Registry of every named variable in `src/parameters.scad`. Companion to `DESIGN_SPEC.md` (which explains *why* each value is what it is) and `design/ALGORITHM.md` (which explains *how* the geometry is built from them).

**Rules that govern this file**

1. A value appears **once**. If it can be computed, it belongs in §12 (Derived), never in §1-§11.
2. Every clearance comes from a fit class in §2. A literal gap anywhere in the source is a defect (V-131).
3. Every parameter carries a valid range. `tests/test_parametric_extremes.py` rebuilds at both ends (V-160).
4. Values marked **[D-nn]** were changed from PRD v2.0; see `DESIGN_SPEC.md` §13 for the reason. Values marked **[A-nn]** are assumptions; see §14.
5. Units: mm, deg, N, N·mm, MPa, g. Identifiers carry `_deg`, `_n`, `_mpa`, `_g` suffixes where they are not mm.

---

## 1. Global configuration and material

| Parameter | Units | Default | Valid range | Derived from | Purpose |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `handedness` | - | +1 | {-1, +1} | - | +1 = mechanisms on +Z flank (right hand). -1 mirrors the whole assembly about Z=0 (V-162). |
| `material` | - | "PLA_PLUS" | {"PLA_PLUS","PETG"} | - | Selects the property block below. |
| `E_flex_mpa` | MPa | 3300 | 1800 … 3600 | `material` | Flexural modulus; drives every spring force. **[A-09]** |
| `sigma_y_mpa` | MPa | 55 | 40 … 70 | `material` | Flexural yield. |
| `sigma_allow_cyclic_mpa` | MPa | 25 | 15 … 30 | `0.45 * sigma_y_mpa` | Working-stress limit, 10⁴ cycles (R-M1). |
| `sigma_allow_sustained_mpa` | MPa | 8 | 5 … 12 | `0.15 * sigma_y_mpa` | Creep limit for preloaded flexures (R-M2). |
| `strain_assembly_max` | - | 0.015 | 0.010 … 0.030 | `material` | One-time snap-fit strain limit (R-M3). |
| `mu_pla` | - | 0.30 | 0.20 … 0.45 | - | Printed-plastic friction coefficient. **[A-08]** |
| `rho_eff_g_mm3` | g/mm³ | 0.00042 | 0.00030 … 0.00060 | infill | Effective density for the mass check (V-176). **[A-14]** |
| `fn_curve` | - | 96 | 32 … 256 | - | Facet count for curved surfaces; must satisfy chordal deviation ≤ 0.01 mm at the largest radius (V-104). |
| `preview_mode` | bool | false | - | - | Low-`$fn` fast preview; must never be true for an export build. |

## 2. Fit classes and tolerances

| Parameter | Units | Default | Valid range | Derived from | Purpose |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `fit_clearance_sliding` | mm/side | 0.20 | 0.10 … 0.35 | - | FC-SLIDE: dovetail flanks, fire-button bore. |
| `fit_clearance_rotary` | mm/side | 0.25 | 0.15 … 0.40 | - | FC-ROTARY: trim bore, hat gimbal. |
| `fit_clearance_snap` | mm/side | 0.15 | 0.08 … 0.30 | - | FC-SNAP: hooks, barbs, seam. |
| `fit_clearance_static` | mm/side | 0.10 | 0.05 … 0.20 | - | FC-STATIC: keys, locating ribs. |
| `fit_clearance_pivot` | mm/side | 0.10 | 0.05 … 0.20 | - | FC-PIVOT: trigger trunnion, guard pins. **[D-03]** |
| `hole_comp` | mm (dia) | 0.10 | 0.00 … 0.25 | printer | FDM hole-shrinkage compensation, applied once in `bore()`. |
| `wall_exterior` | mm | 2.40 | 1.60 … 3.60 | - | Load-bearing exterior wall (6 perimeters at 0.40). |
| `wall_internal` | mm | 1.80 | 1.20 … 2.60 | - | Internal partitions and bosses. |
| `feature_min` | mm | 0.80 | 0.60 … 1.20 | - | Minimum positive feature (P-5). |
| `deboss_depth` | mm | 0.50 | 0.30 … 0.90 | - | Text and arrow deboss depth (P-6). |
| `gap_print_min` | mm | 0.40 | 0.30 … 0.60 | - | Minimum gap between separate walls (P-7). |
| `internal_fillet_radius` | mm | 0.60 | 0.40 … 1.50 | - | Minimum internal corner / spring root fillet (P-8). |
| `bed_chamfer` | mm | 0.60 | 0.30 … 1.00 | - | Build-plate edge chamfer, elephant's-foot relief (P-9). |
| `overhang_max_deg` | deg | 45.0 | 30.0 … 50.0 | - | Support-free overhang limit (P-1). |
| `bridge_max` | mm | 12.0 | 6.0 … 20.0 | - | Maximum unsupported bridge (P-11). |

## 3. Master envelope

| Parameter | Units | Default | Valid range | Derived from | Purpose |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `overall_length` | mm | 86.0 | 70 … 110 | **derived, §12.1** | Assembly X extent — an assertion target, not an input. |
| `overall_height` | mm | 72.0 | 55 … 95 | **derived, §12.1** | Assembly Y extent. |
| `chassis_length` | mm | 82.0 | 65 … 100 | - | Upper chassis X extent (datum B → D). |
| `chassis_height` | mm | 36.0 | 26 … 48 | - | Upper chassis Y extent (datum A → E). |
| `chassis_width` | mm | 26.5 | 20 … 34 | - | Assembly Z extent; nothing may exceed it. |
| `grip_drop` | mm | 30.0 | 22 … 45 | - | Grip Y extent below datum A. **[A-01][D-13]** |
| `mass_target_g` | g | 58.0 | 40 … 80 | - | Mass acceptance target (V-176). |

## 4. Upper chassis (ATH_01)

| Parameter | Units | Default | Valid range | Derived from | Purpose |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `crown_chamfer` | mm | 3.00 | 1.0 … 6.0 | - | 45° chamfer leg on both top edges. |
| `front_lower_chamfer` | mm | 12.00 | 6.0 … 18.0 | - | 45° nose chamfer leg, from (82, 12) to (70, 0). Sets where the seam perimeter ends. |
| `collar_w` | mm | 18.00 | 12 … 24 | - | Snout collar Z extent. |
| `collar_h` | mm | 20.00 | 14 … 28 | - | Snout collar Y extent. |
| `collar_depth` | mm | 10.00 | 6 … 14 | **derived, §12.2** | Collar X extent = `bezel_depth - bezel_protrusion`. |
| `snout_cavity_rear_x` | mm | 66.00 | 60 … 74 | **derived, §12.4** | Rear wall of the fire-button spring bore. **[D-06]** |
| `latch_pocket_w` | mm | 3.50 | 2.5 … 5.0 | - | Bezel latch pocket width. |
| `latch_pocket_h` | mm | 1.80 | 1.2 … 2.6 | - | Bezel latch pocket height. |

## 5. Lower grip shell (ATH_02) and ergonomics

| Parameter | Units | Default | Valid range | Derived from | Purpose |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `grip_rake_angle_deg` | deg | 108.0 | 95 … 120 | - | Angle from +X to the grip's downward centreline, measured through −Y. |
| `grip_root_x` | mm | 30.00 | 20 … 45 | - | X station where the grip centreline meets datum A. |
| `grip_root_depth` | mm | 26.00 | 20 … 32 | - | Grip section, local fore-aft, at the root. **[A-11]** |
| `grip_butt_depth` | mm | 24.00 | 18 … 30 | - | Grip section, local fore-aft, at the butt. **[A-11]** |
| `palm_swell_width` | mm | 26.10 | 20 … 26.5 | ≤ `chassis_width` | Max grip Z width. **[D-02]** — was 28.0, which broke the width budget. |
| `finger_groove_count` | - | 3 | 2 … 4 | - | Anatomical scallops. |
| `finger_groove_depth` | mm | 2.20 | 1.2 … 3.5 | - | Scallop depth. |
| `finger_groove_r` | mm | 11.00 | 8 … 16 | - | Scallop radius. |
| `finger_groove_pitch` | mm | 12.00 | 9 … 16 | - | Scallop spacing along the grip axis. **[A-11]** |
| `rib_count` | - | 10 | 6 … 16 | - | Traction ribs. |
| `rib_width` | mm | 1.20 | 0.8 … 2.0 | - | Rib width. |
| `rib_depth` | mm | 0.80 | 0.4 … 1.5 | - | Rib recess depth. |
| `rib_pitch` | mm | 2.20 | 1.6 … 3.5 | - | Rib spacing. |

## 6. Front bezel (ATH_03), guard (ATH_04), fire button (ATH_05)

| Parameter | Units | Default | Valid range | Derived from | Purpose |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `bezel_w` | mm | 22.00 | 16 … 28 | - | Bezel Z extent. |
| `bezel_h` | mm | 24.00 | 18 … 32 | - | Bezel Y extent. |
| `bezel_depth` | mm | 12.00 | 8 … 18 | - | Bezel X extent. |
| `bezel_protrusion` | mm | 2.00 | 0.5 … 5.0 | - | How far the bezel stands proud of datum D. **[A-02]** |
| `bezel_center_y` | mm | 22.00 | 14 … 28 | - | Bezel centreline height. **[A-03][D-14]** |
| `bezel_chamfer` | mm | 1.50 | 0.8 … 3.0 | - | Perimeter chamfer leg, 45°. |
| `bezel_barb_len` | mm | 10.50 | 8 … 14 | ≥ §12.6 strain limit | Snap barb length. **[D-12]** |
| `bezel_barb_w` | mm | 2.80 | 2.0 … 4.0 | - | Snap barb width. |
| `bezel_barb_t` | mm | 1.40 | 1.0 … 2.0 | - | Snap barb thickness. |
| `snap_undercut` | mm | 0.80 | 0.4 … 1.2 | - | Retention undercut, all permanent snaps. |
| `guard_hood_w` | mm | 15.00 | 10 … 20 | - | Guard Z extent. |
| `guard_hood_l` | mm | 19.00 | 14 … 26 | - | Guard length along the face. |
| `guard_hood_h` | mm | 4.50 | 3.0 … 7.0 | - | Guard hood height (contributes to the X chain). |
| `guard_recess_depth` | mm | 2.50 | 1.0 … 4.0 | - | Pocket in the bezel face that swallows the hood. **[A-02]** |
| `guard_wall` | mm | 1.60 | 1.2 … 2.4 | - | Hood wall. |
| `guard_pin_d` | mm | 2.35 | 1.8 … 3.2 | - | Hinge pin diameter. |
| `guard_pin_len` | mm | 3.00 | 2.0 … 4.5 | - | Hinge pin length. |
| `guard_open_deg` | deg | 90.0 | 80 … 110 | - | Open detent angle. |
| `guard_overtravel_deg` | deg | 100.0 | 90 … 120 | - | Hard stop. |
| `guard_cam_lobe` | mm | 0.80 | 0.4 … 1.4 | - | Over-centre lobe eccentricity. |
| `guard_cam_base_r` | mm | 3.20 | 2.0 … 5.0 | - | Cam base radius. |
| `guard_cam_leaf_len` | mm | 12.00 | 10 … 18 | ≥ §12.6 stress limit | Bi-stable leaf length in the bezel. |
| `guard_cam_leaf_w` | mm | 6.00 | 3 … 10 | **OQ-3** | Leaf width — the only force term still unconstrained. |
| `guard_cam_leaf_t` | mm | 0.90 | 0.7 … 1.3 | - | Leaf thickness. |
| `fire_btn_size` | mm | 10.50 | 8 … 14 | - | Square head side. |
| `fire_btn_head_t` | mm | 3.60 | 2.5 … 5.0 | - | Head thickness. |
| `fire_btn_proud` | mm | 3.00 | 2.0 … 4.5 | < `guard_hood_h - guard_wall` | Head height above the guard recess floor at rest. **[A-16]** |
| `fire_btn_travel` | mm | 3.50 | 2.0 … 5.0 | - | Working stroke. |
| `fire_btn_flange` | mm | 12.50 | 11 … 15 | > `fire_btn_bore` | Retaining flange side. |
| `fire_btn_flange_t` | mm | 1.20 | 0.8 … 2.0 | - | Flange thickness. |
| `fire_btn_force_n` | N | 3.20 | 1.5 … 5.0 | - | Return-force target at full stroke. |
| `serpentine_loops` | - | 6 | 4 … 9 | - | Half-loops in series. **[D-06]** |
| `serpentine_loop_r` | mm | 5.00 | 3.5 … 6.5 | - | Mean arc radius. **[D-06]** |
| `serpentine_beam_w` | mm | 1.10 | 0.8 … 1.6 | - | In-plane bending thickness. |
| `serpentine_beam_t` | mm | 4.80 | 2.0 … 7.0 | **tuning knob, §12.5** | Out-of-plane depth; the designated force-tuning parameter. **[D-06]** |
| `serpentine_free_h` | mm | 13.50 | 10 … 18 | - | Free height along X. |
| `fire_btn_stop_reserve` | mm | 1.00 | 0.5 … 2.0 | - | Gap between the hard stop and the spring's solid height. |

## 7. Hat switch (ATH_06) and its chassis cradle

| Parameter | Units | Default | Valid range | Derived from | Purpose |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `hat_center_x` | mm | 46.00 | 34 … 58 | - | Gimbal station on the top deck. **[A-04]** |
| `hat_cap_od` | mm | 17.50 | 13 … 22 | - | Cap base diameter. |
| `hat_cap_h` | mm | 11.50 | 8 … 16 | - | Cap height from the base plane to the crown. |
| `hat_cap_protrusion` | mm | 6.00 | 3 … 10 | - | Cap height above datum E; enters the Y chain. **[A-01]** |
| `hat_ball_d` | mm | 7.50 | 5 … 10 | - | Gimbal hemisphere diameter. |
| `hat_deflection_deg` | deg | 14.00 | 8 … 20 | - | Tilt limit per axis. |
| `hat_arm_r` | mm | 7.00 | 5 … 8.5 | < `hat_cap_od/2` | Radius at which arm tips act. **[A-13]** |
| `hat_spring_arm_count` | - | 4 | 3 … 6 | - | Star arms. |
| `hat_spring_arm_len` | mm | 17.00 | 12 … 22 | **derived, §12.7** | Developed arm length. **[D-08]** |
| `hat_spring_arm_width` | mm | 4.00 | 2.5 … 6.0 | **tuning knob** | Radial ribbon width; the force term. **[D-08]** |
| `hat_spring_arm_thick` | mm | 0.85 | 0.75 … 1.20 | ≥ `flexure_min` | Bending thickness (along Y). |
| `hat_arm_sweep_deg` | deg | 150.0 | 110 … 200 | - | Spiral sweep. |
| `hat_arm_mean_r` | mm | 6.50 | 5 … 8 | **derived, §12.7** | Spiral mean radius. |
| `hat_detent_depth` | mm | 0.60 | 0.3 … 1.0 | - | Deck detent pocket depth. |
| `hat_detent_flank_deg` | deg | 40.0 | 25 … 55 | - | Detent pocket flank angle. |
| `hat_force_n` | N | 2.80 | 1.5 … 4.5 | - | Self-centring force target. |
| `hat_recess_relief_deg` | deg | 16.0 | ≥ `hat_deflection_deg + 2` | - | Conical relief under the cap rim. |

## 8. Trim wheel (ATH_07), pocket and pawl

| Parameter | Units | Default | Valid range | Derived from | Purpose |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `trim_wheel_center_x` | mm | 61.00 | 52 … 66 | - | Wheel axis station. **[A-05]** |
| `trim_wheel_center_y` | mm | 8.80 | 6 … 12 | **derived, §12.8** | Set by the required rim protrusion below datum A. **[A-05]** |
| `trim_wheel_od` | mm | 22.00 | 16 … 26 | - | Rotor diameter. |
| `trim_wheel_width` | mm | 6.80 | 4 … 9 | - | Rotor Z width. |
| `trim_rim_proud` | mm | 2.20 | 1.2 … 3.5 | - | Rim protrusion below datum A through the underside window. |
| `trim_post_d` | mm | 5.00 | 3.5 … 7 | - | Chassis trunnion post. |
| `trim_pocket_clear_r` | mm | 1.00 | 0.6 … 2.0 | - | Radial pocket clearance. |
| `trim_pocket_clear_z` | mm | 0.60 | 0.3 … 1.2 | - | Axial pocket clearance per face. |
| `trim_snap_head_d` | mm | 6.20 | 5.6 … 7.5 | > `trim_bore_d` | Mushroom retention head. |
| `trim_snap_head_t` | mm | 1.30 | 0.9 … 2.0 | - | Head thickness. |
| `trim_snap_slot_len` | mm | 7.00 | 5 … 9 | **§12.6 strain** | Length of the four post relief slots. |
| `trim_snap_slot_w` | mm | 0.80 | 0.5 … 1.2 | ≥ `gap_print_min` | Slot width. |
| `knurl_facets` | - | 32 | 20 … 48 | - | Diamond knurl count. |
| `knurl_depth` | mm | 0.70 | 0.4 … 1.2 | - | Knurl depth. |
| `knurl_helix_deg` | deg | 45.0 | 30 … 60 | - | Crossed-helix angle. |
| `ratchet_teeth_count` | - | 20 | 12 … 32 | - | Internal ratchet teeth. |
| `ratchet_tooth_depth` | mm | 1.10 | 0.6 … 1.8 | - | Tooth depth. |
| `ratchet_pitch_r` | mm | 7.00 | 5.5 … 8.5 | **§12.8 web check** | Ratchet pitch radius. **[A-12][D-05]** |
| `ratchet_torque_nmm` | N·mm | 12.00 | 6 … 20 | - | Click torque target. |
| `pawl_len` | mm | 17.70 | 13 … 22 | **derived, §12.8** | Pawl developed length. **[D-05]** |
| `pawl_width` | mm | 3.60 | 2.5 … 6.0 | **tuning knob** | Pawl width; the force term. **[D-05]** |
| `pawl_thickness` | mm | 1.05 | 0.8 … 1.5 | - | Pawl bending thickness. |
| `pawl_preload` | mm | 0.40 | 0.20 … 0.75 | ≤ §12.6 creep limit | Radial interference at rest. |

## 9. Throttle (ATH_08) and its chassis rail

| Parameter | Units | Default | Valid range | Derived from | Purpose |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `throttle_stroke` | mm | 28.00 | 12 … 34 | - | Total carriage travel. |
| `throttle_carriage_len` | mm | 15.00 | 10 … 24 | **OQ-1** | Carriage X length. **[D-01]** |
| `rail_start_x` | mm | 3.00 | 2.4 … 8 | ≥ `wall_exterior` | Rail rear end station. |
| `rail_center_y` | mm | 22.00 | 16 … 28 | **§12.9 packaging** | Rail centreline height. **[A-06]** |
| `rail_end_clear` | mm | 0.50 | 0.3 … 1.2 | - | Slack at each rail end. |
| `dovetail_mouth_w` | mm | 7.00 | 5 … 10 | - | Dovetail slot mouth (Y). |
| `dovetail_base_w` | mm | 10.50 | 8 … 14 | > `dovetail_mouth_w` | Dovetail slot base (Y). |
| `dovetail_angle_deg` | deg | 45.0 | 30 … 60 | - | Undercut angle. |
| `rail_channel_depth` | mm | 7.40 | 4 … 10 | **derived, §12.9** | Depth of the flank trough that swallows the carriage and tab. |
| `tab_recess` | mm | 0.40 | 0.2 … 1.0 | - | How far the tab's outer face sits inside datum F. |
| `throttle_tab_len` | mm | 12.00 | 8 … 18 | ≤ `throttle_carriage_len` | Thumb tab X length. |
| `throttle_tab_h` | mm | 8.00 | 5 … 12 | - | Thumb tab Y height. |
| `tab_ridge_count` | - | 4 | 2 … 8 | - | Traction ridges. |
| `tab_ridge_r` | mm | 0.50 | 0.3 … 0.9 | - | Ridge radius. |
| `afterburner_pos_ratio` | - | 0.85 | 0.6 … 0.95 | - | Fraction of stroke at which the gate breaks. |
| `afterburner_lift` | mm | 1.10 | 0.6 … 1.8 | - | Ramp peak lift. |
| `afterburner_ramp_angle_deg` | deg | 30.0 | 15 … 45 | - | Incline angle. |
| `afterburner_drop_angle_deg` | deg | 65.0 | 50 … 80 | - | Drop-off angle. |
| `throttle_glide_force_n` | N | 0.80 | 0.3 … 1.5 | - | Force over the smooth stroke. |
| `throttle_break_force_n` | N | 4.30 | 2.5 … 6.5 | - | Total force at the gate. |
| `throttle_leaf_len` | mm | 28.41 | 20 … 34 | **derived, §12.9** | Detent leaf developed length. **[D-07]** |
| `throttle_leaf_width` | mm | 4.00 | 2.5 … 6.0 | **tuning knob** | Leaf width; the force term (stress-neutral). **[D-07]** |
| `throttle_leaf_thick` | mm | 2.63 | 1.6 … 3.2 | **derived, §12.9** | Leaf bending thickness. **[D-07]** |
| `throttle_leaf_fold_r` | mm | 2.60 | 2.20 … 3.25 | ≥ (`throttle_leaf_width`+`gap_print_min`)/2 | Fold radius; sets arm spacing. |
| `throttle_leaf_arms` | - | 2 | 2 … 4 | **§12.9 envelope fit** | Arms in the folded leaf. |
| `carriage_plate_t` | mm | 4.80 | 3.0 … 6.5 | **derived, §12.9** | Carriage plate thickness; hosts the leaf pocket and its travel. |
| `detent_follower_r` | mm | 1.20 | 0.8 … 2.0 | - | Follower nose radius. |
| `throttle_detent_preload` | mm | 0.45 | 0.20 … 0.75 | ≤ §12.6 creep limit | Leaf preload at rest. **[D-07]** |

## 10. Trigger (ATH_09) and its grip cradle

| Parameter | Units | Default | Valid range | Derived from | Purpose |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `trigger_pivot_x` | mm | 58.00 | 48 … 64 | - | Pivot station. **[A-07]** |
| `trigger_pivot_y` | mm | -4.00 | -10 … 0 | - | Pivot height (below datum A). **[A-07]** |
| `trigger_trunnion_d` | mm | 3.80 | 3.0 … 5.0 | - | Trunnion diameter. |
| `trigger_trunnion_len` | mm | 7.60 | 5 … 10 | - | Trunnion total length. |
| `trigger_shoe_r` | mm | 16.00 | 12 … 22 | - | Finger saddle radius. |
| `trigger_contact_r` | mm | 18.00 | 14 … 24 | - | Radius from pivot to the finger contact point. **[A-07]** |
| `trigger_travel_deg` | deg | 15.00 | 8 … 22 | - | Total rotation. |
| `trigger_stage1_travel` | mm | 3.00 | 1.5 … 5.0 | - | Stage-1 shoe travel. |
| `trigger_stage1_len` | mm | 21.20 | 15 … 26 | **derived, §12.10** | Stage-1 leaf developed length. **[D-09]** |
| `trigger_stage1_width` | mm | 14.60 | 8 … 18 | **tuning knob** | Stage-1 leaf width; the force term. **[D-09]** |
| `trigger_stage1_thick` | mm | 0.75 | 0.60 … 1.10 | ≥ `flexure_min` | Stage-1 bending thickness. |
| `trigger_stage1_force_n` | N | 1.60 | 0.8 … 3.0 | - | Stage-1 force target. |
| `trigger_stage2_len` | mm | 12.20 | 9 … 16 | **derived, §12.10** | Stage-2 tooth beam length. |
| `trigger_stage2_width` | mm | 6.00 | 4 … 9 | **tuning knob** | Stage-2 tooth width. |
| `trigger_stage2_thick` | mm | 1.35 | 1.0 … 1.8 | - | Stage-2 tooth thickness. |
| `trigger_stage2_deflect` | mm | 0.55 | 0.3 … 0.9 | - | Stop-bar interference. |
| `trigger_gate_angle_deg` | deg | 45.0 | 30 … 60 | - | Stop-bar gate flank. |
| `trigger_break_force_n` | N | 5.20 | 3.0 … 8.0 | - | Stage-2 break force target. |
| `trigger_tooth_r` | mm | 9.46 | 6 … 14 | **derived, §12.10** | Radius at which the stage-2 tooth acts. |
| `trigger_overtravel_deg` | deg | 0.60 | 0.2 … 1.5 | - | Rotation past full travel before the hard shelf. |
| `trigger_cradle_mouth_w` | mm | 3.40 | 2.5 … 4.0 | < `trigger_trunnion_d` | Snap-in entry width. |
| `trigger_cradle_wall_len` | mm | 7.50 | 5 … 12 | **§12.6 strain** | Cradle spring-wall length. |
| `trigger_cradle_wall_t` | mm | 2.00 | 1.5 … 3.0 | - | Cradle spring-wall thickness. |

## 11. Seam, snaps and alignment keys

| Parameter | Units | Default | Valid range | Derived from | Purpose |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `seam_tongue_thick` | mm | 1.20 | 0.8 … 2.0 | - | Tongue thickness. |
| `seam_tongue_height` | mm | 0.80 | 0.5 … 1.5 | - | Tongue step height. |
| `seam_lead_in` | mm | 0.40 | 0.2 … 0.8 | - | 45° lead-in on the tongue. |
| `snap_hook_count` | - | 4 | 2 … 6 | - | Chassis-to-grip hooks. |
| `snap_hook_len` | mm | 15.00 | 11 … 20 | **§12.6 strain** | Hook length. **[A-15]** |
| `snap_hook_w` | mm | 3.50 | 2.5 … 5.0 | - | Hook width. |
| `snap_hook_t` | mm | 1.60 | 1.2 … 2.2 | - | Hook thickness. |
| `snap_barb_depth` | mm | 1.20 | 0.8 … 1.8 | - | Barb radial depth. |
| `snap_lead_angle_deg` | deg | 30.0 | 20 … 40 | - | Insertion lead-in angle. |
| `snap_return_angle_deg` | deg | 45.0 | 0 … 60 | - | Return face; 0 = permanent, 45 = serviceable. |
| `snap_hook_stations_x` | mm[] | [12.0, 46.0] | within [0, 70] | **§12.9 packaging** | Hook X stations (both flanks). |
| `snap_hook_z` | mm | 9.50 | 6 … 11 | - | Hook lateral offset. |
| `key_side` | mm | 4.00 | 3 … 6 | - | Alignment key cross-section. |
| `key_len` | mm | 8.00 | 6 … 12 | - | Alignment key length (straddles datum A). |
| `key_stations_x` | mm[] | [30.0, 58.0] | within [0, 70] | - | Key X stations, on Z = 0. |
| `key_chamfer` | mm | 0.60 | 0.3 … 1.0 | - | Key end lead-in. |
| `flexure_min` | mm | 0.75 | 0.60 … 1.00 | - | Minimum flexure thickness (P-4). |
| `guard_hinge_slot_w` | mm | 2.10 | 1.6 … 2.3 | < `guard_pin_d` | Radial snap-entry slot in the stanchions. |
| `guard_stanchion_len` | mm | 9.00 | 7 … 14 | **§12.6 strain** | Stanchion ear length. |
| `guard_stanchion_t` | mm | 3.20 | 2.4 … 4.5 | - | Stanchion ear thickness. |

---

## 12. Derived Relationships

Everything below is **computed** in `src/parameters.scad`. None of it may be typed as a literal anywhere. Each block shows the formula and its value at the defaults.

### 12.1 Envelope chains
```
overall_length   = chassis_length + bezel_protrusion + (guard_hood_h - guard_recess_depth)   = 86.00
overall_height   = hat_cap_protrusion + chassis_height + grip_drop                           = 72.00
overall_width    = chassis_width                                                             = 26.50
chassis_front_x  = chassis_length                                                            = 82.00
deck_y           = chassis_height                                                            = 36.00
flank_z          = chassis_width / 2                                                         = 13.25
seam_x_max       = chassis_length - front_lower_chamfer                                      = 70.00
```

### 12.2 Bezel and collar
```
bezel_front_x    = chassis_length + bezel_protrusion                       = 84.00
bezel_rear_x     = bezel_front_x - bezel_depth                             = 72.00
collar_depth     = bezel_depth - bezel_protrusion                          = 10.00
collar_x0        = bezel_rear_x                                            = 72.00
bezel_cavity_w   = collar_w + 2*fit_clearance_static                       = 18.20
bezel_cavity_h   = collar_h + 2*fit_clearance_static                       = 20.20
guard_closed_x   = bezel_front_x - guard_recess_depth + guard_hood_h       = 86.00
guard_hinge_x    = bezel_front_x - 1.00                                    = 83.00
guard_hinge_y    = bezel_center_y + bezel_h/2 - 2.00                       = 32.00
guard_inner_clear= guard_hood_h - guard_wall - 0.40                        =  2.50   -- see ASSERT-07
```

### 12.3 Fire button axial stack (all stations measured along +X)
```
fire_btn_bore        = fire_btn_size + 2*fit_clearance_sliding            = 10.90
recess_floor_x       = bezel_front_x - guard_recess_depth                 = 81.50
btn_head_front_x     = recess_floor_x + fire_btn_proud                    = 84.50
btn_head_rear_x      = btn_head_front_x - fire_btn_head_t                 = 80.90
btn_flange_rear_x    = btn_head_rear_x - fire_btn_flange_t                = 79.70
snout_cavity_rear_x  = btn_flange_rear_x - serpentine_free_h - 0.20       = 66.00
btn_shoulder_pocket  = fire_btn_bore + 2*1.50                             = 13.90
```

### 12.4 Serpentine spring (ATH_05)
```
serpentine_len_dev   = PI * serpentine_loop_r                             = 15.708
serpentine_pitch     = serpentine_free_h / serpentine_loops               =  2.250
serpentine_gap       = serpentine_pitch - serpentine_beam_w               =  1.150
serpentine_solid_h   = serpentine_loops*serpentine_beam_w + 2*fire_btn_flange_t = 9.00
serpentine_work_h    = serpentine_free_h - fire_btn_travel                = 10.00
serpentine_footprint = 2*serpentine_loop_r + serpentine_beam_w            = 11.10
I_serp               = serpentine_beam_t * serpentine_beam_w^3 / 12       =  0.5327 mm^4
k_serp               = E_flex_mpa*serpentine_beam_t*serpentine_beam_w^3
                       / (serpentine_loops * serpentine_len_dev^3)        =  0.9066 N/mm
F_serp               = k_serp * fire_btn_travel                           =  3.173 N   (target 3.20)
sigma_serp           = 3*E_flex_mpa*fire_btn_travel*serpentine_beam_w
                       / (serpentine_loops * serpentine_len_dev^2)        = 25.75 MPa
-- force tuning knob (solve for depth from the target):
serpentine_beam_t    = fire_btn_force_n * serpentine_loops * serpentine_len_dev^3
                       / (E_flex_mpa * serpentine_beam_w^3 * fire_btn_travel)   = 4.84 -> 4.80
```

### 12.5 Trim wheel, ratchet and pawl
```
trim_bore_d          = trim_post_d + 2*fit_clearance_rotary               =  5.50
trim_pocket_d        = trim_wheel_od + 2*trim_pocket_clear_r              = 24.00
trim_pocket_depth    = trim_wheel_width + 2*trim_pocket_clear_z           =  8.00
trim_pocket_floor_z  = flank_z - trim_pocket_depth                        =  5.25
trim_wheel_mid_z     = trim_pocket_floor_z + trim_pocket_clear_z + trim_wheel_width/2 = 9.25
trim_post_len        = trim_pocket_depth - trim_pocket_clear_z            =  7.40
ratchet_tooth_pitch  = 2*PI*ratchet_pitch_r / ratchet_teeth_count         =  2.199
ratchet_incl_angle   = 2*atan(ratchet_tooth_pitch/(2*ratchet_tooth_depth))= 89.97 deg
ratchet_tip_r        = ratchet_pitch_r - ratchet_tooth_depth/2            =  6.45
ratchet_root_r       = ratchet_pitch_r + ratchet_tooth_depth/2            =  7.55
ratchet_web          = ratchet_tip_r - trim_bore_d/2                      =  3.70   -- ASSERT-05
ramp_factor_ratchet  = (tan(45)+mu_pla)/(1-mu_pla*tan(45))                =  1.857
pawl_deflect         = pawl_preload + ratchet_tooth_depth                 =  1.500
I_pawl               = pawl_width * pawl_thickness^3 / 12                 =  0.3473 mm^4
k_pawl               = 3*E_flex_mpa*I_pawl / pawl_len^3                   =  0.620 N/mm
F_pawl               = k_pawl * pawl_deflect                              =  0.930 N
torque_ratchet       = F_pawl * ramp_factor_ratchet * ratchet_pitch_r     = 12.09 N.mm  (target 12.0)
sigma_pawl           = 3*E_flex_mpa*pawl_deflect*pawl_thickness/(2*pawl_len^2) = 24.88 MPa
sigma_pawl_rest      = 3*E_flex_mpa*pawl_preload*pawl_thickness/(2*pawl_len^2) =  6.63 MPa
-- length solved from the stress limit, width solved from the torque target:
pawl_len   = sqrt(3*E_flex_mpa*pawl_deflect*pawl_thickness/(2*sigma_allow_cyclic_mpa))  = 17.66 -> 17.70
k_pawl_req = ratchet_torque_nmm/(ramp_factor_ratchet*ratchet_pitch_r*pawl_deflect)      =  0.6153 N/mm
pawl_width = 4*k_pawl_req*pawl_len^3/(E_flex_mpa*pawl_thickness^3)                      =  3.57 -> 3.60
```

### 12.6 Snap-fit assembly strain (R-M3, `strain = 3*y*t/(2*L^2)`)
```
hook_deflect      = snap_barb_depth + fit_clearance_snap  = 1.350
strain_hook       = 3*1.350*snap_hook_t/(2*snap_hook_len^2)              = 0.0144  (1.44 %)  PASS
k_hook            = E_flex_mpa*snap_hook_w*snap_hook_t^3/(4*snap_hook_len^3) = 3.504 N/mm
F_insert_assembly = snap_hook_count * k_hook * hook_deflect * 1.060      = 20.1 N

barb_deflect      = snap_undercut + fit_clearance_snap    = 0.950
strain_barb       = 3*0.950*bezel_barb_t/(2*bezel_barb_len^2)            = 0.0148  (1.48 %)  PASS
strain_stanchion  = 3*((guard_pin_d-guard_hinge_slot_w)/2)*guard_stanchion_t
                    /(2*guard_stanchion_len^2)                           = 0.0074  (0.74 %)  PASS
strain_trim_finger= 3*((trim_snap_head_d-trim_bore_d)/2)*trim_snap_head_t
                    /(2*trim_snap_slot_len^2)                            = 0.0139  (1.39 %)  PASS
strain_cradle     = 3*((trigger_trunnion_d-trigger_cradle_mouth_w)/2)*trigger_cradle_wall_t
                    /(2*trigger_cradle_wall_len^2)                       = 0.0107  (1.07 %)  PASS
-- minimum legal length for any snap, used to solve the four lengths above:
snap_len_min(y,t) = sqrt(3*y*t/(2*strain_assembly_max))
```

### 12.7 Hat switch star spring
```
hat_base_y          = deck_y - (hat_cap_h - hat_cap_protrusion)          = 30.50
hat_cradle_d        = hat_ball_d + 2*fit_clearance_rotary                =  8.00
hat_recess_d        = hat_cap_od + 2*0.50                                = 18.50
hat_recess_depth    = hat_cap_h - hat_cap_protrusion                     =  5.50
hat_tip_deflect     = hat_arm_r * sin(hat_deflection_deg)                =  1.6935
hat_spring_arm_len  = hat_arm_mean_r * hat_arm_sweep_deg * PI/180        = 17.02
I_hat               = hat_spring_arm_width*hat_spring_arm_thick^3/12     =  0.2047 mm^4
k_hat_arm           = 3*E_flex_mpa*I_hat / hat_spring_arm_len^3          =  0.4110 N/mm
F_hat               = hat_spring_arm_count * k_hat_arm * hat_tip_deflect =  2.784 N  (target 2.80)
sigma_hat           = 3*E_flex_mpa*hat_tip_deflect*hat_spring_arm_thick
                      /(2*hat_spring_arm_len^2)                          = 24.60 MPa
hat_rim_drop        = (hat_cap_od/2) * sin(hat_deflection_deg)           =  2.116  -- relief must exceed this
```

### 12.8 Trim wheel placement
```
trim_wheel_center_y = trim_wheel_od/2 - trim_rim_proud                   =  8.80
trim_window_len     = 2*sqrt((trim_wheel_od/2)^2 - trim_wheel_center_y^2) + 2.0 = 15.2 -> 16.00
trim_window_w       = trim_wheel_width + 2*0.60                          =  8.00
grip_relief_len     = trim_window_len + 1.00                             = 17.00
grip_relief_w       = trim_window_w  + 1.00                              =  9.00
grip_relief_depth   = trim_rim_proud + 0.80                              =  3.00
```

### 12.9 Throttle rail and detent leaf
```
rail_len              = throttle_carriage_len + throttle_stroke + 2*rail_end_clear  = 44.00
rail_end_x            = rail_start_x + rail_len                                     = 47.00
dovetail_flare        = (dovetail_base_w - dovetail_mouth_w)/2                      =  1.75
dovetail_depth        = dovetail_flare / tan(dovetail_angle_deg)                    =  1.75
carriage_plate_t      = throttle_leaf_thick + leaf_deflect + gap_print_min          =  4.58 -> 4.80
rail_channel_depth    = dovetail_depth + carriage_plate_t + tab_h_z + tab_recess - dovetail_depth
                      = carriage_plate_t + tab_h_z + tab_recess                     =  7.40
channel_floor_z       = flank_z - rail_channel_depth                                =  5.85
dovetail_floor_z      = channel_floor_z - dovetail_depth                            =  4.10
rail_channel_h        = dovetail_base_w + 2.00                                      = 12.50
tenon_base_w          = dovetail_base_w  - 2*fit_clearance_sliding                  = 10.10
tenon_mouth_w         = dovetail_mouth_w - 2*fit_clearance_sliding                  =  6.60
leaf_arm_len          = (throttle_leaf_len - (throttle_leaf_arms-1)*PI*throttle_leaf_fold_r)
                        / throttle_leaf_arms                                        = 10.121
leaf_env_x            = leaf_arm_len + throttle_leaf_fold_r + throttle_leaf_width/2 = 14.72
leaf_env_y            = (throttle_leaf_arms-1)*2*throttle_leaf_fold_r + throttle_leaf_width = 9.20
leaf_tip_offset       = leaf_env_x                                                  = 14.72
follower_home_x       = rail_end_clear + leaf_tip_offset                            = 15.22
afterburner_travel    = throttle_stroke * afterburner_pos_ratio                     = 23.80
ramp_apex_x           = follower_home_x + afterburner_travel                        = 39.02
follower_full_x       = follower_home_x + throttle_stroke                           = 43.22  -- ASSERT-21
ramp_run_up           = afterburner_lift / tan(afterburner_ramp_angle_deg)          =  1.905
ramp_drop_off         = afterburner_lift / tan(afterburner_drop_angle_deg)          =  0.513
ramp_footprint        = ramp_run_up + ramp_drop_off                                 =  2.418
overtravel_available  = throttle_stroke * (1 - afterburner_pos_ratio)               =  4.200  -- ASSERT-11
leaf_deflect          = throttle_detent_preload + afterburner_lift                  =  1.550
ramp_factor_throttle  = (tan(afterburner_ramp_angle_deg)+mu_pla)
                        /(1-mu_pla*tan(afterburner_ramp_angle_deg))                 =  1.0612
I_leaf                = throttle_leaf_width*throttle_leaf_thick^3/12                =  6.0637 mm^4
k_leaf                = 3*E_flex_mpa*I_leaf / throttle_leaf_len^3                   =  2.6180 N/mm
F_leaf_normal         = k_leaf * leaf_deflect                                       =  4.058 N
F_break               = F_leaf_normal * ramp_factor_throttle                        =  4.307 N (target 4.30)
sigma_leaf            = 3*E_flex_mpa*leaf_deflect*throttle_leaf_thick
                        /(2*throttle_leaf_len^2)                                    = 25.00 MPa
sigma_leaf_rest       = 3*E_flex_mpa*throttle_detent_preload*throttle_leaf_thick
                        /(2*throttle_leaf_len^2)                                    =  7.26 MPa
-- the two-equation solve that produced L and t for the chosen width b:
--   t/L^2 = 2*sigma_allow_cyclic_mpa/(3*E_flex_mpa*leaf_deflect)   = 3.2584e-3
--   b*t^3/L^3 = 4*k_leaf_req/E_flex_mpa                            = 3.1702e-3
guide_ratio           = throttle_carriage_len / dovetail_base_w                     =  1.43  -- ASSERT-12
```

### 12.10 Trigger force chain
```
trigger_stage1_deg    = asin(trigger_stage1_travel / trigger_contact_r)             =  9.59 deg
trigger_total_travel  = trigger_contact_r * trigger_travel_deg * PI/180             =  4.712 mm
I_t1                  = trigger_stage1_width*trigger_stage1_thick^3/12              =  0.5133 mm^4
k_t1                  = 3*E_flex_mpa*I_t1 / trigger_stage1_len^3                    =  0.5333 N/mm
F_stage1              = k_t1 * trigger_stage1_travel                                =  1.600 N (target 1.60)
sigma_t1              = 3*E_flex_mpa*trigger_stage1_travel*trigger_stage1_thick
                        /(2*trigger_stage1_len^2)                                   = 24.78 MPa
I_t2                  = trigger_stage2_width*trigger_stage2_thick^3/12              =  1.2302 mm^4
k_t2                  = 3*E_flex_mpa*I_t2 / trigger_stage2_len^3                    =  6.707 N/mm
F_t2_normal           = k_t2 * trigger_stage2_deflect                               =  3.689 N
ramp_factor_gate      = (tan(trigger_gate_angle_deg)+mu_pla)
                        /(1-mu_pla*tan(trigger_gate_angle_deg))                     =  1.857
F_t2_tangential       = F_t2_normal * ramp_factor_gate                              =  6.850 N
-- tooth radius solved from the break-force target, never typed in:
trigger_tooth_r       = (trigger_break_force_n - trigger_stage1_force_n)
                        * trigger_contact_r / F_t2_tangential                       =  9.46 mm
F_break_total         = F_stage1 + F_t2_tangential*trigger_tooth_r/trigger_contact_r =  5.20 N
sigma_t2              = 3*E_flex_mpa*trigger_stage2_deflect*trigger_stage2_thick
                        /(2*trigger_stage2_len^2)                                   = 24.69 MPa
trigger_socket_d      = trigger_trunnion_d + 2*fit_clearance_pivot                  =  4.00
```

### 12.11 Grip geometry
```
grip_axis_dir      = [cos(grip_rake_angle_deg), -sin(grip_rake_angle_deg), 0] = [-0.30902, -0.95106, 0]
grip_axial_len     = grip_drop / sin(grip_rake_angle_deg)                     = 31.546
grip_butt_x        = grip_root_x + grip_drop / tan(grip_rake_angle_deg)       = 20.252
grip_x_min         = grip_butt_x - (grip_butt_depth/2)*sin(grip_rake_angle_deg) = 8.84
grip_groove_start  = 0.22 * grip_axial_len                                    =  6.94
```

### 12.12 Fit-derived mating dimensions (repeat of DESIGN_SPEC §5.1, single source)
```
guard_pin_hole_d = guard_pin_d + 2*fit_clearance_pivot   = 2.55
snap_pocket_w    = snap_hook_w + 2*fit_clearance_snap    = 3.80
key_socket_side  = key_side    + 2*fit_clearance_static  = 4.20
key_socket_depth = key_len/2   + fit_clearance_static    = 4.10
seam_groove_w    = seam_tongue_thick  + 2*fit_clearance_snap = 1.50
seam_groove_d    = seam_tongue_height + fit_clearance_snap   = 0.95
```

---

## 13. Compile-Time Assertions

These belong at the bottom of `src/parameters.scad` as OpenSCAD `assert()` calls (or `raise` in a CadQuery port). A build that trips any of them must fail, not warn. V-160 exercises them at every range endpoint.

| ID | Assertion | Guards |
| :-- | :-- | :-- |
| ASSERT-01 | `overall_length == 86.0` (±1e-6) | X chain |
| ASSERT-02 | `overall_height == 72.0` | Y chain |
| ASSERT-03 | `palm_swell_width <= chassis_width` | width budget (D-02) |
| ASSERT-04 | `rail_end_x + wall_internal <= trim_pocket_x0` | flank packaging |
| ASSERT-05 | `ratchet_web >= feature_min` | D-05 |
| ASSERT-06 | `serpentine_work_h - serpentine_solid_h >= fire_btn_stop_reserve` | F-03 |
| ASSERT-07 | `guard_inner_clear >= fire_btn_proud - 0.50` | guard closes over the button |
| ASSERT-08 | `serpentine_gap >= fire_btn_travel/serpentine_loops + gap_print_min` | loops cannot collide |
| ASSERT-09 | `hat_recess_relief_deg >= hat_deflection_deg + 2` | F-10 |
| ASSERT-10 | `snout_cavity_max_abs_z + wall_internal <= trim_pocket_floor_z` | F-06 |
| ASSERT-11 | `ramp_footprint < overtravel_available` | ramp fits in the over-travel |
| ASSERT-12 | `guide_ratio >= 1.40` | F-05 |
| ASSERT-13 | every `sigma_*` ≤ `sigma_allow_cyclic_mpa` | R-M1 |
| ASSERT-14 | every `sigma_*_rest` ≤ `sigma_allow_sustained_mpa` | R-M2 |
| ASSERT-15 | every `strain_*` ≤ `strain_assembly_max` | R-M3 |
| ASSERT-16 | every flexure thickness ≥ `flexure_min` | P-4 |
| ASSERT-17 | `wall_exterior >= 6*0.40` and `wall_internal >= 4*0.40` | P-2, P-3 |
| ASSERT-18 | `abs(F_computed - F_target)/F_target <= 0.15` for all six mechanisms | V-143 |
| ASSERT-19 | `seam_x_max == chassis_length - front_lower_chamfer` and all hook/key stations < `seam_x_max` | seam exists where the snaps are |
| ASSERT-20 | `trim_wheel_center_y - trim_wheel_od/2 == -trim_rim_proud` | rim protrusion |
| ASSERT-21 | `follower_home_x + throttle_stroke <= rail_len` | leaf tip stays on the rail |
| ASSERT-22 | `leaf_env_x <= throttle_carriage_len` and `leaf_env_y <= dovetail_base_w` | folded leaf fits the carriage |
| ASSERT-23 | `2*throttle_leaf_fold_r - throttle_leaf_width >= gap_print_min` | folded arms cannot fuse |

---

## 14. Material Re-Targeting (PETG)

Switching `material` to `"PETG"` changes `E_flex_mpa` 3300 → 2000, which scales every spring force by 0.606 and leaves every stress unchanged in the same geometry. To hold the force targets, the **width/depth** terms scale by `3300/2000 = 1.65` (R-M4 — width does not affect stress):

| Parameter | PLA+ | PETG |
| :-- | :-- | :-- |
| `serpentine_beam_t` | 4.80 | 7.92 → clamp to 7.00, accept 2.83 N (−12 %) |
| `throttle_leaf_width` | 4.00 | 6.60 → drives `leaf_env_y` to 11.80, above the 10.50 carriage; needs a 3-arm re-solve |
| `hat_spring_arm_width` | 4.00 | 6.60 |
| `pawl_width` | 3.60 | 5.94 |
| `trigger_stage1_width` | 14.60 | 24.09 → exceeds the 21.7 mm grip interior; reduce `trigger_stage1_len` to 18.6 and re-solve |
| `trigger_stage2_width` | 6.00 | 9.90 |

Three of six do not fit at 1.65×. **PETG is therefore not a drop-in substitution** — it needs its own geometry pass. This is OQ-6; it must be answered before Phase 2 rather than discovered during it.
