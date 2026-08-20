"""Build ATH_06_4WAY_HAT_SWITCH from the authoritative CadQuery model."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cadquery as cq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from geometry_engine.aero_throttle import AeroThrottleParameters, phase2_ath06


def main() -> int:
    parameters = AeroThrottleParameters(material="PETG")
    hat = phase2_ath06(parameters)
    for directory, extension in ((PROJECT_ROOT / "output/stl", ".stl"), (PROJECT_ROOT / "output/step", ".step")):
        directory.mkdir(parents=True, exist_ok=True)
        cq.exporters.export(hat, str(directory / f"ATH_06_4WAY_HAT_SWITCH{extension}"))
    preview_dir = PROJECT_ROOT / "output/preview"
    preview_dir.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(hat, str(preview_dir / "ATH_06_4WAY_HAT_SWITCH.svg"))
    report_dir = PROJECT_ROOT / "output/reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = parameters.report()
    report["material_allocation"] = {"ATH_06": "PETG"}
    report["hat_petg_resolve"] = {
        "topology": "two-level alternating star: opposite arms per plane",
        "arm_planes_y_mm": [parameters.hat_lower_arm_y, parameters.hat_upper_arm_y],
        "arm_width_mm": parameters.hat_spring_arm_width_active,
        "arm_thickness_mm": parameters.hat_spring_arm_thick_active,
        "developed_length_mm": parameters.hat_spring_arm_len,
        "force_at_14_deg_n": parameters.hat_force_computed_n,
        "cyclic_stress_mpa": parameters.hat_stress_mpa,
    }
    (report_dir / "parameters-phase2-ath06.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (report_dir / "phase2-ath06-manifest.json").write_text(json.dumps({
        "phase": 2,
        "component": "ATH_06_4WAY_HAT_SWITCH",
        "engine": "CadQuery/OCCT",
        "material": "PETG",
        "exports": ["STL", "STEP", "SVG preview"],
    }, indent=2) + "\n", encoding="utf-8")
    print("PHASE 2 ATH_06 BUILD: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
