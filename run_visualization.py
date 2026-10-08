"""
Main Entrypoint Script for Statistical Visualizations & Publication Tables.
Generates Gambar 1 - 6 and Tabel 1, 2, 11 from the Research Design Document.

Usage in Terminal / VS Code:
    python run_visualization.py
"""

import time
import pandas as pd

from src.models.logistic_regression import load_cleaned_dataset, fit_all_models
from src.visualization.exploratory_plots import (
    plot_fig1_npl_distribution,
    plot_fig2_npl_by_categories,
    plot_fig3_vehicle_age_curve,
    plot_fig4_simpsons_paradox
)
from src.visualization.model_plots import (
    plot_fig5_roc_curves,
    plot_fig6_calibration_curves
)
from src.visualization.descriptive_tables import (
    generate_table1_characteristics,
    generate_table2_npl_distribution,
    generate_table11_bivariate_analysis
)


def run_visualization_pipeline():
    print("=" * 75)
    print("  STATISTICAL VISUALIZATIONS & PUBLICATION TABLES PIPELINE")
    print("  Mengacu pada: Laporan Design Riset NPL Gadai Kendaraan (Bab 17)")
    print("=" * 75)
    t_start = time.time()

    # Step 1: Load Cleaned Dataset
    print("\n[Langkah 1/3] Memuat Dataset Bersih...")
    df = load_cleaned_dataset()
    print(f"  Dataset siap: {len(df):,} baris × {len(df.columns)} kolom.")

    # Step 2: Generate Descriptive Tables (Tabel 1, 2, 11)
    print("\n[Langkah 2/3] Membuat Tabel Karakteristik & Bivariat...")
    t1 = generate_table1_characteristics(df)
    t2 = generate_table2_npl_distribution(df)
    t11 = generate_table11_bivariate_analysis(df)

    # Step 3: Generate Figures (Gambar 1 - 6)
    print("\n[Langkah 3/3] Membuat Grafik Statistik Beresolusi Tinggi (300 DPI)...")
    plot_fig1_npl_distribution(df)
    plot_fig2_npl_by_categories(df)
    plot_fig3_vehicle_age_curve(df)
    plot_fig4_simpsons_paradox(df)

    # Fit models for ROC and Calibration curves
    print("\n  -> Mengestimasi model regresi untuk Kurva ROC & Kalibrasi...")
    models, _ = fit_all_models(df)
    plot_fig5_roc_curves(models, df)
    plot_fig6_calibration_curves(models, df)

    total_time = time.time() - t_start
    print("\n" + "=" * 75)
    print(f" PIPELINE VISUALISASI SELESAI DALAM {total_time:.2f} DETIK")
    print(" - Direktori Gambar (PNG 300 DPI) : output/figures/")
    print("   * fig1_npl_distribution.png")
    print("   * fig2_npl_rate_by_categories.png")
    print("   * fig3_vehicle_age_vs_npl.png")
    print("   * fig4_simpsons_paradox_ltv_stnk.png")
    print("   * fig5_roc_curves_comparison.png")
    print("   * fig6_calibration_curves.png")
    print(" - Direktori Tabel Riset (CSV)    : output/tables/")
    print("   * tabel1_karakteristik_transaksi.csv")
    print("   * tabel2_distribusi_npl.csv")
    print("   * tabel11_analisis_bivariat_lengkap.csv")
    print("=" * 75)


if __name__ == "__main__":
    run_visualization_pipeline()
