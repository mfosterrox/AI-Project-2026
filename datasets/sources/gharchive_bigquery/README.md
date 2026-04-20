# Data source: GH Archive on Google BigQuery (dynamic activity and temporal data)

**Project site:** [gharchive.org](https://www.gharchive.org/)  
**Query console:** [Google Cloud BigQuery](https://console.cloud.google.com/bigquery)  
**Public tables:** `githubarchive.day.*`, `githubarchive.month.*`, etc.

## What it provides

Hourly and daily **event-level** logs since 2011: `WatchEvent`, `ForkEvent`, `IssuesEvent`, `PullRequestEvent`, `PushEvent`, releases, and more. You can aggregate per repository: commit cadence, star growth velocity (weekly or monthly buckets), issue and PR throughput, release frequency, and time-series suitable for sequence models (for example LSTM) over repo history.

## Why it is useful here

Static snapshots miss **maintenance and adoption dynamics**. GH Archive fills temporal gaps and supports growth proxies, response-time aggregates, and richer activity features than CSV-only baselines.

## How to use (not auto-downloaded)

BigQuery needs a **GCP project**, billing or free tier, and authenticated clients (`bq` CLI or `google-cloud-bigquery`). This repo does **not** pull BigQuery results automatically (size and cost vary).

1. See **`scripts/sql/gharchive_example.sql`** for a parameterized pattern: filter by repo list, event types, and date range, then `GROUP BY` repo.
2. Export query results to **CSV or Parquet** under:

   `datasets/downloads/gharchive_bigquery/`

   Use a descriptive file name (for example `push_counts_2024Q4.parquet`).

3. Merge on the same **repo key** you use for the Kaggle base (see `datasets/sources/kaggle_github_repos/README.md`).

## Quotas

BigQuery’s free usage tier is limited; scope queries with **partition filters** (dates) and restrict to your repo allowlist early in the `WHERE` clause.
