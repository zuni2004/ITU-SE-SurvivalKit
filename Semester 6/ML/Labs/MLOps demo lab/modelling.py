import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature

import pandas as pd
import joblib
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
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

# ------------------------------------------------------------------
# Data
# ------------------------------------------------------------------
iris = load_iris()
X, y = iris.data, iris.target
feature_names = list(iris.feature_names)
target_names = list(iris.target_names)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

train_df = pd.DataFrame(X_train, columns=feature_names)
train_df["target"] = y_train
mlflow_train_ds = mlflow.data.from_pandas(
    train_df, name="iris_train", targets="target"
)

# ------------------------------------------------------------------
# Train + track
# ------------------------------------------------------------------
max_iter = 200

with mlflow.start_run(run_name="logistic_regression_baseline"):

    mlflow.set_tags({
        "model_type": "LogisticRegression",
        "dataset": "iris",
        "split_strategy": "train_test_split",
        "mlflow.note.content": (
            "Logistic Regression baseline trained on the full Iris dataset."
        ),
    })

    mlflow.log_params({
        "model": "LogisticRegression",
        "max_iter": max_iter,
        "random_state": 42,
        "test_size": 0.2,
        "n_features": len(feature_names),
        "n_classes": len(target_names),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
    })

    mlflow.log_input(mlflow_train_ds, context="training")

    model = LogisticRegression(max_iter=max_iter)
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
    })

    input_example = pd.DataFrame(X_test[:5], columns=feature_names)
    signature = infer_signature(
        pd.DataFrame(X_train, columns=feature_names),
        model.predict(X_train),
    )
    mlflow.sklearn.log_model(
        model,
        name="logistic_regression_model",
        signature=signature,
        input_example=input_example,
    )

    # Also persist locally for the FastAPI server
    joblib.dump(model, "model.pkl")

    print(f"Accuracy:  {acc:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print("Model saved as model.pkl")