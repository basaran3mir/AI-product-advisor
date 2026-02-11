import os
import sys  
import pandas as pd
import json
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATASET_PATH = "src/app/outputs/datasets/final/step8_final_model_ready.csv"
EXCLUDED_FEATURES = {
    "urun_fiyat",
    "urun_puan"
}

@app.route('/')
def home():
    return "API Home Page"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    param = data.get('param', '')

    return jsonify({'your param': param})

@app.route('/get_features', methods=['GET'])
def get_features():
    df = pd.read_csv(DATASET_PATH)
    features = [
        col for col in df.columns
        if col not in EXCLUDED_FEATURES
    ]

    return Response(
        json.dumps({"features": features}, ensure_ascii=False),
        mimetype="application/json; charset=utf-8"
    )

if __name__ == '__main__':
    app.run()