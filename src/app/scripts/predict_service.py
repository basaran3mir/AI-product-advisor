import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

from .dataset.dataset_processor import ProductDataPreprocessor


class PredictService:

    def __init__(self, task: str):
        """
        task: "price" veya "point"
        """

        self.task = task

        BASE_DIR = Path(__file__).resolve().parents[4]
        MODEL_DIR = BASE_DIR / "AI-product-advisor/src/app/output/model"

        if task == "price":
            model_path = MODEL_DIR / "price/xgboost_urun_fiyat_model.pkl"
            features_path = MODEL_DIR / "price/model_features.json"
            self.log_transformed = True

        elif task == "point":
            model_path = MODEL_DIR / "point/xgboost_urun_puan_model.pkl"
            features_path = MODEL_DIR / "point/model_features.json"
            self.log_transformed = False

        else:
            raise ValueError("task must be 'price' or 'point'")

        self.model = joblib.load(model_path)

        with open(features_path, "r", encoding="utf-8") as f:
            self.model_features = json.load(f)

        if task == "price":
            self.processor = ProductDataPreprocessor(
                input_path="",
                process_dir="",
                output_dir="",
                mode="predict",
                target="urun_fiyat",
                exclude="urun_puan"
            )
        elif task == "point":
            self.processor = ProductDataPreprocessor(
                input_path="",
                process_dir="",
                output_dir="",
                mode="predict",
                target="urun_puan",
                exclude="urun_fiyat"
            )

    # =====================================
    # PREDICT
    # =====================================

    def predict(self, input_df: pd.DataFrame) -> float:

        X_processed = self.processor.transform_for_prediction(input_df)

        X_processed = X_processed.reindex(
            columns=self.model_features,
            fill_value=0
        )

        raw_pred = self.model.predict(X_processed)[0]

        if self.log_transformed:
            result = float(np.expm1(raw_pred))
        else:
            result = float(raw_pred)

        return result

    # =====================================
    # EXPECTED FEATURES
    # =====================================

    def get_expected_features(self):
        return self.model_features
