#!/usr/bin/env python3
"""
Download / clone / snapshot datasets listed in datasets/manifest.json (version 2).

Invoked by ``scripts/ingest_data.py`` (do not need to run this file directly unless debugging).

Each source uses ``source_key`` (folder under datasets/downloads/) and is documented in
``datasets/sources/<source_key>/README.md``.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


SOURCE_LABEL = "manifest_orchestrator"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_manifest(root: Path) -> dict:
    path = root / "datasets" / "manifest.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def manifest_sources(manifest: dict) -> list[dict]:
    if isinstance(manifest.get("sources"), list):
        return manifest["sources"]
    # v1 compatibility
    return [
        {**a, "type": "http_github_raw"}
        for a in (manifest.get("artifacts") or [])
    ]


def env_truthy(name: str | None) -> bool:
    if not name:
        return False
    return os.environ.get(name, "").strip() in ("1", "true", "True", "yes", "YES")


def env_optional_enabled(spec: dict) -> bool:
    """Optional heavy fetchers require env_enable=1 or global FETCH_ENABLE_ALL_OPTIONAL=1."""
    if env_truthy("FETCH_ENABLE_ALL_OPTIONAL"):
        return True
    return env_truthy(spec.get("env_enable"))


def github_primary_url(owner: str, repo: str, ref: str, path_on_repo: str) -> str:
    path_on_repo = path_on_repo.lstrip("/")
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path_on_repo}"


def http_download(url: str, dest: Path, timeout: int = 300) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "AI-Project-2026-fetch_datasets/1.0"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    dest.write_bytes(data)
    return len(data)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_coordinates(manifest: dict) -> tuple[str, str, str]:
    coord = manifest.get("github_coordinates") or {}
    owner = os.environ.get(coord.get("owner_env", "DATA_GITHUB_OWNER"), "").strip()
    repo = os.environ.get(coord.get("repo_env", "DATA_GITHUB_REPO"), "").strip()
    ref = os.environ.get(coord.get("ref_env", "DATA_GITHUB_REF"), "").strip()
    if not owner:
        owner = (coord.get("default_owner") or "").strip()
    if not repo:
        repo = (coord.get("default_repo") or "").strip()
    if not ref:
        ref = (coord.get("default_ref") or "main").strip()
    return owner, repo, ref


def url_candidates(
    owner: str,
    repo: str,
    ref: str,
    primary_path: str,
    fallback_url: str | None,
    use_fallback: bool,
) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if owner and repo:
        out.append((github_primary_url(owner, repo, ref, primary_path), "primary"))
    if use_fallback and fallback_url and (fallback_url, "fallback") not in out:
        out.append((fallback_url, "fallback"))
    if not out:
        raise RuntimeError(
            "No URL available: set DATA_GITHUB_OWNER and DATA_GITHUB_REPO for your repo, "
            "or enable FETCH_USE_LEGACY_FALLBACK=1 with a manifest fallback_url."
        )
    return out


def fetch_http_github_raw(
    root: Path,
    spec: dict,
    owner: str,
    repo: str,
    ref: str,
    use_fallback: bool,
    downloads: Path,
    log: dict,
) -> None:
    aid = spec["id"]
    source_key = spec.get("source_key", "unknown")
    primary_path = spec["primary_path_on_repo"]
    fallback = spec.get("fallback_url")
    filename = spec["download_filename"]
    dest = downloads / source_key / filename

    try:
        candidates = url_candidates(
            owner, repo, ref, primary_path, fallback, use_fallback
        )
    except RuntimeError as e:
        print(f"[{aid}] skip: {e}", file=sys.stderr)
        log["artifacts"].append({"id": aid, "status": "skipped", "error": str(e)})
        return

    nbytes = -1
    url = ""
    label = ""
    for url, label in candidates:
        print(f"[{aid}] source_key={source_key} try ({label}) -> {url}")
        try:
            nbytes = http_download(url, dest)
            break
        except urllib.error.HTTPError as e:
            if e.code == 404 and url != candidates[-1][0]:
                print("    404; trying next candidate...")
                continue
            msg = f"HTTP {e.code} for {url}"
            print(f"[{aid}] {msg}", file=sys.stderr)
            log["artifacts"].append(
                {
                    "id": aid,
                    "status": "error",
                    "source_key": source_key,
                    "url_attempted": url,
                    "url_label": label,
                    "error": msg,
                }
            )
            return
        except urllib.error.URLError as e:
            msg = str(e.reason if hasattr(e, "reason") else e)
            print(f"[{aid}] URL error: {msg}", file=sys.stderr)
            log["artifacts"].append(
                {
                    "id": aid,
                    "status": "error",
                    "source_key": source_key,
                    "url_attempted": url,
                    "url_label": label,
                    "error": msg,
                }
            )
            return

    if nbytes < 0:
        return

    digest = sha256_file(dest)
    entry: dict = {
        "id": aid,
        "status": "ok",
        "type": "http_github_raw",
        "source_key": source_key,
        "data_source": source_key,
        "url": url,
        "url_label": label,
        "stored_relative": str(dest.relative_to(root)),
        "bytes": nbytes,
        "sha256": digest,
    }
    for rel in spec.get("notebook_copies") or []:
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dest, target)
        entry.setdefault("notebook_copies_written", []).append(rel)
    log["artifacts"].append(entry)
    print(f"    wrote {dest.relative_to(root)} ({nbytes} bytes)")


def fetch_kaggle_dataset(root: Path, spec: dict, downloads: Path, log: dict) -> None:
    aid = spec["id"]
    source_key = spec.get("source_key", "kaggle_github_repos")
    slug = spec["kaggle_slug"]
    dest_parent = downloads / source_key
    dest_parent.mkdir(parents=True, exist_ok=True)

    kaggle_bin = shutil.which("kaggle")
    if not kaggle_bin:
        log["artifacts"].append(
            {
                "id": aid,
                "status": "skipped",
                "type": "kaggle_dataset",
                "source_key": source_key,
                "error": "kaggle CLI not on PATH; pip install kaggle and configure ~/.kaggle/kaggle.json",
            }
        )
        print(f"[{aid}] skip: kaggle CLI not found", file=sys.stderr)
        return

    cmd = [
        kaggle_bin,
        "datasets",
        "download",
        "-d",
        slug,
        "-p",
        str(dest_parent),
        "--unzip",
    ]
    print(f"[{aid}] source_key={source_key} -> {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True, cwd=str(root))
    except subprocess.CalledProcessError as e:
        log["artifacts"].append(
            {
                "id": aid,
                "status": "error",
                "type": "kaggle_dataset",
                "source_key": source_key,
                "error": str(e),
            }
        )
        print(f"[{aid}] kaggle download failed: {e}", file=sys.stderr)
        return

    log["artifacts"].append(
        {
            "id": aid,
            "status": "ok",
            "type": "kaggle_dataset",
            "source_key": source_key,
            "data_source": source_key,
            "kaggle_slug": slug,
            "stored_directory": str(dest_parent.relative_to(root)),
        }
    )
    print(f"    completed Kaggle download into {dest_parent.relative_to(root)}")


def fetch_git_shallow_clone(root: Path, spec: dict, downloads: Path, log: dict) -> None:
    aid = spec["id"]
    source_key = spec.get("source_key", "github_advisory_database")
    git_url = spec["git_url"]
    target_dir = spec.get("target_dir", "repo")
    dest = downloads / source_key / target_dir

    if not shutil.which("git"):
        log["artifacts"].append(
            {
                "id": aid,
                "status": "skipped",
                "type": "git_shallow_clone",
                "error": "git not on PATH",
            }
        )
        print(f"[{aid}] skip: git not found", file=sys.stderr)
        return

    if env_truthy("FETCH_REFRESH_GIT_CLONES") and dest.exists():
        shutil.rmtree(dest)

    if dest.exists():
        log["artifacts"].append(
            {
                "id": aid,
                "status": "ok",
                "type": "git_shallow_clone",
                "source_key": source_key,
                "data_source": source_key,
                "note": "clone already present; set FETCH_REFRESH_GIT_CLONES=1 to reclone",
                "stored_relative": str(dest.relative_to(root)),
            }
        )
        print(f"[{aid}] exists, skip: {dest.relative_to(root)}")
        return

    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["git", "clone", "--depth", "1", git_url, str(dest)]
    print(f"[{aid}] source_key={source_key} -> {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True, cwd=str(root))
    except subprocess.CalledProcessError as e:
        log["artifacts"].append(
            {
                "id": aid,
                "status": "error",
                "type": "git_shallow_clone",
                "source_key": source_key,
                "error": str(e),
            }
        )
        print(f"[{aid}] git clone failed: {e}", file=sys.stderr)
        return

    log["artifacts"].append(
        {
            "id": aid,
            "status": "ok",
            "type": "git_shallow_clone",
            "source_key": source_key,
            "data_source": source_key,
            "git_url": git_url,
            "stored_relative": str(dest.relative_to(root)),
        }
    )
    print(f"    cloned to {dest.relative_to(root)}")


def fetch_huggingface_snapshot(root: Path, spec: dict, downloads: Path, log: dict) -> None:
    aid = spec["id"]
    source_key = spec.get("source_key", "huggingface_commitpackft")
    repo_id = spec["repo_id"]
    local_dir = downloads / source_key

    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        log["artifacts"].append(
            {
                "id": aid,
                "status": "skipped",
                "type": "huggingface_snapshot",
                "error": "huggingface_hub not installed (pip install -r requirements-datasets.txt)",
            }
        )
        print(f"[{aid}] skip: huggingface_hub missing", file=sys.stderr)
        return

    local_dir.mkdir(parents=True, exist_ok=True)
    print(f"[{aid}] source_key={source_key} snapshot_download {repo_id} -> {local_dir}")
    try:
        snapshot_download(
            repo_id=repo_id,
            repo_type="dataset",
            local_dir=str(local_dir),
            resume_download=True,
        )
    except Exception as e:
        log["artifacts"].append(
            {
                "id": aid,
                "status": "error",
                "type": "huggingface_snapshot",
                "source_key": source_key,
                "error": repr(e),
            }
        )
        print(f"[{aid}] snapshot_download failed: {e}", file=sys.stderr)
        return

    log["artifacts"].append(
        {
            "id": aid,
            "status": "ok",
            "type": "huggingface_snapshot",
            "source_key": source_key,
            "data_source": source_key,
            "repo_id": repo_id,
            "stored_relative": str(local_dir.relative_to(root)),
        }
    )
    print(f"    snapshot at {local_dir.relative_to(root)}")


def record_manual(root: Path, spec: dict, log: dict) -> None:
    aid = spec["id"]
    entry = {
        "id": aid,
        "status": "manual",
        "type": "manual",
        "source_key": spec.get("source_key"),
        "description": spec.get("description"),
    }
    if spec.get("readme_relative"):
        entry["readme_relative"] = spec["readme_relative"]
    if spec.get("sql_template_relative"):
        entry["sql_template_relative"] = spec["sql_template_relative"]
    log["artifacts"].append(entry)
    print(f"[{aid}] manual source — see {spec.get('readme_relative', 'datasets/README.md')}")


def main() -> int:
    root = repo_root()
    use_fallback = os.environ.get("FETCH_USE_LEGACY_FALLBACK", "1").strip() not in (
        "0",
        "false",
        "False",
    )
    if os.environ.get("SKIP_DATASET_FETCH", "").strip() in ("1", "true", "True"):
        print("SKIP_DATASET_FETCH is set; skipping dataset downloads.")
        return 0

    manifest = load_manifest(root)
    sources = manifest_sources(manifest)
    if not sources:
        print("No sources in manifest.")
        return 0

    owner, repo, ref = resolve_coordinates(manifest)
    downloads = root / "datasets" / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)

    log: dict = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source_label": SOURCE_LABEL,
        "manifest_version": manifest.get("version", 1),
        "use_legacy_fallback": use_fallback,
        "resolved_github": {"owner": owner or None, "repo": repo or None, "ref": ref},
        "artifacts": [],
    }

    for spec in sources:
        stype = spec.get("type", "http_github_raw")
        if stype == "http_github_raw":
            fetch_http_github_raw(
                root, spec, owner, repo, ref, use_fallback, downloads, log
            )
        elif stype == "kaggle_dataset":
            if not env_optional_enabled(spec):
                log["artifacts"].append(
                    {
                        "id": spec["id"],
                        "status": "skipped",
                        "type": stype,
                        "reason": f"set {spec.get('env_enable')}=1 or FETCH_ENABLE_ALL_OPTIONAL=1",
                    }
                )
                print(
                    f"[{spec['id']}] skip (optional): export {spec.get('env_enable')}=1",
                    file=sys.stderr,
                )
                continue
            fetch_kaggle_dataset(root, spec, downloads, log)
        elif stype == "git_shallow_clone":
            if not env_optional_enabled(spec):
                log["artifacts"].append(
                    {
                        "id": spec["id"],
                        "status": "skipped",
                        "type": stype,
                        "reason": f"set {spec.get('env_enable')}=1 or FETCH_ENABLE_ALL_OPTIONAL=1",
                    }
                )
                print(
                    f"[{spec['id']}] skip (optional): export {spec.get('env_enable')}=1",
                    file=sys.stderr,
                )
                continue
            fetch_git_shallow_clone(root, spec, downloads, log)
        elif stype == "huggingface_snapshot":
            if not env_optional_enabled(spec):
                log["artifacts"].append(
                    {
                        "id": spec["id"],
                        "status": "skipped",
                        "type": stype,
                        "reason": f"set {spec.get('env_enable')}=1 or FETCH_ENABLE_ALL_OPTIONAL=1",
                    }
                )
                print(
                    f"[{spec['id']}] skip (optional): export {spec.get('env_enable')}=1",
                    file=sys.stderr,
                )
                continue
            fetch_huggingface_snapshot(root, spec, downloads, log)
        elif stype == "manual":
            record_manual(root, spec, log)
        else:
            log["artifacts"].append(
                {
                    "id": spec.get("id", "unknown"),
                    "status": "skipped",
                    "error": f"unknown source type: {stype}",
                }
            )

    log_path = downloads / "fetch_log.json"
    log_path.write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(f"Wrote {log_path.relative_to(root)}")

    errors = [a for a in log["artifacts"] if a.get("status") == "error"]
    non_manual = [a for a in log["artifacts"] if a.get("type") != "manual"]
    skipped = [a for a in non_manual if a.get("status") == "skipped"]
    if errors:
        return 1
    if non_manual and len(skipped) == len(non_manual):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
