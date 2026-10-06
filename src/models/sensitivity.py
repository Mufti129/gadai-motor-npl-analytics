"""
Sensitivity Analysis Module.
Tests coefficient stability across missing-data subsets (specifically the 82% missing pekerjaan)
to detect potential selection bias or model instability.
"""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from src.config import FORMULA_MODEL_2, FORMULA_JOB_SUBSET


def run_occupation_sensitivity_analysis(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Compare core parameter estimates between:
    1. Full Dataset (N = 139,493) without pekerjaan
    2. Occupation Subset (N ~ 24,857) without pekerjaan
    3. Occupation Subset (N ~ 24,857) WITH pekerjaan
    """
    print("\n[Sensitivity] Menjalankan Sensitivity Analysis pada subset data pekerjaan...")

    # Filter subset with recorded occupation
    sub_df = df[df["pekerjaan_group"] != "TIDAK ISI"].copy()
    n_full = len(df)
    n_sub = len(sub_df)

    # 1. Full Dataset Model 2
    m_full = smf.logit(FORMULA_MODEL_2, data=df).fit(disp=False)

    # 2. Subset Model WITHOUT pekerjaan
    m_sub_base = smf.logit(FORMULA_MODEL_2, data=sub_df).fit(disp=False)

    # 3. Subset Model WITH pekerjaan
    m_sub_job = smf.logit(FORMULA_JOB_SUBSET, data=sub_df).fit(disp=False)

    # Compare core variables
    core_vars = [
        "C(kondisi_stnk, Treatment(reference='A/N SENDIRI'))[T.A/N ORANG LAIN]",
        "usia_kendaraan_thn",
        "pinjaman_juta",
        "LTV_MAX"
    ]

    clean_var_names = {
        "C(kondisi_stnk, Treatment(reference='A/N SENDIRI'))[T.A/N ORANG LAIN]": "STNK A/N Orang Lain",
        "usia_kendaraan_thn": "Usia Kendaraan (thn)",
        "pinjaman_juta": "Pinjaman Pokok (Juta Rp)",
        "LTV_MAX": "LTV_MAX"
    }

    comparison_rows = []
    for var in core_vars:
        beta_full = m_full.params.get(var, np.nan)
        or_full = np.exp(beta_full)
        
        beta_sub_base = m_sub_base.params.get(var, np.nan)
        or_sub_base = np.exp(beta_sub_base)

        beta_sub_job = m_sub_job.params.get(var, np.nan)
        or_sub_job = np.exp(beta_sub_job)

        pct_change = ((beta_sub_job - beta_sub_base) / beta_sub_base) * 100 if beta_sub_base != 0 else np.nan

        comparison_rows.append({
            "Variabel Inti": clean_var_names.get(var, var),
            "Full Dataset OR (N=139k)": round(or_full, 3),
            "Subset Tanpa Job OR (N=25k)": round(or_sub_base, 3),
            "Subset DENGAN Job OR (N=25k)": round(or_sub_job, 3),
            "Perubahan Beta (%):": round(pct_change, 2),
            "Stabilitas": "STABIL (|Δ| < 15%)" if abs(pct_change) < 15 else "SENSITIF"
        })

    sens_df = pd.DataFrame(comparison_rows)
    meta = {
        "n_full": n_full,
        "n_subset": n_sub,
        "pct_retained": round((n_sub / n_full) * 100, 2)
    }
    return sens_df, meta
