# Data source: `github_graphql_api` (GitHub GraphQL API)

## What this is

**Scripts:** `scripts/nodejs/githubGraphQLApiCallsDO_V2.js`, `scripts/nodejs/githubGraphQLApiCallsDO_V3.js`  
**Input:** CSV rows under `scripts/nodejs/repos/` (from the REST step or your own list)  
**Output directory:** `scripts/nodejs/graphQlData/` — JSON per batch (`file_<start>_<end>.json`)

## Credentials

Requires `TOKEN` (PAT) and slice bounds `START` / `END` in `scripts/nodejs/.env`.

## Downstream

Convert JSON to CSV with `scripts/python/json_to_csv.py`, merge with `scripts/python/merge.py` as needed. Those artifacts can be copied into `datasets/downloads/` manually if you want a single “downloads” tree; the default fetch manifest only covers **published raw CSVs** (`github_raw` source).
