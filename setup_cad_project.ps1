[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateNotNullOrEmpty()]
    [string]$ProjectName,

    [Parameter(Position = 1)]
    [string]$Destination = (Get-Location).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Ensure-Directory {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        throw "Cannot create directory because a file already exists: $Path"
    }

    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
        Write-Host "Created directory: $Path"
    }
}

function Ensure-File {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [string]$Content = ''
    )

    if (Test-Path -LiteralPath $Path -PathType Container) {
        throw "Cannot create file because a directory already exists: $Path"
    }

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        # UTF8 is supported by both Windows PowerShell 5.1 and PowerShell 7.
        Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
        Write-Host "Created file: $Path"
    }
}

function Ensure-InstructionFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Content
    )

    if (Test-Path -LiteralPath $Path -PathType Container) {
        throw "Cannot create file because a directory already exists: $Path"
    }

    # Populate a new (or still-empty) instruction file, but never replace
    # instructions the project owner has already customized.
    if ((Test-Path -LiteralPath $Path -PathType Leaf) -and
        -not [string]::IsNullOrWhiteSpace((Get-Content -LiteralPath $Path -Raw))) {
        Write-Host "Retained existing instruction file: $Path"
        return
    }

    Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
    Write-Host "Populated instruction file: $Path"
}

function Initialize-GitRepository {
    param([Parameter(Mandatory = $true)][string]$Path)

    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($null -eq $git) {
        Write-Warning 'Git was not found. Install Git, then run "git init" in the project before significant changes.'
        return
    }

    & git -C $Path rev-parse --is-inside-work-tree *> $null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Git repository already available for: $Path"
        return
    }

    & git -C $Path init
    if ($LASTEXITCODE -ne 0) {
        throw "Git initialization failed for: $Path"
    }

    Write-Host "Initialized Git repository: $Path"
}

if ([string]::IsNullOrWhiteSpace($ProjectName)) {
    throw 'ProjectName cannot be empty.'
}

if ([IO.Path]::GetFileName($ProjectName) -ne $ProjectName -or
    $ProjectName.IndexOfAny([IO.Path]::GetInvalidFileNameChars()) -ge 0) {
    throw 'ProjectName must be a single valid folder name, not a path.'
}

$resolvedDestination = [IO.Path]::GetFullPath($Destination)
Ensure-Directory -Path $resolvedDestination

$projectRoot = Join-Path $resolvedDestination $ProjectName
Ensure-Directory -Path $projectRoot

$directories = @(
    'design',
    'design/REFERENCES',
    'prompts',
    'geometry_engine',
    'geometry_engine/primitives',
    'geometry_engine/features',
    'geometry_engine/profiles',
    'geometry_engine/manufacturing',
    'geometry_engine/exporters',
    'src',
    'scripts',
    'tests',
    'output',
    'output/preview',
    'output/stl',
    'output/step',
    'output/reports',
    'iterations',
    'iterations/v001',
    'iterations/v002'
)

foreach ($directory in $directories) {
    Ensure-Directory -Path (Join-Path $projectRoot $directory)
}

$files = [ordered]@{
    'README.md'               = "# $ProjectName`r`n`r`nParametric CAD project.`r`n`r`nStart-prompt templates for the two-agent workflow are in `prompts/`.`r`n`r`nConfigure the CAD engine in `cad_config.json`; build, export, render, and validate with `python scripts/build.py`.`r`n`r`nConfigure the independent validation suite using `validation_config.json`."
    'PROJECT.md'              = ''
    'DESIGN_SPEC.md'          = ''
    'PARAMETERS.md'           = ''
    'CHANGELOG.md'            = ''
    'OWNERSHIP.md'            = ''
    'WORKFLOW.md'             = ''
    'RELEASE_CHECKLIST.md'    = ''
    '.gitignore'              = ''
    'cad_config.json'         = ''
    'design/DESIGN_REVIEW.md' = ''
    'design/ALGORITHM.md'     = ''
    'design/FEATURE_DATA_MODEL.md' = ''
    'design/VISUAL_REVIEW.md' = ''
    'src/main.scad'           = ''
    'src/geometry.scad'       = ''
    'src/parameters.scad'     = ''
    'output/stl/.gitkeep'     = ''
    'output/step/.gitkeep'    = ''
    'output/preview/.gitkeep' = ''
    'output/reports/.gitkeep' = ''
    'scripts/build.py'        = ''
    'scripts/validate.py'     = ''
    'scripts/render.py'       = ''
    'scripts/release_check.py' = ''
    'scripts/analyze_mesh.py' = ''
    'scripts/cad_config.py' = ''
    'scripts/validation_utils.py' = ''
    'validation_config.json' = ''
    'requirements.txt' = ''
    'tests/README.md' = ''
    'tests/test_dimensions.py' = ''
    'tests/test_volume.py' = ''
    'tests/test_manifold.py' = ''
    'tests/test_clearances.py' = ''
    'tests/test_features.py' = ''
    'tests/test_parametric_extremes.py' = ''
    'tests/test_geometry.py' = ''
    'tests/test_printability.py' = ''
    'geometry_engine/__init__.py' = ''
    'geometry_engine/feature_model.py' = ''
    'geometry_engine/README.md' = ''
    'geometry_engine/primitives/__init__.py' = ''
    'geometry_engine/primitives/coordinates.py' = ''
    'geometry_engine/primitives/topology.py' = ''
    'geometry_engine/features/__init__.py' = ''
    'geometry_engine/features/feature_catalog.py' = ''
    'geometry_engine/features/patterns.py' = ''
    'geometry_engine/profiles/__init__.py' = ''
    'geometry_engine/profiles/boundary.py' = ''
    'geometry_engine/profiles/height_map.py' = ''
    'geometry_engine/manufacturing/__init__.py' = ''
    'geometry_engine/manufacturing/clearances.py' = ''
    'geometry_engine/manufacturing/printability.py' = ''
    'geometry_engine/exporters/__init__.py' = ''
    'geometry_engine/exporters/openscad.py' = ''
    'geometry_engine/exporters/cadquery.py' = ''
}

foreach ($file in $files.GetEnumerator()) {
    Ensure-File -Path (Join-Path $projectRoot $file.Key) -Content $file.Value
}

$claudeInstructions = @'
# CAD PROJECT __EM_DASH__ CLAUDE INSTRUCTIONS

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

parameter __RIGHT_ARROW__ derived geometry __RIGHT_ARROW__ feature __RIGHT_ARROW__ final solid

rather than:

hard-coded coordinate __RIGHT_ARROW__ hard-coded coordinate __RIGHT_ARROW__ hard-coded coordinate

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
'@

$codexInstructions = @'
# CAD PROJECT __EM_DASH__ CODEX INSTRUCTIONS

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
'@

$projectTemplate = @'
# Project Brief

## Objective

[Describe what will be manufactured and its intended use.]

## CAD Engine

[OpenSCAD / CadQuery / FreeCAD]

## Manufacturing Process and Material

[FDM / SLA / CNC / etc.; material; machine constraints]

## References

Place source images, models, and notes in `design/REFERENCES/` and list them here.

## Open Questions

- [ ]
'@

$designSpecTemplate = @'
# Design Specification

## Coordinate System and Units

## Overall Dimensions

## Required Features and Relationships

## Topology and Feature Hierarchy

## Tolerances and Clearances

## Manufacturing Constraints

## Acceptance Criteria

## Assumptions

## Open Questions
'@

$parametersTemplate = @'
# Parameter Definitions

| Parameter | Units | Default | Allowed Range | Derived From | Purpose |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

## Derived Relationships

Document every calculated value and its formula. Do not duplicate derived values as independent parameters.
'@

$changelogTemplate = @'
# Changelog

## Unreleased

### Iteration Template

- Changed files:
- Reason for change:
- Expected effect:
- Validation performed:
- Remaining issues:

---
'@

$ownershipTemplate = @'
# File Ownership

## Claude-owned design authority

- `PROJECT.md`
- `DESIGN_SPEC.md`
- `PARAMETERS.md`
- `design/`

## Codex-owned implementation authority

- `src/`
- `scripts/`
- `tests/`
- generated output and reports

Agents communicate through design documents and review requests. Do not silently overwrite another agent's owned files. Changes across ownership boundaries require an explicit approved design or review request.
'@

$workflowTemplate = @'
# Two-Agent CAD Workflow

1. Claude: use `prompts/START_CAD_PROJECT.md` to produce the design specification, parameters, and algorithm.
2. Codex: use `prompts/CODEX_PHASE_2_IMPLEMENTATION.md` to implement, export, and validate.
3. Claude: use `prompts/CLAUDE_PHASE_3_REVIEW.md`; save results to `design/DESIGN_REVIEW.md`.
4. Codex: use `prompts/CODEX_PHASE_4_CORRECTION.md`; update `CHANGELOG.md`.
5. Claude: use `prompts/CLAUDE_PHASE_5_ACCEPTANCE.md` and complete `RELEASE_CHECKLIST.md`.

## Commands

```text
python -m pip install -r requirements.txt
python scripts/build.py
python scripts/release_check.py
git add .
git commit -m "Working parametric baseline"
```

`python scripts/build.py` is the evidence-producing command. A successful render alone is not a release criterion.
'@

$releaseChecklistTemplate = @'
# Release Checklist

Release is permitted only when every required item is checked and supported by the current build report.

- [ ] BUILD: PASS
- [ ] GEOMETRY: PASS
- [ ] DIMENSIONS: PASS
- [ ] TOPOLOGY: PASS
- [ ] PARAMETRIC SWEEP: PASS
- [ ] PRINTABILITY: PASS
- [ ] PROJECT TESTS: PASS
- [ ] CLAUDE REVIEW: PASS
- [ ] VISUAL REVIEW: PASS
- [ ] `design/DESIGN_REVIEW.md` has no unresolved BLOCKER or MAJOR issue.
- [ ] `output/reports/build-report.json` and `output/reports/validation-report.json` are current.

Release version:

Reviewed by:

Date:
'@

$visualReviewTemplate = @'
# Visual Review

Visual review complements objective validation; it does not replace it.

## Reviewed Outputs

- Preview path:
- STL/STEP version:
- Reviewer:
- Date:

## Checks

- [ ] Intended external profile preserved
- [ ] Proportions preserved
- [ ] Intended design language preserved
- [ ] No unexpected visual artifacts

Result: PASS / FAIL

Notes:
'@

$featureDataModelTemplate = @'
# Feature Data Model

Use `geometry_engine.feature_model.Feature` for feature-heavy or recurring design families. Every generated feature should record:

- `feature_id`
- `position`
- `orientation`
- `dimensions`
- `classification`
- `profile_level`
- `height`
- `feature_type`

Keep feature data separate from CAD-engine calls so geometry can be regenerated, inspected, and tested deterministically.
'@

$gitignoreTemplate = @'
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.venv/
venv/

# Generated CAD outputs and reports
output/stl/*
output/step/*
output/preview/*
output/reports/*
!output/**/.gitkeep

# Local CAD application files
*.blend1
*.FCStd1
'@

$cadConfig = @'
{
  "engine": "openscad",
  "source": "src/main.scad",
  "exports": {
    "stl": "output/stl/model.stl",
    "step": "output/step/model.step",
    "preview": "output/preview/model.png"
  },
  "commands": {
    "stl_export": ["openscad", "-o", "{stl_path}", "{source}"],
    "step_export": [],
    "preview": ["openscad", "--render", "-o", "{preview_path}", "{source}"]
  }
}
'@

$cadConfigScript = @'
"""CAD-engine configuration and command helpers."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "cad_config.json"


def load_cad_config() -> dict[str, Any]:
    with CONFIG_PATH.open(encoding="utf-8") as config_file:
        config = json.load(config_file)
    if not isinstance(config, dict):
        raise RuntimeError("cad_config.json must contain a JSON object")
    return config


def project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def export_path(config: dict[str, Any], name: str) -> Path:
    value = config.get("exports", {}).get(name)
    if not value:
        raise RuntimeError(f"cad_config.json is missing exports.{name}")
    return project_path(value)


def command_for(config: dict[str, Any], name: str) -> list[str]:
    command = config.get("commands", {}).get(name, [])
    if not command:
        return []
    if not isinstance(command, list) or not all(isinstance(part, str) for part in command):
        raise RuntimeError(f"commands.{name} must be a list of strings")
    exports = config.get("exports", {})
    context = {
        "project_root": str(PROJECT_ROOT),
        "source": str(project_path(config.get("source", "src/main.scad"))),
        "stl_path": str(project_path(exports.get("stl", "output/stl/model.stl"))),
        "step_path": str(project_path(exports.get("step", "output/step/model.step"))),
        "preview_path": str(project_path(exports.get("preview", "output/preview/model.png"))),
    }
    return [part.format(**context) for part in command]


def run_command(command: list[str], label: str) -> None:
    if not command:
        raise RuntimeError(f"No command configured for {label}")
    result = subprocess.run(command, cwd=PROJECT_ROOT, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"{label} failed with exit code {result.returncode}")
'@

$renderScript = @'
"""Generate the configured preview image."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cad_config import command_for, export_path, load_cad_config, run_command


def main() -> int:
    config = load_cad_config()
    preview = export_path(config, "preview")
    preview.parent.mkdir(parents=True, exist_ok=True)
    command = command_for(config, "preview")
    if not command:
        print("PREVIEW: SKIPPED (configure commands.preview in cad_config.json)")
        return 0
    run_command(command, "preview export")
    if not preview.is_file():
        raise RuntimeError(f"Preview command completed without creating {preview}")
    print(f"PREVIEW: PASS ({preview})")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"PREVIEW: FAIL - {error}", file=sys.stderr)
        raise SystemExit(1)
'@

$buildScript = @'
"""Build, export, render, validate, and report a CAD project."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cad_config import PROJECT_ROOT, command_for, export_path, load_cad_config, run_command


def run_step(name: str, action) -> tuple[str, str]:
    try:
        action()
        return "PASS", ""
    except Exception as error:
        return "FAIL", str(error)


def remove_generated_file(path: Path) -> None:
    output_root = (PROJECT_ROOT / "output").resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(output_root)
    except ValueError as error:
        raise RuntimeError(f"Refusing to clean a path outside output/: {path}") from error
    if resolved.is_file():
        resolved.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-step", action="store_true", help="Do not export STEP")
    parser.add_argument("--skip-preview", action="store_true", help="Do not generate preview")
    parser.add_argument("--skip-validation", action="store_true", help="Do not run validation (report remains incomplete)")
    parser.add_argument("--no-clean", action="store_true", help="Preserve existing generated output files")
    args = parser.parse_args()

    config = load_cad_config()
    results: dict[str, dict[str, str]] = {}

    if not args.no_clean:
        clean_targets = [
            export_path(config, "stl"),
            export_path(config, "step"),
            export_path(config, "preview"),
            PROJECT_ROOT / "output/reports/build-report.json",
            PROJECT_ROOT / "output/reports/validation-report.json",
        ]
        status, details = run_step("Clean", lambda: [remove_generated_file(path) for path in clean_targets])
        results["CLEAN"] = {"status": status, "details": details}

    stl = export_path(config, "stl")
    stl.parent.mkdir(parents=True, exist_ok=True)
    status, details = run_step("STL export", lambda: run_command(command_for(config, "stl_export"), "STL export"))
    if status == "PASS" and not stl.is_file():
        status, details = "FAIL", f"STL export did not create {stl}"
    results["BUILD"] = {"status": status, "details": details}

    if not args.skip_step:
        step_command = command_for(config, "step_export")
        if step_command:
            step = export_path(config, "step")
            step.parent.mkdir(parents=True, exist_ok=True)
            status, details = run_step("STEP export", lambda: run_command(step_command, "STEP export"))
            if status == "PASS" and not step.is_file():
                status, details = "FAIL", f"STEP export did not create {step}"
            results["STEP"] = {"status": status, "details": details}
        else:
            results["STEP"] = {"status": "SKIPPED", "details": "No commands.step_export is configured"}

    if not args.skip_preview:
        preview_command = command_for(config, "preview")
        if preview_command:
            preview = export_path(config, "preview")
            preview.parent.mkdir(parents=True, exist_ok=True)
            status, details = run_step("Preview", lambda: run_command(preview_command, "preview export"))
            if status == "PASS" and not preview.is_file():
                status, details = "FAIL", f"Preview export did not create {preview}"
            results["PREVIEW"] = {"status": status, "details": details}
        else:
            results["PREVIEW"] = {"status": "SKIPPED", "details": "No commands.preview is configured"}

    if args.skip_validation:
        results["VALIDATION"] = {"status": "INCOMPLETE", "details": "Validation was skipped"}
    else:
        validation = subprocess.run([sys.executable, "scripts/validate.py"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=False)
        results["VALIDATION"] = {
            "status": "PASS" if validation.returncode == 0 else "FAIL",
            "details": (validation.stdout + validation.stderr).strip(),
        }

    release_ready = all(item["status"] == "PASS" for item in results.values() if item["status"] != "SKIPPED")
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine": config.get("engine"),
        "status": "PASS" if release_ready else "FAIL",
        "results": results,
    }
    report_path = PROJECT_ROOT / "output/reports/build-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"CAD BUILD RESULT: {report['status']}")
    print(f"Report: {report_path}")
    return 0 if release_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
'@

$releaseCheckScript = @'
"""Verify the evidence required to release a CAD model."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def report_status(path: Path) -> str:
    if not path.is_file():
        return "MISSING"
    try:
        return str(json.loads(path.read_text(encoding="utf-8")).get("status", "MISSING"))
    except json.JSONDecodeError:
        return "INVALID"


def contains_pass(path: Path, accepted_markers: tuple[str, ...]) -> bool:
    if not path.is_file():
        return False
    content = path.read_text(encoding="utf-8")
    return any(marker in content for marker in accepted_markers)


def main() -> int:
    checks = {
        "BUILD": report_status(PROJECT_ROOT / "output/reports/build-report.json") == "PASS",
        "VALIDATION": report_status(PROJECT_ROOT / "output/reports/validation-report.json") == "PASS",
        "DESIGN REVIEW": contains_pass(PROJECT_ROOT / "design/DESIGN_REVIEW.md", ("DESIGN REVIEW: PASS", "FINAL ACCEPTANCE: PASS")),
        "VISUAL REVIEW": contains_pass(PROJECT_ROOT / "design/VISUAL_REVIEW.md", ("Result: PASS",)),
    }
    checklist = PROJECT_ROOT / "RELEASE_CHECKLIST.md"
    checks["RELEASE CHECKLIST"] = checklist.is_file() and "- [ ]" not in checklist.read_text(encoding="utf-8")
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "checks": checks,
    }
    report_path = PROJECT_ROOT / "output/reports/release-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"[{ 'PASS' if passed else 'FAIL' }] {name}")
    print(f"RELEASE CHECK: {status}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
'@

$geometryEngineReadme = @'
# Reusable Geometry Engine

This optional, engine-neutral layer is for recurring or feature-heavy design families. Keep geometric data and constraints here; keep the chosen CAD engine's source in `src/`.

The provided modules establish the Chapter 16 layout and the Chapter 17 feature data model. Extend them only when a project benefits from reusable primitives, profiles, patterns, manufacturing checks, or exporters.
'@

$featureModel = @'
"""Engine-neutral data model for deterministically generated CAD features."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


Vector3 = tuple[float, float, float]


@dataclass(frozen=True)
class Feature:
    feature_id: str
    position: Vector3
    orientation: Vector3 = (0.0, 0.0, 0.0)
    dimensions: Mapping[str, float] = field(default_factory=dict)
    classification: str = ""
    profile_level: int | None = None
    height: float | None = None
    feature_type: str = ""

    def __post_init__(self) -> None:
        if not self.feature_id:
            raise ValueError("feature_id must not be empty")
        if len(self.position) != 3 or len(self.orientation) != 3:
            raise ValueError("position and orientation must each contain three values")
        if any(value <= 0 for value in self.dimensions.values()):
            raise ValueError("feature dimensions must be positive")
'@

$coordinatesModule = @'
"""Coordinate helpers for reusable geometry generation."""

from __future__ import annotations


def translate(point: tuple[float, float, float], offset: tuple[float, float, float]) -> tuple[float, float, float]:
    return tuple(a + b for a, b in zip(point, offset))
'@

$topologyModule = @'
"""Topology policy definitions shared by geometry generators and tests."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TopologyPolicy:
    require_watertight: bool = True
    max_connected_components: int = 1
'@

$featureCatalogModule = @'
"""Feature catalog keyed by deterministic feature ID."""

from __future__ import annotations

from geometry_engine.feature_model import Feature


def index_by_id(features: list[Feature]) -> dict[str, Feature]:
    indexed = {feature.feature_id: feature for feature in features}
    if len(indexed) != len(features):
        raise ValueError("feature IDs must be unique")
    return indexed
'@

$patternsModule = @'
"""Deterministic placement patterns."""

from __future__ import annotations


def linear_positions(count: int, spacing: float, origin: float = 0.0) -> list[float]:
    if count < 1:
        raise ValueError("count must be at least one")
    if spacing <= 0:
        raise ValueError("spacing must be positive")
    return [origin + index * spacing for index in range(count)]
'@

$boundaryModule = @'
"""Boundary-profile placeholder for a reusable design family."""

from __future__ import annotations


def rectangular_boundary(width: float, depth: float) -> tuple[tuple[float, float], ...]:
    if width <= 0 or depth <= 0:
        raise ValueError("boundary dimensions must be positive")
    return ((0.0, 0.0), (width, 0.0), (width, depth), (0.0, depth))
'@

$heightMapModule = @'
"""Height-map placeholder for profile-based geometry."""

from __future__ import annotations


def constant_height(value: float):
    if value <= 0:
        raise ValueError("height must be positive")
    return lambda _x, _y: value
'@

$clearancesModule = @'
"""Manufacturing clearance policy."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClearancePolicy:
    minimum_clearance_mm: float

    def __post_init__(self) -> None:
        if self.minimum_clearance_mm <= 0:
            raise ValueError("minimum_clearance_mm must be positive")
'@

$printabilityModule = @'
"""Printability policy used by project-specific validation checks."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PrintabilityPolicy:
    minimum_wall_mm: float
    minimum_feature_mm: float
    maximum_unsupported_overhang_degrees: float
'@

$openscadExporterModule = @'
"""OpenSCAD export command builder."""

from __future__ import annotations

from pathlib import Path


def stl_command(source: Path, output: Path) -> list[str]:
    return ["openscad", "-o", str(output), str(source)]
'@

$cadqueryExporterModule = @'
"""CadQuery export command builder; adapt the script arguments to the project."""

from __future__ import annotations

from pathlib import Path


def script_command(source: Path) -> list[str]:
    return ["python", str(source)]
'@

$emptyPythonModule = @'
"""Package marker for reusable geometry modules."""
'@

$geometryCompatibilityTest = @'
"""Compatibility entry point; geometry checks live in the focused test modules."""
'@

$printabilityCompatibilityTest = @'
"""Compatibility entry point; configure printability checks in validation_config.json."""
'@

$validationConfig = @'
{
  "mesh_path": "output/stl/model.stl",
  "bounds_tolerance_mm": 0.1,
  "expected_bounds_mm": null,
  "expected_minimum_mm": null,
  "min_volume_mm3": null,
  "max_volume_mm3": null,
  "require_watertight": true,
  "max_connected_components": 1,
  "project_checks": {
    "clearances": {
      "required": false,
      "command": []
    },
    "features": {
      "required": false,
      "command": []
    },
    "self_intersections": {
      "required": false,
      "command": []
    }
  },
  "parametric_sweeps": []
}
'@

$validationRequirements = @'
# Mesh analysis dependency used by scripts/analyze_mesh.py and tests.
trimesh>=4.0
numpy>=1.24
'@

$validationReadme = @'
# Validation Suite

Run the complete validation suite from the project root:

```text
python scripts/validate.py
```

Configure `validation_config.json` before treating the result as release evidence. The default configuration deliberately has no expected dimensions or volume, and refers to `output/stl/model.stl`.

## Test ownership

- `test_dimensions.py`: bounding box and placement.
- `test_volume.py`: non-zero and configured volume limits.
- `test_manifold.py`: mesh validity, watertightness, components, and an optional self-intersection command.
- `test_clearances.py`: project-specific clearance and manufacturability command.
- `test_features.py`: project-specific feature, spacing, symmetry, and mating-geometry command.
- `test_parametric_extremes.py`: rebuilds configured parameter sweeps and validates every exported mesh.

`trimesh` is required for mesh-based checks. Install the project dependencies with:

```text
python -m pip install -r requirements.txt
```

## Project-specific checks

Generic STL analysis cannot reliably infer a design's intended features, clearances, or all self-intersections. Configure each required check under `project_checks` with a command that exits 0 only when the stated constraint passes. Commands run from the project root. For example:

```json
"clearances": {
  "required": true,
  "command": ["python", "scripts/check_clearances.py"]
}
```

## Parameter sweeps

Each `parametric_sweeps` item needs a `name`, a build `command`, and the generated `mesh_path`. It may also set `expected_bounds_mm`, `min_volume_mm3`, and `max_volume_mm3`. The sweep test rejects missing, non-watertight, empty, or out-of-range meshes.
'@

$validationUtils = @'
"""Shared utilities for independent CAD validation tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "validation_config.json"


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.is_file():
        raise RuntimeError(f"Missing validation configuration: {CONFIG_PATH}")
    with CONFIG_PATH.open(encoding="utf-8") as config_file:
        config = json.load(config_file)
    if not isinstance(config, dict):
        raise RuntimeError("validation_config.json must contain a JSON object")
    return config


def project_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def require_mesh(test_case: Any, mesh_path: str | Path | None = None) -> Any:
    config = load_config()
    selected_path = mesh_path or config.get("mesh_path")
    if not selected_path:
        test_case.skipTest("No mesh_path is configured in validation_config.json")

    path = project_path(selected_path)
    if not path.is_file():
        test_case.skipTest(f"Mesh has not been exported yet: {path}")

    try:
        import trimesh
    except ImportError:
        test_case.skipTest("Install requirements.txt to enable mesh validation")

    mesh = trimesh.load_mesh(path, process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))
    if not isinstance(mesh, trimesh.Trimesh):
        raise RuntimeError(f"Unsupported mesh type loaded from {path}: {type(mesh)!r}")
    return mesh


def assert_mesh_basics(test_case: Any, mesh: Any, label: str = "mesh") -> None:
    test_case.assertGreater(len(mesh.vertices), 0, f"{label} has no vertices")
    test_case.assertGreater(len(mesh.faces), 0, f"{label} has no faces")
    test_case.assertTrue(mesh.vertices.size > 0, f"{label} has no vertex data")
    test_case.assertTrue(mesh.faces.size > 0, f"{label} has no face data")
    test_case.assertTrue(bool(mesh.is_winding_consistent), f"{label} has inconsistent face winding")


def run_check_command(test_case: Any, check_name: str) -> None:
    config = load_config()
    check = config.get("project_checks", {}).get(check_name, {})
    command = check.get("command", []) if isinstance(check, dict) else []
    required = bool(check.get("required", False)) if isinstance(check, dict) else False

    if not command:
        if required:
            test_case.fail(
                f"Required project check '{check_name}' has no command in validation_config.json"
            )
        test_case.skipTest(f"No project-specific '{check_name}' check is configured")

    if not isinstance(command, list) or not all(isinstance(item, str) for item in command):
        test_case.fail(f"project_checks.{check_name}.command must be a list of strings")

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    message = (result.stdout + result.stderr).strip()
    test_case.assertEqual(result.returncode, 0, f"{check_name} check failed:\n{message}")


def run_sweep_command(sweep: dict[str, Any]) -> None:
    command = sweep.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(item, str) for item in command):
        raise RuntimeError("Every parametric sweep needs a non-empty command list")
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        raise RuntimeError(f"Sweep '{sweep.get('name', '<unnamed>')}' build failed:\n{output}")
'@

$analyzeMeshScript = @'
"""Print a machine-readable summary of an STL/mesh file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validation_utils import assert_mesh_basics, project_path, require_mesh


class MeshCheck:
    def skipTest(self, message: str) -> None:
        raise RuntimeError(message)

    def assertGreater(self, actual: float, expected: float, message: str) -> None:
        if not actual > expected:
            raise RuntimeError(message)

    def assertTrue(self, value: bool, message: str) -> None:
        if not value:
            raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mesh", nargs="?", help="Mesh path relative to the project root")
    args = parser.parse_args()

    try:
        mesh = require_mesh(MeshCheck(), args.mesh)
        assert_mesh_basics(MeshCheck(), mesh)
    except RuntimeError as error:
        print(f"ANALYSIS: FAIL\n{error}", file=sys.stderr)
        return 2

    summary = {
        "mesh_path": str(project_path(args.mesh)) if args.mesh else None,
        "bounds_mm": [float(value) for value in mesh.extents],
        "minimum_mm": [float(value) for value in mesh.bounds[0]],
        "maximum_mm": [float(value) for value in mesh.bounds[1]],
        "volume_mm3": float(mesh.volume),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "connected_components": int(mesh.body_count),
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'@

$validateScript = @'
"""Run CAD validation tests and write a machine-readable report."""

from __future__ import annotations

import argparse
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ReportingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.records.append({"test": test.id(), "status": "PASS"})

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.records.append({"test": test.id(), "status": "SKIP", "reason": reason})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.records.append({"test": test.id(), "status": "FAIL", "details": self._exc_info_to_string(err, test)})

    def addError(self, test, err):
        super().addError(test, err)
        self.records.append({"test": test.id(), "status": "ERROR", "details": self._exc_info_to_string(err, test)})


class ReportingRunner(unittest.TextTestRunner):
    resultclass = ReportingResult


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", default="output/reports/validation-report.json")
    parser.add_argument("--verbosity", type=int, default=2)
    args = parser.parse_args()

    suite = unittest.defaultTestLoader.discover(str(PROJECT_ROOT / "tests"), pattern="test_*.py")
    result = ReportingRunner(verbosity=args.verbosity).run(suite)
    passed = result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
    status = "PASS" if result.wasSuccessful() and passed else "INCOMPLETE" if result.wasSuccessful() else "FAIL"

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "tests_run": result.testsRun,
        "passed": passed,
        "failed": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "results": result.records,
    }
    report_path = PROJECT_ROOT / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\nCAD VALIDATION RESULT: {status}")
    print(f"Report: {report_path}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
'@

$testDimensions = @'
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validation_utils import load_config, require_mesh


class DimensionTests(unittest.TestCase):
    def test_expected_bounding_box(self) -> None:
        config = load_config()
        expected = config.get("expected_bounds_mm")
        if expected is None:
            self.skipTest("expected_bounds_mm is not configured")
        self.assertEqual(len(expected), 3, "expected_bounds_mm must contain [X, Y, Z]")
        mesh = require_mesh(self)
        tolerance = float(config.get("bounds_tolerance_mm", 0.1))
        for axis, actual, target in zip("XYZ", mesh.extents, expected):
            self.assertAlmostEqual(float(actual), float(target), delta=tolerance, msg=f"{axis} dimension differs from specification")

    def test_expected_minimum_position(self) -> None:
        config = load_config()
        expected = config.get("expected_minimum_mm")
        if expected is None:
            self.skipTest("expected_minimum_mm is not configured")
        self.assertEqual(len(expected), 3, "expected_minimum_mm must contain [X, Y, Z]")
        mesh = require_mesh(self)
        tolerance = float(config.get("bounds_tolerance_mm", 0.1))
        for axis, actual, target in zip("XYZ", mesh.bounds[0], expected):
            self.assertAlmostEqual(float(actual), float(target), delta=tolerance, msg=f"{axis} minimum position differs from specification")


if __name__ == "__main__":
    unittest.main()
'@

$testVolume = @'
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validation_utils import load_config, require_mesh


class VolumeTests(unittest.TestCase):
    def test_non_zero_volume(self) -> None:
        mesh = require_mesh(self)
        self.assertGreater(float(mesh.volume), 0.0, "Mesh must have non-zero volume")

    def test_volume_limits(self) -> None:
        config = load_config()
        minimum = config.get("min_volume_mm3")
        maximum = config.get("max_volume_mm3")
        if minimum is None and maximum is None:
            self.skipTest("No volume limits are configured")
        mesh = require_mesh(self)
        volume = float(mesh.volume)
        if minimum is not None:
            self.assertGreaterEqual(volume, float(minimum), "Mesh volume is below the approved minimum")
        if maximum is not None:
            self.assertLessEqual(volume, float(maximum), "Mesh volume exceeds the approved maximum")


if __name__ == "__main__":
    unittest.main()
'@

$testManifold = @'
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validation_utils import assert_mesh_basics, load_config, require_mesh, run_check_command


class ManifoldTests(unittest.TestCase):
    def test_mesh_basics_and_winding(self) -> None:
        mesh = require_mesh(self)
        assert_mesh_basics(self, mesh)

    def test_watertightness(self) -> None:
        config = load_config()
        if not config.get("require_watertight", True):
            self.skipTest("Watertightness is not required for this project")
        mesh = require_mesh(self)
        self.assertTrue(bool(mesh.is_watertight), "Mesh is not watertight")

    def test_connected_components(self) -> None:
        config = load_config()
        maximum = config.get("max_connected_components")
        if maximum is None:
            self.skipTest("max_connected_components is not configured")
        mesh = require_mesh(self)
        self.assertLessEqual(int(mesh.body_count), int(maximum), "Mesh has more disconnected solids than allowed")

    def test_project_self_intersection_check(self) -> None:
        run_check_command(self, "self_intersections")


if __name__ == "__main__":
    unittest.main()
'@

$testClearances = @'
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validation_utils import run_check_command


class ClearanceTests(unittest.TestCase):
    def test_clearances_and_manufacturing_constraints(self) -> None:
        run_check_command(self, "clearances")


if __name__ == "__main__":
    unittest.main()
'@

$testFeatures = @'
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validation_utils import run_check_command


class FeatureTests(unittest.TestCase):
    def test_required_features_and_relationships(self) -> None:
        run_check_command(self, "features")


if __name__ == "__main__":
    unittest.main()
'@

$testParametricExtremes = @'
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validation_utils import assert_mesh_basics, load_config, require_mesh, run_sweep_command


class ParametricExtremeTests(unittest.TestCase):
    def test_configured_parameter_sweeps(self) -> None:
        sweeps = load_config().get("parametric_sweeps", [])
        if not sweeps:
            self.skipTest("No parametric_sweeps are configured")

        for sweep in sweeps:
            with self.subTest(sweep=sweep.get("name", "<unnamed>")):
                run_sweep_command(sweep)
                mesh = require_mesh(self, sweep.get("mesh_path"))
                assert_mesh_basics(self, mesh, f"Sweep {sweep.get('name', '<unnamed>')}")
                self.assertTrue(bool(mesh.is_watertight), "Sweep mesh is not watertight")
                self.assertGreater(float(mesh.volume), 0.0, "Sweep mesh has zero volume")

                expected = sweep.get("expected_bounds_mm")
                if expected is not None:
                    tolerance = float(sweep.get("bounds_tolerance_mm", 0.1))
                    for actual, target in zip(mesh.extents, expected):
                        self.assertAlmostEqual(float(actual), float(target), delta=tolerance)

                minimum = sweep.get("min_volume_mm3")
                maximum = sweep.get("max_volume_mm3")
                if minimum is not None:
                    self.assertGreaterEqual(float(mesh.volume), float(minimum))
                if maximum is not None:
                    self.assertLessEqual(float(mesh.volume), float(maximum))


if __name__ == "__main__":
    unittest.main()
'@

$claudeDesignPrompt = @'
# Claude Start Prompt - Phase 1: Design Specification

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
4. Maximum unsupported overhang: [...] degrees
5. [...]

PARAMETRIC REQUIREMENTS:
The following must be user-adjustable:
- [...]
- [...]
- [...]

OUTPUT:
[OpenSCAD / CadQuery / STEP / STL]

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
11. Produce design/ALGORITHM.md.

Do not invent missing dimensions.

Clearly mark assumptions as ASSUMPTION.

Clearly mark unresolved questions as OPEN QUESTION.

The result should be sufficiently precise that another engineer can implement it without making design decisions.
'@

$codexImplementationPrompt = @'
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
'@

$claudeReviewPrompt = @'
# Claude Start Prompt - Phase 3: Independent Design Review

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

Save the review to:

design/DESIGN_REVIEW.md

Finish with:

DESIGN REVIEW: PASS / FAIL
'@

$codexCorrectionPrompt = @'
# Codex Start Prompt - Phase 4: Review Corrections

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
'@

$claudeAcceptancePrompt = @'
# Claude Start Prompt - Phase 5: Final Acceptance Review

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
'@

$genericClaudePrompt = @'
# Generic Claude Prompt

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
'@

$genericCodexPrompt = @'
# Generic Codex Prompt

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
'@

$masterWorkflowPrompt = @'
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
'@

# Keep this script ASCII-only so Windows PowerShell 5.1 parses it correctly
# even when the file is saved as UTF-8 without a byte-order mark.
$emDash = [string][char]0x2014
$rightArrow = [string][char]0x2192
$claudeInstructions = $claudeInstructions.Replace('__EM_DASH__', $emDash).Replace('__RIGHT_ARROW__', $rightArrow)
$codexInstructions = $codexInstructions.Replace('__EM_DASH__', $emDash).Replace('__RIGHT_ARROW__', $rightArrow)

Ensure-InstructionFile -Path (Join-Path $projectRoot 'CLAUDE.md') -Content $claudeInstructions
Ensure-InstructionFile -Path (Join-Path $projectRoot 'AGENTS.md') -Content $codexInstructions
Ensure-InstructionFile -Path (Join-Path $projectRoot 'PROJECT.md') -Content $projectTemplate
Ensure-InstructionFile -Path (Join-Path $projectRoot 'DESIGN_SPEC.md') -Content $designSpecTemplate
Ensure-InstructionFile -Path (Join-Path $projectRoot 'PARAMETERS.md') -Content $parametersTemplate
Ensure-InstructionFile -Path (Join-Path $projectRoot 'CHANGELOG.md') -Content $changelogTemplate
Ensure-InstructionFile -Path (Join-Path $projectRoot 'OWNERSHIP.md') -Content $ownershipTemplate
Ensure-InstructionFile -Path (Join-Path $projectRoot 'WORKFLOW.md') -Content $workflowTemplate
Ensure-InstructionFile -Path (Join-Path $projectRoot 'RELEASE_CHECKLIST.md') -Content $releaseChecklistTemplate
Ensure-InstructionFile -Path (Join-Path $projectRoot '.gitignore') -Content $gitignoreTemplate
Ensure-InstructionFile -Path (Join-Path $projectRoot 'cad_config.json') -Content $cadConfig
Ensure-InstructionFile -Path (Join-Path $projectRoot 'design/FEATURE_DATA_MODEL.md') -Content $featureDataModelTemplate
Ensure-InstructionFile -Path (Join-Path $projectRoot 'design/VISUAL_REVIEW.md') -Content $visualReviewTemplate
Ensure-InstructionFile -Path (Join-Path $projectRoot 'prompts/START_CAD_PROJECT.md') -Content $claudeDesignPrompt
Ensure-InstructionFile -Path (Join-Path $projectRoot 'prompts/CODEX_PHASE_2_IMPLEMENTATION.md') -Content $codexImplementationPrompt
Ensure-InstructionFile -Path (Join-Path $projectRoot 'prompts/CLAUDE_PHASE_3_REVIEW.md') -Content $claudeReviewPrompt
Ensure-InstructionFile -Path (Join-Path $projectRoot 'prompts/CODEX_PHASE_4_CORRECTION.md') -Content $codexCorrectionPrompt
Ensure-InstructionFile -Path (Join-Path $projectRoot 'prompts/CLAUDE_PHASE_5_ACCEPTANCE.md') -Content $claudeAcceptancePrompt
Ensure-InstructionFile -Path (Join-Path $projectRoot 'prompts/GENERIC_CLAUDE.md') -Content $genericClaudePrompt
Ensure-InstructionFile -Path (Join-Path $projectRoot 'prompts/GENERIC_CODEX.md') -Content $genericCodexPrompt
Ensure-InstructionFile -Path (Join-Path $projectRoot 'prompts/TWO_AGENT_WORKFLOW.md') -Content $masterWorkflowPrompt
Ensure-InstructionFile -Path (Join-Path $projectRoot 'validation_config.json') -Content $validationConfig
Ensure-InstructionFile -Path (Join-Path $projectRoot 'requirements.txt') -Content $validationRequirements
Ensure-InstructionFile -Path (Join-Path $projectRoot 'tests/README.md') -Content $validationReadme
Ensure-InstructionFile -Path (Join-Path $projectRoot 'scripts/validation_utils.py') -Content $validationUtils
Ensure-InstructionFile -Path (Join-Path $projectRoot 'scripts/cad_config.py') -Content $cadConfigScript
Ensure-InstructionFile -Path (Join-Path $projectRoot 'scripts/build.py') -Content $buildScript
Ensure-InstructionFile -Path (Join-Path $projectRoot 'scripts/render.py') -Content $renderScript
Ensure-InstructionFile -Path (Join-Path $projectRoot 'scripts/release_check.py') -Content $releaseCheckScript
Ensure-InstructionFile -Path (Join-Path $projectRoot 'scripts/analyze_mesh.py') -Content $analyzeMeshScript
Ensure-InstructionFile -Path (Join-Path $projectRoot 'scripts/validate.py') -Content $validateScript
Ensure-InstructionFile -Path (Join-Path $projectRoot 'tests/test_dimensions.py') -Content $testDimensions
Ensure-InstructionFile -Path (Join-Path $projectRoot 'tests/test_volume.py') -Content $testVolume
Ensure-InstructionFile -Path (Join-Path $projectRoot 'tests/test_manifold.py') -Content $testManifold
Ensure-InstructionFile -Path (Join-Path $projectRoot 'tests/test_clearances.py') -Content $testClearances
Ensure-InstructionFile -Path (Join-Path $projectRoot 'tests/test_features.py') -Content $testFeatures
Ensure-InstructionFile -Path (Join-Path $projectRoot 'tests/test_parametric_extremes.py') -Content $testParametricExtremes
Ensure-InstructionFile -Path (Join-Path $projectRoot 'tests/test_geometry.py') -Content $geometryCompatibilityTest
Ensure-InstructionFile -Path (Join-Path $projectRoot 'tests/test_printability.py') -Content $printabilityCompatibilityTest
Ensure-InstructionFile -Path (Join-Path $projectRoot 'geometry_engine/README.md') -Content $geometryEngineReadme
Ensure-InstructionFile -Path (Join-Path $projectRoot 'geometry_engine/__init__.py') -Content $emptyPythonModule
Ensure-InstructionFile -Path (Join-Path $projectRoot 'geometry_engine/feature_model.py') -Content $featureModel
Ensure-InstructionFile -Path (Join-Path $projectRoot 'geometry_engine/primitives/__init__.py') -Content $emptyPythonModule
Ensure-InstructionFile -Path (Join-Path $projectRoot 'geometry_engine/primitives/coordinates.py') -Content $coordinatesModule
Ensure-InstructionFile -Path (Join-Path $projectRoot 'geometry_engine/primitives/topology.py') -Content $topologyModule
Ensure-InstructionFile -Path (Join-Path $projectRoot 'geometry_engine/features/__init__.py') -Content $emptyPythonModule
Ensure-InstructionFile -Path (Join-Path $projectRoot 'geometry_engine/features/feature_catalog.py') -Content $featureCatalogModule
Ensure-InstructionFile -Path (Join-Path $projectRoot 'geometry_engine/features/patterns.py') -Content $patternsModule
Ensure-InstructionFile -Path (Join-Path $projectRoot 'geometry_engine/profiles/__init__.py') -Content $emptyPythonModule
Ensure-InstructionFile -Path (Join-Path $projectRoot 'geometry_engine/profiles/boundary.py') -Content $boundaryModule
Ensure-InstructionFile -Path (Join-Path $projectRoot 'geometry_engine/profiles/height_map.py') -Content $heightMapModule
Ensure-InstructionFile -Path (Join-Path $projectRoot 'geometry_engine/manufacturing/__init__.py') -Content $emptyPythonModule
Ensure-InstructionFile -Path (Join-Path $projectRoot 'geometry_engine/manufacturing/clearances.py') -Content $clearancesModule
Ensure-InstructionFile -Path (Join-Path $projectRoot 'geometry_engine/manufacturing/printability.py') -Content $printabilityModule
Ensure-InstructionFile -Path (Join-Path $projectRoot 'geometry_engine/exporters/__init__.py') -Content $emptyPythonModule
Ensure-InstructionFile -Path (Join-Path $projectRoot 'geometry_engine/exporters/openscad.py') -Content $openscadExporterModule
Ensure-InstructionFile -Path (Join-Path $projectRoot 'geometry_engine/exporters/cadquery.py') -Content $cadqueryExporterModule

Initialize-GitRepository -Path $projectRoot

Write-Host ''
Write-Host 'CAD project structure is ready:' -ForegroundColor Green
Write-Host $projectRoot
