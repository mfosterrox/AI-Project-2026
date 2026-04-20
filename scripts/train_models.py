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


def check_tensorflow_runtime() -> int:
    """TensorFlow has no official wheels for Python 3.14+; requirements-local skips installing it."""
    if sys.version_info >= (3, 14):
        print(
            "[train] Python 3.14+ cannot run this notebook: TensorFlow has no PyPI wheels yet.\n"
            "[train] Recreate the venv with Python 3.12 or 3.13, then reinstall deps, e.g.:\n"
            "        brew install python@3.12\n"
            "        /opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv\n"
            "        source .venv/bin/activate && pip install -r requirements-local.txt\n"
            "        python3 scripts/train_models.py",
            file=sys.stderr,
        )
        return 1
    try:
        import tensorflow  # noqa: F401
    except ImportError:
        print(
            "[train] tensorflow is not installed. Use Python 3.10–3.13 and: pip install -r requirements-local.txt",
            file=sys.stderr,
        )
        return 1
    return 0


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
    p.add_argument(
        "--skip-preflight",
        action="store_true",
        help="Skip TensorFlow / Python version check (not recommended).",
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
        if sys.version_info >= (3, 14):
            print(
                "\n[train] Note: your default python is 3.14+ — open the notebook with a 3.12/3.13 kernel "
                "or TensorFlow imports will fail.",
                file=sys.stderr,
            )
        return 0

    if not args.skip_preflight:
        pre = check_tensorflow_runtime()
        if pre != 0:
            return pre

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
