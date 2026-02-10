import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from lightgbm import LGBMRegressor
import joblib
import os

# Veri setini yükle
current_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(current_dir, '..', '..', 'outputs', 'datasets', 'dataset_encoded.csv')
df = pd.read_csv(dataset_path)

# Hedef değişken: urun_fiyat
target = 'urun_fiyat'
y = df[target]

# Hariç tutulacak sütunlar
exclude_columns = ['urun_fiyat', 'urun_puan']

# Özellikler (features)
X = df.drop(columns=exclude_columns)

# Eğitim ve test veri setlerine ayır
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Özellikleri normalize et
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# LightGBM modelini eğit
model = LGBMRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=7,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    verbose=-1
)

model.fit(X_train_scaled, y_train)

# Tahminler yap
y_train_pred = model.predict(X_train_scaled)
y_test_pred = model.predict(X_test_scaled)

# Performans metriklerini hesapla
train_mse = mean_squared_error(y_train, y_train_pred)
test_mse = mean_squared_error(y_test, y_test_pred)
train_rmse = np.sqrt(train_mse)
test_rmse = np.sqrt(test_mse)
train_mae = mean_absolute_error(y_train, y_train_pred)
test_mae = mean_absolute_error(y_test, y_test_pred)
train_r2 = r2_score(y_train, y_train_pred)
test_r2 = r2_score(y_test, y_test_pred)

# Performans metriklerini txt dosyasına kaydet
metrics_output_path = os.path.join(
    current_dir, '..', '..', 'outputs', 'models', 'model_performance_metrics.txt'
)

with open(metrics_output_path, 'w', encoding='utf-8') as f:
    f.write("=" * 60 + "\n")
    f.write("YAPAY ZEKA MODELI PERFORMANS METRİKLERİ\n")
    f.write("=" * 60 + "\n\n")
    
    f.write("VERİ SET BİLGİLERİ:\n")
    f.write("-" * 60 + "\n")
    f.write(f"Toplam veri sayısı: {len(df)}\n")
    f.write(f"Eğitim veri sayısı: {len(X_train)}\n")
    f.write(f"Test veri sayısı: {len(X_test)}\n")
    f.write(f"Özellik sayısı: {X.shape[1]}\n")
    f.write(f"Hedef değişken: {target}\n")
    f.write(f"Hariç tutulan özellikleri: {', '.join(exclude_columns)}\n\n")
    
    f.write("MODEL BİLGİLERİ:\n")
    f.write("-" * 60 + "\n")
    f.write(f"Model tipi: LightGBM Regressor\n")
    f.write(f"Ağaç sayısı: 200\n")
    f.write(f"Öğrenme oranı: 0.05\n")
    f.write(f"Maksimum derinlik: 7\n\n")
    
    f.write("EĞİTİM VERİ SETİ SONUÇLARI:\n")
    f.write("-" * 60 + "\n")
    f.write(f"Mean Squared Error (MSE): {train_mse:.2f}\n")
    f.write(f"Root Mean Squared Error (RMSE): {train_rmse:.2f}\n")
    f.write(f"Mean Absolute Error (MAE): {train_mae:.2f}\n")
    f.write(f"R² Skoru: {train_r2:.4f}\n\n")
    
    f.write("TEST VERİ SETİ SONUÇLARI:\n")
    f.write("-" * 60 + "\n")
    f.write(f"Mean Squared Error (MSE): {test_mse:.2f}\n")
    f.write(f"Root Mean Squared Error (RMSE): {test_rmse:.2f}\n")
    f.write(f"Mean Absolute Error (MAE): {test_mae:.2f}\n")
    f.write(f"R² Skoru: {test_r2:.4f}\n\n")
    
    f.write("ÖZET:\n")
    f.write("-" * 60 + "\n")
    f.write(f"Ortalama Tahmin Hatası (Test): ±{test_mae:.2f} TL\n")
    f.write(f"Model Açıklama Oranı (Test): {test_r2*100:.2f}%\n")
    f.write("=" * 60 + "\n")

# Modeli kaydet
model_output_path = os.path.join(
    current_dir, '..', '..', 'outputs', 'models', 'price_prediction_model.pkl'
)
joblib.dump(model, model_output_path)

# Scaler'ı kaydet
scaler_output_path = os.path.join(
    current_dir, '..', '..', 'outputs', 'models', 'feature_scaler.pkl'
)
joblib.dump(scaler, scaler_output_path)

print(f"✓ Model başarıyla eğitildi!")
print(f"✓ Model kaydedildi: {model_output_path}")
print(f"✓ Scaler kaydedildi: {scaler_output_path}")
print(f"✓ Performans metrikleri kaydedildi: {metrics_output_path}")
print(f"\nTest Sonuçları:")
print(f"  RMSE: {test_rmse:.2f}")
print(f"  MAE: {test_mae:.2f}")
print(f"  R² Skoru: {test_r2:.4f}")
