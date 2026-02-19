import json
import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

from .dataset.dataset_processor import ProductDataPreprocessor

BASE_DIR = Path(__file__).resolve().parents[3]
MODEL_DIR = BASE_DIR / "src/app/output/model"
DATA_PATH = os.path.join(
    BASE_DIR,
    "src/app/output/dataset/processed/step4_numeric_cleaned.csv"
)

class PredictService:

    def __init__(self, task: str):
        """
        task: "price" veya "point"
        """

        self.task = task

        if task == "price":
            model_path = MODEL_DIR / "price/xgboost_urun_fiyat_model.pkl"
            features_path = MODEL_DIR / "price/model_features.json"
            self.log_transformed = True

        elif task == "point":
            model_path = MODEL_DIR / "point/xgboost_urun_puan_model.pkl"
            features_path = MODEL_DIR / "point/model_features.json"
            self.log_transformed = False

        else:
            raise ValueError("task must be 'price' or 'point'")

        self.df = pd.read_csv(DATA_PATH)
        self.model = joblib.load(model_path)

        with open(features_path, "r", encoding="utf-8") as f:
            self.model_features = json.load(f)

        self.processor = ProductDataPreprocessor(
            input_path="",
            processed_dir="",
            output_dir="",
            mode="predict"
        )

    # =====================================
    # PREDICT
    # =====================================

    def get_features(self):
        features = list(self.df.columns)
        
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
                    unique_values = sorted(self.df[field].dropna().astype(str).unique().tolist())
                    categories[cat].append({
                        "name": field,
                        "label": clean_name,
                        "values": unique_values,
                        "unit": unit
                    })
                    matched = True
                    break
            if not matched:
                unique_values = sorted(self.df[field].dropna().astype(str).unique().tolist())
                categories["Diğer"].append({
                    "name": field,
                    "label": field,
                    "values": unique_values,
                    "unit": unit
                })

        # Sadece dolu kategorileri döndür
        categories = {k: v for k, v in categories.items() if v}

        return categories

    def predict(self, input_df: pd.DataFrame) -> float:

        X_processed = self.processor.transform_for_prediction(input_df)

        X_processed = X_processed.reindex(
            columns=self.model_features,
            fill_value=0
        )

        raw_pred = self.model.predict(X_processed)[0]

        result = float(np.expm1(raw_pred))

        return result

    def get_closest_products(self, column, target_value, top_n=10):
        df_copy = self.df.copy()

        df_copy["urun_fiyat"] = np.expm1(df_copy["urun_fiyat"])
        df_copy["urun_puan"]  = np.expm1(df_copy["urun_puan"])

        df_copy["distance"] = (df_copy[column] - target_value).abs()

        closest = df_copy.sort_values("distance").head(top_n)

        result_df = closest.drop(columns=["distance"])

        # 🔥 JSON-safe hale getir
        result_df = result_df.replace([np.nan, np.inf, -np.inf], None)

        return result_df.to_dict(orient="records")