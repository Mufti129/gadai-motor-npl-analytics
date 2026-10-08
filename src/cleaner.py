"""
Data Cleaning & Target Rectification Module.
Removes corrupt test records, parses numeric/date types, and rectifies target NPL logic.
"""

from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd

from src.config import (
    DAYS_LATE_THRESHOLD,
    DAYS_LATE_THRESHOLD_30,
    DAYS_LATE_THRESHOLD_90,
    STATUS_NPL_ACTIVE,
    STATUS_LUNAS,
    CORRUPT_NAMES_FILTER
)


def remove_anomalies(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Remove corrupted system records and #DIV/0! test cases.

    Returns:
    --------
    cleaned_df : pd.DataFrame
    audit_stats : dict
    """
    initial_rows = len(df)

    # Condition 1: Dummy test records by name
    mask_corrupt_name = df["nama_nasabah"].astype(str).str.strip().isin(CORRUPT_NAMES_FILTER)

    # Condition 2: Division by zero string in LTV or Zona LTV
    mask_div0 = (df["Zona LTV"].astype(str) == "#DIV/0!") | (df["LTV"].astype(str) == "#DIV/0!")

    # Combined filter
    drop_mask = mask_corrupt_name | mask_div0
    dropped_count = int(drop_mask.sum())

    cleaned_df = df[~drop_mask].copy()

    stats = {
        "initial_rows": initial_rows,
        "dropped_anomalies": dropped_count,
        "remaining_rows": len(cleaned_df)
    }
    print(f"[Cleaner] Eliminasi baris anomali: {dropped_count} baris dibuang. Sisa: {len(cleaned_df):,} baris.")
    return cleaned_df, stats


def rectify_target_npl(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Re-evaluate and rectify the target Non-Performing Loan (NPL) columns for both:
    1. Standard Operational Gadai (>30 days overdue) -> NPL_clean / NPL_30
    2. Regulatory / OJK Kolektibilitas 5 (>90 days overdue) -> NPL_90 / NPL_clean_90
    
    Formula:
        NPL_30 (NPL_clean) = 1 if (Days Late > 30) AND (status_gadai in ['Berjalan', 'Proses Lelang']), else 0.
        NPL_90 (NPL_clean_90) = 1 if (Days Late > 90) AND (status_gadai in ['Berjalan', 'Proses Lelang']), else 0.
        Semua transaksi 'Lunas' bernilai 0.
    """
    df = df.copy()

    # Ensure Days Late is integer
    df["Days Late"] = pd.to_numeric(df["Days Late"], errors="coerce").fillna(0).astype(int)

    # Active/troubled loan status filter
    is_active_status = df["status_gadai"].isin(STATUS_NPL_ACTIVE)

    # 1. Kriteria NPL > 30 Hari (Standar Operasional Gadai)
    is_delayed_30 = df["Days Late"] > DAYS_LATE_THRESHOLD_30
    df["NPL_clean"] = (is_delayed_30 & is_active_status).astype(int)
    df["NPL_30"] = df["NPL_clean"]

    # 2. Kriteria NPL > 90 Hari (Standar Kolektibilitas OJK / Perbankan)
    is_delayed_90 = df["Days Late"] > DAYS_LATE_THRESHOLD_90
    df["NPL_90"] = (is_delayed_90 & is_active_status).astype(int)
    df["NPL_clean_90"] = df["NPL_90"]

    # 3. Kategori Bucket NPL Komparatif
    # 0 = Lancar, 1 = Overdue Ringan 1-30 hari, 2 = NPL Operasional 31-90 hari, 3 = NPL Berat >90 hari
    def assign_npl_category(row):
        if row["status_gadai"] == STATUS_LUNAS:
            return "Lunas (Lancar)"
        days = row["Days Late"]
        if days <= 0:
            return "Tepat Waktu"
        elif days <= 30:
            return "Keterlambatan 1-30 Hari (DPD 1-30)"
        elif days <= 90:
            return "NPL Transisi 31-90 Hari (DPD 31-90)"
        else:
            return "NPL Berat > 90 Hari (DPD >90 / Bad Debt)"

    df["kategori_kolektibilitas"] = df.apply(assign_npl_category, axis=1)

    # Compare with raw NPL column if available
    mismatch_stats = {}
    if "NPL" in df.columns:
        raw_npl = pd.to_numeric(df["NPL"], errors="coerce").fillna(0).astype(int)
        df["NPL_raw"] = raw_npl
        mismatches = df[df["NPL_clean"] != df["NPL_raw"]]
        mismatch_stats = {
            "total_mismatches": len(mismatches),
            "proses_lelang_corrected_to_1": int(((df["status_gadai"] == "Proses Lelang") & (df["NPL_clean"] == 1) & (df["NPL_raw"] == 0)).sum()),
            "lunas_corrected_to_0": int(((df["status_gadai"] == STATUS_LUNAS) & (df["NPL_clean"] == 0) & (df["NPL_raw"] == 1)).sum()),
            "npl_30_count": int(df["NPL_30"].sum()),
            "npl_30_rate_pct": float(df["NPL_30"].mean() * 100),
            "npl_90_count": int(df["NPL_90"].sum()),
            "npl_90_rate_pct": float(df["NPL_90"].mean() * 100)
        }
        print(f"[Cleaner] Validasi Target NPL:")
        print(f"  - Total mismatch formula Excel vs Aturan Bisnis: {len(mismatches)} baris")
        print(f"  - Kasus 'Proses Lelang' dikoreksi menjadi 1 (Macet): {mismatch_stats['proses_lelang_corrected_to_1']} baris")
        print(f"  - Kasus 'Lunas' dikoreksi menjadi 0 (Lancar): {mismatch_stats['lunas_corrected_to_0']} baris")
        print(f"  - NPL Rate (>30 Hari / Operasional) : {df['NPL_30'].mean()*100:.2f}% ({df['NPL_30'].sum():,} pinjaman)")
        print(f"  - NPL Rate (>90 Hari / OJK Standard): {df['NPL_90'].mean()*100:.2f}% ({df['NPL_90'].sum():,} pinjaman)")

    return df, mismatch_stats


def cast_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cast numeric and date columns to standard data types.
    """
    df = df.copy()

    # String identifiers
    for col in ["fraktur", "no_identitas", "nama_nasabah", "cabang"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()

    # Numeric ratio columns
    numeric_cols = [
        "pinjaman_pokok_awal", "pinjaman_pokok_efektif", "nilai_barang_awal",
        "nilai_taksiran", "pinjaman_maksimum", "jasa_awal", "biaya_asuransi",
        "nilai_admin", "total_jasa_terbayar", "frekuensi_cicilan_masuk",
        "total_nominal_pembayaran_masuk", "Usia Kendaraan_2(thn)"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Float ratio columns
    for col in ["LTV", "LTV_MAX"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Date parsing
    date_cols = [
        "tanggal_gadai", "pajakstnk", "tgl_gadai_transaksi",
        "tanggal_jatuh_tempo_sebelum", "tanggal_jatuh_tempo_sekarang",
        "tanggal_pembayaran_terakhir", "tanggal_penarikan"
    ]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    print("[Cleaner] Standarisasi tipe data (numerik, rasio, tanggal) selesai.")
    return df
