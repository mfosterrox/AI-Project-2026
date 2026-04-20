#!/usr/bin/env bash
# One-time local setup: Node data-collection deps, dirs, and .env template.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
NODE_DIR="$ROOT/scripts/nodejs"

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is required for the GitHub API scripts. Install LTS from https://nodejs.org/ (v18 or newer recommended)."
  exit 1
fi

NODE_MAJOR="$(node -p "process.versions.node.split('.')[0]" 2>/dev/null || echo 0)"
if [[ "${NODE_MAJOR}" -lt 16 ]]; then
  echo "Warning: Node.js v16+ is recommended (found v$(node -v))."
fi

cd "$NODE_DIR"
mkdir -p graphQlData repos

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created scripts/nodejs/.env — edit TOKEN (and OAuth fields if you use getting_repos_v2.js)."
else
  echo "Keeping existing scripts/nodejs/.env"
fi

npm install

echo "Fetching training datasets (see datasets/README.md)..."
set +e
python3 "$ROOT/scripts/python/fetch_datasets.py"
fetch_status=$?
set -e
if [[ "$fetch_status" -ne 0 ]]; then
  echo "Dataset fetch reported an issue (exit $fetch_status). Re-run: ./scripts/bash/fetch_datasets.sh"
  echo "  Override: SKIP_DATASET_FETCH=1 ./scripts/bash/setup_local.sh  |  Disable legacy URLs: FETCH_USE_LEGACY_FALLBACK=0"
fi
echo "  Optional large sources: pip install -r requirements-datasets.txt then e.g."
echo "    FETCH_ENABLE_ALL_OPTIONAL=1 ./scripts/bash/fetch_datasets.sh"
echo "    or FETCH_ENABLE_KAGGLE=1 FETCH_ENABLE_ADVISORY_DB=1 FETCH_ENABLE_HF_COMMITPACKFT=1"

echo "Local setup finished."
echo "  • Train models: from repo root, create a venv and pip install -r requirements-local.txt, then open notebooks/ in Jupyter."
echo "  • Refresh data: cd scripts/nodejs && node githubGraphQLApiCallsDO_V3.js (after placing repo CSVs under repos/ and setting START/END in .env)."
