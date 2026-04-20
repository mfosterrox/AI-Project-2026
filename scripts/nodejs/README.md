# GitHub REST / GraphQL collectors

- `getting_repos_v2.js` — REST search (`CLIENT_ID` / `CLIENT_SECRET` in `.env`)
- `githubGraphQLApiCallsDO_V2.js` / `githubGraphQLApiCallsDO_V3.js` — GraphQL enrichment (`TOKEN`, `START`, `END`)

Copy `.env.example` to `.env`, then `npm install` (or run `python3 scripts/ingest_data.py` from the repo root).
