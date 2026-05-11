#!/usr/bin/env bash
# One-shot setup + data download + model training (macOS).
# From repo root:  bash scripts/setup_and_train_mac.sh
# Or:              chmod +x scripts/setup_and_train_mac.sh && ./scripts/setup_and_train_mac.sh
#
# Options:
#   --skip-brew       Do not run `brew install` for libomp (XGBoost needs OpenMP on Apple Silicon Intel Homebrew).
#   --skip-fetch      Skip data download (use existing PreprocessData.csv).
#   --recreate-venv   Remove .venv and create a fresh one.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SKIP_BREW=0
SKIP_FETCH=0
RECREATE_VENV=0
for arg in "$@"; do
  case "$arg" in
    --skip-brew) SKIP_BREW=1 ;;
    --skip-fetch) SKIP_FETCH=1 ;;
    --recreate-venv) RECREATE_VENV=1 ;;
    *)
      echo "Unknown option: $arg" >&2
      echo "Usage: $0 [--skip-brew] [--skip-fetch] [--recreate-venv]" >&2
      exit 1
      ;;
  esac
done

die() { echo "[setup_and_train] ERROR: $*" >&2; exit 1; }

echo "[setup_and_train] Repository root: $ROOT"

# --- OpenMP for XGBoost on macOS (Apple Silicon / Homebrew) ---
if [[ "$(uname -s)" == "Darwin" ]] && [[ "$SKIP_BREW" -eq 0 ]]; then
  if command -v brew &>/dev/null; then
    if brew list libomp &>/dev/null 2>&1; then
      echo "[setup_and_train] libomp already installed (Homebrew)."
    else
      echo "[setup_and_train] Installing libomp (OpenMP) for XGBoost via Homebrew..."
      brew install libomp
    fi
  else
    echo "[setup_and_train] Homebrew not found. If XGBoost fails to load, install: brew install libomp" >&2
  fi
fi

# --- Pick Python 3.12 or 3.13 (TensorFlow has no wheels for 3.14+) ---
pick_python() {
  local candidates=(
    python3.12
    python3.13
    /opt/homebrew/opt/python@3.12/bin/python3.12
    /opt/homebrew/opt/python@3.13/bin/python3.13
    /usr/local/opt/python@3.12/bin/python3.12
    /usr/local/opt/python@3.13/bin/python3.13
  )
  local c p
  for c in "${candidates[@]}"; do
    if command -v "$c" &>/dev/null; then
      p="$(command -v "$c")"
      if "$p" -c 'import sys; raise SystemExit(0 if (3,12)<=sys.version_info<(3,14) else 1)' 2>/dev/null; then
        echo "$p"
        return 0
      fi
    fi
  done
  return 1
}

PY="$(pick_python)" || die "Need Python 3.12 or 3.13 on PATH (TensorFlow). Example: brew install python@3.12"
echo "[setup_and_train] Using Python: $PY ($("$PY" --version 2>&1))"

# --- Virtual environment ---
if [[ "$RECREATE_VENV" -eq 1 ]] && [[ -d "$ROOT/.venv" ]]; then
  echo "[setup_and_train] Removing existing .venv (--recreate-venv)"
  rm -rf "$ROOT/.venv"
fi

if [[ ! -d "$ROOT/.venv" ]]; then
  echo "[setup_and_train] Creating .venv with $PY"
  "$PY" -m venv "$ROOT/.venv"
fi

# shellcheck source=/dev/null
source "$ROOT/.venv/bin/activate"

if python -c 'import sys; sys.exit(0 if sys.version_info >= (3, 14) else 1)'; then
  die "Active Python is 3.14+. Remove .venv and rerun: rm -rf .venv && bash scripts/setup_and_train_mac.sh"
fi

echo "[setup_and_train] Upgrading pip and installing requirements-local.txt"
python -m pip install --upgrade pip
pip install -r "$ROOT/requirements-local.txt"

# --- Download data ---
if [[ "$SKIP_FETCH" -eq 0 ]]; then
  echo "[setup_and_train] Downloading data (manifest fetch, no Node/npm)"
  python "$ROOT/scripts/ingest_data.py" --fetch-only --no-node
else
  echo "[setup_and_train] Skipping fetch (--skip-fetch)"
fi

# --- Sanity check for training CSV ---
if [[ ! -f "$ROOT/notebooks/PreprocessData.csv" ]] && [[ ! -f "$ROOT/data/notebook_inputs/PreprocessData.csv" ]]; then
  die "PreprocessData.csv not found under notebooks/ or data/notebook_inputs/. Run without --skip-fetch or copy the file."
fi

# --- Train ---
echo "[setup_and_train] Running training notebook via scripts/train_models.py"
python "$ROOT/scripts/train_models.py"

echo "[setup_and_train] Done. Executed notebook: notebooks/_executed/training_models.executed.ipynb"
