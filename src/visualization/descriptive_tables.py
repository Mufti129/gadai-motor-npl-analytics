"""
Descriptive & Bivariate Research Tables Module (Tabel 1, 2, 11).
Generates publication-ready summary tables corresponding to Section 17 in Research Design PDF.
"""

from pathlib import Path
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from scipy import stats

from src.config import TABLES_OUTPUT_DIR, TABEL1_CSV, TABEL2_CSV, TABEL11_CSV


def generate_table1_characteristics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tabel 1: Karakteristik Seluruh Transaksi Gadai Kendaraan (Kuantitatif).
    """
    TABLES_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    num_cols = {
        "pinjaman_pokok_awal": "Pinjaman Pokok Awal (Rp)",
        "nilai_barang_awal": "Nilai Taksiran Barang Awal (Rp)",
        "usia_kendaraan_thn": "Usia Kendaraan (Tahun)",
        "LTV": "Actual LTV",
        "LTV_MAX": "LTV Maximum Allowed",
        "Days Late": "Hari Keterlambatan (Days Late)"
    }

    rows = []
    for col, label in num_cols.items():
        if col in df.columns:
            s = pd.to_numeric(df[col], errors="coerce").dropna()
            q25 = np.percentile(s, 25)
            q75 = np.percentile(s, 75)
            rows.append({
                "Variabel": label,
                "N Observasi": len(s),
                "Mean": round(s.mean(), 2),
                "Standar Deviasi": round(s.std(), 2),
                "Median": round(s.median(), 2),
                "Q1 (25%)": round(q25, 2),
                "Q3 (75%)": round(q75, 2),
                "IQR": round(q75 - q25, 2),
                "Min": round(s.min(), 2),
                "Max": round(s.max(), 2)
            })

    t1_df = pd.DataFrame(rows)
    t1_df.to_csv(TABEL1_CSV, index=False)
    print(f"[Tabel] Tabel 1 (Karakteristik Data) disimpan: {TABEL1_CSV.name}")
    return t1_df


def generate_table2_npl_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tabel 2: Distribusi Status NPL Komparatif (Kriteria >30 Hari vs >90 Hari).
    """
    TABLES_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total = len(df)
    npl_30_cnt = int(df["NPL_30"].sum()) if "NPL_30" in df.columns else int(df["NPL_clean"].sum())
    npl_90_cnt = int(df["NPL_90"].sum()) if "NPL_90" in df.columns else 0
    transition_cnt = npl_30_cnt - npl_90_cnt
    non_cnt = total - npl_30_cnt

    t2_df = pd.DataFrame([
        {"Status / Klasifikasi": "Kredit Lancar (Non-NPL / <= 30 Hari)", "Frekuensi": non_cnt, "Persentase (%)": round((non_cnt/total)*100, 2), "Definisi / Acuan": "Days Late <= 30 atau Lunas"},
        {"Status / Klasifikasi": "Kredit Macet NPL > 30 Hari (Operasional)", "Frekuensi": npl_30_cnt, "Persentase (%)": round((npl_30_cnt/total)*100, 2), "Definisi / Acuan": "Days Late > 30 Hari (Standar Gadai)"},
        {"Status / Klasifikasi": "  ├── NPL Transisi (DPD 31-90 Hari)", "Frekuensi": transition_cnt, "Persentase (%)": round((transition_cnt/total)*100, 2), "Definisi / Acuan": "31 <= Days Late <= 90 Hari"},
        {"Status / Klasifikasi": "  └── NPL Berat / Macet > 90 Hari (OJK)", "Frekuensi": npl_90_cnt, "Persentase (%)": round((npl_90_cnt/total)*100, 2), "Definisi / Acuan": "Days Late > 90 Hari (Standar OJK Kolektibilitas 5)"},
        {"Status / Klasifikasi": "Total Seluruh Populasi", "Frekuensi": total, "Persentase (%)": 100.0, "Definisi / Acuan": "139.493 Transaksi Valid"}
    ])

    t2_df.to_csv(TABEL2_CSV, index=False)
    print(f"[Tabel] Tabel 2 (Distribusi NPL Komparatif) disimpan: {TABEL2_CSV.name}")
    return t2_df


def generate_table11_bivariate_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tabel 11: Ringkasan Analisis Bivariat Lengkap.
    Uji Chi-Square, Cramer's V, Odds Ratio (95% CI), dan p-value untuk tiap variabel kategorik.
    """
    TABLES_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    cat_factors = [
        ("kondisi_stnk", "Kepemilikan STNK"),
        ("pajak_status", "Status Pajak STNK"),
        ("merk_group", "Merk Motor"),
        ("skala_pinjaman_std", "Skala Pinjaman Pokok"),
        ("usia_kendaraan_bin", "Kelompok Usia Motor"),
        ("zona_ltv_std", "Zona LTV"),
        ("is_repeat_borrower", "Riwayat Nasabah (Repeat vs Baru)")
    ]

    bivariate_rows = []

    for col, factor_label in cat_factors:
        if col in df.columns:
            ct = pd.crosstab(df[col], df["NPL_clean"])
            chi2, p, dof, _ = stats.chi2_contingency(ct)
            n = ct.values.sum()
            cramer_v = np.sqrt(chi2 / (n * (min(ct.shape) - 1)))

            for cat in ct.index:
                npl_1 = ct.loc[cat, 1] if 1 in ct.columns else 0
                npl_0 = ct.loc[cat, 0] if 0 in ct.columns else 0
                sub_total = npl_1 + npl_0
                rate = (npl_1 / sub_total) * 100 if sub_total > 0 else 0

                # 2x2 table vs the rest
                c = ct[1].sum() - npl_1
                d = ct[0].sum() - npl_0
                if (npl_0 * c) > 0:
                    or_val = (npl_1 * d) / (npl_0 * c)
                    se = np.sqrt(1/npl_1 + 1/npl_0 + 1/c + 1/d)
                    ci_l = np.exp(np.log(or_val) - 1.96 * se)
                    ci_u = np.exp(np.log(or_val) + 1.96 * se)
                else:
                    or_val, ci_l, ci_u = np.nan, np.nan, np.nan

                bivariate_rows.append({
                    "Faktor Risiko": factor_label,
                    "Kategori": str(cat),
                    "N Total": sub_total,
                    "N Macet": npl_1,
                    "NPL Rate (%)": round(rate, 2),
                    "Chi-Square (df)": f"{chi2:.1f} ({dof})",
                    "p-value": f"{p:.4e}",
                    "Cramer's V": round(cramer_v, 3),
                    "Crude OR": round(or_val, 3) if not np.isnan(or_val) else "-",
                    "95% CI OR": f"[{ci_l:.3f}, {ci_u:.3f}]" if not np.isnan(ci_l) else "-"
                })

    t11_df = pd.DataFrame(bivariate_rows)
    t11_df.to_csv(TABEL11_CSV, index=False)
    print(f"[Tabel] Tabel 11 (Analisis Bivariat Lengkap) disimpan: {TABEL11_CSV.name}")
    return t11_df
