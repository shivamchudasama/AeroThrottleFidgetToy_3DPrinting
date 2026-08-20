from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validation_utils import assert_mesh_basics, load_config, require_mesh, run_sweep_command


class ParametricExtremeTests(unittest.TestCase):
    def test_configured_parameter_sweeps(self) -> None:
        sweeps = load_config().get("parametric_sweeps", [])
        if not sweeps:
            self.skipTest("No parametric_sweeps are configured")

        for sweep in sweeps:
            with self.subTest(sweep=sweep.get("name", "<unnamed>")):
                run_sweep_command(sweep)
                mesh = require_mesh(self, sweep.get("mesh_path"))
                assert_mesh_basics(self, mesh, f"Sweep {sweep.get('name', '<unnamed>')}")
                self.assertTrue(bool(mesh.is_watertight), "Sweep mesh is not watertight")
                self.assertGreater(float(mesh.volume), 0.0, "Sweep mesh has zero volume")

                expected = sweep.get("expected_bounds_mm")
                if expected is not None:
                    tolerance = float(sweep.get("bounds_tolerance_mm", 0.1))
                    for actual, target in zip(mesh.extents, expected):
                        self.assertAlmostEqual(float(actual), float(target), delta=tolerance)

                minimum = sweep.get("min_volume_mm3")
                maximum = sweep.get("max_volume_mm3")
                if minimum is not None:
                    self.assertGreaterEqual(float(mesh.volume), float(minimum))
                if maximum is not None:
                    self.assertLessEqual(float(mesh.volume), float(maximum))


if __name__ == "__main__":
    unittest.main()
