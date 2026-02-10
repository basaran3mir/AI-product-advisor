from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.api.types import is_object_dtype, is_string_dtype


TURKISH_MAP = str.maketrans(
    {
        "\u0131": "i",
        "\u0130": "i",
        "\u015f": "s",
        "\u015e": "s",
        "\u011f": "g",
        "\u011e": "g",
        "\u00fc": "u",
        "\u00dc": "u",
        "\u00f6": "o",
        "\u00d6": "o",
        "\u00e7": "c",
        "\u00c7": "c",
    }
)


def normalize_col(name: str) -> str:
    name = name.translate(TURKISH_MAP)
    name = unicodedata.normalize("NFKD", name)
    name = "".join(ch for ch in name if not unicodedata.combining(ch))
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_{2,}", "_", name).strip("_")
    return name


def normalize_text(value: str) -> str:
    value = value.translate(TURKISH_MAP)
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(r"\s{2,}", " ", value).strip()
    return value


def extract_number(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.replace(",", ".", regex=False)
    extracted = s.str.extract(r"([-+]?\d*\.?\d+)")[0]
    return pd.to_numeric(extracted, errors="coerce")


def parse_bool(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip().str.lower()
    s = s.replace({"nan": np.nan})
    return s.map({"var": 1, "yok": 0})


def parse_resolution(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    s = series.astype(str)
    wh = s.str.extract(r"(\d+)\s*x\s*(\d+)")
    w = pd.to_numeric(wh[0], errors="coerce")
    h = pd.to_numeric(wh[1], errors="coerce")
    return w, h


CHIPSET_BRANDS: list[tuple[str, str]] = [
    ("Apple", r"\bapple\b|\bbionic\b"),
    ("Samsung Exynos", r"\bexynos\b|\bexynoss\b|\bsamsung\b"),
    ("Qualcomm", r"\bqualcomm\b|\bsnapdragon\b"),
    ("MediaTek", r"\bmediatek\b|\bmedia\s*tek\b|\bdimensity\b|\bhelio\b|\bmtk\b"),
    ("Unisoc", r"\bunisoc\b|\bspreadtrum\b"),
    ("HiSilicon Kirin", r"\bhisilicon\b|\bkirin\b|\bhuawei\b"),
    ("Google Tensor", r"\btensor\b|\bgoogle\b"),
]


def map_chipset_brand(series: pd.Series) -> tuple[pd.Series, list[str]]:
    unknowns: list[str] = []

    def map_one(value: object) -> object:
        if pd.isna(value):
            return np.nan
        text = normalize_text(str(value))
        if not text:
            return np.nan
        for brand, pattern in CHIPSET_BRANDS:
            if re.search(pattern, text):
                return brand
        unknowns.append(str(value))
        return "Other"

    mapped = series.map(map_one)
    return mapped, sorted(set(unknowns))


def clean_dataframe(
    df: pd.DataFrame,
    keep_resolution: bool,
    keep_chipset: bool,
    normalize_text_values: bool,
) -> tuple[pd.DataFrame, dict[str, str], list[str]]:
    rename_map = {c: normalize_col(c) for c in df.columns}
    df = df.rename(columns=rename_map)

    for col in df.columns:
        if is_object_dtype(df[col]) or is_string_dtype(df[col]):
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({"": np.nan, "nan": np.nan})

    for col in ["fiyat_tl", "puan", "temel_bilgiler_cikis_yili"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    unit_cols = [
        "ekran_ekran_boyutu",
        "ekran_ekran_yenileme_hizi",
        "batarya_batarya_kapasitesi_tipik",
        "batarya_hizli_sarj_gucu_maks",
        "kamera_kamera_cozunurlugu",
        "kamera_on_kamera_cozunurlugu",
        "temel_donanim_bellek_ram",
        "temel_donanim_dahili_depolama",
        "temel_donanim_cpu_uretim_teknolojisi",
        "tasarim_kalinlik",
        "tasarim_agirlik",
    ]
    for col in unit_cols:
        if col in df.columns:
            df[col] = extract_number(df[col])

    bool_cols = [
        "batarya_kablosuz_sarj",
        "kamera_optik_goruntu_sabitleyici_ois",
        "ozellikler_suya_dayaniklilik",
    ]
    for col in bool_cols:
        if col in df.columns:
            df[col] = parse_bool(df[col])

    unknown_chipsets: list[str] = []
    chipset_col = "temel_donanim_yonga_seti_chipset"
    if chipset_col in df.columns:
        brand, unknown_chipsets = map_chipset_brand(df[chipset_col])
        df["temel_donanim_yonga_seti_marka"] = brand
        if not keep_chipset:
            df = df.drop(columns=[chipset_col])

    res_col = "ekran_ekran_cozunurlugu"
    if res_col in df.columns:
        w, h = parse_resolution(df[res_col])
        df["ekran_cozunurluk_genislik"] = w
        df["ekran_cozunurluk_yukseklik"] = h
        df["ekran_piksel_milyon"] = (w * h) / 1_000_000
        df["ekran_aspect_orani"] = w / h
        if not keep_resolution:
            df = df.drop(columns=[res_col])

    if normalize_text_values:
        for col in df.columns:
            if is_object_dtype(df[col]) or is_string_dtype(df[col]):
                df[col] = df[col].map(lambda v: normalize_text(v) if isinstance(v, str) else v)

    return df, rename_map, unknown_chipsets


def encode_dataframe(
    df: pd.DataFrame,
    encoding: str,
    target: str | None,
    dummy_na: bool,
    impute_numeric: str,
    missing_flags: bool,
    categorical_missing: str,
    missing_token: str,
    bool_as_int: bool,
) -> tuple[pd.DataFrame, dict[str, list[str]] | None, dict[str, object]]:
    if encoding == "none":
        return df, None, {}

    if target and target in df.columns:
        y = df[target]
        x = df.drop(columns=[target])
    else:
        y = None
        x = df

    x = x.copy()
    cat_cols = [c for c in x.columns if is_object_dtype(x[c]) or is_string_dtype(x[c])]
    num_cols = [c for c in x.columns if c not in cat_cols]
    meta: dict[str, object] = {}

    if categorical_missing == "explicit" and cat_cols:
        for col in cat_cols:
            x[col] = x[col].where(~x[col].isna(), other=missing_token)
        meta["categorical_missing"] = {"token": missing_token, "columns": cat_cols}

    if missing_flags:
        flag_cols: list[str] = []
        for col in num_cols:
            if x[col].isna().any():
                flag_col = f"{col}__missing"
                x[flag_col] = x[col].isna().astype(int)
                flag_cols.append(flag_col)
        if flag_cols:
            meta["missing_flags"] = flag_cols

    if impute_numeric == "median":
        impute_values: dict[str, float] = {}
        for col in num_cols:
            if x[col].isna().any():
                median = x[col].median(skipna=True)
                if pd.isna(median):
                    median = 0.0
                x[col] = x[col].fillna(median)
                impute_values[col] = float(median)
        if impute_values:
            meta["numeric_imputation"] = {"strategy": "median", "values": impute_values}
    elif impute_numeric != "none":
        raise ValueError(f"Unsupported impute strategy: {impute_numeric}")

    if encoding == "onehot":
        x_enc = pd.get_dummies(x, columns=cat_cols, dummy_na=dummy_na)
        if y is not None:
            x_enc[target] = y
        if bool_as_int:
            bool_cols = [c for c in x_enc.columns if x_enc[c].dtype == "bool"]
            if bool_cols:
                x_enc[bool_cols] = x_enc[bool_cols].astype(int)
                meta["bool_cast"] = {"columns": bool_cols}
        return x_enc, None, meta

    if encoding == "ordinal":
        mappings: dict[str, list[str]] = {}
        x_enc = x.copy()
        for col in cat_cols:
            cat = pd.Categorical(x_enc[col])
            x_enc[col] = cat.codes
            mappings[col] = [str(v) for v in cat.categories]
        if y is not None:
            x_enc[target] = y
        if bool_as_int:
            bool_cols = [c for c in x_enc.columns if x_enc[c].dtype == "bool"]
            if bool_cols:
                x_enc[bool_cols] = x_enc[bool_cols].astype(int)
                meta["bool_cast"] = {"columns": bool_cols}
        return x_enc, mappings, meta

    raise ValueError(f"Unsupported encoding: {encoding}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean and encode filtered_dataset.csv.")
    parser.add_argument("--input", default="src/app/outputs/datasets/filtered_dataset.csv")
    parser.add_argument("--clean-out", default="src/app/outputs/datasets/dataset_clean.csv")
    parser.add_argument("--encoded-out", default="src/app/outputs/datasets/dataset_encoded.csv")
    parser.add_argument("--report-out", default="src/app/outputs/datasets/encoding_report.json")
    parser.add_argument(
        "--encoding",
        default="onehot",
        choices=["onehot", "ordinal", "none"],
        help="Encoding strategy for categorical columns.",
    )
    parser.add_argument("--target", default=None, help="Optional target column to exclude from encoding.")
    parser.add_argument("--dummy-na", action="store_true", help="Add a dummy column for NaN categories.")
    parser.add_argument("--keep-resolution", action="store_true", help="Keep raw resolution string column.")
    parser.add_argument("--keep-chipset", action="store_true", help="Keep full chipset column (default drops it).")
    parser.add_argument(
        "--normalize-text-values",
        action="store_true",
        help="Normalize categorical text values to ASCII lowercase.",
    )
    parser.add_argument(
        "--impute-numeric",
        default="median",
        choices=["median", "none"],
        help="Impute missing numeric values (default: median).",
    )
    parser.add_argument(
        "--missing-flags",
        default="on",
        choices=["on", "off"],
        help="Add missing indicator flags for numeric columns with NaNs.",
    )
    parser.add_argument(
        "--categorical-missing",
        default="explicit",
        choices=["explicit", "none"],
        help="Handle missing categoricals by using a missing token.",
    )
    parser.add_argument(
        "--missing-token",
        default="__missing__",
        help="Token used when categorical-missing is explicit.",
    )
    parser.add_argument(
        "--bool-as-int",
        default="on",
        choices=["on", "off"],
        help="Cast boolean columns to 0/1.",
    )
    args = parser.parse_args()

    df = pd.read_csv(args.input, encoding="utf-8")
    df_clean, rename_map, unknown_chipsets = clean_dataframe(
        df,
        keep_resolution=args.keep_resolution,
        keep_chipset=args.keep_chipset,
        normalize_text_values=args.normalize_text_values,
    )
    df_clean.to_csv(args.clean_out, index=False)

    report = {
        "rows": int(len(df_clean)),
        "columns": list(df_clean.columns),
        "renamed_columns": rename_map,
    }
    if unknown_chipsets:
        report["unknown_chipsets"] = unknown_chipsets

    if args.encoding != "none":
        df_encoded, mappings, meta = encode_dataframe(
            df_clean,
            encoding=args.encoding,
            target=args.target,
            dummy_na=args.dummy_na,
            impute_numeric=args.impute_numeric,
            missing_flags=args.missing_flags == "on",
            categorical_missing=args.categorical_missing,
            missing_token=args.missing_token,
            bool_as_int=args.bool_as_int == "on",
        )
        df_encoded.to_csv(args.encoded_out, index=False)
        if mappings is not None:
            report["ordinal_mappings"] = mappings
        if meta:
            report["encoding"] = meta

    Path(args.report_out).write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
