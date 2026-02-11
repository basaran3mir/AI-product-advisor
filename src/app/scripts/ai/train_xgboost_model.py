import os
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

import xgboost as xgb


# =====================================
# CONFIG
# =====================================

BASE_DIR = Path(__file__).resolve().parents[4]
DATA_PATH = BASE_DIR / "src/app/output/dataset/final/step8_final_model_ready.csv"   # son step çıktın
OUTPUT_DIR = BASE_DIR / "src/app/output/model"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "urun_fiyat"
EXCLUDE_FROM_MODEL = ["urun_puan"]  # bilinçli olarak dışarıda


# =====================================
# LOAD DATA
# =====================================

df = pd.read_csv(DATA_PATH)

if TARGET not in df.columns:
    raise ValueError(f"{TARGET} bulunamadı.")

# Target ve feature ayrımı
X = df.drop(columns=[TARGET] + EXCLUDE_FROM_MODEL, errors="ignore")
y = df[TARGET]


# =====================================
# TRAIN / VALIDATION / TEST SPLIT
# =====================================

X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.30, random_state=42
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.50, random_state=42
)

print(f"Train size: {len(X_train)}")
print(f"Validation size: {len(X_val)}")
print(f"Test size: {len(X_test)}")


# =====================================
# MODEL CONFIGURATION
# =====================================

model = xgb.XGBRegressor(
    n_estimators=2000,
    learning_rate=0.03,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    tree_method="hist",
    early_stopping_rounds=50,
    eval_metric="rmse"
)

# =====================================
# TRAINING
# =====================================

model.fit(
    X_train,
    y_train,
    eval_set=[(X_val, y_val)],
    verbose=False
)

# =====================================
# EVALUATION
# =====================================

def evaluate(model, X, y, dataset_name):
    preds = model.predict(X)
    rmse = np.sqrt(mean_squared_error(y, preds))
    mae = mean_absolute_error(y, preds)
    r2 = r2_score(y, preds)

    return {
        "dataset": dataset_name,
        "rmse": rmse,
        "mae": mae,
        "r2": r2
    }


train_metrics = evaluate(model, X_train, y_train, "train")
val_metrics = evaluate(model, X_val, y_val, "validation")
test_metrics = evaluate(model, X_test, y_test, "test")


# =====================================
# FEATURE IMPORTANCE
# =====================================

importance_df = pd.DataFrame({
    "feature": X.columns,
    "importance": model.feature_importances_
}).sort_values(by="importance", ascending=False)

importance_df.to_csv(OUTPUT_DIR / "feature_importance.csv", index=False)


# =====================================
# SAVE MODEL
# =====================================

model.save_model(OUTPUT_DIR / "xgboost_price_model.json")

# ayrıca joblib ile de kaydediyoruz
joblib.dump(model, OUTPUT_DIR / "xgboost_price_model.pkl")


# =====================================
# SAVE PERFORMANCE REPORT
# =====================================

report_path = OUTPUT_DIR / "model_performance_report.txt"

with open(report_path, "w", encoding="utf-8") as f:

    f.write("=" * 60 + "\n")
    f.write("XGBOOST FİYAT TAHMİN MODELİ – PERFORMANS RAPORU\n")
    f.write("=" * 60 + "\n\n")

    f.write(f"Oluşturulma Tarihi: {datetime.now()}\n\n")

    f.write("VERİ SETİ BOYUTLARI\n")
    f.write("-" * 30 + "\n")
    f.write(f"Toplam kayıt: {len(df)}\n")
    f.write(f"Eğitim: {len(X_train)}\n")
    f.write(f"Validation: {len(X_val)}\n")
    f.write(f"Test: {len(X_test)}\n\n")

    for metrics in [train_metrics, val_metrics, test_metrics]:
        f.write(f"{metrics['dataset'].upper()} METRİKLERİ\n")
        f.write("-" * 30 + "\n")
        f.write(f"RMSE: {metrics['rmse']:.6f}\n")
        f.write(f"MAE:  {metrics['mae']:.6f}\n")
        f.write(f"R2:   {metrics['r2']:.6f}\n\n")

    f.write("EN ÖNEMLİ 20 FEATURE\n")
    f.write("-" * 30 + "\n")

    for _, row in importance_df.head(20).iterrows():
        f.write(f"{row['feature']}: {row['importance']:.6f}\n")


print("Model eğitimi tamamlandı.")
print(f"Model kaydedildi: {OUTPUT_DIR}")
