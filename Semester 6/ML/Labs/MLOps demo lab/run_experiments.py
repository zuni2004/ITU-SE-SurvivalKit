import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature

import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    classification_report,
)

import csv


TRACKING_URI = "sqlite:///mlruns.db"
EXPERIMENT_NAME = "iris_decision_tree_grid_search"


def main():
    depths = [2, 3, 5, 10]
    criteria = ["gini", "entropy"]

    # ------------------------------------------------------------------
    # MLflow setup — explicit tracking URI so the UI and scripts agree
    # ------------------------------------------------------------------
    mlflow.set_tracking_uri(TRACKING_URI)

    experiment = mlflow.set_experiment(EXPERIMENT_NAME)
    mlflow.set_experiment_tags({
        "mlflow.note.content": (
            "Grid search over DecisionTreeClassifier hyperparameters "
            "(max_depth × criterion) on the Iris dataset. "
            "Tracks accuracy, F1, precision and recall per run."
        ),
        "dataset": "iris",
        "task": "multiclass_classification",
        "framework": "scikit-learn",
    })

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------
    data = load_iris()
    X = data.data
    y = data.target
    feature_names = list(data.feature_names)
    target_names = list(data.target_names)

    df = pd.DataFrame(X, columns=feature_names)
    df["target"] = y

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # MLflow dataset objects for lineage tracking
    train_df = pd.DataFrame(
        np.hstack([X_train, y_train.reshape(-1, 1)]),
        columns=feature_names + ["target"],
    )
    test_df = pd.DataFrame(
        np.hstack([X_test, y_test.reshape(-1, 1)]),
        columns=feature_names + ["target"],
    )
    mlflow_train_ds = mlflow.data.from_pandas(
        train_df, name="iris_train", targets="target"
    )
    mlflow_test_ds = mlflow.data.from_pandas(
        test_df, name="iris_test", targets="target"
    )

    results = []
    best_run_id = None
    best_acc = -1.0

    for d in depths:
        for crit in criteria:
            run_name = f"depth_{d}_crit_{crit}"
            with mlflow.start_run(run_name=run_name) as run:

                # ---- Tags ------------------------------------------------
                mlflow.set_tags({
                    "model_type": "DecisionTreeClassifier",
                    "dataset": "iris",
                    "split_strategy": "train_test_split",
                    "mlflow.note.content": (
                        f"DecisionTree with max_depth={d}, criterion={crit}"
                    ),
                })

                # ---- Parameters ------------------------------------------
                mlflow.log_params({
                    "model": "DecisionTreeClassifier",
                    "max_depth": d,
                    "criterion": crit,
                    "random_state": 42,
                    "test_size": 0.2,
                    "n_features": len(feature_names),
                    "n_classes": len(target_names),
                    "train_samples": len(X_train),
                    "test_samples": len(X_test),
                    "serialization": "cloudpickle",
                })

                # ---- Dataset lineage -------------------------------------
                mlflow.log_input(mlflow_train_ds, context="training")
                mlflow.log_input(mlflow_test_ds, context="validation")

                # ---- Train -----------------------------------------------
                model = DecisionTreeClassifier(
                    max_depth=d, criterion=crit, random_state=42
                )
                model.fit(X_train, y_train)

                # ---- Predict & evaluate ----------------------------------
                y_pred = model.predict(X_test)
                acc = accuracy_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred, average="macro")
                precision = precision_score(y_test, y_pred, average="macro")
                recall = recall_score(y_test, y_pred, average="macro")

                mlflow.log_metrics({
                    "accuracy": acc,
                    "f1_score": f1,
                    "precision": precision,
                    "recall": recall,
                })

                # Per-class metrics
                report = classification_report(
                    y_test, y_pred, target_names=target_names, output_dict=True
                )
                for cls in target_names:
                    mlflow.log_metrics({
                        f"f1_{cls}": report[cls]["f1-score"],
                        f"precision_{cls}": report[cls]["precision"],
                        f"recall_{cls}": report[cls]["recall"],
                    })

                # Tree depth actually used (may be < max_depth on small data)
                mlflow.log_metric("tree_depth_actual", model.get_depth())
                mlflow.log_metric("n_leaves", model.get_n_leaves())

                # ---- Model (with signature & example) --------------------
                input_example = pd.DataFrame(
                    X_test[:5], columns=feature_names
                )
                signature = infer_signature(
                    pd.DataFrame(X_train, columns=feature_names),
                    model.predict(X_train),
                )
                mlflow.sklearn.log_model(
                    model,
                    name="decision_tree_model",
                    signature=signature,
                    input_example=input_example,
                )

                print(
                    f"Run {run_name}: acc={acc:.4f}  f1={f1:.4f}  "
                    f"precision={precision:.4f}  recall={recall:.4f}"
                )

                results.append({
                    "run_name": run_name,
                    "max_depth": d,
                    "criterion": crit,
                    "accuracy": acc,
                    "f1_score": f1,
                    "precision": precision,
                    "recall": recall,
                })

                if acc > best_acc:
                    best_acc = acc
                    best_run_id = run.info.run_id

    # ------------------------------------------------------------------
    # Write & log aggregated results CSV
    # ------------------------------------------------------------------
    csv_path = "results.csv"
    fieldnames = [
        "run_name", "max_depth", "criterion",
        "accuracy", "f1_score", "precision", "recall",
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({k: r[k] for k in fieldnames})

    with mlflow.start_run(run_name="grid_search_summary") as summary_run:
        mlflow.set_tags({
            "mlflow.note.content": "Aggregated results across all grid-search runs.",
            "best_run_id": best_run_id,
        })
        mlflow.log_param("n_runs", len(results))
        mlflow.log_metric("best_accuracy", best_acc)
        mlflow.log_artifact(csv_path, artifact_path="summary")

    print(f"\nBest run: {best_run_id}  accuracy={best_acc:.4f}")
    print(f"MLflow UI: mlflow ui --backend-store-uri {TRACKING_URI} --default-artifact-root mlruns")


if __name__ == "__main__":
    main()
