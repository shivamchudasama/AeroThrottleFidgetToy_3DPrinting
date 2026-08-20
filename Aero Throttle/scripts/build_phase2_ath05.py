"""Build ATH_05_FIRE_BUTTON_PLUNGER from the authoritative CadQuery model."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cadquery as cq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from geometry_engine.aero_throttle import AeroThrottleParameters, phase2_ath05


def main() -> int:
    parameters = AeroThrottleParameters(material="PETG")
    button = phase2_ath05(parameters)
    for directory, extension in ((PROJECT_ROOT / "output/stl", ".stl"), (PROJECT_ROOT / "output/step", ".step")):
        directory.mkdir(parents=True, exist_ok=True)
        cq.exporters.export(button, str(directory / f"ATH_05_FIRE_BUTTON_PLUNGER{extension}"))
    preview_dir = PROJECT_ROOT / "output/preview"
    preview_dir.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(button, str(preview_dir / "ATH_05_FIRE_BUTTON_PLUNGER.svg"))
    report_dir = PROJECT_ROOT / "output/reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = parameters.report()
    report["material_allocation"] = {"ATH_05": "PETG"}
    report["fire_button_petg_resolve"] = {
        "topology": "six laterally folded arc spans in the XY spring plane",
        "anchor_rear_x_mm": parameters.serpentine_anchor_rear_x,
        "spring_depth_mm": parameters.serpentine_beam_t_active,
        "spring_width_mm": parameters.serpentine_beam_w_active,
        "full_stroke_force_n": parameters.serpentine_force_n,
        "cyclic_stress_mpa": parameters.serpentine_stress_mpa,
    }
    (report_dir / "parameters-phase2-ath05.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (report_dir / "phase2-ath05-manifest.json").write_text(json.dumps({
        "phase": 2,
        "component": "ATH_05_FIRE_BUTTON_PLUNGER",
        "engine": "CadQuery/OCCT",
        "material": "PETG",
        "exports": ["STL", "STEP", "SVG preview"],
    }, indent=2) + "\n", encoding="utf-8")
    print("PHASE 2 ATH_05 BUILD: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
