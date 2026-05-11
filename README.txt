AI-Project-2026 — run instructions
====================================
Python 3.12 or 3.13 only. Not 3.14+.

  python3.12 -m venv .venv
  source .venv/bin/activate          Windows: .venv\Scripts\activate
  pip install -r requirements-local.txt

macOS if XGBoost errors about libomp:
  brew install libomp

Put PreprocessData.csv in data/notebook_inputs/ OR notebooks/
(use a row subset if your zip must stay small).

  python versions.py                 writes package_versions.txt
  python run.py                      trains (output under notebooks/_executed/)

Optional:
  python run.py ingest               fetch CSVs from data/manifest.json
  bash scripts/setup_and_train_mac.sh
