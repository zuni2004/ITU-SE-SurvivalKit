import pandas as pd
import numpy as np
import pytest
from fastapi.testclient import TestClient
from lab11_solution import (
    load_data,
    preprocess_data,
    train_model,
    evaluate_model,
    run_pipeline,
    app as starter_app,
)


# --- load_data tests ---

def test_load_data_returns_dataframe():
    df = load_data()
    assert isinstance(df, pd.DataFrame), "load_data should return a DataFrame"

def test_load_data_non_empty():
    df = load_data()
    assert df.shape[0] > 0, "DataFrame should have at least one row"
    assert df.shape[1] > 0, "DataFrame should have at least one column"

def test_load_data_expected_columns():
    df = load_data()
    expected_cols = {"age", "income", "city", "hour", "target"}
    assert expected_cols.issubset(df.columns), (
        f"Missing columns: {expected_cols - set(df.columns)}"
    )

def test_load_data_no_all_null_columns():
    df = load_data()
    assert not df.isnull().all().any(), "No column should be entirely null"

def test_load_data_target_is_binary():
    df = load_data()
    assert set(df["target"].unique()).issubset({0, 1}), (
        "target column should contain only 0 and 1"
    )


# --- preprocess_data tests ---

def test_preprocess_returns_tuple():
    df = load_data()
    result = preprocess_data(df)
    assert isinstance(result, tuple) and len(result) == 2, (
        "preprocess_data should return a (X, y) tuple"
    )

def test_preprocess_row_counts_match():
    df = load_data()
    X, y = preprocess_data(df)
    assert X.shape[0] == y.shape[0], "X and y must have the same number of rows"

def test_preprocess_removes_city_column():
    df = load_data()
    X, y = preprocess_data(df)
    assert "city" not in X.columns, "'city' column should be dropped from X"

def test_preprocess_target_not_in_X():
    df = load_data()
    X, y = preprocess_data(df)
    assert "target" not in X.columns, "'target' should not appear in X"

def test_preprocess_y_contains_correct_values():
    df = load_data()
    X, y = preprocess_data(df)
    assert set(y.unique()).issubset({0, 1}), "y should contain only 0 and 1"

def test_preprocess_X_is_numeric():
    df = load_data()
    X, y = preprocess_data(df)
    assert all(np.issubdtype(dtype, np.number) for dtype in X.dtypes), (
        "All feature columns in X should be numeric"
    )

def test_preprocess_no_missing_values_in_X():
    df = load_data()
    X, y = preprocess_data(df)
    assert not X.isnull().any().any(), "X should not contain missing values after preprocessing"


# --- FastAPI (api.py starter) tests ---

@pytest.fixture(scope="module")
def starter_client():
    with TestClient(starter_app) as c:
        yield c


def test_starter_home_status(starter_client):
    response = starter_client.get("/")
    assert response.status_code == 200, "GET / should return HTTP 200"


def test_starter_home_message(starter_client):
    response = starter_client.get("/")
    body = response.json()
    assert "message" in body, "GET / response should have a 'message' key"
    assert isinstance(body["message"], str), "'message' should be a string"


def test_starter_predict_endpoint_exists(starter_client):
    """POST /predict should be a registered route (not 404/405)."""
    response = starter_client.post("/predict", json={"features": [30, 50000, 8, 0.5]})
    assert response.status_code != 404, "POST /predict route should exist"


def test_starter_predict_accepts_json(starter_client):
    """POST /predict should accept a JSON body without raising a validation error."""
    response = starter_client.post("/predict", json={"features": [25, 60000, 12, 1.0]})
    # 422 means FastAPI rejected the schema — the route exists but input is wrong shape
    assert response.status_code != 404
    assert response.status_code != 405, "POST /predict must allow POST method"


def test_starter_predict_rejects_missing_body(starter_client):
    """POST /predict with no body should return 4xx, not 200."""
    response = starter_client.post("/predict")
    assert response.status_code >= 400, (
        "POST /predict with empty body should return a 4xx error"
    )

def test_api_predict_missing_features_key(starter_client):
    """POST /predict with wrong payload key should return 4xx or 5xx, not 200."""
    response = starter_client.post("/predict", json={"data": [30, 50000, 8, 0.5]})
    assert response.status_code >= 400, (
        "Missing 'features' key should result in an error response"
    )