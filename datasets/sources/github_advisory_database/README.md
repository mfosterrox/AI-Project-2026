# Data source: GitHub Advisory Database (security and trust signals)

**Upstream repository:** [github/advisory-database](https://github.com/github/advisory-database)  
**Local clone (when fetch enabled):** `datasets/downloads/github_advisory_database/advisory-database/`  
**Manifest id:** `github_advisory_database_clone`

## What it provides

JSON advisories under `advisories/` (including GitHub-reviewed entries): CVEs, affected **packages** and **ecosystems** (npm, PyPI, RubyGems, etc.), and references that can be mapped to repositories or packages you care about. You can derive **counts of open or resolved advisories**, severity buckets, and recency features.

## Why it is useful here

Adds an explicit **security / trust** dimension that correlates with maintenance quality and ecosystem risk, and can interact with **language** effects (for example density of memory-safety issues in C/C++ vs Rust).

## Automated fetch (optional)

Requires **`git`** on your PATH.

```bash
export FETCH_ENABLE_ADVISORY_DB=1
python3 scripts/ingest_data.py --fetch-only
```

This performs a **shallow clone** (`--depth 1`) of the advisory database into `datasets/downloads/github_advisory_database/advisory-database/`. If the directory already exists, the clone is skipped unless you set **`FETCH_REFRESH_GIT_CLONES=1`** (the script removes the target directory first when that is set).

## How to use in modeling

Parse JSON with Python (or a community parser), aggregate **per package or per repo identifier**, then join to your Kaggle-derived table on ecosystem-specific keys (for example npm package name + scope) or via a mapping table from package → GitHub repo.

## Merge keys

Advisories are often **package-centric**; you may need an intermediate mapping from package coordinates to **`owner/repo`** before merging to the Kaggle base.
