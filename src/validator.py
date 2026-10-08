"""
Data Validation & Quality Assurance Module.
Runs programmatic assertions to guarantee clean dataset integrity before statistical modeling.
"""

import json
from pathlib import Path
from typing import Dict, Any
import pandas as pd

from src.config import AUDIT_REPORT_JSON, OUTPUT_DIR


def validate_clean_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Execute data integrity assertions and generate a quality audit report.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report: Dict[str, Any] = {}

    total_rows = len(df)
    report["total_rows"] = total_rows
    report["total_columns"] = len(df.columns)

    # 1. Assertions on Target Variable (>30 Days & >90 Days)
    assert "NPL_clean" in df.columns, "Kolom NPL_clean tidak ditemukan!"
    assert "NPL_30" in df.columns, "Kolom NPL_30 tidak ditemukan!"
    assert "NPL_90" in df.columns, "Kolom NPL_90 tidak ditemukan!"
    assert df["NPL_clean"].isnull().sum() == 0, "Ditemukan nilai NULL pada NPL_clean!"
    assert df["NPL_90"].isnull().sum() == 0, "Ditemukan nilai NULL pada NPL_90!"
    
    unique_npl_30 = set(df["NPL_30"].unique())
    unique_npl_90 = set(df["NPL_90"].unique())
    assert unique_npl_30.issubset({0, 1}), f"Nilai NPL_30 tidak valid: {unique_npl_30}"
    assert unique_npl_90.issubset({0, 1}), f"Nilai NPL_90 tidak valid: {unique_npl_90}"
    assert (df["NPL_90"] <= df["NPL_30"]).all(), "Error: NPL_90 harus merupakan subset dari NPL_30!"

    npl_30_count = int(df["NPL_30"].sum())
    npl_30_rate = (npl_30_count / total_rows) * 100

    npl_90_count = int(df["NPL_90"].sum())
    npl_90_rate = (npl_90_count / total_rows) * 100

    report["target_summary"] = {
        "npl_30_count": npl_30_count,
        "npl_30_rate_pct": round(npl_30_rate, 4),
        "npl_90_count": npl_90_count,
        "npl_90_rate_pct": round(npl_90_rate, 4),
        "transition_31_90_count": npl_30_count - npl_90_count,
        "transition_31_90_rate_pct": round((npl_30_count - npl_90_count) / total_rows * 100, 4),
        "non_npl_30_count": total_rows - npl_30_count,
        "non_npl_90_count": total_rows - npl_90_count
    }

    # 2. Specific Verification on Previously Identified Mismatches
    # Check Lunas Row (Faktur 11208251226017)
    lunas_sample = df[df["fraktur"] == "11208251226017"]
    if len(lunas_sample) > 0:
        lunas_npl = int(lunas_sample["NPL_clean"].values[0])
        assert lunas_npl == 0, f"Error: Baris Lunas Faktur 11208251226017 memiliki NPL_clean = {lunas_npl} (harus 0)!"
        report["verification_lunas_faktur_11208251226017"] = "PASSED (NPL_clean = 0)"

    # Check Proses Lelang with Days Late > 30
    lelang_overdue = df[(df["status_gadai"] == "Proses Lelang") & (df["Days Late"] > 30)]
    assert (lelang_overdue["NPL_clean"] == 1).all(), "Error: Ditemukan baris Proses Lelang menunggak > 30 hari yang tidak berstatus NPL = 1!"
    report["verification_proses_lelang_count"] = f"PASSED ({len(lelang_overdue)} baris berstatus NPL_clean = 1)"

    # 3. Check Duplicate Transactions
    duplicate_fraktur = int(df["fraktur"].duplicated().sum())
    report["duplicate_fraktur_count"] = duplicate_fraktur

    # 4. Feature Summaries by NPL Rate
    def calc_group_npl(col_name: str) -> Dict[str, Any]:
        if col_name not in df.columns:
            return {}
        agg = df.groupby(col_name)["NPL_clean"].agg(["count", "sum", "mean"]).to_dict("index")
        return {
            str(k): {
                "total": v["count"],
                "npl": int(v["sum"]),
                "npl_rate_pct": round(v["mean"] * 100, 2)
            }
            for k, v in agg.items()
        }

    report["risk_distribution"] = {
        "kondisi_stnk": calc_group_npl("kondisi_stnk"),
        "pajak_status": calc_group_npl("pajak_status"),
        "merk_group": calc_group_npl("merk_group"),
        "skala_pinjaman_std": calc_group_npl("skala_pinjaman_std"),
        "usia_kendaraan_bin": calc_group_npl("usia_kendaraan_bin"),
        "zona_ltv_std": calc_group_npl("zona_ltv_std"),
        "is_repeat_borrower": calc_group_npl("is_repeat_borrower")
    }

    # Save to JSON
    with open(AUDIT_REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"[Validator] Validasi integritas data: SEMUA PENGUJIAN LOLOS (PASSED).")
    print(f"[Validator] Laporan audit disimpan ke: {AUDIT_REPORT_JSON}")
    return report
