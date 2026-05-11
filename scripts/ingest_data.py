#!/usr/bin/env python3
"""Manifest fetch + optional npm. From repo root: python scripts/ingest_data.py"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def node_ingestion(root: Path, skip: bool) -> int:
    if skip:
        return 0
    node = shutil.which("node")
    if not node:
        return 0
    node_dir = root / "scripts" / "nodejs"
    node_dir.mkdir(parents=True, exist_ok=True)
    (node_dir / "graphQlData").mkdir(exist_ok=True)
    (node_dir / "repos").mkdir(exist_ok=True)
    if not (node_dir / "package.json").is_file():
        return 0
    env_file = node_dir / ".env"
    example = node_dir / ".env.example"
    if not env_file.exists() and example.exists():
        shutil.copy(example, env_file)
    r = subprocess.run(["npm", "install"], cwd=str(node_dir), check=False)
    if r.returncode != 0:
        print("[ingest] npm install failed.", file=sys.stderr, flush=True)
        return r.returncode
    return 0


def fetch_ingestion(root: Path, skip: bool) -> int:
    if skip:
        return 0
    fetcher = root / "scripts" / "python" / "fetch_datasets.py"
    if not fetcher.is_file():
        print(f"[ingest] missing {fetcher}", file=sys.stderr, flush=True)
        return 1
    r = subprocess.run([sys.executable, str(fetcher)], cwd=str(root), check=False)
    return r.returncode


def main() -> int:
    p = argparse.ArgumentParser(description="ingest_data.py")
    p.add_argument("--no-node", action="store_true")
    p.add_argument("--no-fetch", action="store_true")
    p.add_argument("--node-only", action="store_true")
    p.add_argument("--fetch-only", action="store_true")
    args = p.parse_args()

    root = repo_root()
    os.chdir(root)

    skip_node = args.no_node or args.fetch_only
    skip_fetch = args.no_fetch or args.node_only
    if os.environ.get("SKIP_DATASET_FETCH", "").strip() in ("1", "true", "True"):
        skip_fetch = True

    code = node_ingestion(root, skip=skip_node)
    if code != 0:
        return code
    code = fetch_ingestion(root, skip=skip_fetch)
    if code != 0:
        return code

    print("[ingest] ok — run: python run.py", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
