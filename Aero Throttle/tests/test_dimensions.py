from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validation_utils import load_config, require_mesh


class DimensionTests(unittest.TestCase):
    def test_expected_bounding_box(self) -> None:
        config = load_config()
        expected = config.get("expected_bounds_mm")
        if expected is None:
            self.skipTest("expected_bounds_mm is not configured")
        self.assertEqual(len(expected), 3, "expected_bounds_mm must contain [X, Y, Z]")
        mesh = require_mesh(self)
        tolerance = float(config.get("bounds_tolerance_mm", 0.1))
        for axis, actual, target in zip("XYZ", mesh.extents, expected):
            self.assertAlmostEqual(float(actual), float(target), delta=tolerance, msg=f"{axis} dimension differs from specification")

    def test_expected_minimum_position(self) -> None:
        config = load_config()
        expected = config.get("expected_minimum_mm")
        if expected is None:
            self.skipTest("expected_minimum_mm is not configured")
        self.assertEqual(len(expected), 3, "expected_minimum_mm must contain [X, Y, Z]")
        mesh = require_mesh(self)
        tolerance = float(config.get("bounds_tolerance_mm", 0.1))
        for axis, actual, target in zip("XYZ", mesh.bounds[0], expected):
            self.assertAlmostEqual(float(actual), float(target), delta=tolerance, msg=f"{axis} minimum position differs from specification")


if __name__ == "__main__":
    unittest.main()
