# Data layout

Bulk downloads go under **`data/downloads/`** (gitignored). Tracked pieces are **`data/manifest.json`**, this README, and **`data/sources/<name>/README.md`** for each source.

## Tracked vs ignored

| Path | Git |
|------|-----|
| `data/README.md` (this file) | Tracked |
| `data/manifest.json` | Tracked — `sources[]` per fetcher |
| `data/sources/<name>/README.md` | Tracked |
| `data/notebook_inputs/README.md` | Tracked |
| `scripts/sql/gharchive_example.sql` | Tracked |
| `data/downloads/**` | **Ignored** |
| `data/notebook_inputs/*.csv` | Usually ignored (copies for local runs) |

## Primary sources

| # | `source_key` | Role | Automation |
|---|----------------|------|------------|
| 1 | `kaggle_github_repos` | Static base repos | Optional Kaggle CLI + `FETCH_ENABLE_KAGGLE=1` |
| 2 | `gharchive_bigquery` | GH Archive / BigQuery | Manual export → `data/downloads/gharchive_bigquery/` |
| 3 | `github_advisory_database` | Advisories | Optional clone + `FETCH_ENABLE_ADVISORY_DB=1` |
| 4 | `huggingface_commitpackft` | CommitPackFT | Optional + `FETCH_ENABLE_HF_COMMITPACKFT=1` |
| 5 | `github_api_live` | REST/GraphQL enrichment | Manual / Node collectors |
| — | `github_raw` | Legacy bootstrap CSVs | HTTP fetch by default |

Details: **`data/sources/<source_key>/README.md`**.

## Fetch

```bash
pip install -r requirements-datasets.txt
export FETCH_ENABLE_KAGGLE=1   # opt in as needed
python3 scripts/ingest_data.py --fetch-only
```

## Notebook copies

Successful `github_raw` fetches copy into **`notebooks/data.csv`** and **`data/notebook_inputs/PreprocessData.csv`** (see `data/manifest.json`).

## Adding a source

1. Add `data/sources/<source_key>/README.md`.
2. Append to `data/manifest.json` → `sources`.
