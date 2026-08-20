"""Generate the configured preview image."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cad_config import command_for, export_path, load_cad_config, run_command


def main() -> int:
    config = load_cad_config()
    preview = export_path(config, "preview")
    preview.parent.mkdir(parents=True, exist_ok=True)
    command = command_for(config, "preview")
    if not command:
        print("PREVIEW: SKIPPED (configure commands.preview in cad_config.json)")
        return 0
    run_command(command, "preview export")
    if not preview.is_file():
        raise RuntimeError(f"Preview command completed without creating {preview}")
    print(f"PREVIEW: PASS ({preview})")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"PREVIEW: FAIL - {error}", file=sys.stderr)
        raise SystemExit(1)
