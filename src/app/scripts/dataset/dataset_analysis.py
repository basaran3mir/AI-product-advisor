import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime


class DatasetAnalyzer:
    """
    Dataset EDA ve kalite analiz sınıfı
    - Genel istatistikler
    - Missing analizi
    - Cardinality analizi
    - Numeric summary
    - Target analizi
    """

    def __init__(
        self,
        input_path: str | Path,
        output_path: str | Path,
        target_column: str = "urun_fiyat",
        exclude_column: str | None = "urun_puan"
    ):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.target_column = target_column
        self.exclude_column = exclude_column

        self.df: pd.DataFrame | None = None

    # =====================================
    # LOAD DATA
    # =====================================

    def load_data(self):
        self.df = pd.read_csv(self.input_path)
        print("Dataset yüklendi.")

    # =====================================
    # GENERAL INFO
    # =====================================

    def _general_info(self):
        num_products = self.df.shape[0]
        num_features_total = self.df.shape[1]

        feature_columns = self.df.columns.tolist()

        if self.target_column in feature_columns:
            feature_columns.remove(self.target_column)

        if self.exclude_column and self.exclude_column in feature_columns:
            feature_columns.remove(self.exclude_column)

        num_features_model = len(feature_columns)

        total_missing_cells = self.df.isnull().sum().sum()

        return {
            "num_products": num_products,
            "num_features_total": num_features_total,
            "num_features_model": num_features_model,
            "total_missing_cells": total_missing_cells
        }

    # =====================================
    # DATA TYPE ANALYSIS
    # =====================================

    def _dtype_analysis(self):
        dtype_counts = self.df.dtypes.value_counts()
        dtype_table = pd.DataFrame({
            "column": self.df.columns,
            "dtype": self.df.dtypes.astype(str)
        })

        return dtype_counts, dtype_table

    # =====================================
    # MISSING ANALYSIS
    # =====================================

    def _missing_analysis(self):
        missing_count = self.df.isnull().sum()
        missing_percentage = (
            missing_count / self.df.shape[0]
        ) * 100

        missing_df = pd.DataFrame({
            "missing_count": missing_count,
            "missing_percentage": missing_percentage
        }).sort_values(by="missing_count", ascending=False)

        missing_per_row = self.df.isnull().sum(axis=1)

        row_missing_distribution = {
            "eksiksiz_urun": (missing_per_row == 0).sum(),
            "1_3_eksik": ((missing_per_row >= 1) & (missing_per_row <= 3)).sum(),
            "4_7_eksik": ((missing_per_row >= 4) & (missing_per_row <= 7)).sum(),
            "8_15_eksik": ((missing_per_row >= 8) & (missing_per_row <= 15)).sum(),
            "15_plus_eksik": (missing_per_row > 15).sum()
        }

        return missing_df, row_missing_distribution

    # =====================================
    # CARDINALITY ANALYSIS
    # =====================================

    def _cardinality_analysis(self):
        unique_counts = self.df.nunique().sort_values(ascending=False)
        high_cardinality_columns = unique_counts[unique_counts > 50]
        return unique_counts, high_cardinality_columns

    # =====================================
    # NUMERIC SUMMARY
    # =====================================

    def _numeric_summary(self):
        numeric_df = self.df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            return pd.DataFrame()
        return numeric_df.describe().T

    # =====================================
    # TARGET ANALYSIS
    # =====================================

    def _target_analysis(self):
        if self.target_column in self.df.columns:
            return self.df[self.target_column].describe()
        return None

    # =====================================
    # BUILD REPORT
    # =====================================

    def build_report(self) -> str:
        general = self._general_info()
        dtype_counts, _ = self._dtype_analysis()
        missing_df, row_missing_dist = self._missing_analysis()
        unique_counts, high_card = self._cardinality_analysis()
        numeric_summary = self._numeric_summary()
        target_analysis = self._target_analysis()

        report = []
        report.append("=" * 60)
        report.append("DATASET ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Generated at: {datetime.now()}")
        report.append("")

        report.append("GENERAL INFORMATION")
        report.append("-" * 40)
        report.append(f"Toplam Ürün Sayısı: {general['num_products']}")
        report.append(f"Toplam Feature Sayısı (Target dahil): {general['num_features_total']}")
        report.append(f"Model Feature Sayısı (exclude hariç): {general['num_features_model']}")
        report.append(f"Toplam Eksik Hücre Sayısı: {general['total_missing_cells']}")
        report.append("")

        report.append("DATA TYPE DISTRIBUTION")
        report.append("-" * 40)
        report.append(dtype_counts.to_string())
        report.append("")

        report.append("COLUMN BAZLI EKSİK VERİ ANALİZİ")
        report.append("-" * 40)
        report.append(missing_df.to_string())
        report.append("")

        report.append("ÜRÜN BAZLI EKSİK FEATURE DAĞILIMI")
        report.append("-" * 40)
        for k, v in row_missing_dist.items():
            report.append(f"{k}: {v}")
        report.append("")

        report.append("CARDINALITY ANALİZİ")
        report.append("-" * 40)
        report.append(unique_counts.to_string())
        report.append("")
        report.append("High Cardinality Columns (>50):")
        report.append(high_card.to_string())
        report.append("")

        if not numeric_summary.empty:
            report.append("NUMERIC FEATURE SUMMARY")
            report.append("-" * 40)
            report.append(numeric_summary.to_string())
            report.append("")

        if target_analysis is not None:
            report.append(f"TARGET ({self.target_column}) ANALYSIS")
            report.append("-" * 40)
            report.append(target_analysis.to_string())
            report.append("")

        return "\n".join(report)

    # =====================================
    # SAVE REPORT
    # =====================================

    def save_report(self, report_text: str):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(report_text)

        print(f"Rapor kaydedildi: {self.output_path}")

    # =====================================
    # FULL PIPELINE
    # =====================================

    def run(self):
        self.load_data()
        report_text = self.build_report()
        self.save_report(report_text)
        print("Dataset analizi tamamlandı.")

if __name__ == "__main__":
    price_analyzer = DatasetAnalyzer(
        input_path="src/app/output/dataset/raw/full_dataset.csv",
        output_path="src/app/output/dataset/price/dataset_analysis.txt",
        target_column="urun_fiyat",
        exclude_column="urun_puan"
    )

    point_analyzer = DatasetAnalyzer(
        input_path="src/app/output/dataset/raw/full_dataset.csv",
        output_path="src/app/output/dataset/point/dataset_analysis.txt",
        target_column="urun_puan",
        exclude_column="urun_fiyat"
    )

    price_analyzer.run()
    point_analyzer.run()