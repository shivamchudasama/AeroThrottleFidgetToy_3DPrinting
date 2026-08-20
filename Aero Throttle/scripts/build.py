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
