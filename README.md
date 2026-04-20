# Mapping Programming Languages to Open-Source Project Effectiveness Using Neural Networks

## Overview

This repository studies how **programming language** (and related repository signals) relate to **open-source project effectiveness**, operationalized as **GitHub star count** for repositories with more than 100 stars. The pipeline collects repository metadata via the GitHub REST and GraphQL APIs, engineers features (including language indicators such as JavaScript, Python, Java, and others), and compares models—including **deep neural networks**—against gradient boosting, CatBoost, and random forests.

Predictions draw on owner and organization activity: commits, forks, issues, pull requests, update cadence, README metrics, and more. Different model families are trained and evaluated on the collected dataset.

## Repository setup

After you create the GitHub repository with the title above, clone it locally and set these placeholders wherever they appear (README, notebooks, `scripts/bash`):

- `YOUR_GITHUB_USERNAME` — your GitHub user or organization
- `YOUR_REPO_NAME` — the repository name you chose on GitHub (for example `mapping-programming-languages-effectiveness`)

## Local development (run and test models)

Everything can run on your laptop: notebooks for training/evaluation, and optional Node.js scripts if you want to refresh GitHub data.

1. **One-time environment**
   - Install [Node.js](https://nodejs.org/) (LTS v18+ recommended) for the data pipeline scripts.
   - Install [Python 3.10+](https://www.python.org/) for Jupyter and the models.

2. **Bootstrap scripts and secrets**

   ```bash
   chmod +x scripts/bash/setup_local.sh
   ./scripts/bash/setup_local.sh
   ```

   This installs npm dependencies under `scripts/nodejs/`, creates `graphQlData/` and `repos/`, and copies `scripts/nodejs/.env.example` to `scripts/nodejs/.env` if `.env` is missing. Edit `.env` and set at least `TOKEN` (GitHub personal access token with appropriate repo/API scopes) before running the GraphQL collectors.

   It also runs **`scripts/python/fetch_datasets.py`**, which reads **`datasets/manifest.json`** (version 2 `sources`): default **HTTP** pulls for legacy notebook CSVs, **manual** entries for BigQuery GH Archive and live GitHub API (documented only), and **optional** pulls for **Kaggle** (`FETCH_ENABLE_KAGGLE=1`), **Advisory DB** shallow clone (`FETCH_ENABLE_ADVISORY_DB=1`), and **Hugging Face CommitPackFT** (`FETCH_ENABLE_HF_COMMITPACKFT=1`), or set **`FETCH_ENABLE_ALL_OPTIONAL=1`**. Install **`pip install -r requirements-datasets.txt`** before optional sources. Set `SKIP_DATASET_FETCH=1` to skip everything, or configure `DATA_GITHUB_OWNER` / `DATA_GITHUB_REPO` / `DATA_GITHUB_REF` for your own raw CSVs. See **`datasets/README.md`**.

3. **Python venv and Jupyter**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements-local.txt
   jupyter notebook
   ```

   Open `notebooks/VisualizePreprocess.ipynb` then `notebooks/training_models.ipynb` (or use JupyterLab). Place or download your CSV inputs as each notebook expects; if cells still use `from keras...` on Python 3, switch imports to `from tensorflow.keras...` to match the TensorFlow stack in `requirements-local.txt`.

4. **Optional: collect data from GitHub** (same machine; respect [rate limits](https://docs.github.com/en/graphql/overview/resource-limitations))

   ```bash
   cd scripts/nodejs
   # node getting_repos_v2.js      # REST search; needs CLIENT_ID / CLIENT_SECRET in .env
   # node githubGraphQLApiCallsDO_V3.js
   ```

   Put the repo list CSV under `scripts/nodejs/repos/` as referenced in the script. Use conservative `START` / `END` in `.env` while testing.

The file `scripts/bash/local_dev_cmds` mirrors these steps. `settingUpDOServer.sh` is kept as a thin wrapper that runs `setup_local.sh` for any old instructions that still mention it.

## Dataset

We combine a **Kaggle** base ([donbarbos/github-repos](https://www.kaggle.com/datasets/donbarbos/github-repos)), optional **GH Archive** aggregates (BigQuery), the **GitHub Advisory Database**, **CommitPackFT** (Hugging Face), and **GitHub REST/GraphQL** enrichment—see **`datasets/README.md`**. **Bulk files are not committed:** `setup_local.sh` (or `./scripts/bash/fetch_datasets.sh`) fills **`datasets/downloads/`** per `datasets/manifest.json`. Each source has **`datasets/sources/<name>/README.md`**. Legacy notebook CSVs still come from the `github_raw` HTTP entries. For feature lists, see the summary section below.

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

### Bash scripts

- **setup_local.sh** <br>
  filepath: scripts/bash/setup_local.sh<br>
  Prepares your machine for local work: checks for Node.js, runs `npm install` in `scripts/nodejs/`, creates `graphQlData/` and `repos/`, and seeds `scripts/nodejs/.env` from `.env.example` when needed.

- **settingUpDOServer.sh** <br>
  filepath: scripts/bash/settingUpDOServer.sh<br>
  Legacy filename; it now delegates to `setup_local.sh` so older docs still work.

- **fetch_datasets.sh** <br>
  filepath: scripts/bash/fetch_datasets.sh<br>
  Runs `scripts/python/fetch_datasets.py` to download manifest-listed files into `datasets/downloads/` and refresh notebook copies.

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
  Reads `datasets/manifest.json` (`sources[]` with `type`: HTTP GitHub raw, Kaggle CLI, shallow `git clone`, Hugging Face `snapshot_download`, or `manual`). Writes under `datasets/downloads/<source_key>/` and `fetch_log.json`; each source is documented in `datasets/sources/<source_key>/README.md`.

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
  In this notebook, we train different models with hyperparameter tuning on our dataset and compare their results at the end. For details on models trained, their prediction scores, and so on, check the summary below.

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

- **Gradient Boost Regressor**
- **Cat Boost Regressor**
- **Random Forest Regressor**
- **Deep Neural Network**

### Evaluation Metrics

- **R^2 score**<br>
  ![R^2 score formula](./images/1.png)

### Results

![Result bar graph of different models](./images/2.png)
