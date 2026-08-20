"""Build ATH_08_THROTTLE_SLIDER from the authoritative CadQuery model."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cadquery as cq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from geometry_engine.aero_throttle import AeroThrottleParameters, phase2_ath08


def main() -> int:
    parameters = AeroThrottleParameters(material="PETG")
    slider = phase2_ath08(parameters)
    stem = "ATH_08_THROTTLE_SLIDER"
    for directory, extension in ((PROJECT_ROOT / "output/stl", ".stl"), (PROJECT_ROOT / "output/step", ".step")):
        directory.mkdir(parents=True, exist_ok=True)
        cq.exporters.export(slider, str(directory / f"{stem}{extension}"))
    preview_dir = PROJECT_ROOT / "output/preview"
    preview_dir.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(slider, str(preview_dir / f"{stem}.svg"))
    report_dir = PROJECT_ROOT / "output/reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = parameters.report()
    report["material_allocation"] = {"ATH_08": "PETG"}
    report["throttle_petg_resolve"] = {
        "leaf_topology": "two-arm folded U leaf",
        "developed_length_mm": parameters.throttle_leaf_len,
        "width_mm": parameters.throttle_leaf_width_active,
        "thickness_mm": parameters.throttle_leaf_thick_active,
        "plate_thickness_mm": parameters.throttle_carriage_plate_t_active,
        "tab_thickness_mm": parameters.throttle_tab_h_z,
        "break_force_n": parameters.throttle_break_force_computed_n,
        "cyclic_stress_mpa": parameters.throttle_leaf_stress_mpa,
        "rest_stress_mpa": parameters.throttle_leaf_rest_stress_mpa,
    }
    (report_dir / "parameters-phase2-ath08.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (report_dir / "phase2-ath08-manifest.json").write_text(json.dumps({
        "phase": 2,
        "component": stem,
        "engine": "CadQuery/OCCT",
        "material": "PETG",
        "exports": ["STL", "STEP", "SVG preview"],
    }, indent=2) + "\n", encoding="utf-8")
    print("PHASE 2 ATH_08 BUILD: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
