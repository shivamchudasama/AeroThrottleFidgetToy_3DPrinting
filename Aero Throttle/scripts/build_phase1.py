"""Export the Phase 1 CadQuery structural-root components and evidence."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cadquery as cq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from geometry_engine.aero_throttle import AeroThrottleParameters, phase1_components


def export_shape(shape: cq.Workplane, stem: str) -> None:
    for directory, extension in ((PROJECT_ROOT / "output/stl", ".stl"), (PROJECT_ROOT / "output/step", ".step")):
        directory.mkdir(parents=True, exist_ok=True)
        cq.exporters.export(shape, str(directory / f"{stem}{extension}"))


def main() -> int:
    params = AeroThrottleParameters()
    parts = phase1_components(params)
    for part_id, part in parts.items():
        export_shape(part, part_id)
    assembly = parts["ATH_01"].union(parts["ATH_02"])
    export_shape(assembly, "ATH_PHASE1_STRUCTURAL_ASSEMBLY")
    preview_dir = PROJECT_ROOT / "output/preview"
    preview_dir.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(assembly, str(preview_dir / "ATH_PHASE1_STRUCTURAL_ASSEMBLY.svg"))
    report_dir = PROJECT_ROOT / "output/reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "parameters-phase1.json").write_text(json.dumps(params.report(), indent=2) + "\n", encoding="utf-8")
    (report_dir / "phase1-manifest.json").write_text(json.dumps({
        "phase": 1,
        "engine": "CadQuery/OCCT",
        "materials": {"ATH_01": "Matte PLA", "ATH_02": "Matte PLA", "ATH_10": "Matte PLA"},
        "exports": sorted(parts),
    }, indent=2) + "\n", encoding="utf-8")
    print("PHASE 1 BUILD: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
