#!/usr/bin/env python3
"""
1/2 — Data ingestion: Node.js API tooling (optional) + dataset fetch from manifests.

Replaces the former split between setup_local.sh and fetch_datasets.sh.
Run from repository root:  python3 scripts/ingest_data.py
"""
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
        print("[ingest] Skipping Node.js / npm setup (--no-node or --fetch-only).", flush=True)
        return 0
    node = shutil.which("node")
    if not node:
        print(
            "[ingest] Node.js not found; skipping npm install. "
            "Install Node LTS if you need GitHub REST/GraphQL collectors.",
            file=sys.stderr,
            flush=True,
        )
        return 0
    node_dir = root / "scripts" / "nodejs"
    node_dir.mkdir(parents=True, exist_ok=True)
    (node_dir / "graphQlData").mkdir(exist_ok=True)
    (node_dir / "repos").mkdir(exist_ok=True)
    if not (node_dir / "package.json").is_file():
        print(
            "[ingest] scripts/nodejs/ has no package.json — skipping npm install. "
            "Restore scripts/nodejs from the repository (see README Node section).",
            file=sys.stderr,
            flush=True,
        )
        return 0
    env_file = node_dir / ".env"
    example = node_dir / ".env.example"
    if not env_file.exists() and example.exists():
        shutil.copy(example, env_file)
        print(f"[ingest] Created {env_file} from .env.example — add TOKEN etc. if using collectors.", flush=True)
    print("[ingest] npm install (scripts/nodejs)…", flush=True)
    r = subprocess.run(["npm", "install"], cwd=str(node_dir), check=False)
    if r.returncode != 0:
        print("[ingest] npm install failed.", file=sys.stderr, flush=True)
        return r.returncode
    return 0


def fetch_ingestion(root: Path, skip: bool) -> int:
    if skip:
        print("[ingest] Skipping dataset fetch (--no-fetch or SKIP_DATASET_FETCH).", flush=True)
        return 0
    fetcher = root / "scripts" / "python" / "fetch_datasets.py"
    if not fetcher.is_file():
        print(f"[ingest] Missing {fetcher}", file=sys.stderr, flush=True)
        return 1
    print("[ingest] Running manifest fetch (datasets/manifest.json)…", flush=True)
    r = subprocess.run([sys.executable, str(fetcher)], cwd=str(root), check=False)
    if r.returncode != 0:
        print(
            "[ingest] fetch_datasets exited non-zero. "
            "Try SKIP_DATASET_FETCH=1 or see datasets/README.md.",
            file=sys.stderr,
            flush=True,
        )
    return r.returncode


def main() -> int:
    p = argparse.ArgumentParser(description="Data ingestion: Node tooling + dataset downloads.")
    p.add_argument("--no-node", action="store_true", help="Skip npm install and .env bootstrap under scripts/nodejs/.")
    p.add_argument("--no-fetch", action="store_true", help="Skip datasets/manifest.json fetch.")
    p.add_argument("--node-only", action="store_true", help="Only Node/npm setup (no manifest fetch).")
    p.add_argument("--fetch-only", action="store_true", help="Only manifest fetch (no Node/npm).")
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

    print(
        "[ingest] Done. Next: python3 scripts/train_models.py   (or open notebooks in Jupyter).",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
