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
                 process_dir: str,
                 output_dir: str,
                 target: str = "urun_fiyat",
                 exclude: str = "urun_puan"):

        self.input_path = input_path
        self.process_dir = Path(process_dir)
        self.output_dir = Path(output_dir)

        self.process_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.TARGET = target
        self.EXCLUDE = exclude

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

    def save_step(self, filename):
        self.df.to_csv(self.process_dir / filename, index=False)

    # ========================================================
    # STEP 0 — LOAD
    # ========================================================

    def step0_load(self):
        self.df = pd.read_csv(self.input_path)
        self.save_step("step0_raw.csv")

    # ========================================================
    # STEP 1 — DROP NULL TARGET
    # ========================================================

    def step1_drop_null_target(self):
        self.df = self.df[self.df[self.TARGET].notna()]
        self.save_step("step1_drop_null_target.csv")

    # ========================================================
    # STEP 2 — LOG TRANSFORM TARGET
    # ========================================================

    def step2_log_transform(self):
        self.df[self.TARGET] = np.log1p(self.df[self.TARGET])
        self.save_step("step2_log_target.csv")

    # ========================================================
    # STEP 3 — KEEP SELECTED COLUMNS
    # ========================================================

    def step3_keep_columns(self):

        include_columns = [
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
            'kablosuz_bağlantilar_bluetooth_versiyonu',
            'kablosuz_bağlantilar_nfc',
            'i̇şleti̇m_si̇stemi̇_i̇şletim_sistemi',
            'özelli̇kler_suya_dayanıklılık'
        ]

        existing_include = [col for col in include_columns if col in self.df.columns]
        self.df = self.df[existing_include].copy()

        if self.EXCLUDE in self.df.columns:
            self.df.drop(columns=[self.EXCLUDE], inplace=True)

        self.save_step("step3_keep_selected_columns.csv")

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

        self.save_step("step4_numeric_cleaned.csv")

    # ========================================================
    # STEP 5 — BINARY MAPPING
    # ========================================================

    def step5_binary_mapping(self):

        self.binary_columns = [
            "batarya_hızlı_şarj",
            "batarya_kablosuz_şarj",
            "kamera_optik_görüntü_sabitleyici_ois",
            "ağ_bağlantilari_5g",
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

        self.save_step("step5_binary_encoded.csv")

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

        if self.TARGET in numeric_cols:
            numeric_cols.remove(self.TARGET)

        for col in numeric_cols:
            if col not in self.binary_columns:
                self.df[col] = self.df[col].fillna(self.df[col].median())

        # Categorical → Unknown
        categorical_cols = self.df.select_dtypes(include=["object"]).columns.tolist()

        for col in categorical_cols:
            self.df[col] = self.df[col].fillna("Unknown")

        self.save_step("step6_missing_handled.csv")

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

        self.save_step("step7_onehot_encoded.csv")

    # ========================================================
    # STEP 8 — FINAL SAVE
    # ========================================================

    def step8_finalize(self):

        self.df.to_csv(
            self.process_dir / "step8_final_model_ready.csv",
            index=False
        )

        self.df.to_csv(
            self.output_dir / "step8_final_model_ready.csv",
            index=False
        )

        print("Final Shape:", self.df.shape)
        print("Missing values left:", self.df.isnull().sum().sum())

    # ========================================================
    # RUN ALL
    # ========================================================

    def run(self):

        self.step0_load()
        self.step1_drop_null_target()
        self.step2_log_transform()
        self.step3_keep_columns()
        self.step4_numeric_cleaning()
        self.step5_binary_mapping()
        self.step6_handle_missing()
        self.step7_one_hot()
        self.step8_finalize()

        print("Tüm adımlar tamamlandı.")

if __name__ == "__main__":

    processor = ProductDataPreprocessor(
        input_path="src/app/output/dataset/raw/full_dataset.csv",
        process_dir="src/app/output/dataset/processed_step",
        output_dir="src/app/output/dataset/final"
    )

    processor.run()
