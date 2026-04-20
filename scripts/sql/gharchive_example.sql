-- GH Archive on BigQuery — pattern for per-repo aggregates (edit table dates and repo filter).
-- Dataset: https://www.gharchive.org/ — use partition filters to control scan size and cost.
--
-- Replace `your_project.your_dataset.repo_allowlist` with a table of repos to score, e.g. columns:
--   owner STRING, name STRING   OR   full_name STRING  (format: 'torvalds/linux')

-- Example: monthly table wildcard (adjust year/month pattern to match available tables).
SELECT
  repo.name AS repo_name,
  type AS event_type,
  COUNT(*) AS event_count
FROM `githubarchive.month.202501`
WHERE repo.name IN (
  SELECT full_name FROM `your_project.your_dataset.repo_allowlist`
)
  AND type IN ('PushEvent', 'WatchEvent', 'ForkEvent', 'IssuesEvent', 'PullRequestEvent')
GROUP BY repo.name, type
ORDER BY repo_name, event_type;

-- Export results from the BigQuery UI (Save Results → CSV/Parquet) into:
--   datasets/downloads/gharchive_bigquery/
-- and document the export filename in your merge notebook.
