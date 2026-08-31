# Iris ML Demo

A small end-to-end machine-learning project on the classic [Iris dataset](https://scikit-learn.org/stable/datasets/toy_dataset.html#iris-dataset). It covers model training, hyperparameter grid search, experiment tracking with MLflow, and serving predictions via a FastAPI endpoint.

---

## Project structure

```
demos/
├── modelling.py          # Logistic Regression baseline — trains & saves model.pkl
├── train.py              # Single DecisionTree training run tracked in MLflow
├── run_experiments.py    # Grid search (max_depth × criterion) tracked in MLflow
├── main.py               # FastAPI inference server (POST /predict)
├── results.csv           # Aggregated grid-search results (auto-generated)
├── model.pkl             # Serialised model loaded by the API (auto-generated)
└── mlruns.db             # SQLite MLflow tracking store (auto-generated)
```

---

## Requirements

```
scikit-learn
mlflow
pandas
numpy
fastapi
uvicorn
joblib
```

Install everything in one step:

```bash
pip install scikit-learn mlflow pandas numpy fastapi uvicorn joblib
```

---

## Scripts

### `modelling.py` — Logistic Regression baseline

Trains a `LogisticRegression` model on the Iris dataset, tracks the run in MLflow, and writes `model.pkl` for the API server.

```bash
python modelling.py
```

**Tracked in MLflow**

| Kind | Name |
|------|------|
| Params | `model`, `max_iter`, `random_state`, `test_size`, `n_features`, `n_classes`, `train_samples`, `test_samples` |
| Metrics | `accuracy`, `f1_score`, `precision`, `recall` |
| Dataset | `iris_train` (training context) |
| Model | `logistic_regression_model` (with signature & input example) |

---

### `train.py` — Single DecisionTree run

Trains a single `DecisionTreeClassifier` with configurable `max_depth` and `criterion` and logs everything to MLflow.

```bash
python train.py
```

Edit the two constants near the top of the file to change hyperparameters:

```python
max_depth = 3
criterion = "gini"   # or "entropy"
```

**Tracked in MLflow**

| Kind | Name |
|------|------|
| Params | `model`, `max_depth`, `criterion`, `random_state`, `test_size`, `n_features`, `n_classes`, `train_samples`, `test_samples` |
| Metrics | `accuracy`, `f1_score`, `precision`, `recall`, `tree_depth_actual`, `n_leaves` |
| Datasets | `iris_train` (training), `iris_test` (validation) |
| Model | `decision_tree_model` (with signature & input example) |

---

### `run_experiments.py` — Grid search

Performs a full grid search over:

- `max_depth` ∈ `[2, 3, 5, 10]`
- `criterion` ∈ `["gini", "entropy"]`

producing **8 training runs** plus a `grid_search_summary` run that logs the aggregated `results.csv` as an artifact.

```bash
python run_experiments.py
```

**Tracked per run**

| Kind | Name |
|------|------|
| Params | `model`, `max_depth`, `criterion`, `random_state`, `test_size`, `n_features`, `n_classes`, `train_samples`, `test_samples`, `serialization` |
| Metrics | `accuracy`, `f1_score`, `precision`, `recall`, `tree_depth_actual`, `n_leaves`, per-class `f1_*` / `precision_*` / `recall_*` |
| Datasets | `iris_train` (training), `iris_test` (validation) |
| Model | `decision_tree_model` (with signature & input example) |
| Tags | `model_type`, `dataset`, `split_strategy`, `mlflow.note.content` |

**Summary run extras**

| Kind | Name |
|------|------|
| Params | `n_runs` |
| Metrics | `best_accuracy` |
| Tags | `best_run_id` |
| Artifact | `summary/results.csv` |

---

## MLflow UI

All scripts share a single SQLite tracking store (`mlruns.db`) and the experiment `iris_decision_tree_grid_search`. Launch the UI after running any script:

```bash
mlflow ui --backend-store-uri sqlite:///mlruns.db --default-artifact-root mlruns
```

Then open <http://127.0.0.1:5000> in your browser.

> **Why SQLite?** The file-based backend (`mlruns/`) does not support the Overview tab or full experiment metadata. The SQLite backend enables all UI features.

---

## FastAPI inference server

`main.py` loads `model.pkl` (produced by `modelling.py`) and exposes a prediction endpoint.

```bash
uvicorn main:app --reload
```

**POST** `http://127.0.0.1:8000/predict`

```json
{
  "features": [5.1, 3.5, 1.4, 0.2]
}
```

Response:

```json
{
  "prediction": "setosa",
  "confidence": 0.97
}
```

Interactive docs are available at <http://127.0.0.1:8000/docs>.

---

## Typical workflow

```bash
# 1. Train baseline and produce model.pkl
python modelling.py

# 2. Run the full grid search
python run_experiments.py

# 3. Inspect results in the MLflow UI
mlflow ui --backend-store-uri sqlite:///mlruns.db --default-artifact-root mlruns

# 4. Serve predictions
uvicorn main:app --reload
```
