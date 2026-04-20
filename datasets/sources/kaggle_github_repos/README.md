# Data source: Kaggle — Most popular GitHub repositories (primary static base)

**Kaggle dataset:** [donbarbos/github-repos](https://www.kaggle.com/datasets/donbarbos/github-repos)  
**Manifest id:** `kaggle_most_popular_github_repos`  
**Download directory:** `datasets/downloads/kaggle_github_repos/` (after successful fetch)

## What it provides

215k+ repositories with **>167 stars** (dataset description on Kaggle). Typical fields include stars, forks, issues, watchers, primary language, creation date, description, license, topics (depending on export version), owner metadata, and related popularity signals.

## Why it is useful here

Aligns with the original star-prediction framing and the legacy Doodies feature set. Use as the **tabular base**: filter to 10k–50k repos if needed, derive features (for example `log(stars)`, forks/stars, age from timestamps), then merge other sources on **normalized repo URL** or **owner/name**.

## Automated fetch (optional)

1. Install the [Kaggle API](https://www.kaggle.com/docs/api): `pip install kaggle`, then place **`~/.kaggle/kaggle.json`** (API credentials from your Kaggle account).
2. Enable the fetcher:

   ```bash
   export FETCH_ENABLE_KAGGLE=1
   python3 scripts/ingest_data.py --fetch-only
   ```

The orchestrator runs `kaggle datasets download -d donbarbos/github-repos` into `datasets/downloads/kaggle_github_repos/` and `--unzip` when supported.

## Manual alternative

Download the CSV/ZIP from the Kaggle dataset page and extract into **`datasets/downloads/kaggle_github_repos/`** yourself. Document the file name you used in your merge notebook.

## Merge keys

Prefer **`full_name`** or **`url`** style identifiers consistent across Kaggle, GH Archive exports, and GitHub API responses after normalization (lowercase owner, strip `https://github.com/`).
