#!/usr/bin/env bash
# Legacy entry point — forwards to scripts/ingest_data.py (data ingestion).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
exec python3 "$ROOT/scripts/ingest_data.py" "$@"
