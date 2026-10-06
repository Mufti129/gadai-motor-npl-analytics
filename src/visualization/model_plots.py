"""
Model Evaluation Visualizations Module (Gambar 5 - 6).
Generates ROC Curves and Probability Calibration Curves for model discrimination and reliability.
"""

from pathlib import Path
from typing import Dict, Any
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.calibration import calibration_curve

from src.config import FIGURES_OUTPUT_DIR
from src.visualization.style import (
    set_publication_style,
    PRIMARY_BLUE,
    DANGER_RED,
    SUCCESS_GREEN,
    WARNING_ORANGE
)


def plot_fig5_roc_curves(models: Dict[str, Any], df: pd.DataFrame) -> Path:
    """
    Gambar 5: Perbandingan Kurva ROC (Receiver Operating Characteristic)
    Model 1 (Core), Model 2 (Core + LTV_MAX), dan Model 4 (Full Enhanced Model).
    """
    set_publication_style()
    FIGURES_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_OUTPUT_DIR / "fig5_roc_curves_comparison.png"

    y_true = df["NPL_clean"].values

    models_to_plot = [
        ("Model 1 (Core Risk Model)", "#7f8c8d", "--", 1.8),
        ("Model 2 (Core + LTV_MAX)", PRIMARY_BLUE, "-", 2.2),
        ("Model 4 (Full Enhanced Model)", DANGER_RED, "-", 2.5)
    ]

    fig, ax = plt.subplots(figsize=(8, 7))

    # Diagonal line (random guess)
    ax.plot([0, 1], [0, 1], color="#bdc3c7", linestyle=":", linewidth=1.5, label="Baseline Acak (AUC = 0.5000)")

    for name, color, style, lw in models_to_plot:
        # Check direct name or trimmed name
        m = models.get(name) or models.get(name.replace(" Model", ""))
        if m is not None:
            y_pred = m.predict(df)
            fpr, tpr, _ = roc_curve(y_true, y_pred)
            auc = roc_auc_score(y_true, y_pred)
            ax.plot(fpr, tpr, color=color, linestyle=style, linewidth=lw,
                    label=f"{name.replace(' Model)', ')')} (AUC = {auc:.4f})")

    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("False Positive Rate (1 - Specificity)", fontsize=11, weight="bold")
    ax.set_ylabel("True Positive Rate (Sensitivity / Recall)", fontsize=11, weight="bold")
    ax.set_title("Gambar 5: Perbandingan Kurva ROC Antar Model Regresi Logistik\n(Evaluasi Kemampuan Diskriminasi Risiko Kredit)",
                 fontsize=13, weight="bold", pad=15)
    ax.legend(loc="lower right", fontsize=10, frameon=True)

    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"[Visualisasi] Gambar 5 disimpan: {out_path.name}")
    return out_path


def plot_fig6_calibration_curves(models: Dict[str, Any], df: pd.DataFrame) -> Path:
    """
    Gambar 6: Kurva Kalibrasi Probabilitas Prediksi Risiko vs Kejadian Aktual.
    Menampilkan perbandingan kalibrasi Model 1, Model 2, dan Model 4.
    """
    set_publication_style()
    FIGURES_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_OUTPUT_DIR / "fig6_calibration_curves.png"

    y_true = df["NPL_clean"].values
    fig, ax = plt.subplots(figsize=(8, 7))

    # Skala realistis risiko kredit ritel (Prevalensi NPL = 6,91%, max decile ~15%)
    max_axis = 0.20
    ax.plot([0, max_axis], [0, max_axis], color="#7f8c8d", linestyle=":", linewidth=1.8, label="Kalibrasi Sempurna (y = x)")

    # Garis rata-rata NPL nasional
    ax.axvline(0.0691, color="#e2e8f0", linestyle="--", linewidth=1.0)
    ax.axhline(0.0691, color="#e2e8f0", linestyle="--", linewidth=1.0)

    models_to_plot = [
        ("Model 1 (Core Risk Model)", "#7f8c8d", "--^", "Kalibrasi Model 1 (Core)"),
        ("Model 2 (Core + LTV_MAX)", PRIMARY_BLUE, "-o", "Kalibrasi Model 2 (+ LTV_MAX)"),
        ("Model 4 (Full Enhanced Model)", DANGER_RED, "-s", "Kalibrasi Model 4 (+ Repeat Borrower)")
    ]

    for name, color, mark, label_display in models_to_plot:
        m = models.get(name) or models.get(name.replace(" Model", ""))
        if m is not None:
            y_pred = m.predict(df)
            prob_true, prob_pred = calibration_curve(y_true, y_pred, n_bins=10, strategy="quantile")
            ax.plot(prob_pred, prob_true, mark, color=color, linewidth=2.0, markersize=6.5, label=label_display)

    ax.set_xlim([0.0, max_axis])
    ax.set_ylim([0.0, max_axis])
    ax.set_xlabel("Rata-rata Probabilitas Prediksi Risiko (Predicted Risk)", fontsize=11, weight="bold")
    ax.set_ylabel("Proporsi Aktual Kredit Macet (Observed NPL)", fontsize=11, weight="bold")
    ax.set_title("Gambar 6: Kurva Kalibrasi Keandalan Probabilitas Risiko (Calibration Curve)\n(Evaluasi Akurasi Probabilitas per 10 Desil Transaksi)",
                 fontsize=13, weight="bold", pad=15)
    
    # Anotasi penjelasan desil empiris
    ax.annotate(
        "Rata-rata Prevalensi NPL Portofolio = 6,91%\n(10 Desil Populasi N = 139.493)",
        xy=(0.0691, 0.0691), xytext=(0.09, 0.035),
        arrowprops=dict(facecolor="#475569", arrowstyle="->", lw=1.2),
        fontsize=9, weight="semibold", color="#334155",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#f8fafc", edgecolor="#cbd5e1", alpha=0.9)
    )

    ax.legend(loc="upper left", fontsize=9.5, frameon=True)

    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"[Visualisasi] Gambar 6 disimpan: {out_path.name}")
    return out_path
