"""Build ATH_09_DUAL_TRIGGER from the authoritative CadQuery model."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cadquery as cq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from geometry_engine.aero_throttle import AeroThrottleParameters, phase2_ath09


def main() -> int:
    parameters = AeroThrottleParameters(material="PETG")
    trigger = phase2_ath09(parameters)
    stem = "ATH_09_DUAL_TRIGGER"
    for directory, extension in ((PROJECT_ROOT / "output/stl", ".stl"), (PROJECT_ROOT / "output/step", ".step")):
        directory.mkdir(parents=True, exist_ok=True)
        cq.exporters.export(trigger, str(directory / f"{stem}{extension}"))
    preview_dir = PROJECT_ROOT / "output/preview"
    preview_dir.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(trigger, str(preview_dir / f"{stem}.svg"))
    report_dir = PROJECT_ROOT / "output/reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = parameters.report()
    report["material_allocation"] = {"ATH_09": "PETG"}
    report["trigger_petg_resolve"] = {
        "stage1_topology": "curved XY return leaf",
        "stage1_developed_length_mm": parameters.trigger_stage1_len,
        "stage1_width_mm": parameters.trigger_stage1_width_active,
        "stage1_thickness_mm": parameters.trigger_stage1_thick_active,
        "stage1_force_n": parameters.trigger_stage1_force_computed_n,
        "stage1_cyclic_stress_mpa": parameters.trigger_stage1_stress_mpa,
        "stage2_topology": "XY gate tooth",
        "stage2_length_mm": parameters.trigger_stage2_len,
        "stage2_width_mm": parameters.trigger_stage2_width_active,
        "stage2_thickness_mm": parameters.trigger_stage2_thick_active,
        "stage2_cyclic_stress_mpa": parameters.trigger_stage2_stress_mpa,
        "derived_tooth_radius_mm": parameters.trigger_tooth_r,
        "break_force_n": parameters.trigger_break_force_computed_n,
    }
    (report_dir / "parameters-phase2-ath09.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (report_dir / "phase2-ath09-manifest.json").write_text(json.dumps({
        "phase": 2,
        "component": stem,
        "engine": "CadQuery/OCCT",
        "material": "PETG",
        "exports": ["STL", "STEP", "SVG preview"],
    }, indent=2) + "\n", encoding="utf-8")
    print("PHASE 2 ATH_09 BUILD: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
