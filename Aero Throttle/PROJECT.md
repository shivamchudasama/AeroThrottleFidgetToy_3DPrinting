# Project Brief — Aero-Throttle (Prototype 01)

## Objective

Manufacture a 100% 3D-printable, zero-fastener, zero-metal-spring, zero-adhesive mechanical fidget device inspired by modern fighter jet HOTAS (Hands On Throttle And Stick) avionics cockpit controls. The device features 10 modular snap-fit components providing 6+ distinct tactile fidget mechanisms powered completely by integral compliant plastic mechanisms (cantilever leaf springs, 3D serpentine flexures, bi-stable over-center cams, and acoustic ratchet pawls).

## CAD Engine

OpenSCAD (`src/main.scad`, `src/parameters.scad`, `src/geometry.scad`) with AP242 `.STEP` and high-resolution manifold `.3MF` / `.STL` exports.

## Manufacturing Process and Material

- **Process:** FDM / FFF 3D Printing (100% Support-Free, single/multi-material bed layouts).
- **Materials:** PLA / PLA+ (primary for high spring stiffness and crisp acoustic feedback) or PETG / ABS / ASA (for maximum flexural fatigue life).
- **Machine Constraints:** 0.40 mm nozzle, 0.16–0.20 mm layer height, minimum wall thickness 2.40 mm (6 perimeters), minimum flexure beam thickness 0.75 mm.

## References

- Concept PRD: `idea/Aero Throttle CAD Design Specification.md`
- Concept Portfolio: `idea/Fidget Toy Prototypes Portfolio.md`
- Hero & Exploded technical renders: `C:/Users/chuda/.gemini/antigravity-ide/brain/293b7304-2725-4fe3-8bf9-53c688c7c8d4/aero_throttle_hero_1787163721644.jpg`
- Concept sketch: `C:/Users/chuda/.gemini/antigravity-ide/brain/5324f30b-bc16-4635-a890-31f0949b9622/prototype1_aero_throttle_1787157922526.jpg`

## Open Questions

- [ ] Exact optimum interference preload for trim wheel ratchet pawl in PETG vs PLA (-0.40 mm to -0.75 mm range).
- [ ] User preference on single-plate multi-color vs individual mono-color STL exports for multi-part printing.
