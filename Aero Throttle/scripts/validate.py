"""Run CAD validation tests and write a machine-readable report."""

from __future__ import annotations

import argparse
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ReportingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.records.append({"test": test.id(), "status": "PASS"})

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.records.append({"test": test.id(), "status": "SKIP", "reason": reason})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.records.append({"test": test.id(), "status": "FAIL", "details": self._exc_info_to_string(err, test)})

    def addError(self, test, err):
        super().addError(test, err)
        self.records.append({"test": test.id(), "status": "ERROR", "details": self._exc_info_to_string(err, test)})


class ReportingRunner(unittest.TextTestRunner):
    resultclass = ReportingResult


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", default="output/reports/validation-report.json")
    parser.add_argument("--verbosity", type=int, default=2)
    args = parser.parse_args()

    suite = unittest.defaultTestLoader.discover(str(PROJECT_ROOT / "tests"), pattern="test_*.py")
    result = ReportingRunner(verbosity=args.verbosity).run(suite)
    passed = result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
    status = "PASS" if result.wasSuccessful() and passed else "INCOMPLETE" if result.wasSuccessful() else "FAIL"

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "tests_run": result.testsRun,
        "passed": passed,
        "failed": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "results": result.records,
    }
    report_path = PROJECT_ROOT / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\nCAD VALIDATION RESULT: {status}")
    print(f"Report: {report_path}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
