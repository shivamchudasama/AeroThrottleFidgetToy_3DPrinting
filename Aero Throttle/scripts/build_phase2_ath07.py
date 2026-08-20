"""Build ATH_07_ROTARY_TRIM_WHEEL from the authoritative CadQuery model."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cadquery as cq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from geometry_engine.aero_throttle import AeroThrottleParameters, phase2_ath07


def main() -> int:
    parameters = AeroThrottleParameters(material="PLA_PLUS")
    wheel = phase2_ath07(parameters)
    for directory, extension in ((PROJECT_ROOT / "output/stl", ".stl"), (PROJECT_ROOT / "output/step", ".step")):
        directory.mkdir(parents=True, exist_ok=True)
        cq.exporters.export(wheel, str(directory / f"ATH_07_ROTARY_TRIM_WHEEL{extension}"))
    preview_dir = PROJECT_ROOT / "output/preview"
    preview_dir.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(wheel, str(preview_dir / "ATH_07_ROTARY_TRIM_WHEEL.svg"))
    report_dir = PROJECT_ROOT / "output/reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = parameters.report()
    report["material_allocation"] = {"ATH_07": "Matte PLA"}
    report["trim_wheel"] = {
        "axis_datum_k_mm": [parameters.trim_wheel_center_x, parameters.trim_wheel_center_y],
        "rotor_od_mm": parameters.trim_wheel_od,
        "rotor_width_mm": parameters.trim_wheel_width,
        "rotary_clearance_per_side_mm": parameters.fit_clearance_rotary,
        "ratchet_teeth_count": parameters.ratchet_teeth_count,
        "ratchet_pitch_radius_mm": parameters.ratchet_pitch_r,
        "ratchet_included_angle_deg": parameters.ratchet_incl_angle_deg,
        "hub_web_mm": parameters.wall_internal,
        "pawl_analysis_material": "PLA_PLUS",
        "pawl_torque_nmm": parameters.pawl_torque_nmm,
        "pawl_cyclic_stress_mpa": parameters.pawl_stress_mpa,
        "pawl_rest_stress_mpa": parameters.pawl_rest_stress_mpa,
    }
    (report_dir / "parameters-phase2-ath07.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (report_dir / "phase2-ath07-manifest.json").write_text(json.dumps({
        "phase": 2,
        "component": "ATH_07_ROTARY_TRIM_WHEEL",
        "engine": "CadQuery/OCCT",
        "material": "Matte PLA",
        "exports": ["STL", "STEP", "SVG preview"],
    }, indent=2) + "\n", encoding="utf-8")
    print("PHASE 2 ATH_07 BUILD: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
