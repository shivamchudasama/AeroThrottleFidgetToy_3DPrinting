from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validation_utils import load_config, require_mesh


class VolumeTests(unittest.TestCase):
    def test_non_zero_volume(self) -> None:
        mesh = require_mesh(self)
        self.assertGreater(float(mesh.volume), 0.0, "Mesh must have non-zero volume")

    def test_volume_limits(self) -> None:
        config = load_config()
        minimum = config.get("min_volume_mm3")
        maximum = config.get("max_volume_mm3")
        if minimum is None and maximum is None:
            self.skipTest("No volume limits are configured")
        mesh = require_mesh(self)
        volume = float(mesh.volume)
        if minimum is not None:
            self.assertGreaterEqual(volume, float(minimum), "Mesh volume is below the approved minimum")
        if maximum is not None:
            self.assertLessEqual(volume, float(maximum), "Mesh volume exceeds the approved maximum")


if __name__ == "__main__":
    unittest.main()
