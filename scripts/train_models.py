#!/usr/bin/env python3
"""Run notebooks/training_models.ipynb via nbconvert (from repo root: python3 scripts/train_models.py)."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def check_tensorflow_runtime() -> int:
    if sys.version_info >= (3, 14):
        print("[train] Need Python 3.12 or 3.13 for TensorFlow. See README.md", file=sys.stderr)
        return 1
    try:
        import tensorflow  # noqa: F401
    except ImportError:
        print("[train] pip install -r requirements-local.txt (Python 3.12/3.13)", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Execute notebooks/training_models.ipynb")
    p.add_argument("--notebook", type=Path, default=None)
    p.add_argument("--output-dir", type=Path, default=None)
    p.add_argument("--interactive", action="store_true", help="Print jupyter command only")
    p.add_argument("--skip-preflight", action="store_true")
    args = p.parse_args()

    root = repo_root()
    nb = (args.notebook or (root / "notebooks" / "training_models.ipynb")).resolve()
    if not nb.is_file():
        print(f"[train] Notebook not found: {nb}", file=sys.stderr)
        return 1

    if args.interactive:
        print(f"jupyter notebook {nb.relative_to(root)}")
        return 0

    if not args.skip_preflight:
        pre = check_tensorflow_runtime()
        if pre != 0:
            return pre

    out_dir = (args.output_dir or (root / "notebooks" / "_executed")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    jupyter = shutil.which("jupyter")
    if not jupyter:
        print("[train] jupyter not found; pip install -r requirements-local.txt", file=sys.stderr)
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
    r = subprocess.run(cmd, cwd=str(root), check=False)
    if r.returncode != 0:
        return r.returncode
    print(out_dir / f"{nb.stem}.executed.ipynb")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
