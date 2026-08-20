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
