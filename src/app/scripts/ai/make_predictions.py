import pandas as pd
import numpy as np
import os
import joblib

from sklearn.model_selection import train_test_split


# =========================
# DOSYA YOLLARI
# =========================
current_dir = os.path.dirname(os.path.abspath(__file__))

dataset_path = os.path.join(
    current_dir, '..', '..', 'outputs', 'datasets', 'dataset_encoded.csv'
)

model_path = os.path.join(
    current_dir, '..', '..', 'outputs', 'models', 'price_prediction_model.pkl'
)

output_path = os.path.join(
    current_dir, '..', '..', 'outputs', 'models', 'sample_predictions.txt'
)


# =========================
# VERİ & MODEL YÜKLE
# =========================
df = pd.read_csv(dataset_path)
model = joblib.load(model_path)

target = "urun_fiyat"
exclude_columns = ["urun_fiyat", "urun_puan"]

X = df.drop(columns=exclude_columns)
y = df[target]


# =========================
# TRAIN / VAL / TEST (EĞİTİMLE AYNI)
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
# TAHMİNLER
# =========================
y_pred = model.predict(X_test)


# =========================
# KARŞILAŞTIRMA TABLOSU
# =========================
comparison_df = pd.DataFrame({
    "Gerçek Fiyat": y_test.values,
    "Tahmin Fiyat": y_pred
})

comparison_df["Hata (TL)"] = comparison_df["Gerçek Fiyat"] - comparison_df["Tahmin Fiyat"]
comparison_df["Hata (%)"] = (
    comparison_df["Hata (TL)"] / comparison_df["Gerçek Fiyat"] * 100
).round(2)

comparison_df = comparison_df.reset_index(drop=True)


# =========================
# TXT RAPOR
# =========================
with open(output_path, "w", encoding="utf-8") as f:
    f.write("=" * 80 + "\n")
    f.write("XGBOOST – ÜRÜN FİYAT TAHMİN ANALİZİ\n")
    f.write("=" * 80 + "\n\n")

    f.write("GENEL ÖZET:\n")
    f.write("-" * 80 + "\n")
    f.write(f"Test edilen ürün sayısı : {len(comparison_df)}\n")
    f.write(f"Ortalama hata (TL)      : {comparison_df['Hata (TL)'].abs().mean():.2f}\n")
    f.write(f"Ortalama hata (%)       : {comparison_df['Hata (%)'].abs().mean():.2f}\n")
    f.write(f"Min hata (TL)           : {comparison_df['Hata (TL)'].abs().min():.2f}\n")
    f.write(f"Max hata (TL)           : {comparison_df['Hata (TL)'].abs().max():.2f}\n\n")

    f.write("BİLGİ:\n")
    f.write("-" * 80 + "\n")
    f.write("Pozitif hata → Model fiyatı düşük tahmin etti\n")
    f.write("Negatif hata → Model fiyatı yüksek tahmin etti\n\n")

    f.write("İLK 10 ÖRNEK:\n")
    f.write("-" * 80 + "\n")
    f.write(comparison_df.head(10).to_string(index=True))

    f.write("\n\nEN İYİ 5 TAHMİN (En düşük % hata):\n")
    f.write("-" * 80 + "\n")
    f.write(comparison_df.nsmallest(5, "Hata (%)").to_string(index=True))

    f.write("\n\nEN KÖTÜ 5 TAHMİN (En yüksek % hata):\n")
    f.write("-" * 80 + "\n")
    f.write(comparison_df.nlargest(5, "Hata (%)").to_string(index=True))

    f.write("\n\nFİYAT ARALIKLARINA GÖRE PERFORMANS:\n")
    f.write("-" * 80 + "\n")

    price_ranges = [
        (0, 20000, "0 – 20.000 TL"),
        (20000, 40000, "20.000 – 40.000 TL"),
        (40000, 60000, "40.000 – 60.000 TL"),
        (60000, 100000, "60.000 – 100.000 TL"),
        (100000, float("inf"), "100.000+ TL")
    ]

    for min_p, max_p, label in price_ranges:
        mask = (comparison_df["Gerçek Fiyat"] >= min_p) & (comparison_df["Gerçek Fiyat"] < max_p)
        if mask.sum() > 0:
            subset = comparison_df[mask]
            f.write(f"\n{label}\n")
            f.write(f"  Ürün sayısı : {len(subset)}\n")
            f.write(f"  Ort. hata   : {subset['Hata (TL)'].abs().mean():.2f} TL\n")
            f.write(f"  Ort. hata % : {subset['Hata (%)'].abs().mean():.2f}%\n")

    f.write("\n" + "=" * 80 + "\n")


# =========================
# KONSOL ÖZET
# =========================
print("✓ Tahmin analizi tamamlandı")
print(f"✓ Rapor kaydedildi: {output_path}\n")

print("ÖZET:")
print(f"- Test örnek sayısı : {len(comparison_df)}")
print(f"- Ortalama hata     : {comparison_df['Hata (TL)'].abs().mean():.2f} TL")
print(f"- Ortalama hata %   : {comparison_df['Hata (%)'].abs().mean():.2f}%")
