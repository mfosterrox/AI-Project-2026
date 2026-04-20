# Data source: Hugging Face — CommitPackFT (commit-level activity)

**Dataset card:** [bigcode/commitpackft](https://huggingface.co/datasets/bigcode/commitpackft)  
**Larger corpus (optional):** [bigcode/commitpack](https://huggingface.co/datasets/bigcode/commitpack) (~4TB — use streaming or subsets only)  
**Local snapshot (when fetch enabled):** `datasets/downloads/huggingface_commitpackft/`  
**Manifest id:** `huggingface_commitpackft`

## What it provides

A **~2 GB** instruction-style filtered set of permissively licensed commits across many languages, with metadata such as repository name, timestamps, messages, and diff-related fields (see the dataset card for the exact schema). Use it to approximate **commit cadence**, **churn** (lines added or deleted), and **temporal patterns** per repository after aggregation.

## Why it is useful here

Supplements static repo tables with **fine-grained development activity** without scraping every commit from the GitHub API. Aggregates feed both tabular features and sequence-style modeling.

## Automated fetch (optional)

Requires Python package **`huggingface_hub`** (`pip install -r requirements-datasets.txt`).

```bash
export FETCH_ENABLE_HF_COMMITPACKFT=1
python3 scripts/ingest_data.py --fetch-only
```

This calls `snapshot_download` for `bigcode/commitpackft` into `datasets/downloads/huggingface_commitpackft/`. The first run can take significant time and disk space.

## Manual / streaming alternative

Use the `datasets` library with **`streaming=True`** to iterate and filter to your repo list without storing the full snapshot; aggregate offline and write Parquet or CSV into the same downloads folder.

## Merge keys

Use normalized **`repository_name`** or equivalent field from the dataset card, aligned with **`owner/repo`** from Kaggle or GitHub API.
