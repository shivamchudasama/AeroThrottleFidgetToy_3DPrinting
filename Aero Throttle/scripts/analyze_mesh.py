"""Print a machine-readable summary of an STL/mesh file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validation_utils import assert_mesh_basics, project_path, require_mesh


class MeshCheck:
    def skipTest(self, message: str) -> None:
        raise RuntimeError(message)

    def assertGreater(self, actual: float, expected: float, message: str) -> None:
        if not actual > expected:
            raise RuntimeError(message)

    def assertTrue(self, value: bool, message: str) -> None:
        if not value:
            raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mesh", nargs="?", help="Mesh path relative to the project root")
    args = parser.parse_args()

    try:
        mesh = require_mesh(MeshCheck(), args.mesh)
        assert_mesh_basics(MeshCheck(), mesh)
    except RuntimeError as error:
        print(f"ANALYSIS: FAIL\n{error}", file=sys.stderr)
        return 2

    summary = {
        "mesh_path": str(project_path(args.mesh)) if args.mesh else None,
        "bounds_mm": [float(value) for value in mesh.extents],
        "minimum_mm": [float(value) for value in mesh.bounds[0]],
        "maximum_mm": [float(value) for value in mesh.bounds[1]],
        "volume_mm3": float(mesh.volume),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "connected_components": int(mesh.body_count),
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
