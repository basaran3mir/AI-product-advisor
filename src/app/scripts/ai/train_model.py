import pandas as pd
import numpy as np
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from xgboost import XGBRegressor


# =========================
# DOSYA YOLLARI
# =========================
current_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(
    current_dir, '..', '..', 'outputs', 'datasets', 'dataset_encoded.csv'
)

model_dir = os.path.join(current_dir, '..', '..', 'outputs', 'models')
os.makedirs(model_dir, exist_ok=True)


# =========================
# VERİYİ YÜKLE
# =========================
df = pd.read_csv(dataset_path)

target = "urun_fiyat"
exclude_columns = ["urun_fiyat", "urun_puan"]

X = df.drop(columns=exclude_columns)
y = df[target]


# =========================
# TRAIN / VALIDATION / TEST
# =========================
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y,
    test_size=0.30,
    random_state=42
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp,
    test_size=0.50,
    random_state=42
)


# =========================
# XGBOOST MODELİ
# =========================
model = XGBRegressor(
    n_estimators=1200,
    learning_rate=0.03,
    max_depth=7,
    min_child_weight=3,
    subsample=0.8,
    colsample_bytree=0.8,

    reg_alpha=0.1,
    reg_lambda=1.2,

    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1,

    early_stopping_rounds=50,
    eval_metric="rmse"
)


# =========================
# MODELİ EĞİT
# =========================
model.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    verbose=False
)


# =========================
# TAHMİNLER
# =========================
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)


# =========================
# METRİKLER
# =========================
train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))

train_mae = mean_absolute_error(y_train, y_train_pred)
test_mae = mean_absolute_error(y_test, y_test_pred)

train_r2 = r2_score(y_train, y_train_pred)
test_r2 = r2_score(y_test, y_test_pred)


# =========================
# METRİKLERİ KAYDET
# =========================
metrics_path = os.path.join(model_dir, "model_performance_metrics.txt")

with open(metrics_path, "w", encoding="utf-8") as f:
    f.write("=" * 60 + "\n")
    f.write("XGBOOST FİYAT TAHMİN MODELİ – PERFORMANS RAPORU\n")
    f.write("=" * 60 + "\n\n")

    f.write("VERİ SETİ:\n")
    f.write(f"- Toplam kayıt: {len(df)}\n")
    f.write(f"- Eğitim: {len(X_train)}\n")
    f.write(f"- Validation: {len(X_val)}\n")
    f.write(f"- Test: {len(X_test)}\n")
    f.write(f"- Özellik sayısı: {X.shape[1]}\n\n")

    f.write("MODEL PARAMETRELERİ:\n")
    f.write(f"- Ağaç sayısı (max): 1200\n")
    f.write(f"- Öğrenme oranı: 0.03\n")
    f.write(f"- Maks derinlik: 7\n")
    f.write(f"- Early stopping: 50\n\n")

    f.write("EĞİTİM SONUÇLARI:\n")
    f.write(f"- RMSE: {train_rmse:.2f}\n")
    f.write(f"- MAE: {train_mae:.2f}\n")
    f.write(f"- R²: {train_r2:.4f}\n\n")

    f.write("TEST SONUÇLARI:\n")
    f.write(f"- RMSE: {test_rmse:.2f}\n")
    f.write(f"- MAE: {test_mae:.2f}\n")
    f.write(f"- R²: {test_r2:.4f}\n")

    f.write("=" * 60 + "\n")


# =========================
# MODELİ KAYDET
# =========================
model_path = os.path.join(model_dir, "price_prediction_model.pkl")
joblib.dump(model, model_path)


# =========================
# LOG
# =========================
print("✓ Model başarıyla eğitildi")
print(f"✓ Model kaydedildi: {model_path}")
print(f"✓ Metrikler kaydedildi: {metrics_path}")
print("\nTest Performansı:")
print(f"  RMSE: {test_rmse:.2f}")
print(f"  MAE : {test_mae:.2f}")
print(f"  R²  : {test_r2:.4f}")
