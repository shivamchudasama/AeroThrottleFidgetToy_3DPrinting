# Two-Agent Parametric CAD Workflow — Claude + GPT/Codex

## Purpose

This document defines a repeatable CLI-based workflow for parametric 3D modeling using two AI agents:

- **Claude Opus** — Design Architect / Geometry Reviewer
- **GPT-5.6 / Codex** — CAD Implementation Engineer / Test Engineer
- **OpenSCAD / CadQuery / FreeCAD CLI** — deterministic geometry engines
- **Python validation scripts** — objective geometry/manufacturing judge
- **Git** — version control and safe iteration

The goal is to avoid treating either LLM as the final authority on geometry. The LLMs design, implement, inspect, and iterate; deterministic CAD tools and validation scripts decide whether the generated model is objectively correct.

This workflow is particularly suited to:
- OpenSCAD
- CadQuery
- STEP/STL generation
- 3D-printable products
- complex parametric assemblies
- design-for-manufacturing workflows

---

# 1. Core Workflow

```text
                         YOUR IDEA
                            │
                            ▼
                 ┌─────────────────────┐
                 │   CLAUDE OPUS CLI   │
                 │                     │
                 │ Design Architect    │
                 │ Constraint analysis │
                 │ Parametric strategy │
                 │ Geometry algorithm  │
                 └──────────┬──────────┘
                            │
                            ▼
                  DESIGN_SPEC.md
                            │
                            ▼
                 ┌─────────────────────┐
                 │    GPT CODEX CLI    │
                 │                     │
                 │ CAD implementation  │
                 │ OpenSCAD/CadQuery   │
                 │ Test infrastructure │
                 └──────────┬──────────┘
                            │
                            ▼
                   PARAMETRIC SOURCE
                     .scad / .py
                            │
                            ▼
                 ┌─────────────────────┐
                 │   CAD CLI ENGINE    │
                 │                     │
                 │ OpenSCAD / CadQuery │
                 └──────────┬──────────┘
                            │
                    STL / STEP
                            │
                            ▼
                 ┌─────────────────────┐
                 │ GEOMETRY VALIDATOR  │
                 │                     │
                 │ dimensions          │
                 │ manifoldness        │
                 │ intersections       │
                 │ wall thickness      │
                 │ feature integrity   │
                 │ printability        │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │  GPT CODEX CLI      │
                 │ Fix implementation  │
                 └──────────┬──────────┘
                            │
                            ▼
                         PASS?
                       /       \
                     NO         YES
                     │           │
                     └─────┐     ▼
                           │   RELEASE
                           │
                           └──► ITERATE
```

The fundamental separation is:

> **Claude decides what the geometry should mean and how the algorithm should work. GPT/Codex implements that design and makes it executable and testable. Deterministic tools verify the result.**

---

# 2. Agent Responsibilities

## 2.1 Claude Opus — Design Architect / Reviewer

Claude is responsible for:

- understanding the design intent
- interpreting reference images and requirements
- extracting explicit requirements
- identifying hidden constraints
- defining the coordinate system
- defining topology
- designing the parametric architecture
- designing the geometry-generation algorithm
- identifying geometric failure modes
- defining acceptance tests
- reviewing GPT/Codex implementations
- analyzing validation failures
- recommending precise implementation changes

Claude is **not** the primary implementation agent.

Claude should not casually rewrite implementation code. Its primary responsibility is design intent, algorithms, constraints, and independent review.

---

## 2.2 GPT-5.6 / Codex — CAD Implementation Engineer

GPT/Codex is responsible for:

- implementing the approved design specification
- writing OpenSCAD/CadQuery/FreeCAD scripts
- building the CAD model
- generating STL/STEP outputs
- generating previews
- writing and running tests
- debugging geometry
- fixing implementation failures
- validating parameter changes
- maintaining implementation quality

GPT/Codex is the implementation authority, but not the design-intent authority.

---

## 2.3 Deterministic CAD Engine

Use the appropriate CLI engine:

- **OpenSCAD** for CSG-heavy parametric models
- **CadQuery** for more advanced parametric mechanical/engineering CAD
- **FreeCAD** where its feature-based/B-Rep ecosystem is advantageous

OpenSCAD can be driven from the command line to generate STL/PNG and supports parameter overrides with `-D`.

CadQuery is scriptable, parametric, and supports exports such as STEP, STL.

---

## 2.4 Python Validation Layer

Python should be the objective judge wherever possible.

Validation can include:

- dimensions
- volume
- manifoldness
- self-intersections
- minimum wall thickness
- minimum feature size
- clearances
- feature integrity
- expected feature counts
- topology
- project-specific constraints
- parameter-sweep behavior
- printability-related checks

The model must not be considered correct merely because the CAD script compiles or the render looks good.

---

# 3. Never Let Both Models Edit the Same Files

Establish clear ownership.

## Claude-owned files

```text
design/
    DESIGN_REVIEW.md
    ALGORITHM.md
    REFERENCES/
```

and the design-level documents:

```text
DESIGN_SPEC.md
PARAMETERS.md
```

## GPT/Codex-owned files

```text
src/
    *.scad
    *.py

tests/
    *.py

scripts/
    build.*
    validate.*
    render.*
```

The models should communicate through documents rather than continuously modifying the same source files.

This prevents the common failure mode where two agents repeatedly "fix" each other's code and gradually destroy the original design intent.

---

# 4. Recommended Project Structure

```text
my-model/
│
├── README.md
├── PROJECT.md
├── DESIGN_SPEC.md
├── PARAMETERS.md
├── CHANGELOG.md
├── CLAUDE.md
├── AGENTS.md
│
├── design/
│   ├── DESIGN_REVIEW.md
│   ├── ALGORITHM.md
│   └── REFERENCES/
│
├── src/
│   ├── main.scad
│   ├── geometry.scad
│   └── parameters.scad
│
├── scripts/
│   ├── build.py
│   ├── validate.py
│   ├── render.py
│   └── analyze_mesh.py
│
├── tests/
│   ├── test_dimensions.py
│   ├── test_geometry.py
│   └── test_printability.py
│
├── output/
│   ├── preview/
│   ├── stl/
│   ├── step/
│   └── reports/
│
└── iterations/
    ├── v001/
    ├── v002/
    └── ...
```

---

# 5. Persistent Claude Instructions — `CLAUDE.md`

Place the following in the project root.

```markdown
# CAD PROJECT — CLAUDE INSTRUCTIONS

## Role

You are the DESIGN ARCHITECT and CAD REVIEWER for this project.

You are NOT the primary implementation agent.

Your responsibilities are:

1. Understand the design intent.
2. Convert natural-language requirements into explicit engineering constraints.
3. Develop the parametric geometry strategy.
4. Identify ambiguities and hidden constraints.
5. Design algorithms before implementation.
6. Review generated CAD code.
7. Analyze validation failures.
8. Recommend precise changes to the implementation agent.

Do not make arbitrary aesthetic or geometric changes merely because they seem preferable.

---

## Core Principle

The final model must be:

- parametric
- deterministic
- reproducible
- manufacturable
- dimensionally controlled
- testable
- maintainable

Never accept "looks approximately correct" as a validation criterion.

---

## Parametric Design Rules

Every important dimension must originate from named parameters.

Do not hard-code derived dimensions.

Prefer:

parameter → derived geometry → feature → final solid

rather than:

hard-coded coordinate → hard-coded coordinate → hard-coded coordinate

---

## Geometry Rules

Before recommending implementation:

1. Define coordinate system.
2. Define units.
3. Define origin.
4. Define primary dimensions.
5. Define topology.
6. Define feature hierarchy.
7. Define dependencies.
8. Define tolerances.
9. Define manufacturability constraints.

---

## 3D Printing Rules

Consider:

- minimum wall thickness
- minimum feature size
- clearance
- unsupported overhangs
- bridging
- assembly tolerance
- mesh manifoldness
- self-intersections
- non-zero solid volume
- print orientation

Never declare a model printable without checking these.

---

## Review Protocol

When reviewing an implementation:

1. Read the complete implementation.
2. Compare it against DESIGN_SPEC.md.
3. Identify violations.
4. Separate:
   - functional failures
   - geometric failures
   - dimensional failures
   - aesthetic failures
   - implementation quality issues
5. Give each issue a severity:
   - BLOCKER
   - MAJOR
   - MINOR
   - OPTIONAL
6. Do not rewrite the implementation unless explicitly requested.

---

## Communication With GPT/Codex

When implementation changes are required, produce a precise engineering change request.

Use this format:

### ISSUE
What is wrong.

### ROOT CAUSE
Why it happened.

### REQUIRED CHANGE
Exactly what must change.

### CONSTRAINTS
What must remain unchanged.

### ACCEPTANCE TEST
How the change will be verified.

Never say merely:
"Make the geometry better."

---

## Validation

A successful build is NOT sufficient.

The following must independently pass:

- source compilation
- CAD generation
- expected dimensions
- topology checks
- mesh validity
- printability checks
- project-specific geometry tests
- visual inspection

---

## Change Discipline

Never change multiple unrelated subsystems in one iteration.

Every iteration must identify:

- changed files
- reason for change
- expected effect
- validation performed
- remaining issues
```

---

# 6. Persistent GPT/Codex Instructions — `AGENTS.md`

Place the following in the project root.

```markdown
# CAD PROJECT — CODEX INSTRUCTIONS

## Role

You are the CAD IMPLEMENTATION ENGINEER.

Claude Opus acts as the design architect and reviewer.

Your job is to implement the approved design specification accurately.

---

## Source of Truth

Read these files before modifying code:

1. PROJECT.md
2. DESIGN_SPEC.md
3. PARAMETERS.md
4. design/ALGORITHM.md

Do not infer missing requirements from memory.

If a requirement is ambiguous, stop and report the ambiguity.

---

## Implementation Rules

Use:

- parametric variables
- deterministic geometry
- reusable modules/functions
- derived dimensions
- explicit coordinate systems
- numerical tolerances

Avoid:

- unexplained magic numbers
- duplicated geometry logic
- arbitrary offsets
- unnecessary mesh manipulation
- manually positioned geometry where a parametric relationship exists

---

## Build Rule

After every significant geometry change:

1. Build the model.
2. Generate STL/STEP as appropriate.
3. Run validation.
4. Generate a preview.
5. Inspect validation results.
6. Fix failures.
7. Repeat.

Do not stop merely because the CAD script compiles.

---

## Validation Rule

Never modify validation scripts simply to make the model pass.

If a test is incorrect, explain why before changing it.

---

## Change Rule

Make the smallest change that fixes the identified problem.

Preserve all previously passing requirements.

---

## Output

At completion report:

BUILD: PASS/FAIL
GEOMETRY: PASS/FAIL
DIMENSIONS: PASS/FAIL
PRINTABILITY: PASS/FAIL
PROJECT TESTS: PASS/FAIL

Then list:

- files changed
- parameters changed
- tests executed
- remaining known limitations
```

---

# 7. Phase 1 — Design Specification

Do not begin a project by immediately asking an LLM to generate an STL.

First create a design specification.

## Claude Start Prompt

Save this prompt as:

```text
prompts/START_CAD_PROJECT.md
```

Use:

```text
You are the design architect for a new parametric 3D CAD project.

PROJECT:
[PROJECT NAME]

OBJECTIVE:
[What are we trying to manufacture?]

REFERENCE:
[Describe attached images / reference models / existing designs]

TARGET MANUFACTURING METHOD:
[FDM / resin / CNC / laser-cut / hybrid]

TARGET MATERIAL:
[PLA / PETG / ABS / wood / etc.]

TARGET SIZE:
Width: [X] mm
Height: [Y] mm
Depth: [Z] mm

PRIMARY DESIGN REQUIREMENTS:
1. [...]
2. [...]
3. [...]

GEOMETRIC CONSTRAINTS:
1. [...]
2. [...]
3. [...]

MANUFACTURING CONSTRAINTS:
1. Minimum wall: [...] mm
2. Minimum feature: [...] mm
3. Clearance: [...] mm
4. Maximum unsupported overhang: [...]°
5. [...]

PARAMETRIC REQUIREMENTS:
The following must be user-adjustable:
- [...]
- [...]
- [...]

OUTPUT:
OpenSCAD / CadQuery / STEP / STL

YOUR TASK:

Do NOT write implementation code yet.

Instead:

1. Decompose the design.
2. Identify all explicit constraints.
3. Identify hidden constraints.
4. Define the coordinate system.
5. Define the parametric architecture.
6. Determine the geometry-generation algorithm.
7. Identify potential geometric failure modes.
8. Define validation tests.
9. Produce DESIGN_SPEC.md.
10. Produce PARAMETERS.md.
11. Produce ALGORITHM.md.

Do not invent missing dimensions.

Clearly mark assumptions as ASSUMPTION.

Clearly mark unresolved questions as OPEN QUESTION.

The result should be sufficiently precise that another engineer can implement it without making design decisions.
```

Claude's output becomes the design authority for implementation.

---

# 8. Phase 2 — GPT/Codex Implementation

Once Claude has produced:

```text
DESIGN_SPEC.md
PARAMETERS.md
design/ALGORITHM.md
```

start GPT/Codex.

## Implementation Prompt

```text
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

At the end provide:

BUILD RESULT
GEOMETRY RESULT
VALIDATION RESULT
FILES CHANGED
KNOWN LIMITATIONS
```

For CadQuery projects, replace the OpenSCAD source path with the appropriate `.py` implementation and build/export command.

---

# 9. Phase 3 — Independent Claude Review

Once GPT has generated the first implementation, switch back to Claude.

## Review Prompt

```text
Review the current implementation as a strict CAD design reviewer.

Read:

DESIGN_SPEC.md
PARAMETERS.md
design/ALGORITHM.md

Then inspect:

src/
tests/
output/reports/

Do NOT modify files yet.

Determine:

1. Does the implementation satisfy the design specification?
2. Are all constraints represented?
3. Are any geometric assumptions incorrect?
4. Are there hidden topology problems?
5. Are any parameters incorrectly coupled?
6. Are dimensions truly parametric?
7. Are there unnecessary hard-coded values?
8. Is the implementation scalable when dimensions change?
9. Will the geometry remain valid at parameter extremes?
10. Does the resulting geometry preserve the intended visual design?

For every problem produce:

ISSUE:
ROOT CAUSE:
SEVERITY:
REQUIRED CHANGE:
CONSTRAINTS THAT MUST NOT CHANGE:
ACCEPTANCE TEST:

Finish with:

DESIGN REVIEW: PASS / FAIL
```

Save the review to:

```text
design/DESIGN_REVIEW.md
```

---

# 10. Phase 4 — GPT/Codex Correction

Run GPT/Codex again.

```text
Read design/DESIGN_REVIEW.md.

Address every BLOCKER and MAJOR issue.

For each issue:

1. Locate the responsible implementation.
2. Identify root cause.
3. Make the minimum required change.
4. Preserve all previously passing behavior.
5. Rebuild the model.
6. Run validation.
7. Regenerate preview.
8. Confirm the acceptance test passes.

Do not modify tests merely to make them pass.

Do not address OPTIONAL issues unless they can be fixed without changing design intent.

After completion, update CHANGELOG.md.
```

---

# 11. Phase 5 — Final Claude Acceptance Review

Once the implementation passes its automated validation:

```text
Perform final acceptance review.

The model can be released only if:

- design requirements pass
- geometry tests pass
- manufacturing tests pass
- all BLOCKER/MAJOR issues are resolved

Check the current implementation against:

DESIGN_SPEC.md
PARAMETERS.md
design/ALGORITHM.md
design/DESIGN_REVIEW.md
output/reports/

Do not approve based only on visual appearance.

Finish with:

FINAL ACCEPTANCE: PASS / FAIL
```

---

# 12. Deterministic Build Pipeline

Eventually, create one master command:

```bash
python scripts/build.py
```

It should perform:

```text
clean
 ↓
generate CAD
 ↓
export STL
 ↓
export STEP
 ↓
generate preview
 ↓
run geometry tests
 ↓
run printability tests
 ↓
generate report
```

The ideal build command should produce a machine-readable and human-readable report.

Example:

```text
========================================
CAD VALIDATION REPORT
========================================

BUILD
[PASS] OpenSCAD compilation

DIMENSIONS
[PASS] Width = 300.00 mm
[PASS] Height = 450.00 mm
[PASS] Depth = 8.00 mm

TOPOLOGY
[PASS] Watertight
[PASS] No self intersections
[PASS] Non-zero volume

PRINTABILITY
[PASS] Minimum wall = 1.20 mm
[PASS] Minimum feature = 1.00 mm
[PASS] Clearance = 0.40 mm

PROJECT-SPECIFIC
[PASS] Required features present
[PASS] Feature count = expected value
[PASS] Required symmetry preserved

========================================
RESULT: PASS
========================================
```

GPT/Codex should treat this build report as authoritative evidence rather than relying on its own assertion that the model is correct.

---

# 13. Validation Architecture

Use independent tests.

Recommended structure:

```text
tests/
    test_dimensions.py
    test_volume.py
    test_manifold.py
    test_clearances.py
    test_features.py
    test_parametric_extremes.py
```

The exact test suite depends on the model.

## Validation Categories

### Build

- CAD source compiles
- required dependencies exist
- export completes

### Geometry

- expected bounding box
- expected volume
- watertight mesh
- no self-intersections
- non-zero volume
- expected number of solids/features

### Manufacturing

- minimum wall thickness
- minimum feature size
- clearances
- unsupported overhangs
- bridging
- assembly tolerances
- print orientation considerations

### Project-specific

- required feature count
- required spacing or pitch
- required mating geometry
- required height or depth profile
- required symmetry

### Visual

- intended external profile preserved
- proportions preserved
- intended design language preserved

Visual review is complementary; it must not replace objective geometry tests.

---

# 14. The Three Different Kinds of Correctness

Always distinguish:

```text
Visual correctness
        ≠
Geometric correctness
        ≠
Manufacturing correctness
```

A model can look correct and still contain:

- overlapping solids
- non-manifold edges
- self-intersections
- zero-thickness surfaces
- incorrect dimensions
- unprintable features

Therefore the workflow must validate all three dimensions of correctness.

---

# 15. Parametric Testing

A model is not genuinely parametric simply because it contains variables.

It should remain valid when those variables change.

```text
feature_spacing = 10–20 mm
wall_thickness = 1.2–3.0 mm
feature_count = 4–10
overall_width = 250–500 mm
```

do not test only:

```text
feature_spacing = 12
width = 300
```

Use parameter sweeps such as:

```text
10 / 250
10 / 500
20 / 250
20 / 500
```

The objective is to verify that:

- topology remains valid
- geometry remains valid
- constraints remain satisfied
- manufacturing constraints remain satisfied
- design relationships remain intact

A model that only works for its default parameter values is not truly parametric.

---

# 16. Reusable Domain Architecture

For recurring design families, build a reusable geometry engine rather than manually reconstructing the complete model for every project.

Recommended structure:

```text
geometry_engine/
│
├── primitives/
│   ├── coordinates.py
│   └── topology.py
│
├── features/
│   ├── feature_catalog.py
│   └── patterns.py
│
├── profiles/
│   ├── boundary.py
│   └── height_map.py
│
├── manufacturing/
│   ├── clearances.py
│   └── printability.py
│
└── exporters/
    ├── openscad.py
    └── cadquery.py
```

This lets each new design apply a proven algorithm and validated building blocks instead of reinventing its geometry from scratch.

---

# 17. Design Data Model

For complex projects, represent each generated feature as data:

```text
feature_id
position
orientation
dimensions
classification
profile_level
height
feature_type
```

This is more robust than manually positioning hundreds of CAD primitives.

---

# 18. Generic Claude Prompt

```text
Analyze the design brief and any reference material.

Define the parametric geometry strategy and identify the data needed to generate the model deterministically.

Do not write CAD code.

Design the mathematical representation and explain how it should be implemented.

The algorithm must preserve:

- deterministic topology
- parametric overall dimensions
- required feature relationships
- required geometric constraints
- printability constraints
```

---

# 19. Generic GPT/Codex Prompt

```text
Implement the algorithm defined in design/ALGORITHM.md.

Input:

approved design specification
parameter definitions
required constraints

Output:

parametric CAD source
requested CAD exports
validation report

The algorithm must guarantee:

1. The model satisfies the approved constraints.
2. All required features are generated deterministically.
3. Relevant dimensions and relationships are parameterized.
4. Changing supported parameters regenerates the complete model.
5. The resulting topology is valid.

Write unit tests for these properties.

Also validate:

- project-specific feature integrity
- expected feature relationships
- minimum wall thickness
- minimum printable feature size
- clearances
- watertightness
- absence of self-intersections
```

---

# 20. CLI Workflow

A practical manual workflow can initially be:

## Step 1 — Claude

```bash
claude
```

Then:

```text
Analyze the new design brief and create the design specification.

Do not implement CAD yet.
```

Claude produces:

```text
DESIGN_SPEC.md
PARAMETERS.md
design/ALGORITHM.md
```

---

## Step 2 — GPT/Codex

From the same repository:

```bash
codex
```

Then:

```text
Implement the approved design specification.

Build, render and validate the model.
```

---

## Step 3 — Claude Review

```bash
claude
```

Then:

```text
Perform an independent design review of the current implementation.

Do not modify files.
Write design/DESIGN_REVIEW.md.
```

---

## Step 4 — GPT/Codex Fixes

```bash
codex
```

Then:

```text
Read design/DESIGN_REVIEW.md and resolve all BLOCKER and MAJOR issues.

Build and validate again.
```

---

## Step 5 — Claude Final Review

```bash
claude
```

Then:

```text
Perform final acceptance review.

The model can be released only if:
- design requirements pass
- geometry tests pass
- manufacturing tests pass
- all BLOCKER/MAJOR issues are resolved
```

---

# 21. Git-Based Iteration

Use Git from the beginning.

Before significant changes:

```bash
git add .
git commit -m "Working parametric baseline"
```

A typical evolution:

```text
v001
 ↓
v002
 ↓
v003
 ↓
v004
```

Git is preferable to relying only on folders such as `iterations/v001`.

If GPT destroys a previously working implementation, you can revert to the last known-good state.

Claude can also compare the current implementation against the last known-good Git commit:

```text
Compare the current implementation against the last known-good Git commit.

Identify exactly what changed geometrically.

Determine whether any design constraints or previously passing tests were broken.
```

---

# 22. Change Discipline

Every iteration should record:

```text
- changed files
- reason for change
- expected effect
- validation performed
- remaining issues
```

Do not change multiple unrelated subsystems in one iteration.

Prefer:

```text
Issue
 ↓
Root cause
 ↓
Minimal change
 ↓
Build
 ↓
Validation
 ↓
Review
```

rather than large batches of speculative changes.

---

# 23. Master Reusable Prompt

Save this as:

```text
prompts/START_CAD_PROJECT.md
```

```text
We are developing a parametric 3D-printable CAD model using a two-agent workflow.

AGENTS:

Claude Opus:
- design architect
- geometry algorithm designer
- independent reviewer
- design-intent authority

GPT/Codex:
- CAD implementation engineer
- test engineer
- build/debug agent
- implementation authority

CAD ENGINE:
[OpenSCAD / CadQuery / FreeCAD]

MANUFACTURING:
[FDM / SLA / CNC / etc.]

==================================================
PHASE 1 — DESIGN
==================================================

Claude must:

1. Understand the design intent.
2. Extract explicit requirements.
3. Identify implicit constraints.
4. Define coordinate system.
5. Define topology.
6. Define parametric variables.
7. Define derived variables.
8. Design geometry-generation algorithm.
9. Define manufacturing constraints.
10. Define validation criteria.

Do not implement CAD yet.

Produce:

DESIGN_SPEC.md
PARAMETERS.md
design/ALGORITHM.md

==================================================
PHASE 2 — IMPLEMENTATION
==================================================

GPT/Codex must:

1. Read all design documents.
2. Implement the approved algorithm.
3. Keep all primary dimensions parametric.
4. Avoid unexplained magic numbers.
5. Build the CAD model.
6. Export required formats.
7. Generate preview images.
8. Run validation.
9. Fix implementation failures.
10. Produce a build report.

==================================================
PHASE 3 — INDEPENDENT REVIEW
==================================================

Claude must independently review:

- design intent
- topology
- parametric architecture
- geometry
- dimensions
- manufacturing constraints
- implementation quality

Do not modify implementation.

Create:

design/DESIGN_REVIEW.md

Every issue must contain:

ISSUE
ROOT CAUSE
SEVERITY
REQUIRED CHANGE
ACCEPTANCE TEST

==================================================
PHASE 4 — CORRECTION
==================================================

GPT/Codex must:

1. Read DESIGN_REVIEW.md.
2. Fix BLOCKER issues.
3. Fix MAJOR issues.
4. Preserve passing functionality.
5. Run the complete build.
6. Run the complete validation suite.
7. Regenerate outputs.

==================================================
PHASE 5 — ACCEPTANCE
==================================================

The model is complete only when:

BUILD = PASS
GEOMETRY = PASS
DIMENSIONS = PASS
PARAMETRIC TESTS = PASS
PRINTABILITY = PASS
DESIGN REVIEW = PASS

Never declare completion based solely on visual appearance.

==================================================
GENERAL RULE
==================================================

When uncertain:

DO NOT GUESS.

Record the uncertainty and identify the design decision required.

Never silently change design intent to make implementation easier.
```

---

# 24. Recommended Final Architecture

The mature B3D Labs CAD workflow should eventually look like:

```text
                    ┌───────────────┐
                    │  IDEA / IMAGE │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ CLAUDE OPUS   │
                    │ Design        │
                    │ Architecture  │
                    └───────┬───────┘
                            │
                   DESIGN_SPEC.md
                            │
                            ▼
                    ┌───────────────┐
                    │ GPT / CODEX   │
                    │ Implementation│
                    └───────┬───────┘
                            │
                    .SCAD / .PY
                            │
                            ▼
                    ┌───────────────┐
                    │ CAD ENGINE    │
                    └───────┬───────┘
                            │
                       STL / STEP
                            │
                            ▼
                    ┌───────────────┐
                    │ PYTHON TESTS  │
                    │               │
                    │ geometry      │
                    │ dimensions    │
                    │ topology      │
                    │ printability  │
                    └───────┬───────┘
                            │
                         FAIL?
                      ┌─────┴─────┐
                     YES          NO
                      │            │
                      ▼            ▼
                 GPT/CODEX      RELEASE
                      │
                      ▼
                 FIX + TEST
                      │
                      └───────────┐
                                  │
                                  ▼
                         CLAUDE REVIEW
                                  │
                           DESIGN REVIEW
                                  │
                                  └──► NEXT ITERATION
```

---

# 25. Design Philosophy

The key architectural decision is:

> **Do not make Claude and GPT compete to generate the same CAD code.**

Instead:

> **Claude is responsible for the "what" and the "how should the geometry work?"**

> **GPT/Codex is responsible for "make that algorithm execute correctly."**

> **OpenSCAD/CadQuery/FreeCAD is responsible for deterministic geometry generation.**

> **Python tests are responsible for objective verification.**

> **Git is responsible for safe iteration and recovery.**

This separation is particularly effective for complex parametric 3D-printing projects, because the difficult part is not generating OpenSCAD syntax. The difficult part is preserving mathematical, topological, aesthetic, and manufacturing rules while the design becomes increasingly complex.

---

# 26. OpenSCAD vs CadQuery Strategy

Use OpenSCAD when:

- the geometry is primarily constructive solid geometry
- the design is dominated by unions/differences/intersections
- the model is relatively straightforward
- fast parameter experimentation is important

Use CadQuery when:

- the design becomes mechanically complex
- feature relationships matter
- you need robust parametric solids
- STEP is an important deliverable
- the model has engineering-style features
- you need a more CAD-like feature workflow

A sensible long-term approach is to retain OpenSCAD for simpler CSG models and use CadQuery for advanced production-grade models.

---

# 27. Release Criteria

Never release an STL/STEP simply because:

```text
"the model rendered successfully"
```

A release should require:

```text
BUILD                PASS
GEOMETRY             PASS
DIMENSIONS           PASS
TOPOLOGY             PASS
PARAMETRIC SWEEP     PASS
PRINTABILITY         PASS
PROJECT TESTS        PASS
CLAUDE REVIEW        PASS
```

Only then:

```text
                       RELEASE
                          │
             ┌────────────┼
             ▼            ▼
            STL          STEP         
             │            │
             └────────────┼
                          ▼
                    MANUFACTURING
```

---

# 28. Final Operating Principle

The workflow should behave like a software engineering organization compressed into two AI agents:

```text
Claude
  =
System Architect
+
Geometry Designer
+
Code Reviewer

GPT/Codex
  =
Implementation Engineer
+
Test Engineer
+
Debugger

CAD Engine
  =
Deterministic Geometry Executor

Python
  =
Objective Test Harness

Git
  =
Version Control / Recovery
```

The LLMs should reason about the model.

The CAD engine should construct the model.

The validation layer should judge the model.

The Git history should protect the model.

That separation is what turns CLI-based AI CAD generation from an interactive "try another prompt" workflow into a repeatable engineering pipeline.
