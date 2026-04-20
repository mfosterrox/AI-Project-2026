# Mapping Programming Languages to Open-Source Project Effectiveness Using Neural Networks

## Overview

This repository studies how **programming language** (and related repository signals) relate to **open-source project effectiveness**, operationalized as **GitHub star count** for repositories with more than 100 stars. The pipeline collects repository metadata via the GitHub REST and GraphQL APIs, engineers features (including language indicators such as JavaScript, Python, Java, and others), and compares models—including **deep neural networks**—against gradient boosting, CatBoost, and random forests.

Predictions draw on owner and organization activity: commits, forks, issues, pull requests, update cadence, README metrics, and more. Different model families are trained and evaluated on the collected dataset.

## Repository setup

After you create the GitHub repository with the title above, clone it locally and set these placeholders wherever they appear (README, notebooks, `scripts/bash`):

- `YOUR_GITHUB_USERNAME` — your GitHub user or organization
- `YOUR_REPO_NAME` — the repository name you chose on GitHub (for example `mapping-programming-languages-effectiveness`)

## Local development (two pipeline scripts)

Install [Python](https://www.python.org/) and (if you use the GitHub collectors) [Node.js](https://nodejs.org/) LTS.

**TensorFlow / Keras Tuner:** there are **no official TensorFlow wheels for Python 3.14+** yet, so `pip install` would report `No matching distribution found for tensorflow`. Use **Python 3.12 or 3.13** for the training notebook (for example `brew install python@3.12` on macOS, then `/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv`). `requirements-local.txt` uses environment markers so installs still succeed on 3.14 for the non-TF packages.

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-local.txt
```

### 1. Data ingestion — `scripts/ingest_data.py`

Runs **`npm install`** under `scripts/nodejs/` (creates `graphQlData/`, `repos/`, seeds `.env` from `.env.example` when missing), then runs **`scripts/python/fetch_datasets.py`** using **`datasets/manifest.json`**: HTTP bootstrap CSVs, optional Kaggle / advisory clone / Hugging Face sources (see **`datasets/README.md`**). Flags: `--no-node`, `--no-fetch`, `--node-only`, `--fetch-only`. Environment: `SKIP_DATASET_FETCH`, `FETCH_ENABLE_*`, `DATA_GITHUB_*`, etc. Optional pip: **`requirements-datasets.txt`**.

### 2. Model training — `scripts/train_models.py`

Headlessly executes **`notebooks/training_models.ipynb`** with Jupyter (`nbconvert`) and writes **`notebooks/_executed/training_models.executed.ipynb`**. Use **`--interactive`** to print the `jupyter notebook …` command instead. For feature engineering only, still open **`notebooks/VisualizePreprocess.ipynb`** in Jupyter.

### Optional: live GitHub API collection

After step 1, from `scripts/nodejs/` with `.env` configured: `node getting_repos_v2.js` and/or `node githubGraphQLApiCallsDO_V3.js` (respect [rate limits](https://docs.github.com/en/graphql/overview/resource-limitations)).

**Legacy:** `scripts/bash/setup_local.sh` and `fetch_datasets.sh` forward to `ingest_data.py`. See `scripts/bash/local_dev_cmds` for a minimal copy-paste list.

## Dataset

We combine a **Kaggle** base ([donbarbos/github-repos](https://www.kaggle.com/datasets/donbarbos/github-repos)), optional **GH Archive** aggregates (BigQuery), the **GitHub Advisory Database**, **CommitPackFT** (Hugging Face), and **GitHub REST/GraphQL** enrichment—see **`datasets/README.md`**. **Bulk files are not committed:** `python3 scripts/ingest_data.py` fills **`datasets/downloads/`** per `datasets/manifest.json`. Each source has **`datasets/sources/<name>/README.md`**. Legacy notebook CSVs still come from the `github_raw` HTTP entries. For feature lists, see the summary section below.

## Tools used

- Python 3.10+ (recommended for local notebooks; original work also used Python 2.7)
- Jupyter Notebook
- NumPy
- Sklearn
- Pandas
- Keras
- Cat Boost
- Matplot Lib
- seaborn

We also used [Google Colab's](http://colab.research.google.com/) GPU notebooks, so we thank Google for the Colab project and GPU access.

## Code details

Below is a brief description of the code files and folders in the repo.

### Pipeline scripts (primary)

- **`scripts/ingest_data.py`** — Data ingestion: Node/npm bootstrap + manifest downloads (`datasets/manifest.json` → `datasets/downloads/`, notebook copies). Implementation: `scripts/python/fetch_datasets.py`.

- **`scripts/train_models.py`** — Model training: executes `notebooks/training_models.ipynb` via `jupyter nbconvert` into `notebooks/_executed/` (or `--interactive` for manual Jupyter).

### Bash (legacy wrappers)

- **`scripts/bash/setup_local.sh`** → forwards to `python3 scripts/ingest_data.py`.
- **`scripts/bash/fetch_datasets.sh`** → `ingest_data.py --fetch-only`.
- **`scripts/bash/settingUpDOServer.sh`** → same as `setup_local.sh`.

### NodeJs scripts

- **getting_repos_v2.js**<br>
  filepath: scripts/nodejs/getting_repos_v2.js<br>
  This script fetches the basic info of repos having more than 100 stars using the GitHub REST API.

- **githubGraphQLApiCallsDO_V2.js**<br>
  filepath: scripts/nodejs/githubGraphQLApiCallsDO_V2.js<br>
  This script fetches the complete info of the repositories that were fetched by the above script and uses the GitHub GraphQL API. It follows the approach of fetching the data at the fixed rate defined in the env file (for example 730ms per request).

- **githubGraphQLApiCallsDO_V3.js**<br>
  filepath: scripts/nodejs/githubGraphQLApiCallsDO_V3.js<br>
  This script fetches the complete info of the repositories that were fetched by the above script and uses the GitHub GraphQL API. It follows the approach of requesting data for the next repo after receiving the response of the already sent request.

### Python scripts

- **fetch_datasets.py** <br>
  filepath: scripts/python/fetch_datasets.py<br>
  Called by **`scripts/ingest_data.py`**. Reads `datasets/manifest.json` (`sources[]` …) and writes under `datasets/downloads/<source_key>/` plus `fetch_log.json`; each source is documented in `datasets/sources/<source_key>/README.md`.

- **json_to_csv.py**<br>
  filepath: scripts/python/json_to_csv.py<br>
  This script converts the JSON data fetched from GitHub's GraphQL API in the above script to the equivalent CSV file.

- **merge.py**<br>
  filepath: scripts/python/merge.py<br>
  This script merges all the data in multiple CSV files into a single CSV file.

### Jupyter Notebooks

- **VisualizePreprocess.ipynb**<br>
  filepath: notebooks/VisualizePreprocess.ipynb<br>
  Feature engineering is done in this notebook. It visualizes the data and creates new features, modifies existing features, and removes redundant features. For details on features created, check the summary below.

- **training_models.ipynb**<br>
  filepath: notebooks/training_models.ipynb<br>
  Trains **baselines** (Random Forest, sklearn Gradient Boosting, XGBoost, CatBoost) and a **main tuned feed-forward Keras model** (BatchNorm, Dropout, L2, EarlyStopping, ReduceLROnPlateau, **Keras Tuner**). Includes an **optional LSTM** demo on a synthetic weekly proxy (replace with GH Archive sequences when available). Metrics: \\(R^2\\), MAE, MSE. Optional env: `KT_MAX_TRIALS`, `KT_EPOCHS`, `KT_BATCH`, `KERAS_TUNER_DIR`. Regenerate from `scripts/python/build_training_notebook.py` if needed.

## Summary

In this project we predict the number of stars of a GitHub repository that has more than 100 stars. For this we take GitHub repository data from the REST API and GraphQL API. After generating the dataset we visualize and perform feature engineering, then apply various models—including neural networks—and report scores on training and test data.

### Feature Engineering

There are 49 features before pre-processing. After pre-processing (adding new features, removal of redundant features, and modifying existing features) the count changes to 54. All the features are listed below. Some features after pre-processing may not be clear; refer to the VisualizePreprocess.ipynb notebook for details.

#### Original Features

| column 1 | column 2 | column 3 |
| ------------ | ------------- | ------------- |
| branches | commits | createdAt |
| description | diskUsage | followers |
| following | forkCount | gistComments |
| gistStar | gists | hasWikiEnabled |
| iClosedComments | iClosedParticipants | iOpenComments |
| iOpenParticipants | isArchived | issuesClosed |
| issuesOpen | license | location |
| login | members | organizations |
| prClosed | prClosedComments | prClosedCommits |
| prMerged | prMergedComments | prMergedCommits |
| prOpen | prOpenComments | prOpenCommits |
| primaryLanguage | pushedAt | readmeCharCount |
| readmeLinkCount | readmeSize | readmeWordCount |
| releases | reponame | repositories |
| siteAdmin | stars | subscribersCount |
| tags | type | updatedAt |
| websiteUrl |

#### Features after pre-processing

| column 1 | column 2 | column 3 |
| ------------ | ------------- | ------------- |
| branches | commits | createdAt |
| diskUsage | followers | following |
| forkCount | gistComments | gistStar |
| gists | hasWikiEnabled | iClosedComments |
| iClosedParticipants | iOpenComments | iOpenParticipants |
| issuesClosed | issuesOpen | members |
| organizations | prClosed | prClosedComments |
| prClosedCommits | prMerged | prMergedComments |
| prMergedCommits | prOpen | prOpenComments |
| prOpenCommits | pushedAt | readmeCharCount |
| readmeLinkCount | readmeSize | readmeWordCount |
| releases | repositories | subscribersCount |
| tags | type | updatedAt |
| websiteUrl | desWordCount | desCharCount |
| mit_license | nan_license | apache_license |
| other_license | remain_license | JavaScript |
| Python | Java | Objective |
| Ruby | PHP | other_language |

### Models Trained

- **Baselines:** Gradient Boosting (sklearn), CatBoost, Random Forest, XGBoost
- **Main model:** tuned feed-forward **deep neural network** (TensorFlow/Keras: BatchNorm, Dropout, L2, callbacks, Keras Tuner)
- **Optional demo:** small **LSTM** on synthetic weekly-style sequences (illustrative until GH Archive features are merged)

### Evaluation Metrics

- **R^2 score**<br>
  ![R^2 score formula](./images/1.png)

### Results

![Result bar graph of different models](./images/2.png)
