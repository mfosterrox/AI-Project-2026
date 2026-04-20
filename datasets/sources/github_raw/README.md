# Data source: `github_raw` (raw.githubusercontent.com)

## Role in this project

These HTTP CSVs are a **small legacy bootstrap** for the original notebooks (`VisualizePreprocess.ipynb`, `training_models.ipynb`). Your **primary static base** for new work should be **Kaggle** (`datasets/sources/kaggle_github_repos/README.md`), merged with GH Archive, advisories, CommitPackFT, and live API enrichment as needed.

## What this is

CSV artifacts are downloaded over HTTPS from **public raw GitHub URLs** (no GitHub token required for public repos). Each run stores files under:

`datasets/downloads/github_raw/<filename>`

as defined in `datasets/manifest.json` (`download_filename`).

## Configuration

Set these **before** running `python3 scripts/ingest_data.py --fetch-only` (or the full `ingest_data.py` without `--fetch-only`) if your CSVs are published on **your** repository:

| Variable | Meaning |
|----------|---------|
| `DATA_GITHUB_OWNER` | GitHub user or org (e.g. `mfosterrox`) |
| `DATA_GITHUB_REPO` | Repository name (e.g. `AI-Project-2026`) |
| `DATA_GITHUB_REF` | Branch or tag (default `main`) |

Primary URL pattern:

`https://raw.githubusercontent.com/{DATA_GITHUB_OWNER}/{DATA_GITHUB_REPO}/{DATA_GITHUB_REF}/{primary_path_on_repo}`

## Fallback (sample data)

If the primary URL returns 404 and **`FETCH_USE_LEGACY_FALLBACK`** is `1` (default), the fetcher uses the `fallback_url` from the manifest (original upstream sample project) so a fresh clone can still obtain files for local training. The legacy `PreprocessData.csv` object lives under that repo’s **`dataset/`** path on `raw.githubusercontent.com`, not the repository root.

Set `FETCH_USE_LEGACY_FALLBACK=0` to disable and only use your own repo.

## Script entry point

Implemented in **`scripts/python/fetch_datasets.py`** (orchestrator). This README documents the **github_raw** source; the Python file logs which URL succeeded in `datasets/downloads/fetch_log.json`.
