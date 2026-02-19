# ============================================================
# FULL DATA PREPROCESSING PIPELINE (CLASS VERSION)
# ============================================================

import pandas as pd
import numpy as np
import re
from pathlib import Path

class ProductDataPreprocessor:

    def __init__(self,
                 input_path: str,
                 processed_dir: str,
                 output_dir: str,
                 mode: str = "train"):

        self.input_path = input_path
        self.processed_dir = Path(processed_dir)
        self.output_dir = Path(output_dir)
        self.mode = mode

        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.df = None

    # ========================================================
    # HELPER FUNCTIONS
    # ========================================================

    @staticmethod
    def extract_numeric(value):
        if pd.isna(value):
            return np.nan

        value = str(value).strip()

        if value.count(".") > 1:
            value = value.replace(".", "")

        match = re.search(r"\d+(\.\d+)?", value)

        if match:
            return float(match.group())

        return np.nan

    def clean_numeric_column(self, column):
        self.df[column] = self.df[column].apply(self.extract_numeric)

    def save_process_step(self, filename):
        if self.mode == "train":
            self.df.to_csv(self.processed_dir / filename, index=False)

    def save_final_step(self, filename):
        if self.mode == "train":
            self.df.to_csv(self.output_dir / filename, index=False)

    # ========================================================
    # STEP 0 — LOAD
    # ========================================================

    def step0_load(self):
        self.df = pd.read_csv(self.input_path)
        self.save_process_step("step0_raw_dataset.csv")
        
    # ========================================================
    # STEP 1 — KEEP SELECTED COLUMNS
    # ========================================================

    def step1_keep_columns(self):

        include_columns = [
            'urun_id',
            'urun_fiyat',
            'urun_puan',
            'ekran_ekran_boyutu',
            'ekran_ekran_teknolojisi',
            'ekran_ekran_çözünürlüğü_standardı',
            'ekran_ekran_yenileme_hızı',
            'batarya_batarya_kapasitesi_tipik',
            'batarya_hızlı_şarj',
            'batarya_hızlı_şarj_gücü_maks.',
            'batarya_kablosuz_şarj',
            'kamera_kamera_çözünürlüğü',
            'kamera_optik_görüntü_sabitleyici_ois',
            'kamera_video_kayıt_çözünürlüğü',
            'kamera_video_fps_değeri',
            'kamera_ön_kamera_çözünürlüğü',
            'temel_donanim_cpu_çekirdeği',
            'temel_donanim_cpu_üretim_teknolojisi',
            'temel_donanim_antutu_puanı_v10',
            'temel_donanim_bellek_ram',
            'temel_donanim_dahili_depolama',
            'tasarim_kalınlık',
            'tasarim_ağırlık',
            'tasarim_gövde_malzemesi_kapak',
            'ağ_bağlantilari_5g',
            'ağ_bağlantilari_4.5g_desteği',
            'ağ_bağlantilari_4g',
            'ağ_bağlantilari_2g',
            'ağ_bağlantilari_3g',
            'kablosuz_bağlantilar_bluetooth_versiyonu',
            'kablosuz_bağlantilar_nfc',
            'i̇şleti̇m_si̇stemi̇_i̇şletim_sistemi',
            'özelli̇kler_suya_dayanıklılık'
        ]

        existing_include = [col for col in include_columns if col in self.df.columns]
        self.df = self.df[existing_include].copy()

        self.save_process_step("step1_keep_selected_columns.csv")

    # ========================================================
    # STEP 2 — DROP NULL TARGET
    # ========================================================

    def step2_drop_null_target(self):
        self.df = self.df[
            self.df["urun_id"].notna() &
            self.df["urun_fiyat"].notna() &
            self.df["urun_puan"].notna()
        ]
        self.save_process_step("step2_drop_null_target.csv")

    # ========================================================
    # STEP 3 — LOG TRANSFORM TARGET
    # ========================================================

    def step3_log_transform(self):
        self.df["urun_fiyat"] = np.log1p(self.df["urun_fiyat"])
        self.df["urun_puan"] = np.log1p(self.df["urun_puan"])
        self.save_process_step("step3_log_targets.csv")

    # ========================================================
    # STEP 4 — NUMERIC CLEANING
    # ========================================================

    def step4_numeric_cleaning(self):

        numeric_columns = [
            "ekran_ekran_boyutu",
            "batarya_batarya_kapasitesi_tipik",
            "batarya_hızlı_şarj_gücü_maks.",
            "kamera_kamera_çözünürlüğü",
            "kamera_ön_kamera_çözünürlüğü",
            "temel_donanim_cpu_çekirdeği",
            "temel_donanim_cpu_üretim_teknolojisi",
            "temel_donanim_antutu_puanı_v10",
            "temel_donanim_bellek_ram",
            "temel_donanim_dahili_depolama",
            "tasarim_kalınlık",
            "tasarim_ağırlık",
            "ekran_ekran_yenileme_hızı",
            "kamera_video_fps_değeri"
        ]

        for col in numeric_columns:
            if col in self.df.columns:
                self.clean_numeric_column(col)

        self.save_process_step("step4_numeric_cleaned.csv")

    # ========================================================
    # STEP 5 — BINARY MAPPING
    # ========================================================

    def step5_binary_mapping(self):

        self.binary_columns = [
            "batarya_hızlı_şarj",
            "batarya_kablosuz_şarj",
            "kamera_optik_görüntü_sabitleyici_ois",
            "ağ_bağlantilari_5g",
            'ağ_bağlantilari_5g',
            'ağ_bağlantilari_4.5g_desteği',
            'ağ_bağlantilari_4g',
            'ağ_bağlantilari_2g',
            'ağ_bağlantilari_3g',
            "kablosuz_bağlantilar_nfc",
            "özelli̇kler_suya_dayanıklılık"
        ]

        for col in self.binary_columns:
            if col in self.df.columns:
                self.df[col] = (
                    self.df[col]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .map({"var": 1, "yok": 0})
                )

        self.save_process_step("step5_binary_encoded.csv")

    # ========================================================
    # STEP 6 — HANDLE MISSING
    # ========================================================

    def step6_handle_missing(self):

        self.df.replace(r'^\s*$', np.nan, regex=True, inplace=True)

        # Binary → 0
        for col in self.binary_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna(0)

        # Numeric → median
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()

        for col in numeric_cols:
            if col not in self.binary_columns:
                self.df[col] = self.df[col].fillna(self.df[col].median())

        # Categorical → Unknown
        categorical_cols = self.df.select_dtypes(include=["object"]).columns.tolist()

        for col in categorical_cols:
            self.df[col] = self.df[col].fillna("Unknown")

        self.save_process_step("step6_missing_handled.csv")

    # ========================================================
    # STEP 7 — ONE HOT ENCODING
    # ========================================================

    def step7_one_hot(self):

        categorical_cols = self.df.select_dtypes(include=["object"]).columns.tolist()

        low_card_cols = [
            col for col in categorical_cols
            if self.df[col].nunique() <= 20
        ]

        self.df = pd.get_dummies(
            self.df,
            columns=low_card_cols,
            drop_first=True
        )

        self.save_process_step("step7_onehot_encoded.csv")

    # ========================================================
    # STEP 8 — FINAL SAVE
    # ========================================================

    def step8_finalize(self):
        self.save_process_step("step8_final_dataset.csv")
        self.save_final_step("final_dataset.csv")
        print("Final Shape:", self.df.shape)
        print("Missing values left:", self.df.isnull().sum().sum())

    # ========================================================
    # RUN ALL
    # ========================================================

    def run(self):

        self.step0_load()
        self.step1_keep_columns()
        self.step2_drop_null_target()
        self.step3_log_transform()
        self.step4_numeric_cleaning()
        self.step5_binary_mapping()
        self.step6_handle_missing()
        self.step7_one_hot()
        self.step8_finalize()

        print("Tüm adımlar tamamlandı.")

    def transform_for_prediction(self, input_df: pd.DataFrame):
        self.df = input_df.copy()

        # STEP 4
        self.step4_numeric_cleaning()

        # STEP 5
        self.step5_binary_mapping()

        # STEP 6
        self.step6_handle_missing()

        # STEP 7
        self.step7_one_hot()

        return self.df

if __name__ == "__main__":

    processor = ProductDataPreprocessor(
        input_path="src/app/output/dataset/raw/raw_dataset.csv",
        processed_dir="src/app/output/dataset/processed",
        output_dir="src/app/output/dataset/final",
    )

    processor.run()
    
