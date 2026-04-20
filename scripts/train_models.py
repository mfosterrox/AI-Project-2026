#!/usr/bin/env python3
"""
2/2 — Model training: executes the training notebook headlessly (or prints how to run interactively).

Default: jupyter nbconvert --execute notebooks/training_models.ipynb
Run from repository root:  python3 scripts/train_models.py
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def main() -> int:
    p = argparse.ArgumentParser(description="Train / evaluate models via the training notebook.")
    p.add_argument(
        "--notebook",
        type=Path,
        default=None,
        help="Path to notebook (default: notebooks/training_models.ipynb).",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Where to write executed notebook (default: notebooks/_executed).",
    )
    p.add_argument(
        "--interactive",
        action="store_true",
        help="Do not execute; print how to open Jupyter on the training notebook.",
    )
    args = p.parse_args()

    root = repo_root()
    nb = (args.notebook or (root / "notebooks" / "training_models.ipynb")).resolve()
    if not nb.is_file():
        print(f"[train] Notebook not found: {nb}", file=sys.stderr)
        return 1

    if args.interactive:
        print("[train] Open in Jupyter, from repo root:")
        print(f"       jupyter notebook {nb.relative_to(root)}")
        return 0

    out_dir = (args.output_dir or (root / "notebooks" / "_executed")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    jupyter = shutil.which("jupyter")
    if not jupyter:
        print(
            "[train] `jupyter` not on PATH. Install requirements-local.txt then use --interactive,",
            file=sys.stderr,
        )
        return 1

    cmd = [
        jupyter,
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        str(nb),
        "--output-dir",
        str(out_dir),
        "--output",
        f"{nb.stem}.executed.ipynb",
    ]
    print("[train]", " ".join(cmd))
    r = subprocess.run(cmd, cwd=str(root), check=False)
    if r.returncode != 0:
        print("[train] nbconvert failed.", file=sys.stderr)
        return r.returncode
    print(f"[train] Wrote executed notebook under {out_dir.relative_to(root)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
