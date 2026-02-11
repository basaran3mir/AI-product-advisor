# ============================================================
# FULL DATA PREPROCESSING PIPELINE
# Target: urun_fiyat (log transform uygulanacak)
# urun_puan model dışında tutulacak
# ============================================================

import pandas as pd
import numpy as np
import re
from pathlib import Path

# =============================
# CONFIG
# =============================
INPUT_PATH = "src/app/output/dataset/raw/full_dataset.csv"
OUTPUT_DIR = Path("src/app/output/dataset/processed_steps")
OUTPUT_DIR.mkdir(exist_ok=True)

FINAL_OUTPUT_DIR = Path("src/app/output/dataset/final")
FINAL_OUTPUT_DIR.mkdir(exist_ok=True)

TARGET = "urun_fiyat"
EXCLUDE = "urun_puan"

# =============================
# HELPER FUNCTIONS
# =============================

def extract_numeric(value):
    if pd.isna(value):
        return np.nan
    value = str(value).replace(".", "")
    match = re.search(r"\d+(\.\d+)?", value)
    if match:
        return float(match.group())
    return np.nan

def clean_numeric_column(df, column):
    df[column] = df[column].apply(extract_numeric)
    return df

# =============================
# STEP 0 — LOAD
# =============================
df = pd.read_csv(INPUT_PATH)
df.to_csv(OUTPUT_DIR / "step0_raw.csv", index=False)

# =============================
# STEP 1 — DROP NULL TARGET
# =============================
df = df[df[TARGET].notna()]
df.to_csv(OUTPUT_DIR / "step1_drop_null_target.csv", index=False)

# =============================
# STEP 2 — LOG TRANSFORM TARGET
# =============================
df[TARGET] = np.log1p(df[TARGET])
df.to_csv(OUTPUT_DIR / "step2_log_target.csv", index=False)

# =============================
# STEP 3 — KEEP ONLY SELECTED COLUMNS (INCLUDE - EXCLUDE)
# =============================
INCLUDE_COLUMNS = [
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

EXCLUDE_COLUMNS = [
    EXCLUDE
]

existing_include = [col for col in INCLUDE_COLUMNS if col in df.columns]
df = df[existing_include].copy()


df = df.drop(columns=[col for col in EXCLUDE_COLUMNS if col in df.columns])
df.to_csv(OUTPUT_DIR / "step3_keep_selected_columns.csv", index=False)


# =============================
# STEP 4 — NUMERIC CLEANING
# =============================
numeric_columns_to_clean = [
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

for col in numeric_columns_to_clean:
    if col in df.columns:
        df = clean_numeric_column(df, col)

df.to_csv(OUTPUT_DIR / "step4_numeric_cleaned.csv", index=False)

# =============================
# STEP 5 — BINARY MAPPING
# =============================
binary_columns = [
    "batarya_hızlı_şarj",
    "batarya_kablosuz_şarj",
    "kamera_optik_görüntü_sabitleyici_ois",
    "ağ_bağlantilari_5g",
    "kablosuz_bağlantilar_nfc",
    "özelli̇kler_suya_dayanıklılık"
]

for col in binary_columns:
    if col in df.columns:
        df[col] = df[col].map({"Var": 1, "Yok": 0})

df.to_csv(OUTPUT_DIR / "step5_binary_encoded.csv", index=False)

# =============================
# STEP 6 — HANDLE MISSING
# =============================

# Numeric → median
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
numeric_cols.remove(TARGET)

for col in numeric_cols:
    df[col].fillna(df[col].median(), inplace=True)

# Categorical → Unknown
categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()

for col in categorical_cols:
    df[col].fillna("Unknown", inplace=True)

df.to_csv(OUTPUT_DIR / "step6_missing_handled.csv", index=False)

# =============================
# STEP 7 — ONE HOT ENCODING
# =============================
low_cardinality_cols = []

for col in categorical_cols:
    if df[col].nunique() <= 20:
        low_cardinality_cols.append(col)

df = pd.get_dummies(df, columns=low_cardinality_cols, drop_first=True)

df.to_csv(OUTPUT_DIR / "step7_onehot_encoded.csv", index=False)

# =============================
# STEP 8 — FINAL CHECK
# =============================
print("Final Shape:", df.shape)
print("Missing values left:", df.isnull().sum().sum())

df.to_csv(OUTPUT_DIR / "step8_final_model_ready.csv", index=False)

df.to_csv(FINAL_OUTPUT_DIR / "step8_final_model_ready.csv", index=False)

print("Tüm adımlar tamamlandı.")