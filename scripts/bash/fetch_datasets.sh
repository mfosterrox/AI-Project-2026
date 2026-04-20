#!/usr/bin/env bash
# Legacy entry point — manifest fetch only (same as: python3 scripts/ingest_data.py --fetch-only).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
exec python3 "$ROOT/scripts/ingest_data.py" --fetch-only "$@"
