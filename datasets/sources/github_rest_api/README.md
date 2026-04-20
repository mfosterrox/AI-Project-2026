# Data source: `github_rest_api` (GitHub REST Search API)

## What this is

**Script:** `scripts/nodejs/getting_repos_v2.js`  
**Output directory:** `scripts/nodejs/repos/` (created by local setup)

The script calls `https://api.github.com/search/repositories` with date-bucketed queries (`stars:>=100`) and writes CSV files such as `file_2014-01-01_2018-02-15.csv`.

## Credentials

Requires `CLIENT_ID` and `CLIENT_SECRET` from a GitHub OAuth App in `scripts/nodejs/.env` (see `.env.example`).

## Labeling

Output files are produced by the Node process; they are **not** listed in `datasets/manifest.json` because they are generated locally, not downloaded from a static URL. Treat `scripts/nodejs/repos/*.csv` as **REST API** lineage when combining with GraphQL-enriched data.
