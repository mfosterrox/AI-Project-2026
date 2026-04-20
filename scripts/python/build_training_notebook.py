"""One-off generator: writes notebooks/training_models.ipynb (modern TF/Keras pipeline)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "notebooks" / "training_models.ipynb"

cells = []

def md(s):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": [line + "\n" for line in s.strip().split("\n")]})

def code(s):
    lines = s.strip().split("\n")
    src = [ln + "\n" for ln in lines[:-1]] + ([lines[-1] + "\n"] if lines else [])
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": src})

md("""
# GitHub stars regression: **neural network (main)** vs. **baselines**

This notebook **clearly separates**:

- **Part A — Baselines:** tree ensembles (Random Forest, Gradient Boosting, **XGBoost**, **CatBoost**). These are strong non-linear baselines on tabular data.
- **Part B — Main model:** a **tuned feed-forward network** in TensorFlow/Keras with **BatchNormalization**, **Dropout**, and **L2** regularization, trained with **EarlyStopping** and **ReduceLROnPlateau**. Hyperparameters are searched with **Keras Tuner** (small budget for a course run; tighten `max_trials` / epochs if you have GPU time).
- **Part C — Optional LSTM demo:** a **small LSTM** on a **synthetic weekly activity proxy** built from `commits` (replace with real **GH Archive** weekly features when available).

**Metrics:** \\(R^2\\), MAE, MSE on the held-out test set — we compare all models side by side.
""")

code("""
# Optional: uncomment if your environment is missing packages
# !pip install -q tensorflow keras-tuner xgboost catboost scikit-learn pandas matplotlib
""")

code("""
import os
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, regularizers
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

import keras_tuner as kt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from catboost import CatBoostRegressor

warnings.filterwarnings("ignore", category=UserWarning)
tf.random.set_seed(42)
np.random.seed(42)

def metrics_dict(y_true, y_pred):
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "mse": float(mean_squared_error(y_true, y_pred)),
    }
""")

code("""
# Resolve preprocessed CSV (ingest_data.py / fetch copies here, or use ../dataset/)
_here = Path.cwd()
_candidates = [
    _here / "PreprocessData.csv",
    _here.parent / "dataset" / "PreprocessData.csv",
]
path = next((p.resolve() for p in _candidates if p.exists()), None)
if path is None:
    raise FileNotFoundError("PreprocessData.csv not found. Run: python3 scripts/ingest_data.py --fetch-only")

data_df = pd.read_csv(path).iloc[:, 1:]  # match legacy CSV: first column is row index

if "stars" not in data_df.columns:
    raise KeyError("Expected a 'stars' target column.")

X_df = data_df.drop(columns=["stars"])
y = data_df["stars"].astype(np.float32)

commits_series = X_df["commits"].astype(np.float32) if "commits" in X_df.columns else None

if commits_series is not None:
    X_train_df, X_test_df, y_train, y_test, com_tr, com_te = train_test_split(
        X_df, y, commits_series, test_size=0.10, random_state=42
    )
else:
    X_train_df, X_test_df, y_train, y_test = train_test_split(
        X_df, y, test_size=0.10, random_state=42
    )
    com_tr = com_te = None

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train_df).astype(np.float32)
X_test = scaler.transform(X_test_df).astype(np.float32)
n_features = X_train.shape[1]
print("Train:", X_train.shape, "Test:", X_test.shape, "Features:", n_features)
""")

md("""
## Part A — Baseline models (not the primary deliverable)

These models establish a **strong tabular baseline**. Same scaled features and split as the neural network.
""")

code("""
baseline_rows = []

# Random Forest
rf = RandomForestRegressor(
    n_estimators=200, max_depth=None, n_jobs=-1, random_state=42, verbose=0
)
rf.fit(X_train, y_train)
pred_rf = rf.predict(X_test)
baseline_rows.append(("Random Forest", metrics_dict(y_test, pred_rf)))

# Gradient Boosting (sklearn)
gbr = GradientBoostingRegressor(
    n_estimators=200, learning_rate=0.05, max_depth=4, random_state=42, verbose=0
)
gbr.fit(X_train, y_train)
pred_gbr = gbr.predict(X_test)
baseline_rows.append(("Gradient Boosting (sklearn)", metrics_dict(y_test, pred_gbr)))

# XGBoost
xgb = XGBRegressor(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.9,
    reg_lambda=1.0,
    random_state=42,
    n_jobs=-1,
    verbosity=0,
)
xgb.fit(X_train, y_train)
pred_xgb = xgb.predict(X_test)
baseline_rows.append(("XGBoost", metrics_dict(y_test, pred_xgb)))

# CatBoost
cat = CatBoostRegressor(
    iterations=600,
    depth=8,
    learning_rate=0.05,
    loss_function="RMSE",
    random_seed=42,
    verbose=False,
    allow_writing_files=False,
)
X_tr_c, X_val_c, y_tr_c, y_val_c = train_test_split(
    X_train, y_train, test_size=0.15, random_state=0
)
cat.fit(
    X_tr_c,
    y_tr_c,
    eval_set=(X_val_c, y_val_c),
    early_stopping_rounds=40,
    verbose=False,
)
pred_cat = cat.predict(X_test)
baseline_rows.append(("CatBoost", metrics_dict(y_test, pred_cat)))

baseline_df = pd.DataFrame(
    [{"model": m, **v} for m, v in baseline_rows]
).set_index("model")
print(baseline_df.sort_values("r2", ascending=False).to_string())
""")

md("""
## Part B — **Main model:** feed-forward neural network (tuned)

Architecture choices:

- **Dense → BatchNorm → Dropout** blocks with **L2** kernel regularization.
- **EarlyStopping** on `val_loss` and **ReduceLROnPlateau** when validation stalls.
- **Keras Tuner** `RandomSearch` over depth, width, dropout, L2, and learning rate.

> For a quick CPU run, `max_trials` and `epochs` are modest — increase if you have a GPU.
""")

code("""
input_dim = n_features
tuner_dir = Path(os.environ.get("KERAS_TUNER_DIR", str(Path.cwd() / "keras_tuner_scratch")))
tuner_dir.mkdir(parents=True, exist_ok=True)


def build_ffnn(hp: kt.HyperParameters) -> keras.Model:
    l2 = hp.Float("l2", 1e-5, 5e-3, sampling="log")
    reg = regularizers.l2(l2)
    n_layers = hp.Int("n_dense_layers", 1, 3)
    dropout = hp.Float("dropout", 0.1, 0.45, step=0.05)
    lr = hp.Float("learning_rate", 1e-4, 3e-3, sampling="log")

    model = keras.Sequential(name="ffnn_stars")
    model.add(layers.Input(shape=(input_dim,)))
    for i in range(n_layers):
        units = hp.Int(f"units_{i}", min_value=64, max_value=256, step=32)
        model.add(layers.Dense(units, activation="relu", kernel_regularizer=reg))
        model.add(layers.BatchNormalization())
        model.add(layers.Dropout(dropout))
    model.add(layers.Dense(1, activation=None))

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=lr),
        loss="mse",
        metrics=["mae"],
    )
    return model


tuner = kt.RandomSearch(
    hypermodel=build_ffnn,
    objective=kt.Objective("val_loss", direction="min"),
    max_trials=int(os.environ.get("KT_MAX_TRIALS", "8")),
    directory=str(tuner_dir),
    project_name="stars_ffnn",
    overwrite=os.environ.get("KT_OVERWRITE", "1") == "1",
)

es = EarlyStopping(monitor="val_loss", patience=12, restore_best_weights=True, verbose=1)
rlr = ReduceLROnPlateau(
    monitor="val_loss", factor=0.5, patience=5, min_lr=1e-6, verbose=1
)

tuner.search(
    X_train,
    y_train,
    validation_split=0.15,
    epochs=int(os.environ.get("KT_EPOCHS", "40")),
    batch_size=int(os.environ.get("KT_BATCH", "256")),
    callbacks=[es, rlr],
    verbose=1,
)

best_hp = tuner.get_best_hyperparameters(1)[0]
print("Best hyperparameters:", best_hp.values)

best_model = tuner.get_best_models(1)[0]
pred_nn = best_model.predict(X_test, verbose=0).ravel()
nn_metrics = metrics_dict(y_test, pred_nn)
print("Test — main FNN:", nn_metrics)
""")

code("""
# Optional: short retrain on train+val with best hps for slightly cleaner test eval (uses same split holdout)
# Skip if you are time-constrained — the tuner model above already uses EarlyStopping + best weights.

rows = baseline_df.reset_index().rename(columns={"index": "model"})
rows = pd.concat(
    [
        rows,
        pd.DataFrame(
            [{"model": "Neural Net (FNN, tuned)", "r2": nn_metrics["r2"], "mae": nn_metrics["mae"], "mse": nn_metrics["mse"]}]
        ),
    ],
    ignore_index=True,
)

summary = rows.set_index("model").sort_values("r2", ascending=False)
print("\\n=== Test-set comparison (higher R² is better) ===")
print(summary.to_string())

fig, ax = plt.subplots(figsize=(9, 4))
xpos = np.arange(len(summary))
ax.barh(xpos, summary["r2"].values, color="steelblue")
ax.set_yticks(xpos)
ax.set_yticklabels(summary.index.tolist())
ax.set_xlabel("R² (test)")
ax.set_title("Baselines vs main neural network")
ax.axvline(nn_metrics["r2"], color="crimson", linestyle="--", label="FNN")
ax.legend()
plt.tight_layout()
plt.show()

best_baseline_r2 = summary.drop(index=["Neural Net (FNN, tuned)"], errors="ignore")["r2"].max()
print(f"\\nBest baseline R²: {best_baseline_r2:.4f} | Main FNN R²: {nn_metrics['r2']:.4f}")
if nn_metrics["r2"] >= best_baseline_r2 - 1e-4:
    print("FNN matches or beats the best baseline on R² (within numerical tolerance).")
else:
    print("FNN slightly below best baseline — try more tuner trials / epochs or log-transform targets.")
""")

md("""
## Part C — **Optional:** small LSTM on a **weekly activity proxy**

Real temporal features should come from **GH Archive** (weekly commits / stars). Here we build a **toy 5-week sequence** per repo from `commits` (with small deterministic drift + noise) so you can run an LSTM end-to-end without extra files.

**Replace `seq_train` / `seq_test`** with your `(n_samples, n_weeks, n_features)` tensor when GH Archive data is merged.
""")

code("""
if com_tr is None:
    print("No 'commits' column — skipping LSTM demo.")
else:
    rng = np.random.default_rng(42)

    def weekly_proxy(commit_series: pd.Series | np.ndarray) -> np.ndarray:
        c = np.maximum(np.asarray(commit_series, dtype=np.float32), 0.0)
        T = 5
        # pseudo-weekly "activity" around commits (illustrative only)
        seq = np.stack(
            [c * (1.0 + 0.04 * t) + rng.normal(0, 0.02 * (c + 1.0), size=c.shape) for t in range(T)],
            axis=1,
        )
        return seq[..., np.newaxis]  # (n, T, 1)

    seq_train = weekly_proxy(com_tr)
    seq_test = weekly_proxy(com_te)

    lstm = keras.Sequential(
        [
            layers.Input(shape=seq_train.shape[1:]),
            layers.LSTM(32, return_sequences=False),
            layers.Dropout(0.2),
            layers.Dense(16, activation="relu"),
            layers.Dense(1),
        ],
        name="lstm_weekly_proxy",
    )
    lstm.compile(optimizer=keras.optimizers.Adam(1e-3), loss="mse", metrics=["mae"])
    lstm.fit(
        seq_train,
        y_train,
        validation_split=0.15,
        epochs=25,
        batch_size=512,
        callbacks=[
            EarlyStopping(monitor="val_loss", patience=6, restore_best_weights=True)
        ],
        verbose=1,
    )
    pred_lstm = lstm.predict(seq_test, verbose=0).ravel()
    lstm_m = metrics_dict(y_test, pred_lstm)
    print("LSTM (proxy sequences) test metrics:", lstm_m)
""")

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    },
    "cells": cells,
}

OUT.write_text(json.dumps(nb, indent=1), encoding="utf-8")
print("Wrote", OUT)
