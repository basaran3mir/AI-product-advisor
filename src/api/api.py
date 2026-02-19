import os
import sys
import traceback
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import numpy as np

# path ayarı
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(BASE_DIR)

from src.app.scripts.predict_service import PredictService

# Ürün datası (price dataset final hali)
DATA_PATH = os.path.join(
    BASE_DIR,
    "src/app/output/dataset/processed/step4_numeric_cleaned.csv"
)
print("Loading dataset from:", DATA_PATH)

df = pd.read_csv(DATA_PATH)

# --------------------------------------------------
# IMAGE SERVING ENDPOINT
# --------------------------------------------------
IMAGE_DIR = os.path.join(
    BASE_DIR,
    "src/app/output/image"
)

app = Flask(__name__)

CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Service instance (tek sefer yüklenir)
price_service = PredictService(task="price")
point_service = PredictService(task="point")

def get_closest_products(column, target_value, top_n=10):
    df_copy = df.copy()

    df_copy["urun_fiyat"] = np.expm1(df_copy["urun_fiyat"])
    df_copy["urun_puan"]  = np.expm1(df_copy["urun_puan"])

    df_copy["distance"] = (df_copy[column] - target_value).abs()

    closest = df_copy.sort_values("distance").head(top_n)

    result_df = closest.drop(columns=["distance"])

    # 🔥 JSON-safe hale getir
    result_df = result_df.replace([np.nan, np.inf, -np.inf], None)

    return result_df.to_dict(orient="records")

@app.route("/")
def home():
    return "API is running."

@app.route("/images/<path:filename>")
def serve_image(filename):
    return send_from_directory(IMAGE_DIR, filename)

# --------------------------------------------------
# PREDICT ENDPOINT
# --------------------------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON body provided"}), 400

        input_df = pd.DataFrame([data])

        predicted_price = price_service.predict(input_df)
        predicted_point = point_service.predict(input_df)

        closest_by_price = get_closest_products(
            "urun_fiyat",
            predicted_price,
            top_n=10
        )

        closest_by_point = get_closest_products(
            "urun_puan",
            predicted_point,
            top_n=10
        )

        return jsonify({
            "predicted_price": round(predicted_price, 2),
            "predicted_point": round(predicted_point, 2),
            "closest_by_price": closest_by_price,
            "closest_by_point": closest_by_point
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500


# --------------------------------------------------
# FEATURE LIST ENDPOINT
# --------------------------------------------------
@app.route("/get_features", methods=["GET"])
def get_features():
    try:
        # step4_numeric_cleaned.csv dosyasının başlığını oku
        step4_path = os.path.join(
            os.path.dirname(__file__),
            "..", "app", "output", "dataset", "processed", "step4_numeric_cleaned.csv"
        )
        # step4_numeric_cleaned.csv dosyasını oku
        df = pd.read_csv(step4_path, encoding="utf-8")
        features = list(df.columns)

        # Otomatik kategori eşlemesi
        categories = {
            "Ekran": [],
            "Batarya": [],
            "Kamera": [],
            "Temel Donanım": [],
            "Tasarım": [],
            "Ağ": [],
            "Kablosuz Bağlantılar": [],
            "İşletim Sistemi": [],
            "Özellikler": [],
            "Diğer": []
        }
        prefix_map = {
            "Ekran": "ekran_",
            "Batarya": "batarya_",
            "Kamera": "kamera_",
            "Temel Donanım": "temel_donanim_",
            "Tasarım": "tasarim_",
            "Ağ": "ağ_bağlantilari_",
            "Kablosuz Bağlantılar": "kablosuz_bağlantilar_",
            "İşletim Sistemi": "i̇şleti̇m_si̇stemi̇_",
            "Özellikler": "özelli̇kler_"
        }

        # Otomatik birim eşlemesi (field adlarına göre)
        unit_map = {
            # Ekran
            "ekran_ekran_boyutu": "inç",
            "ekran_ekran_yenileme_hızı": "Hz",
            # Batarya
            "batarya_batarya_kapasitesi_tipik": "mAh",
            "batarya_hızlı_şarj_gücü_maks.": "Watt",
            # Kamera
            "kamera_kamera_çözünürlüğü": "MP",
            "kamera_ön_kamera_çözünürlüğü": "MP",
            "kamera_video_fps_değeri": "fps",
            # Temel Donanım
            "temel_donanim_cpu_çekirdeği": "Çekirdek Sayısı",
            "temel_donanim_cpu_üretim_teknolojisi": "nm",
            "temel_donanim_antutu_puanı_v10": "puan",
            "temel_donanim_bellek_ram": "GB",
            "temel_donanim_dahili_depolama": "GB",
            # Tasarım
            "tasarim_kalınlık": "mm",
            "tasarim_ağırlık": "gr",
            # Kablosuz
            "kablosuz_bağlantilar_bluetooth_versiyonu": "",
            # Diğer
            # ... gerekirse eklenebilir ...
        }

        for field in features:
            if field in ["urun_fiyat", "urun_puan", "urun_id"]:
                continue
            matched = False
            unit = unit_map.get(field, "")
            for cat, prefix in prefix_map.items():
                if field.startswith(prefix):
                    clean_name = field[len(prefix):]
                    unique_values = sorted(df[field].dropna().astype(str).unique().tolist())
                    categories[cat].append({
                        "name": field,
                        "label": clean_name,
                        "values": unique_values,
                        "unit": unit
                    })
                    matched = True
                    break
            if not matched:
                unique_values = sorted(df[field].dropna().astype(str).unique().tolist())
                categories["Diğer"].append({
                    "name": field,
                    "label": field,
                    "values": unique_values,
                    "unit": unit
                })

        # Sadece dolu kategorileri döndür
        categories = {k: v for k, v in categories.items() if v}
        return jsonify({"categories": categories})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
