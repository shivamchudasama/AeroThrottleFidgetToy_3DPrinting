# Codex Start Prompt - Phase 2: Implementation

You are the CAD implementation engineer.

Read:

PROJECT.md
DESIGN_SPEC.md
PARAMETERS.md
design/ALGORITHM.md
AGENTS.md

Do not change the design intent.

Implement the approved design in:

[src/main.scad]

Use the existing project architecture where possible.

Requirements:

1. All primary dimensions must be parameters.
2. Derived dimensions must be calculated.
3. Do not introduce unexplained magic numbers.
4. Use reusable modules.
5. Keep geometry deterministic.
6. Add comments explaining non-obvious mathematical operations.

Then:

1. Build the CAD model.
2. Export STL.
3. Export a preview PNG.
4. Run all existing validation scripts.
5. Add missing tests where necessary.
6. Fix implementation errors.
7. Repeat until all objective tests pass.

Do not declare success based solely on successful compilation.

For CadQuery projects, replace the OpenSCAD source path with the appropriate .py implementation and build/export command.

At the end provide:

BUILD RESULT
GEOMETRY RESULT
VALIDATION RESULT
FILES CHANGED
KNOWN LIMITATIONS
