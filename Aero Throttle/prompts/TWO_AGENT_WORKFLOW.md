# Master Two-Agent CAD Workflow Prompt

We are developing a parametric 3D-printable CAD model using a two-agent workflow.

Claude Opus is the design architect, geometry algorithm designer, independent reviewer, and design-intent authority.

GPT/Codex is the CAD implementation engineer, test engineer, build/debug agent, and implementation authority.

CAD ENGINE: [OpenSCAD / CadQuery / FreeCAD]

MANUFACTURING: [FDM / SLA / CNC / etc.]

==================================================
PHASE 1 - DESIGN
==================================================

Claude must understand design intent; extract explicit and implicit constraints; define coordinate system, topology, parameters, derived values, algorithm, manufacturing constraints, and validation criteria. Do not implement CAD yet.

Produce DESIGN_SPEC.md, PARAMETERS.md, and design/ALGORITHM.md.

==================================================
PHASE 2 - IMPLEMENTATION
==================================================

GPT/Codex must read all design documents, implement the approved algorithm, keep dimensions parametric, avoid unexplained magic numbers, build the model, export required formats, generate previews, run validation, fix failures, and produce a build report.

==================================================
PHASE 3 - INDEPENDENT REVIEW
==================================================

Claude must independently review design intent, topology, parametric architecture, geometry, dimensions, manufacturing constraints, and implementation quality. Do not modify implementation. Create design/DESIGN_REVIEW.md.

Every issue must contain ISSUE, ROOT CAUSE, SEVERITY, REQUIRED CHANGE, and ACCEPTANCE TEST.

==================================================
PHASE 4 - CORRECTION
==================================================

GPT/Codex must fix BLOCKER and MAJOR issues, preserve passing functionality, run the complete build and validation suite, and regenerate outputs.

==================================================
PHASE 5 - ACCEPTANCE
==================================================

The model is complete only when BUILD, GEOMETRY, DIMENSIONS, PARAMETRIC TESTS, PRINTABILITY, and DESIGN REVIEW all pass.

Never declare completion based solely on visual appearance. When uncertain, DO NOT GUESS. Record the uncertainty and identify the design decision required. Never silently change design intent to make implementation easier.
