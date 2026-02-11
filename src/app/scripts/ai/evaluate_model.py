import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
from datetime import datetime

# =============================
# PATH CONFIG
# =============================
BASE_DIR = Path(__file__).resolve().parents[4]
DATA_PATH = BASE_DIR / "src/app/output/dataset/final/step8_final_model_ready.csv"
MODEL_PATH = BASE_DIR / "src/app/output/model/xgboost_price_model.pkl"
OUTPUT_DIR = BASE_DIR / "src/app/output/model/evaluation"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "urun_fiyat"

# =============================
# LOAD DATA & MODEL
# =============================
df = pd.read_csv(DATA_PATH)
model = joblib.load(MODEL_PATH)

X = df.drop(columns=[TARGET])
y_log = df[TARGET]

# =============================
# PREDICTION
# =============================
y_pred_log = model.predict(X)

# Log dönüşümünü geri al
y_true = np.expm1(y_log)
y_pred = np.expm1(y_pred_log)

# =============================
# METRICS (REAL TL SPACE)
# =============================
rmse = np.sqrt(mean_squared_error(y_true, y_pred))
mae = mean_absolute_error(y_true, y_pred)
r2 = r2_score(y_true, y_pred)
mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

# =============================
# DETAILED ERROR TABLE
# =============================
results = pd.DataFrame({
    "Gerçek_Fiyat": y_true,
    "Tahmin_Fiyat": y_pred,
})

results["Mutlak_Hata"] = np.abs(results["Gerçek_Fiyat"] - results["Tahmin_Fiyat"])
results["Yuzde_Hata"] = (
    results["Mutlak_Hata"] / results["Gerçek_Fiyat"] * 100
)

results.sort_values("Mutlak_Hata", inplace=True)

results.to_csv(OUTPUT_DIR / "all_predictions.csv", index=False)

# =============================
# BEST & WORST 10
# =============================
best_10 = results.head(10)
worst_10 = results.tail(10)

best_10.to_csv(OUTPUT_DIR / "best_10_predictions.csv", index=False)
worst_10.to_csv(OUTPUT_DIR / "worst_10_predictions.csv", index=False)

# =============================
# SEGMENT ANALYSIS
# =============================
def price_segment(price):
    if price < 10000:
        return "0-10K"
    elif price < 25000:
        return "10K-25K"
    elif price < 50000:
        return "25K-50K"
    elif price < 100000:
        return "50K-100K"
    else:
        return "100K+"

results["Segment"] = results["Gerçek_Fiyat"].apply(price_segment)

segment_analysis = results.groupby("Segment").agg({
    "Mutlak_Hata": "mean",
    "Yuzde_Hata": "mean",
    "Gerçek_Fiyat": "count"
}).rename(columns={"Gerçek_Fiyat": "Adet"})

segment_analysis.to_csv(OUTPUT_DIR / "segment_analysis.csv")

# =============================
# PLOTS
# =============================

# Gerçek vs Tahmin
plt.figure()
plt.scatter(y_true, y_pred)
plt.xlabel("Gerçek Fiyat")
plt.ylabel("Tahmin Fiyat")
plt.title("Gerçek vs Tahmin")
plt.savefig(OUTPUT_DIR / "real_vs_pred.png")
plt.close()

# Residual Plot
residuals = y_true - y_pred
plt.figure()
plt.scatter(y_pred, residuals)
plt.axhline(0)
plt.xlabel("Tahmin Fiyat")
plt.ylabel("Residual (Gerçek - Tahmin)")
plt.title("Residual Plot")
plt.savefig(OUTPUT_DIR / "residual_plot.png")
plt.close()

# =============================
# SAVE METRICS REPORT
# =============================
report_path = OUTPUT_DIR / "evaluation_report.txt"

with open(report_path, "w", encoding="utf-8") as f:
    f.write("============================================================\n")
    f.write("MODEL EVALUATION REPORT (REAL PRICE SPACE)\n")
    f.write("============================================================\n\n")
    f.write(f"Oluşturulma Tarihi: {datetime.now()}\n\n")

    f.write("GENEL METRİKLER\n")
    f.write("----------------------------\n")
    f.write(f"RMSE (TL): {rmse:.2f}\n")
    f.write(f"MAE (TL): {mae:.2f}\n")
    f.write(f"R2: {r2:.4f}\n")
    f.write(f"MAPE (%): {mape:.2f}\n\n")

    f.write("Segment Bazlı Ortalama Hata\n")
    f.write("----------------------------\n")
    f.write(segment_analysis.to_string())
    f.write("\n\n")

print("Evaluation tamamlandı.")
print(f"Rapor kaydedildi: {report_path}")
