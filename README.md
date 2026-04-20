# Mapping Programming Languages to Open-Source Project Effectiveness Using Neural Networks

## Overview

This repository studies how **programming language** (and related repository signals) relate to **open-source project effectiveness**, operationalized as **GitHub star count** for repositories with more than 100 stars. The pipeline collects repository metadata via the GitHub REST and GraphQL APIs, engineers features (including language indicators such as JavaScript, Python, Java, and others), and compares models—including **deep neural networks**—against gradient boosting, CatBoost, and random forests.

Predictions draw on owner and organization activity: commits, forks, issues, pull requests, update cadence, README metrics, and more. Different model families are trained and evaluated on the collected dataset.

## Repository setup

After you create the GitHub repository with the title above, clone it locally and set these placeholders wherever they appear (README, notebooks, `scripts/bash`):

- `YOUR_GITHUB_USERNAME` — your GitHub user or organization
- `YOUR_REPO_NAME` — the repository name you chose on GitHub (for example `mapping-programming-languages-effectiveness`)

## Dataset

We used the GitHub REST API and GraphQL API to collect data for repositories having more than 100 stars. The data is available in the dataset directory. We were able to collect the data faster using DigitalOcean's multiple servers, so we thank [DigitalOcean](http://digitalocean.com) for providing free credits to students to use servers. For details on dataset features, refer to the summary section below.

## Tools used

- Python 2.7
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

### Bash Script

- **settingUpDOServer.sh** <br>
  filepath: scripts/bash/settingUpDOServer.sh<br>
  This is used for configuring the DigitalOcean server.

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
