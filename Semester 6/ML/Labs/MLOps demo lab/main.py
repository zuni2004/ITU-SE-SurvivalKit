from fastapi import FastAPI
from pydantic import BaseModel
import joblib
from pathlib import Path
from typing import List
from sklearn.datasets import load_iris

app = FastAPI()

# Load model from the same directory as this script
MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"
model = joblib.load(MODEL_PATH)

# Load target names for mapping numeric predictions to human-friendly labels
_IRIS = load_iris()
TARGET_NAMES = _IRIS.target_names

class Features(BaseModel):
    features: List[float]

@app.post("/predict")
def predict(features: Features):
    prediction = model.predict([features.features])
    pred_idx = int(prediction[0])
    class_name = TARGET_NAMES[pred_idx]
    return {"prediction": class_name, "confidence": float(model.predict_proba([features.features])[0][pred_idx])}

@app.get("/message")
def read_root(number1: int = 1, number2: int = 2):
    return {"message": "Hello, FastAPI!", "numbers": number1 + number2}