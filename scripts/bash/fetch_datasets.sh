#!/usr/bin/env bash
# Download datasets defined in datasets/manifest.json into datasets/downloads/ (gitignored).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found; install Python 3 to fetch datasets."
  exit 1
fi
exec python3 "$ROOT/scripts/python/fetch_datasets.py" "$@"
