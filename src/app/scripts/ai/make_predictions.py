import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Dosya yollarını ayarla
current_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(current_dir, '..', '..', 'outputs', 'datasets', 'dataset_encoded.csv')
model_path = os.path.join(current_dir, '..', '..', 'outputs', 'models', 'price_prediction_model.pkl')
scaler_path = os.path.join(current_dir, '..', '..', 'outputs', 'models', 'feature_scaler.pkl')
predictions_output_path = os.path.join(current_dir, '..', '..', 'outputs', 'models', 'sample_predictions.txt')

# Veri setini yükle
df = pd.read_csv(dataset_path)

# Modeli ve scaler'ı yükle
model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

# Hedef değişken ve hariç tutulacak sütunlar
target = 'urun_fiyat'
exclude_columns = ['urun_fiyat', 'urun_puan']

# Özellikler
X = df.drop(columns=exclude_columns)
y = df[target]

# Eğitim ve test veri setlerine ayır (model eğitimi ile aynı random_state)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Test veri setini normalize et
X_test_scaled = scaler.transform(X_test)

# Tahminler yap
y_test_pred = model.predict(X_test_scaled)

# Önerileri karşılaştır
comparison_df = pd.DataFrame({
    'Gerçek Fiyat': y_test.values,
    'Tahmin Fiyat': y_test_pred,
    'Hata (TL)': y_test.values - y_test_pred,
    'Hata (%)': ((y_test.values - y_test_pred) / y_test.values * 100).round(2)
})

# Sonuçları sırala
comparison_df = comparison_df.reset_index(drop=True)

# Tahmin sonuçlarını txt dosyasına kaydet
with open(predictions_output_path, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("ÜRÜN FİYAT TAHMİN SONUÇLARI\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("ÖZETİ:\n")
    f.write("-" * 80 + "\n")
    f.write(f"Test edilen ürün sayısı: {len(comparison_df)}\n")
    f.write(f"Ortalama tahmin hatası: {comparison_df['Hata (TL)'].abs().mean():.2f} TL\n")
    f.write(f"Ortalama yüzde hatası: {comparison_df['Hata (%)'].abs().mean():.2f}%\n")
    f.write(f"En düşük tahmin hatası: {comparison_df['Hata (TL)'].abs().min():.2f} TL\n")
    f.write(f"En yüksek tahmin hatası: {comparison_df['Hata (TL)'].abs().max():.2f} TL\n\n")
    
    f.write("BİLGİ:\n")
    f.write("-" * 80 + "\n")
    f.write("Pozitif hata = Model tahmin ettiği fiyat, gerçek fiyattan düşük\n")
    f.write("Negatif hata = Model tahmin ettiği fiyat, gerçek fiyattan yüksek\n\n")
    
    f.write("İLK 10 ÖRNEK TAHMİN:\n")
    f.write("-" * 80 + "\n")
    f.write(comparison_df.head(10).to_string(index=True))
    
    f.write("\n\nSON 10 ÖRNEK TAHMİN:\n")
    f.write("-" * 80 + "\n")
    f.write(comparison_df.tail(10).to_string(index=True))
    
    f.write("\n\nEN İYİ 5 TAHMİN (En düşük hata):\n")
    f.write("-" * 80 + "\n")
    best_predictions = comparison_df.nsmallest(5, 'Hata (%)')
    f.write(best_predictions.to_string(index=True))
    
    f.write("\n\nEN KÖTÜ 5 TAHMİN (En yüksek hata):\n")
    f.write("-" * 80 + "\n")
    worst_predictions = comparison_df.nlargest(5, 'Hata (%)')
    f.write(worst_predictions.to_string(index=True))
    
    f.write("\n\nFİYAT ARALIKLARINA GÖRE TAHMİN PERFORMANSI:\n")
    f.write("-" * 80 + "\n")
    
    # Fiyat aralıklarına göre analiz
    price_ranges = [
        (0, 20000, "0 - 20.000 TL"),
        (20000, 40000, "20.000 - 40.000 TL"),
        (40000, 60000, "40.000 - 60.000 TL"),
        (60000, 100000, "60.000 - 100.000 TL")
    ]
    
    for min_price, max_price, label in price_ranges:
        mask = (comparison_df['Gerçek Fiyat'] >= min_price) & (comparison_df['Gerçek Fiyat'] < max_price)
        if mask.sum() > 0:
            range_data = comparison_df[mask]
            f.write(f"\n{label}:\n")
            f.write(f"  Ürün sayısı: {len(range_data)}\n")
            f.write(f"  Ort. Hata: {range_data['Hata (TL)'].abs().mean():.2f} TL\n")
            f.write(f"  Ort. Hata %: {range_data['Hata (%)'].abs().mean():.2f}%\n")
    
    f.write("\n" + "=" * 80 + "\n")

# Konsola yazdır
print("✓ Tahminler tamamlandı!")
print(f"✓ Tahmin sonuçları kaydedildi: {predictions_output_path}\n")

print("=" * 80)
print("ÜRÜN FİYAT TAHMİN SONUÇLARI ÖZETİ")
print("=" * 80)
print(f"Test edilen ürün sayısı: {len(comparison_df)}")
print(f"Ortalama tahmin hatası: {comparison_df['Hata (TL)'].abs().mean():.2f} TL")
print(f"Ortalama yüzde hatası: {comparison_df['Hata (%)'].abs().mean():.2f}%")
print(f"En düşük tahmin hatası: {comparison_df['Hata (TL)'].abs().min():.2f} TL")
print(f"En yüksek tahmin hatası: {comparison_df['Hata (TL)'].abs().max():.2f} TL")

print("\nİLK 10 ÖRNEK:\n")
print(comparison_df.head(10).to_string())

print("\n\nEN İYİ 5 TAHMİN:\n")
print(comparison_df.nsmallest(5, 'Hata (%)').to_string())

print("\n\nEN KÖTÜ 5 TAHMİN:\n")
print(comparison_df.nlargest(5, 'Hata (%)').to_string())
