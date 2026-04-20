# Datasets layout

All **downloaded or generated bulk files** live under `datasets/downloads/`, which is **gitignored**. Tracked files here are **manifest**, **SQL templates**, and **per-source READMEs** only.

## Tracked vs ignored

| Path | Git |
|------|-----|
| `datasets/README.md` (this file) | Tracked |
| `datasets/manifest.json` | Tracked — `sources[]` with `type` per fetcher |
| `datasets/sources/<name>/README.md` | Tracked — provenance and merge notes |
| `scripts/sql/gharchive_example.sql` | Tracked — BigQuery pattern |
| `datasets/downloads/**` | **Ignored** — CSV, Parquet, clones, HF snapshots, `fetch_log.json` |

## Primary training sources (five + legacy bootstrap)

| # | `source_key` | Role | Automation |
|---|----------------|------|------------|
| 1 | `kaggle_github_repos` | Primary static base (215k+ repos, popularity + language) | Optional: Kaggle CLI + `FETCH_ENABLE_KAGGLE=1` |
| 2 | `gharchive_bigquery` | Temporal activity (GH Archive via BigQuery) | **Manual:** run SQL, export to `datasets/downloads/gharchive_bigquery/` |
| 3 | `github_advisory_database` | Security / trust (advisory JSON) | Optional: `git clone` + `FETCH_ENABLE_ADVISORY_DB=1` |
| 4 | `huggingface_commitpackft` | Commit-level cadence / churn (CommitPackFT) | Optional: `huggingface_hub` + `FETCH_ENABLE_HF_COMMITPACKFT=1` |
| 5 | `github_api_live` | Live REST/GraphQL + community profile | **Manual:** Node scripts in `scripts/nodejs/` or your own batch job |
| — | `github_raw` | Legacy HTTP CSVs for existing notebooks | Default: **HTTP** fetch (no token) |

Details for each live in **`datasets/sources/<source_key>/README.md`**.

## One-command fetch

```bash
pip install -r requirements-datasets.txt   # optional: Kaggle + Hugging Face
export FETCH_ENABLE_KAGGLE=1               # opt in per heavy source
export FETCH_ENABLE_ADVISORY_DB=1
export FETCH_ENABLE_HF_COMMITPACKFT=1
# or: export FETCH_ENABLE_ALL_OPTIONAL=1  # enables all three flags above

./scripts/bash/fetch_datasets.sh
```

HTTP bootstrap + manual sources always run (manual entries only append to `fetch_log.json`). Heavy sources are **skipped** unless their env flag is set (or `FETCH_ENABLE_ALL_OPTIONAL=1`).

## Working copies for notebooks

The HTTP `github_raw` sources still **copy** into `notebooks/data.csv` and `dataset/PreprocessData.csv` when those artifacts succeed. Merge Kaggle / GH Archive / others in your preprocessing notebook using a shared **repo key** (see each source README). For Node-based REST/GraphQL outputs, see also **`datasets/sources/github_rest_api/README.md`** and **`datasets/sources/github_graphql_api/README.md`** (referenced from **`github_api_live`**).

## Adding a source

1. Add a `datasets/sources/<source_key>/README.md`.
2. Append an object to `datasets/manifest.json` → `sources` with a supported `type` (`http_github_raw`, `kaggle_dataset`, `git_shallow_clone`, `huggingface_snapshot`, `manual`).
