import os
import sys
import traceback
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import numpy as np

# path ayarı
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(BASE_DIR)

from src.app.scripts.predict_service import PredictService

# --------------------------------------------------
# IMAGE SERVING ENDPOINT
# --------------------------------------------------
IMAGE_DIR = os.path.join(
    BASE_DIR,
    "src/app/output/image"
)

app = Flask(__name__)

CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Service instance (tek sefer yüklenir)
price_service = PredictService(task="price")
point_service = PredictService(task="point")

@app.route("/")
def home():
    return "API is running."

@app.route("/images/<path:filename>")
def serve_image(filename):
    return send_from_directory(IMAGE_DIR, filename)

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

        predicted_price = price_service.predict(input_df)
        predicted_point = point_service.predict(input_df)

        closest_by_price = price_service.get_closest_products(
            "urun_fiyat",
            predicted_price,
            top_n=10
        )

        closest_by_point = point_service.get_closest_products(
            "urun_puan",
            predicted_point,
            top_n=10
        )

        return jsonify({
            "predicted_price": round(predicted_price, 2),
            "predicted_point": round(predicted_point, 2),
            "closest_by_price": closest_by_price,
            "closest_by_point": closest_by_point
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
        categories = price_service.get_features()
        print(f"Available categories: {categories}")
        return jsonify({"categories": categories})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
