"""
Feature Engineering Module.
Creates analytical risk predictors, scale transformations, and customer history indicators.
"""

import numpy as np
import pandas as pd
from src.config import AGE_BINS, AGE_LABELS, LOAN_BINS, LOAN_LABELS


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate derived risk features and standardized transformation variables.
    """
    df = df.copy()

    # 1. Repeat Borrower Indicator
    if "no_identitas" in df.columns:
        nasabah_counts = df["no_identitas"].value_counts()
        df["nasabah_total_transaksi"] = df["no_identitas"].map(nasabah_counts).fillna(1).astype(int)
        df["is_repeat_borrower"] = (df["nasabah_total_transaksi"] > 1).astype(int)

    # 2. Pinjaman Scaling & Categorization
    if "pinjaman_pokok_awal" in df.columns:
        df["pinjaman_juta"] = df["pinjaman_pokok_awal"] / 1_000_000.0
        df["skala_pinjaman_std"] = pd.cut(
            df["pinjaman_pokok_awal"],
            bins=LOAN_BINS,
            labels=LOAN_LABELS,
            right=True
        ).astype(str)

    # 3. Usia Kendaraan Categorization
    if "Usia Kendaraan_2(thn)" in df.columns:
        df["usia_kendaraan_thn"] = pd.to_numeric(df["Usia Kendaraan_2(thn)"], errors="coerce")
        df["usia_kendaraan_bin"] = pd.cut(
            df["usia_kendaraan_thn"],
            bins=AGE_BINS,
            labels=AGE_LABELS,
            right=True
        ).astype(str)

    # 4. Zona LTV Categorization (Clean)
    if "LTV" in df.columns:
        ltv_val = pd.to_numeric(df["LTV"], errors="coerce")
        conditions = [
            ltv_val <= 0.35,
            (ltv_val > 0.35) & (ltv_val <= 0.40),
            (ltv_val > 0.40) & (ltv_val <= 0.50),
            ltv_val > 0.50
        ]
        choices = ["<=35%", "36%-40%", "41%-50%", ">50%"]
        df["zona_ltv_std"] = np.select(conditions, choices, default="36%-40%")

    # 5. Binary flags for econometric models
    if "kondisi_stnk" in df.columns:
        df["is_stnk_sendiri"] = (df["kondisi_stnk"] == "A/N SENDIRI").astype(int)
    
    if "pajak_status" in df.columns:
        df["is_pajak_aktif"] = (df["pajak_status"] == "Pajak Aktif").astype(int)

    print("[Feature Engineering] Pembuatan fitur prediktor (repeat borrower, pinjaman_juta, age bins, LTV bins) selesai.")
    return df
