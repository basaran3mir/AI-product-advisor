import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime


class DatasetAnalyzer:
    """
    Raw ve Final dataset analiz sınıfı
    """

    def __init__(
        self,
        raw_path: str | Path,
        final_path: str | Path,
        output_dir: str | Path,
    ):
        self.raw_path = Path(raw_path)
        self.final_path = Path(final_path)
        self.output_dir = Path(output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)

    # =====================================
    # CORE ANALYSIS
    # =====================================

    def _analyze(self, df: pd.DataFrame, dataset_name: str) -> str:

        num_rows = df.shape[0]
        num_cols = df.shape[1]
        total_missing = df.isnull().sum().sum()

        dtype_counts = df.dtypes.value_counts()

        missing_df = (
            df.isnull()
            .sum()
            .to_frame("missing_count")
        )
        missing_df["missing_percentage"] = (
            missing_df["missing_count"] / num_rows
        ) * 100

        unique_counts = df.nunique().sort_values(ascending=False)

        numeric_summary = df.select_dtypes(include=[np.number]).describe().T

        report = []
        report.append("=" * 70)
        report.append(f"{dataset_name.upper()} DATASET ANALYSIS")
        report.append("=" * 70)
        report.append(f"Generated at: {datetime.now()}")
        report.append("")

        report.append("GENERAL INFO")
        report.append("-" * 40)
        report.append(f"Satır Sayısı: {num_rows}")
        report.append(f"Sütun Sayısı: {num_cols}")
        report.append(f"Toplam Eksik Hücre: {total_missing}")
        report.append("")

        report.append("DATA TYPE DISTRIBUTION")
        report.append("-" * 40)
        report.append(dtype_counts.to_string())
        report.append("")

        report.append("MISSING ANALYSIS")
        report.append("-" * 40)
        report.append(missing_df.sort_values("missing_count", ascending=False).to_string())
        report.append("")

        report.append("CARDINALITY ANALYSIS")
        report.append("-" * 40)
        report.append(unique_counts.to_string())
        report.append("")

        if not numeric_summary.empty:
            report.append("NUMERIC SUMMARY")
            report.append("-" * 40)
            report.append(numeric_summary.to_string())
            report.append("")

        # Target analizleri (varsa)
        for target in ["urun_fiyat", "urun_puan"]:
            if target in df.columns:
                report.append(f"{target.upper()} SUMMARY")
                report.append("-" * 40)
                report.append(df[target].describe().to_string())
                report.append("")

        return "\n".join(report)

    # =====================================
    # SAVE REPORT
    # =====================================

    def _save_report(self, text: str, filename: str):
        path = self.output_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Rapor kaydedildi: {path}")

    # =====================================
    # RUN
    # =====================================

    def run(self):

        # RAW
        raw_df = pd.read_csv(self.raw_path)
        raw_report = self._analyze(raw_df, "Raw")
        self._save_report(raw_report, "raw_dataset_analysis.txt")

        # FINAL
        final_df = pd.read_csv(self.final_path)
        final_report = self._analyze(final_df, "Final")
        self._save_report(final_report, "final_dataset_analysis.txt")

        print("Tüm dataset analizleri tamamlandı.")

if __name__ == "__main__":

    analyzer = DatasetAnalyzer(
        raw_path="src/app/output/dataset/raw/raw_dataset.csv",
        final_path="src/app/output/dataset/final/final_dataset.csv",
        output_dir="src/app/output/dataset/analysis"
    )

    analyzer.run()
