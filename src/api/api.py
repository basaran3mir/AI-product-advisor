import os
import sys
import traceback
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

# path ayarı
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(BASE_DIR)

from src.app.scripts.predict_service import PredictService

app = Flask(__name__)
CORS(app)

# Service instance (tek sefer yüklenir)
predict_service = PredictService()


@app.route("/")
def home():
    return "Price Prediction API is running."


# --------------------------------------------------
# PREDICT ENDPOINT
# --------------------------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON body provided"}), 400

        input_df = pd.DataFrame([data])

        predicted_price = predict_service.predict(input_df)

        return jsonify({
            "predicted_price": round(predicted_price, 2)
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500


# --------------------------------------------------
# FEATURE LIST ENDPOINT
# --------------------------------------------------
@app.route("/get_features", methods=["GET"])
def get_features():
    try:
        features = predict_service.get_expected_features()
        return jsonify({"features": features})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
