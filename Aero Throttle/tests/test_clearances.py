from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validation_utils import run_check_command


class ClearanceTests(unittest.TestCase):
    def test_clearances_and_manufacturing_constraints(self) -> None:
        run_check_command(self, "clearances")


if __name__ == "__main__":
    unittest.main()
