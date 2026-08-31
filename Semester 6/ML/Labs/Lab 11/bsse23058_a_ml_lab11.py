# ============================================================
# Imports
# ============================================================

# Standard data / ML libraries
import pandas as pd
import numpy as np
import joblib
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

# FastAPI framework — HTTPException is available for use in the API section
from fastapi import FastAPI, HTTPException

# ============================================================
# ML Pipeline
# ============================================================

# Accuracy threshold used by tests to validate pipeline quality
expected_accuracy = 0.8


def load_data():
    """
    Load the dataset from the CSV file.

    Returns:
        pd.DataFrame: The loaded dataframe containing the data.
    """
    df = pd.read_csv("lab10_data.csv")
    return df


def preprocess_data(df):
    """
    Preprocess the input dataframe by cleaning and preparing features and target.

    Args:
        df (pd.DataFrame): The raw dataframe loaded from the CSV.

    Returns:
        tuple: A tuple containing (X, y) where X is the feature matrix and y is the target vector.
    """
    if "city" in df.columns:
        df = df.drop(columns=["city"])

    X = df.drop("target", axis=1)
    y = df["target"]
    return X, y


def train_model(X, y):
    """
    Train a machine learning model using the provided features and target.

    Args:
        X (pd.DataFrame or np.ndarray): The feature matrix.
        y (pd.Series or np.ndarray): The target vector.

    Returns:
        object: The trained model object.
    """
    model = DecisionTreeClassifier(
        random_state=42, max_depth=100, min_samples_split=2, min_samples_leaf=1
    )
    model.fit(X, y)
    return model


def evaluate_model(model, X, y):
    """
    Evaluate the trained model on the given data and return the accuracy.

    Args:
        model (object): The trained model.
        X (pd.DataFrame or np.ndarray): The feature matrix for evaluation.
        y (pd.Series or np.ndarray): The true target values.

    Returns:
        float: The accuracy score of the model.
    """
    predictions = model.predict(X)
    acc = accuracy_score(y, predictions)
    return acc


def run_pipeline():
    """
    Run the complete ML pipeline: load data, preprocess, train, evaluate, and save the model.

    Returns:
        float: The accuracy of the trained model on the training data.
    """
    df = load_data()
    X, y = preprocess_data(df)

    with mlflow.start_run():
        model = train_model(X, y)
        acc = evaluate_model(model, X, y)

        mlflow.log_param("max_depth", 100)
        mlflow.log_param("random_state", 42)

        mlflow.log_metric("accuracy", acc)

        mlflow.sklearn.log_model(model, "decision_tree_model")

        joblib.dump(model, "model.joblib")

        print(f"Pipeline complete. Accuracy: {acc}")
        return acc


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI()

try:
    model = joblib.load("model.joblib")
except:
    model = None


@app.get("/")
def home():
    # Returns a simple status message to confirm the API is reachable.
    return {"message": "ML Model API is running"}


@app.post("/predict")
def predict(data: dict):
    """
    Run inference for a single sample.

    Expected JSON body:
        { "features": [age, income, hour, leak_feature] }

    Returns:
        dict: { "prediction": 0 or 1 }
    """
    if "features" not in data:
        raise HTTPException(
            status_code=422, detail="Missing 'features' key in request body"
        )

    if model is None:
        raise HTTPException(
            status_code=503, detail="Model not loaded. Please run the pipeline first."
        )

    try:
        features = np.array(data["features"]).reshape(1, -1)
        prediction = model.predict(features)
        return {"prediction": int(prediction[0])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inference error: {str(e)}")
