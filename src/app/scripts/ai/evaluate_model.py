import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
from datetime import datetime


class ModelEvaluator:
    """
    Generic model evaluation class
    Supports both log-transformed and normal targets
    """

    def __init__(
        self,
        data_path: Path,
        model_path: Path,
        output_dir: Path,
        target_column: str,
        task_name: str,
        unit: str = "",
        segment_type: str = None,
        ignore_columns: list | None = None
    ):
        self.data_path = data_path
        self.model_path = model_path
        self.output_dir = output_dir
        self.target_column = target_column
        self.task_name = task_name
        self.unit = unit
        self.segment_type = segment_type

        self.ignore_columns = ignore_columns if ignore_columns else []

        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.df = None
        self.model = None
        self.results = None

    # =====================================
    # LOAD
    # =====================================

    def load(self):
        self.df = pd.read_csv(self.data_path)
        self.model = joblib.load(self.model_path)
        print(f"{self.task_name} veri ve model yüklendi.")

    # =====================================
    # PREDICT
    # =====================================

    def predict(self):
        df_copy = self.df.copy()

        # 🔥 Ignore columns güvenli şekilde düşürülür
        cols_to_drop = [
            col for col in self.ignore_columns
            if col in df_copy.columns
        ]

        df_copy = df_copy.drop(columns=cols_to_drop)

        X = df_copy.drop(columns=[self.target_column])
        y_true_raw = df_copy[self.target_column]

        y_pred_raw = self.model.predict(X)

        y_true = np.expm1(y_true_raw)
        y_pred = np.expm1(y_pred_raw)

        self.results = pd.DataFrame({
            "Gerçek": y_true,
            "Tahmin": y_pred,
        })

        self.results["Mutlak_Hata"] = np.abs(
            self.results["Gerçek"] -
            self.results["Tahmin"]
        )

        self.results["Yuzde_Hata"] = (
            self.results["Mutlak_Hata"] /
            self.results["Gerçek"].replace(0, np.nan) * 100
        )

        self.results.sort_values("Mutlak_Hata", inplace=True)

        print("Tahminler üretildi.")


    # =====================================
    # SAVE PREDICTIONS (BEST / WORST)
    # =====================================

    def save_predictions(self):

        # Tüm tahminler
        self.results.to_csv(
            self.output_dir / "all_predictions.csv",
            index=False
        )

        # Mutlak hataya göre sıralanmış kopya
        sorted_results = self.results.sort_values(
            "Mutlak_Hata",
            ascending=True
        )

        best_10 = sorted_results.head(10)
        worst_10 = sorted_results.tail(10)

        best_10.to_csv(
            self.output_dir / "best_10_predictions.csv",
            index=False
        )

        worst_10.to_csv(
            self.output_dir / "worst_10_predictions.csv",
            index=False
        )

        print("Best ve Worst 10 kayıtları kaydedildi.")

    # =====================================
    # METRICS
    # =====================================

    def calculate_metrics(self):
        y_true = self.results["Gerçek"]
        y_pred = self.results["Tahmin"]

        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        mape = np.nanmean(np.abs((y_true - y_pred) / y_true)) * 100

        return {
            "rmse": rmse,
            "mae": mae,
            "r2": r2,
            "mape": mape
        }

    # =====================================
    # SEGMENT ANALYSIS (only if enabled)
    # =====================================

    def _segment_price(self, value):
        if value < 10000:
            return "0-10K"
        elif value < 25000:
            return "10K-25K"
        elif value < 50000:
            return "25K-50K"
        elif value < 100000:
            return "50K-100K"
        else:
            return "100K+"

    def _segment_point(self, value):
        if value < 20:
            return "0-20"
        elif value < 40:
            return "20-40"
        elif value < 60:
            return "40-60"
        elif value < 80:
            return "60-80"
        else:
            return "80-100"
        
    def segment_analysis(self):
        if self.segment_type is None:
            return None

        if self.segment_type == "price":
            self.results["Segment"] = self.results["Gerçek"].apply(
                self._segment_price
            )

        elif self.segment_type == "point":
            self.results["Segment"] = self.results["Gerçek"].apply(
                self._segment_point
            )

        segment_df = self.results.groupby("Segment").agg({
            "Mutlak_Hata": "mean",
            "Yuzde_Hata": "mean",
            "Gerçek": "count"
        }).rename(columns={"Gerçek": "Adet"})

        segment_df.to_csv(
            self.output_dir / "segment_analysis.csv"
        )

        return segment_df

    # =====================================
    # PLOTS
    # =====================================

    def generate_plots(self):
        y_true = self.results["Gerçek"]
        y_pred = self.results["Tahmin"]

        plt.figure()
        plt.scatter(y_true, y_pred)
        plt.xlabel("Gerçek")
        plt.ylabel("Tahmin")
        plt.title(f"{self.task_name} - Gerçek vs Tahmin")
        plt.savefig(self.output_dir / "real_vs_pred.png")
        plt.close()

        residuals = y_true - y_pred
        plt.figure()
        plt.scatter(y_pred, residuals)
        plt.axhline(0)
        plt.xlabel("Tahmin")
        plt.ylabel("Residual")
        plt.title(f"{self.task_name} - Residual Plot")
        plt.savefig(self.output_dir / "residual_plot.png")
        plt.close()

    # =====================================
    # REPORT
    # =====================================

    def save_report(self, metrics: dict, segment_df):

        report_path = self.output_dir / "evaluation_report.txt"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write(f"{self.task_name.upper()} MODEL EVALUATION REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Oluşturulma Tarihi: {datetime.now()}\n\n")

            f.write("GENEL METRİKLER\n")
            f.write("-" * 30 + "\n")
            f.write(f"RMSE: {metrics['rmse']:.4f} {self.unit}\n")
            f.write(f"MAE: {metrics['mae']:.4f} {self.unit}\n")
            f.write(f"R2: {metrics['r2']:.4f}\n")
            f.write(f"MAPE (%): {metrics['mape']:.2f}\n\n")

            if segment_df is not None:
                f.write("Segment Bazlı Ortalama Hata\n")
                f.write("-" * 30 + "\n")
                f.write(segment_df.to_string())
                f.write("\n")

        print(f"Rapor kaydedildi: {report_path}")

    # =====================================
    # PIPELINE
    # =====================================

    def run(self):
        self.load()
        self.predict()
        self.save_predictions()
        metrics = self.calculate_metrics()
        segment_df = self.segment_analysis()
        self.generate_plots()
        self.save_report(metrics, segment_df)

        print(f"{self.task_name} evaluation tamamlandı.")

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parents[4]

    price_evaluator = ModelEvaluator(
        data_path=BASE_DIR / "src/app/output/dataset/final/final_dataset.csv",
        model_path=BASE_DIR / "src/app/output/model/price/xgboost_urun_fiyat_model.pkl",
        output_dir=BASE_DIR / "src/app/output/model/price/evaluation",
        target_column="urun_fiyat",
        task_name="price",
        unit="TL",
        segment_type="price",
        ignore_columns=["urun_puan", "urun_id", "urun_ad"]
    )

    price_evaluator.run()

    point_evaluator = ModelEvaluator(
        data_path=BASE_DIR / "src/app/output/dataset/final/final_dataset.csv",
        model_path=BASE_DIR / "src/app/output/model/point/xgboost_urun_puan_model.pkl",
        output_dir=BASE_DIR / "src/app/output/model/point/evaluation",
        target_column="urun_puan",
        task_name="point",
        unit="Puan",
        segment_type="point",
        ignore_columns=["urun_fiyat", "urun_id", "urun_ad"]
    )

    point_evaluator.run()
