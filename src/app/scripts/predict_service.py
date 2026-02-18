import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

from .dataset.dataset_processor import ProductDataPreprocessor

class PredictService:

    def __init__(self):
        BASE_DIR = Path(__file__).resolve().parents[4]
        MODEL_DIR = BASE_DIR / "AI-product-advisor/src/app/output/model"

        self.model = joblib.load(MODEL_DIR / "xgboost_price_model.pkl")

        with open(MODEL_DIR / "model_features.json", "r", encoding="utf-8") as f:
            self.model_features = json.load(f)

        self.processor = ProductDataPreprocessor(
            input_path="",
            process_dir="",
            output_dir="",
            mode="predict"
        )

    def predict(self, input_df: pd.DataFrame) -> float:

        X_processed = self.processor.transform_for_prediction(input_df)

        X_processed = X_processed.reindex(
            columns=self.model_features,
            fill_value=0
        )

        log_pred = self.model.predict(X_processed)[0]
        price = float(np.expm1(log_pred))

        return price

    def get_expected_features(self):
        return self.model_features
