"""
Main Entrypoint Script for Hierarchical Logistic Regression & Econometric Analysis.
Estimates Models 0-4, executes diagnostics, tests hypotheses H1-H8,
and generates formal research tables and executive reports.

Usage in Terminal / VS Code:
    python run_analysis.py
"""

import time
import pandas as pd

from src.models.logistic_regression import load_cleaned_dataset, fit_all_models
from src.models.diagnostics import evaluate_models_comparison, compute_vif_diagnostics
from src.models.sensitivity import run_occupation_sensitivity_analysis
from src.models.hypothesis_tester import evaluate_hypotheses
from src.utils.table_exporter import export_all_tables, generate_executive_report


def run_analysis_pipeline():
    print("=" * 75)
    print("  HIERARCHICAL LOGISTIC REGRESSION & RISK MODELING PIPELINE")
    print("  Metodologi: Laporan Design Riset NPL Gadai Kendaraan")
    print("=" * 75)
    t_start = time.time()

    # Step 1: Load Cleaned Dataset
    print("\n[Langkah 1/5] Memuat Dataset Bersih...")
    df = load_cleaned_dataset()
    print(f"  Dataset siap: {len(df):,} baris × {len(df.columns)} kolom.")

    # Step 2: Fit Models 0 - 4 (Target NPL > 30 Hari / Operasional)
    print("\n[Langkah 2/6] Mengestimasi Regresi Logistik Bertingkat (Target NPL > 30 Hari)...")
    models_30, coef_df_30 = fit_all_models(df, target_col="NPL_clean")

    # Step 3: Fit Models 0 - 4 (Target NPL > 90 Hari / Standar OJK)
    print("\n[Langkah 3/6] Mengestimasi Regresi Logistik Bertingkat (Target NPL > 90 Hari / OJK)...")
    models_90, coef_df_90 = fit_all_models(df, target_col="NPL_90")

    # Step 4: Comparative Diagnostics & VIF
    print("\n[Langkah 4/6] Menghitung Metrik Evaluasi Model & Uji Multikolinearitas (VIF)...")
    comp_df_30 = evaluate_models_comparison(models_30, df, target_col="NPL_clean")
    comp_df_90 = evaluate_models_comparison(models_90, df, target_col="NPL_90")
    vif_df = compute_vif_diagnostics(df)

    # Step 5: Sensitivity Analysis on Missing Occupation
    print("\n[Langkah 5/6] Menjalankan Sensitivity Analysis (Subset Pekerjaan)...")
    sens_df, sens_meta = run_occupation_sensitivity_analysis(df)

    # Step 6: Formal Hypotheses Evaluation H1 - H8
    print("\n[Langkah 6/6] Menguji 8 Hipotesis Riset Formal (H1 - H8)...")
    hypotheses = evaluate_hypotheses(models_30)

    # Exporting Outputs
    print("\n[Ekspor] Menyimpan Tabel Statistik & Laporan Narasi Eksekutif...")
    from src.config import MODELS_OUTPUT_DIR
    export_all_tables(comp_df_30, coef_df_30, vif_df, sens_df, hypotheses)
    comp_df_90.to_csv(MODELS_OUTPUT_DIR / "model_comparison_table_npl90.csv", index=False)
    coef_df_90.to_csv(MODELS_OUTPUT_DIR / "model_coefficients_npl90.csv", index=False)
    generate_executive_report(comp_df_30, coef_df_30, vif_df, sens_df, hypotheses, total_rows=len(df))

    # Terminal Executive Display
    print("\n" + "=" * 75)
    print(" RINGKASAN PERBANDINGAN MODEL NPL > 30 HARI (OPERASIONAL):")
    print("=" * 75)
    print(comp_df_30[["Model Name", "Parameters (k)", "AIC", "BIC", "McFadden Pseudo R²", "ROC-AUC", "PR-AUC"]].to_string(index=False))

    print("\n" + "=" * 75)
    print(" RINGKASAN PERBANDINGAN MODEL NPL > 90 HARI (STANDAR OJK):")
    print("=" * 75)
    print(comp_df_90[["Model Name", "Parameters (k)", "AIC", "BIC", "McFadden Pseudo R²", "ROC-AUC", "PR-AUC"]].to_string(index=False))

    print("\n" + "=" * 75)
    print(" ESTIMASI KOEFISIEN & ODDS RATIO MODEL 2 (CORE + LTV_MAX):")
    print("=" * 75)
    m2_display = coef_df_30[coef_df_30["Model"] == "Model 2 (Core + LTV_MAX)"][
        ["Variable", "Coefficient (Beta)", "p-value", "Odds Ratio (OR)", "CI 95% Lower", "CI 95% Upper"]
    ]
    print(m2_display.to_string(index=False))

    total_time = time.time() - t_start
    print("\n" + "=" * 75)
    print(f" PIPELINE ANALISIS SELESAI DALAM {total_time:.2f} DETIK")
    print(" - File Laporan Eksekutif : output/LAPORAN_ANALISIS_STATISTIK.md")
    print(" - Tabel Hasil Statistik   : output/models/ (CSV & JSON)")
    print("=" * 75)


if __name__ == "__main__":
    run_analysis_pipeline()
