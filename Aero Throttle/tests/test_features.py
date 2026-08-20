from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validation_utils import run_check_command


class FeatureTests(unittest.TestCase):
    def test_required_features_and_relationships(self) -> None:
        run_check_command(self, "features")


if __name__ == "__main__":
    unittest.main()
