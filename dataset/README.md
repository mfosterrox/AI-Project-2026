# `dataset/` working directory

CSV files placed here (for example **`PreprocessData.csv`**) are normally **produced by the dataset fetcher** or copied from your own pipeline. They are **gitignored** so large files are not committed.

After running `scripts/python/fetch_datasets.py`, you should see `PreprocessData.csv` here when that artifact is included in `datasets/manifest.json`.

See **`datasets/README.md`** for the full layout and source documentation.
