#!/usr/bin/env python3
"""Entry point: python run.py [train|ingest|versions] — see README.txt."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent


def run(cmd: list[str]) -> int:
    return subprocess.call(cmd, cwd=str(repo_root()))


def main() -> int:
    p = argparse.ArgumentParser(description="run.py")
    p.add_argument(
        "command",
        nargs="?",
        default="train",
        choices=("train", "ingest", "versions"),
        help="train | ingest | versions",
    )
    args = p.parse_args()
    root = repo_root()
    py = sys.executable

    if args.command == "train":
        script = root / "scripts" / "train_models.py"
        if not script.is_file():
            print(f"[run.py] Missing {script}", file=sys.stderr)
            return 1
        return run([py, str(script)])

    if args.command == "ingest":
        script = root / "scripts" / "ingest_data.py"
        if not script.is_file():
            print(f"[run.py] Missing {script}", file=sys.stderr)
            return 1
        return run([py, str(script), "--fetch-only", "--no-node"])

    if args.command == "versions":
        v = root / "versions.py"
        if not v.is_file():
            print(f"[run.py] Missing {v}", file=sys.stderr)
            return 1
        return run([py, str(v)])

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
