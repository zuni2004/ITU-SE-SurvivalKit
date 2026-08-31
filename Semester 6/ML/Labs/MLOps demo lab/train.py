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
)

# ------------------------------------------------------------------
# MLflow setup
# ------------------------------------------------------------------
TRACKING_URI = "sqlite:///mlruns.db"
EXPERIMENT_NAME = "iris_decision_tree_grid_search"

mlflow.set_tracking_uri(TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)
mlflow.set_experiment_tags({
    "mlflow.note.content": (
        "Grid search over DecisionTreeClassifier hyperparameters "
        "(max_depth × criterion) on the Iris dataset."
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

# ------------------------------------------------------------------
# Hyperparameters
# ------------------------------------------------------------------
max_depth = 3
criterion = "gini"

# ------------------------------------------------------------------
# Train + track
# ------------------------------------------------------------------
with mlflow.start_run(run_name=f"depth_{max_depth}_crit_{criterion}"):

    mlflow.set_tags({
        "model_type": "DecisionTreeClassifier",
        "dataset": "iris",
        "split_strategy": "train_test_split",
        "mlflow.note.content": (
            f"Single training run: max_depth={max_depth}, criterion={criterion}"
        ),
    })

    mlflow.log_params({
        "model": "DecisionTreeClassifier",
        "max_depth": max_depth,
        "criterion": criterion,
        "random_state": 42,
        "test_size": 0.2,
        "n_features": len(feature_names),
        "n_classes": len(target_names),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
    })

    mlflow.log_input(mlflow_train_ds, context="training")
    mlflow.log_input(mlflow_test_ds, context="validation")

    model = DecisionTreeClassifier(
        max_depth=max_depth,
        criterion=criterion,
        random_state=42,
    )
    model.fit(X_train, y_train)

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
        "tree_depth_actual": model.get_depth(),
        "n_leaves": model.get_n_leaves(),
    })

    input_example = pd.DataFrame(X_test[:5], columns=feature_names)
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

    print(f"Accuracy:  {acc:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")