# Data source: GitHub REST, GraphQL, and community profile (live enrichment)

**REST docs:** [GitHub REST API](https://docs.github.com/en/rest)  
**GraphQL docs:** [GitHub GraphQL API](https://docs.github.com/en/graphql)  
**Community profile (health metrics):** available via repository metadata endpoints (README, `CONTRIBUTING`, `CODE_OF_CONDUCT`, `SECURITY`, license presence, etc.) — see GitHub docs for the current **community profile** fields.

## What it provides

Per repository (subject to token scopes and rate limits):

- Releases (count, recency)
- Contributors (for **bus factor** style proxies)
- Community health indicators (documentation files present)
- Issues and pull requests (open, closed, timing if you paginate history)
- Topics, description updates, and other live fields not in static dumps

## Why it is useful here

Fills **real-time or missing** attributes for a fixed list of repos (for example your 10k–50k Kaggle subset): CHAOSS-inspired health signals, owner strength, and release discipline.

## How to use in this repository

This project already includes **Node.js** collectors under `scripts/nodejs/`:

- `getting_repos_v2.js` — REST search discovery
- `githubGraphQLApiCallsDO_V2.js` / `githubGraphQLApiCallsDO_V3.js` — GraphQL enrichment

Configure **`scripts/nodejs/.env`** (`TOKEN`, optional OAuth IDs for REST). Outputs land in **`scripts/nodejs/repos/`** and **`scripts/nodejs/graphQlData/`** (see sibling READMEs under `datasets/sources/github_rest_api` and `datasets/sources/github_graphql_api`).

For Python-only enrichment, libraries such as **PyGithub** or **`requests`** against REST are fine; **cache aggressively** to respect rate limits (use multiple tokens only if allowed by GitHub’s terms).

## Merge keys

Use **`owner`** + **`name`** or **`full_name`** consistent with your Kaggle and GH Archive keys.

## Automated fetch

There is **no** single static URL for “the API dataset.” The manifest marks this source as **`manual`**; run the Node pipeline or your own batch job, then place derived CSVs under `datasets/downloads/github_api_live/` if you want them beside other pulled artifacts.
