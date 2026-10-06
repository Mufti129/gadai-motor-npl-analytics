"""
Categorical Normalization Module.
Standardizes noisy text categories (pekerjaan, merk, pajak, STNK condition)
into structured groups suitable for statistical inference and risk modeling.
"""

import pandas as pd
from src.config import TOP_BRANDS


def normalize_pekerjaan(val: str) -> str:
    """
    Standardize raw occupation text into clean business categories.
    """
    if pd.isna(val):
        return "TIDAK ISI"
    
    s = str(val).strip().upper()
    if s in ["", "NULL", "NONE", "NAN", "TIDAK ISI", "-"]:
        return "TIDAK ISI"

    # Hierarchy of keyword matching
    if "SWASTA" in s or s == "KARYAWAN":
        return "KARYAWAN SWASTA"
    if "RUMAH TANGGA" in s or s == "IRT":
        return "IBU RUMAH TANGGA"
    if "PELAJAR" in s or "MAHASISWA" in s:
        return "PELAJAR/MAHASISWA"
    if "WIRA" in s or "USAHA" in s or "BISNIS" in s:
        return "WIRASWASTA"
    if "BURUH" in s:
        return "BURUH"
    if "PNS" in s or "NEGERI" in s or "ASN" in s:
        return "PNS"
    if "BELUM" in s or "TIDAK BEKERJA" in s or "MENGANGGUR" in s:
        return "BELUM/TIDAK BEKERJA"
    if "GURU" in s or "DOSEN" in s:
        return "GURU"
    if "DAGANG" in s or "PEDAGANG" in s:
        return "PEDAGANG"
    
    return "LAINNYA"


def normalize_categories(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply category normalization across all key categorical features.
    """
    df = df.copy()

    # 1. Pekerjaan
    if "pekerjaan" in df.columns:
        df["pekerjaan_raw"] = df["pekerjaan"].astype(str).str.strip()
        df["pekerjaan_group"] = df["pekerjaan"].apply(normalize_pekerjaan)
        df["has_pekerjaan_info"] = (df["pekerjaan_group"] != "TIDAK ISI").astype(int)

    # 2. Merk
    if "merk" in df.columns:
        df["merk_raw"] = df["merk"].astype(str).str.strip()
        # Group minor brands into 'LAINNYA'
        df["merk_group"] = df["merk_raw"].apply(lambda x: x if x in TOP_BRANDS else "LAINNYA")

    # 3. Kondisi STNK
    if "kondisi_name" in df.columns:
        df["kondisi_stnk"] = df["kondisi_name"].astype(str).str.strip().str.upper()
        # Ensure only valid categories
        valid_stnk = ["A/N SENDIRI", "A/N ORANG LAIN"]
        df["kondisi_stnk"] = df["kondisi_stnk"].apply(lambda x: x if x in valid_stnk else "LAINNYA")

    # 4. Pajak
    if "pajak" in df.columns:
        df["pajak_status"] = df["pajak"].astype(str).str.strip()
        valid_pajak = ["Pajak Aktif", "Pajak Tidak Aktif"]
        df["pajak_status"] = df["pajak_status"].apply(lambda x: x if x in valid_pajak else "Pajak Tidak Aktif")

    print("[Normalizer] Harmonisasi kategori teks (pekerjaan, merk, STNK, pajak) selesai.")
    return df
