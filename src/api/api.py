import json
import os
import sys

import pandas as pd
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FILTERED_DATASET_CANDIDATES = [
    os.path.join(BASE_DIR, "app", "outputs", "datasets", "processed", "filtered_dataset.csv"),
    os.path.join(BASE_DIR, "app", "outputs", "datasets", "phones", "processed", "filtered_dataset.csv"),
    os.path.join(BASE_DIR, "app", "outputs", "datasets", "computers", "processed", "filtered_dataset.csv"),
    os.path.join(BASE_DIR, "app", "output", "dataset", "final", "step8_final_model_ready.csv"),
    os.path.join(BASE_DIR, "app", "output", "dataset", "processed_step", "step8_final_model_ready.csv"),
    os.path.join(BASE_DIR, "app", "output", "dataset", "raw", "full_dataset.csv"),
]
EXCLUDED_FEATURES = {"urun_fiyat", "urun_puan"}


def collect_feature_columns():
    ordered_columns = []
    seen_columns = set()

    for path in FILTERED_DATASET_CANDIDATES:
        if not os.path.exists(path):
            continue

        dataset_columns = pd.read_csv(path, nrows=0).columns.tolist()
        for column in dataset_columns:
            if column in EXCLUDED_FEATURES or column in seen_columns:
                continue
            seen_columns.add(column)
            ordered_columns.append(column)

    if not ordered_columns:
        raise FileNotFoundError(
            "No filtered dataset found. Checked paths: "
            + ", ".join(FILTERED_DATASET_CANDIDATES)
        )

    return ordered_columns


@app.route("/")
def home():
    return "API Home Page"


@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    param = data.get("param", "")

    return jsonify({"your param": param})


@app.route("/get_features", methods=["GET"])
def get_features():
    try:
        features = collect_feature_columns()
    except Exception as exc:
        return Response(
            json.dumps({"features": [], "error": str(exc)}, ensure_ascii=False),
            status=500,
            mimetype="application/json; charset=utf-8",
        )

    return Response(
        json.dumps({"features": features}, ensure_ascii=False),
        mimetype="application/json; charset=utf-8",
    )


if __name__ == "__main__":
    app.run()
