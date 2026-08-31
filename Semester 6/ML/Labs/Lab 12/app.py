from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np

app = Flask(__name__)

try:
    model = joblib.load("model.joblib")
except:
    model = None


@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    if request.method == "POST":
        try:
            features = [
                float(request.form["f1"]),
                float(request.form["f2"]),
                float(request.form["f3"]),
                float(request.form["f4"]),
            ]

            input_data = np.array(features).reshape(1, -1)
            prediction = int(model.predict(input_data)[0])

        except Exception as e:
            prediction = f"Error: {str(e)}"

    return render_template("index.html", prediction=prediction)


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if not data or "features" not in data:
        return jsonify({"error": "Missing 'features' key"}), 422
    if model is None:
        return jsonify({"error": "Model not loaded"}), 503
    try:
        features = np.array(data["features"]).reshape(1, -1)
        prediction = model.predict(features)
        return jsonify({"prediction": int(prediction[0])})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
