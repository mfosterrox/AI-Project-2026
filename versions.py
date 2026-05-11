#!/usr/bin/env python3
"""Write package_versions.txt (pip freeze). Run inside project venv."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent
    out_path = root / "package_versions.txt"

    lines = [
        f"# Python: {sys.version}",
        f"# Executable: {sys.executable}",
        "",
        "# pip freeze output:",
        "",
    ]

    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=True,
        )
        lines.append(proc.stdout.rstrip() + "\n")
    except subprocess.CalledProcessError as e:
        print(e.stderr or str(e), file=sys.stderr)
        return 1

    text = "\n".join(lines)
    out_path.write_text(text, encoding="utf-8")
    print(text)
    print("Wrote", out_path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
