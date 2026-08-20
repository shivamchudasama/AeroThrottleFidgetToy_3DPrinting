"""Build ATH_04_MISSILE_SAFETY_GUARD from the authoritative CadQuery model."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cadquery as cq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from geometry_engine.aero_throttle import AeroThrottleParameters, phase2_ath04


def main() -> int:
    parameters = AeroThrottleParameters(material="PETG")
    guard = phase2_ath04(parameters)
    for directory, extension in ((PROJECT_ROOT / "output/stl", ".stl"), (PROJECT_ROOT / "output/step", ".step")):
        directory.mkdir(parents=True, exist_ok=True)
        cq.exporters.export(guard, str(directory / f"ATH_04_MISSILE_SAFETY_GUARD{extension}"))
    preview_dir = PROJECT_ROOT / "output/preview"
    preview_dir.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(guard, str(preview_dir / "ATH_04_MISSILE_SAFETY_GUARD.svg"))
    report_dir = PROJECT_ROOT / "output/reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = parameters.report()
    report["material_allocation"] = {"ATH_04": "PETG"}
    report["guard_hinge_bbox_exemption"] = {
        "hood_z_bounds_mm": [-parameters.guard_hood_w / 2, parameters.guard_hood_w / 2],
        "pin_z_bounds_mm": [-parameters.guard_pin_outer_z, parameters.guard_pin_outer_z],
        "cam_can_extend_beyond_hood_bounds": True,
        "approved_reason": "ATH_04 closed bounding box excludes the two hinge pins and dual-flat cam",
    }
    (report_dir / "parameters-phase2-ath04.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (report_dir / "phase2-ath04-manifest.json").write_text(json.dumps({
        "phase": 2,
        "component": "ATH_04_MISSILE_SAFETY_GUARD",
        "engine": "CadQuery/OCCT",
        "material": "PETG",
        "exports": ["STL", "STEP", "SVG preview"],
    }, indent=2) + "\n", encoding="utf-8")
    print("PHASE 2 ATH_04 BUILD: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
