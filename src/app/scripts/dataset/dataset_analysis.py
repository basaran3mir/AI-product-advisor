# ============================================================
# DATASET ANALYSIS SCRIPT
# Target: urun_fiyat
# Excluded (ilk aşama): urun_puan
# Output: dataset_analysis.txt
# ============================================================

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# =============================
# CONFIG
# =============================
INPUT_PATH = "src/app/outputs/datasets/filtered_dataset.csv"   # Dosya yolunu değiştir
OUTPUT_PATH = "src/app/outputs/datasets/dataset_analysis.txt"

TARGET_COLUMN = "urun_fiyat"
EXCLUDE_COLUMN = "urun_puan"

# =============================
# LOAD DATA
# =============================
df = pd.read_csv(INPUT_PATH)

# =============================
# BASIC INFO
# =============================
num_products = df.shape[0]
num_features_total = df.shape[1]

feature_columns = df.columns.tolist()

if TARGET_COLUMN in feature_columns:
    feature_columns.remove(TARGET_COLUMN)

if EXCLUDE_COLUMN in feature_columns:
    feature_columns.remove(EXCLUDE_COLUMN)

num_features_model = len(feature_columns)

# =============================
# DATA TYPE ANALYSIS
# =============================
dtype_counts = df.dtypes.value_counts()

dtype_table = pd.DataFrame({
    "column": df.columns,
    "dtype": df.dtypes.astype(str)
})

# =============================
# MISSING VALUE ANALYSIS
# =============================
missing_count = df.isnull().sum()
missing_percentage = (missing_count / num_products) * 100

missing_df = pd.DataFrame({
    "missing_count": missing_count,
    "missing_percentage": missing_percentage
}).sort_values(by="missing_count", ascending=False)

total_missing_cells = missing_count.sum()

# Row bazlı eksik feature sayısı
missing_per_row = df.isnull().sum(axis=1)

row_missing_distribution = {
    "eksiksiz_urun": (missing_per_row == 0).sum(),
    "1_3_eksik": ((missing_per_row >= 1) & (missing_per_row <= 3)).sum(),
    "4_7_eksik": ((missing_per_row >= 4) & (missing_per_row <= 7)).sum(),
    "8_15_eksik": ((missing_per_row >= 8) & (missing_per_row <= 15)).sum(),
    "15_plus_eksik": (missing_per_row > 15).sum()
}

# =============================
# UNIQUE VALUE ANALYSIS (Cardinality)
# =============================
unique_counts = df.nunique().sort_values(ascending=False)

high_cardinality_columns = unique_counts[unique_counts > 50]

# =============================
# NUMERIC SUMMARY
# =============================
numeric_df = df.select_dtypes(include=[np.number])
numeric_summary = numeric_df.describe().T if not numeric_df.empty else pd.DataFrame()

# =============================
# TARGET ANALYSIS
# =============================
target_analysis = None
if TARGET_COLUMN in df.columns:
    target_analysis = df[TARGET_COLUMN].describe()

# =============================
# BUILD REPORT
# =============================
report = []
report.append("============================================================")
report.append("DATASET ANALYSIS REPORT")
report.append("============================================================")
report.append(f"Generated at: {datetime.now()}")
report.append("")

report.append("------------------------------------------------------------")
report.append("GENERAL INFORMATION")
report.append("------------------------------------------------------------")
report.append(f"Toplam Ürün Sayısı: {num_products}")
report.append(f"Toplam Feature Sayısı (Target dahil): {num_features_total}")
report.append(f"Modelde Kullanılacak Feature Sayısı (urun_puan hariç): {num_features_model}")
report.append(f"Toplam Eksik Hücre Sayısı: {total_missing_cells}")
report.append("")

report.append("------------------------------------------------------------")
report.append("DATA TYPE DISTRIBUTION")
report.append("------------------------------------------------------------")
report.append(dtype_counts.to_string())
report.append("")

report.append("------------------------------------------------------------")
report.append("COLUMN BAZLI EKSİK VERİ ANALİZİ")
report.append("------------------------------------------------------------")
report.append(missing_df.to_string())
report.append("")

report.append("------------------------------------------------------------")
report.append("ÜRÜN BAZLI EKSİK FEATURE DAĞILIMI")
report.append("------------------------------------------------------------")
for k, v in row_missing_distribution.items():
    report.append(f"{k}: {v}")
report.append("")

report.append("------------------------------------------------------------")
report.append("UNIQUE VALUE (CARDINALITY) ANALİZİ")
report.append("------------------------------------------------------------")
report.append(unique_counts.to_string())
report.append("")
report.append("High Cardinality Columns (>50 unique value):")
report.append(high_cardinality_columns.to_string())
report.append("")

if not numeric_summary.empty:
    report.append("------------------------------------------------------------")
    report.append("NUMERIC FEATURE SUMMARY")
    report.append("------------------------------------------------------------")
    report.append(numeric_summary.to_string())
    report.append("")

if target_analysis is not None:
    report.append("------------------------------------------------------------")
    report.append("TARGET (urun_fiyat) ANALYSIS")
    report.append("------------------------------------------------------------")
    report.append(target_analysis.to_string())
    report.append("")

report_text = "\n".join(report)

# =============================
# SAVE REPORT
# =============================
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(report_text)

print("Analiz tamamlandı.")
print(f"Rapor kaydedildi: {OUTPUT_PATH}")
