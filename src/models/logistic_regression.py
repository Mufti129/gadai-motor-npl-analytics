"""
Hierarchical Logistic Regression Estimation Module.
Fits Model 0 (Null), Model 1 (Core), Model 2 (+ LTV_MAX), Model 3 (+ Zona LTV),
and Model 4 (+ Repeat Borrower) using statsmodels.
"""

import pickle
import time
from typing import Dict, Tuple, Any
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

from src.config import (
    CLEANED_DATA_PKL,
    CLEANED_DATA_CSV,
    FORMULA_MODEL_0,
    FORMULA_MODEL_1,
    FORMULA_MODEL_2,
    FORMULA_MODEL_3,
    FORMULA_MODEL_4
)


def load_cleaned_dataset(prefer_csv: bool = True) -> pd.DataFrame:
    """
    Memuat dataset bersih hasil cleansing langsung dari output/data_cleaned.csv.
    Dataset ini merupakan data riil hasil pembersihan dari file raw 'request Mufti_gadaiHP.xlsx'.
    """
    if prefer_csv and CLEANED_DATA_CSV.exists():
        return pd.read_csv(CLEANED_DATA_CSV, low_memory=False)
    elif CLEANED_DATA_PKL.exists():
        with open(CLEANED_DATA_PKL, "rb") as f:
            return pickle.load(f)
    elif CLEANED_DATA_CSV.exists():
        return pd.read_csv(CLEANED_DATA_CSV, low_memory=False)
    else:
        raise FileNotFoundError(
            f"Dataset bersih tidak ditemukan di {CLEANED_DATA_CSV}. Jalankan pipeline cleansing terlebih dahulu!"
        )


def extract_coefficients(model_fit: Any, model_name: str) -> pd.DataFrame:
    """
    Extract parameter estimates, standard errors, z-scores, p-values,
    Odds Ratios, and 95% Confidence Intervals.
    """
    params = model_fit.params
    bse = model_fit.bse
    tvalues = model_fit.tvalues
    pvalues = model_fit.pvalues
    conf_int = model_fit.conf_int()

    df_coef = pd.DataFrame({
        "Model": model_name,
        "Variable": params.index,
        "Coefficient (Beta)": params.values,
        "Standard Error": bse.values,
        "z-statistic": tvalues.values,
        "p-value": pvalues.values,
        "Odds Ratio (OR)": np.exp(params.values),
        "CI 95% Lower": np.exp(conf_int[0].values),
        "CI 95% Upper": np.exp(conf_int[1].values)
    })
    return df_coef


def fit_all_models(df: pd.DataFrame) -> Tuple[Dict[str, Any], pd.DataFrame]:
    """
    Fit hierarchical models Model 0 through Model 4.

    Returns:
    --------
    models : dict of fitted statsmodels objects
    all_coefs_df : concatenated DataFrame of all model coefficients and ORs
    """
    models = {}
    coef_list = []

    model_specs = [
        ("Model 0 (Null Model)", FORMULA_MODEL_0),
        ("Model 1 (Core Risk Model)", FORMULA_MODEL_1),
        ("Model 2 (Core + LTV_MAX)", FORMULA_MODEL_2),
        ("Model 3 (Core + Zona LTV)", FORMULA_MODEL_3),
        ("Model 4 (Full Enhanced Model)", FORMULA_MODEL_4)
    ]

    print("\n[Modeling] Memulai estimasi regresi logistik bertingkat (statsmodels)...")
    for name, formula in model_specs:
        t0 = time.time()
        print(f"  -> Mengestimasi {name} ...")
        m = smf.logit(formula, data=df).fit(disp=False)
        models[name] = m
        coef_df = extract_coefficients(m, name)
        coef_list.append(coef_df)
        print(f"     Selesai dalam {time.time() - t0:.2f} detik. Log-Likelihood: {m.llf:.2f}")

    all_coefs_df = pd.concat(coef_list, ignore_index=True)
    return models, all_coefs_df
