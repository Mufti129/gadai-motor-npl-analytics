"""
Econometric Diagnostics & Model Evaluation Module.
Computes Likelihood Ratio Tests, AIC/BIC, Pseudo R², ROC-AUC, PR-AUC,
Brier Scores, and Variance Inflation Factors (VIF).
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from statsmodels.stats.outliers_influence import variance_inflation_factor
from patsy import dmatrices

from src.config import FORMULA_MODEL_2, FORMULA_MODEL_4


def evaluate_models_comparison(models: Dict[str, Any], df: pd.DataFrame, target_col: str = "NPL_clean") -> pd.DataFrame:
    """
    Generate comparative performance table across all fitted models.
    Corresponds to Table 16 in Research Design PDF.
    """
    y_true = df[target_col].values if target_col in df.columns else df["NPL_clean"].values
    null_model = models.get("Model 0 (Null Model)")
    ll_null = null_model.llf if null_model else list(models.values())[0].llnull

    comparison_rows = []

    for name, m in models.items():
        # Predictions
        y_pred = m.predict(df)
        
        # Likelihood Ratio vs Null Model
        lr_stat = 2 * (m.llf - ll_null)
        df_diff = m.df_model
        p_lr = stats.chi2.sf(lr_stat, df_diff) if df_diff > 0 else 1.0

        # Performance Metrics
        mcfadden_r2 = 1 - (m.llf / ll_null)
        roc_auc = roc_auc_score(y_true, y_pred) if df_diff > 0 else 0.5
        pr_auc = average_precision_score(y_true, y_pred)
        brier = brier_score_loss(y_true, y_pred)

        comparison_rows.append({
            "Model Name": name,
            "Parameters (k)": int(m.df_model + 1),
            "Log-Likelihood": round(m.llf, 2),
            "LR Stat vs Null": round(lr_stat, 2),
            "LR p-value": p_lr,
            "AIC": round(m.aic, 2),
            "BIC": round(m.bic, 2),
            "McFadden Pseudo R²": round(mcfadden_r2, 4),
            "ROC-AUC": round(roc_auc, 4),
            "PR-AUC": round(pr_auc, 4),
            "Brier Score": round(brier, 5)
        })

    comp_df = pd.DataFrame(comparison_rows)
    return comp_df


def compute_vif_diagnostics(df: pd.DataFrame, formula: str = FORMULA_MODEL_2) -> pd.DataFrame:
    """
    Compute Variance Inflation Factors (VIF) to detect multicollinearity
    among predictors in the specified model formula.
    """
    print(f"\n[Diagnostics] Menghitung Variance Inflation Factor (VIF)...")
    y, X = dmatrices(formula, data=df, return_type="dataframe")

    vif_data = []
    for i in range(X.shape[1]):
        col_name = X.columns[i]
        if col_name == "Intercept":
            continue
        vif_val = variance_inflation_factor(X.values, i)
        vif_data.append({
            "Variable": col_name,
            "VIF": round(vif_val, 4),
            "Status": "Aman (VIF < 5)" if vif_val < 5.0 else "Multikolinearitas Tinggi (VIF >= 5)"
        })

    vif_df = pd.DataFrame(vif_data).sort_values("VIF", ascending=False)
    return vif_df
