from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validation_utils import assert_mesh_basics, load_config, require_mesh, run_check_command


class ManifoldTests(unittest.TestCase):
    def test_mesh_basics_and_winding(self) -> None:
        mesh = require_mesh(self)
        assert_mesh_basics(self, mesh)

    def test_watertightness(self) -> None:
        config = load_config()
        if not config.get("require_watertight", True):
            self.skipTest("Watertightness is not required for this project")
        mesh = require_mesh(self)
        self.assertTrue(bool(mesh.is_watertight), "Mesh is not watertight")

    def test_connected_components(self) -> None:
        config = load_config()
        maximum = config.get("max_connected_components")
        if maximum is None:
            self.skipTest("max_connected_components is not configured")
        mesh = require_mesh(self)
        self.assertLessEqual(int(mesh.body_count), int(maximum), "Mesh has more disconnected solids than allowed")

    def test_project_self_intersection_check(self) -> None:
        run_check_command(self, "self_intersections")


if __name__ == "__main__":
    unittest.main()
