import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

import xgboost as xgb

class XGBoostModelTrainer:
    """
    Production-ready XGBoost training pipeline
    """

    def __init__(
        self,
        data_path: Path,
        output_dir: Path,
        target: str = "urun_fiyat",
        exclude_from_model: list[str] | None = None,
        random_state: int = 42,
    ):
        self.data_path = data_path
        self.output_dir = output_dir
        self.target = target
        self.exclude_from_model = exclude_from_model or []
        self.random_state = random_state

        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.df = None
        self.X = None
        self.y = None
        self.model = None

        self.X_train = None
        self.X_val = None
        self.X_test = None
        self.y_train = None
        self.y_val = None
        self.y_test = None

    # =====================================
    # DATA LOADING
    # =====================================

    def load_data(self) -> None:
        self.df = pd.read_csv(self.data_path)

        if self.target not in self.df.columns:
            raise ValueError(f"{self.target} bulunamadı.")

        print("Veri yüklendi.")

    # =====================================
    # FEATURE PREPARATION
    # =====================================

    def prepare_features(self) -> None:
        self.X = self.df.drop(
            columns=[self.target] + self.exclude_from_model,
            errors="ignore"
        )
        self.y = self.df[self.target]

        self._save_feature_order()

        print("Feature hazırlığı tamamlandı.")

    def _save_feature_order(self) -> None:
        feature_path = self.output_dir / "model_features.json"
        with open(feature_path, "w", encoding="utf-8") as f:
            json.dump(list(self.X.columns), f)

    # =====================================
    # DATA SPLIT
    # =====================================

    def split_data(self) -> None:
        X_train, X_temp, y_train, y_temp = train_test_split(
            self.X,
            self.y,
            test_size=0.30,
            random_state=self.random_state
        )

        X_val, X_test, y_val, y_test = train_test_split(
            X_temp,
            y_temp,
            test_size=0.50,
            random_state=self.random_state
        )

        self.X_train, self.X_val, self.X_test = X_train, X_val, X_test
        self.y_train, self.y_val, self.y_test = y_train, y_val, y_test

        print(f"Train size: {len(self.X_train)}")
        print(f"Validation size: {len(self.X_val)}")
        print(f"Test size: {len(self.X_test)}")

    # =====================================
    # MODEL INITIALIZATION
    # =====================================

    def _build_model(self) -> xgb.XGBRegressor:
        return xgb.XGBRegressor(
            n_estimators=2000,
            learning_rate=0.03,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=self.random_state,
            tree_method="hist",
            early_stopping_rounds=50,
            eval_metric="rmse"
        )

    # =====================================
    # TRAINING
    # =====================================

    def train(self) -> None:
        self.model = self._build_model()

        self.model.fit(
            self.X_train,
            self.y_train,
            eval_set=[(self.X_val, self.y_val)],
            verbose=False
        )

        print("Model eğitildi.")

    # =====================================
    # EVALUATION
    # =====================================

    def _evaluate(self, X, y, dataset_name: str) -> dict:
        preds = self.model.predict(X)

        rmse = np.sqrt(mean_squared_error(y, preds))
        mae = mean_absolute_error(y, preds)
        r2 = r2_score(y, preds)

        return {
            "dataset": dataset_name,
            "rmse": rmse,
            "mae": mae,
            "r2": r2
        }

    def evaluate(self) -> dict:
        metrics = {
            "train": self._evaluate(self.X_train, self.y_train, "train"),
            "validation": self._evaluate(self.X_val, self.y_val, "validation"),
            "test": self._evaluate(self.X_test, self.y_test, "test"),
        }

        print("Model değerlendirildi.")
        return metrics

    # =====================================
    # SAVE ARTIFACTS
    # =====================================

    def save_artifacts(self, metrics: dict) -> None:
        self._save_model()
        self._save_feature_importance()
        self._save_report(metrics)

    def _save_model(self) -> None:
        self.model.save_model(self.output_dir / f"xgboost_{self.target}_model.json")
        joblib.dump(self.model, self.output_dir / f"xgboost_{self.target}_model.pkl")

    def _save_feature_importance(self) -> None:
        importance_df = pd.DataFrame({
            "feature": self.X.columns,
            "importance": self.model.feature_importances_
        }).sort_values(by="importance", ascending=False)

        importance_df.to_csv(
            self.output_dir / "feature_importance.csv",
            index=False
        )

    def _save_report(self, metrics: dict) -> None:
        report_path = self.output_dir / "model_performance_report.txt"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("XGBOOST FİYAT TAHMİN MODELİ – PERFORMANS RAPORU\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Oluşturulma Tarihi: {datetime.now()}\n\n")

            f.write("VERİ SETİ BOYUTLARI\n")
            f.write("-" * 30 + "\n")
            f.write(f"Toplam kayıt: {len(self.df)}\n")
            f.write(f"Eğitim: {len(self.X_train)}\n")
            f.write(f"Validation: {len(self.X_val)}\n")
            f.write(f"Test: {len(self.X_test)}\n\n")

            for dataset in metrics.values():
                f.write(f"{dataset['dataset'].upper()} METRİKLERİ\n")
                f.write("-" * 30 + "\n")
                f.write(f"RMSE: {dataset['rmse']:.6f}\n")
                f.write(f"MAE:  {dataset['mae']:.6f}\n")
                f.write(f"R2:   {dataset['r2']:.6f}\n\n")

    # =====================================
    # FULL PIPELINE
    # =====================================

    def run(self) -> None:
        self.load_data()
        self.prepare_features()
        self.split_data()
        self.train()
        metrics = self.evaluate()
        self.save_artifacts(metrics)

        print("Training pipeline tamamlandı.")

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parents[4]

    price_trainer = XGBoostModelTrainer(
        data_path=BASE_DIR / "src/app/output/dataset/price/final/step8_final_model_ready.csv",
        output_dir=BASE_DIR / "src/app/output/model/price",
        target="urun_fiyat",
        exclude_from_model=["urun_puan", "urun_id"]
    )

    price_trainer.run()

    point_trainer = XGBoostModelTrainer(
        data_path=BASE_DIR / "src/app/output/dataset/point/final/step8_final_model_ready.csv",
        output_dir=BASE_DIR / "src/app/output/model/point",
        target="urun_puan",
        exclude_from_model=["urun_fiyat", "urun_id"]
    )

    point_trainer.run()