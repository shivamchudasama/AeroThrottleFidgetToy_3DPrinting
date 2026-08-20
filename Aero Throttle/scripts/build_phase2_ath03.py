"""Build the first Phase 2 PETG subsystem: ATH_03_FRONT_BEZEL_FACEPLATE."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cadquery as cq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from geometry_engine.aero_throttle import AeroThrottleParameters, phase2_ath03


def main() -> int:
    parameters = AeroThrottleParameters(material="PETG")
    bezel = phase2_ath03(parameters)
    for directory, extension in ((PROJECT_ROOT / "output/stl", ".stl"), (PROJECT_ROOT / "output/step", ".step")):
        directory.mkdir(parents=True, exist_ok=True)
        cq.exporters.export(bezel, str(directory / f"ATH_03_FRONT_BEZEL_FACEPLATE{extension}"))
    preview_dir = PROJECT_ROOT / "output/preview"
    preview_dir.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(bezel, str(preview_dir / "ATH_03_FRONT_BEZEL_FACEPLATE.svg"))
    report_dir = PROJECT_ROOT / "output/reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = parameters.report()
    report["material_allocation"] = {"ATH_03": "PETG"}
    report["guard_cam_tuning"] = {
        "status": "first_article_tuning",
        "approved_leaf_width_mm": parameters.guard_cam_leaf_w,
        "target_holding_torque_nmm": None,
    }
    (report_dir / "parameters-phase2-ath03.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (report_dir / "phase2-ath03-manifest.json").write_text(json.dumps({
        "phase": 2,
        "component": "ATH_03_FRONT_BEZEL_FACEPLATE",
        "engine": "CadQuery/OCCT",
        "material": "PETG",
        "exports": ["STL", "STEP", "SVG preview"],
    }, indent=2) + "\n", encoding="utf-8")
    print("PHASE 2 ATH_03 BUILD: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
