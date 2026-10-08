#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate crisp, publication-grade figures optimized for the PDF report layout.
Ensures zero blurry text, zero overlapping labels, and legible fonts at 300 DPI.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.calibration import calibration_curve
import statsmodels.formula.api as smf

OUTPUT_DIR = Path("output")
FIGURES_DIR = OUTPUT_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Color constants
NAVY = "#0F2C59"
ROYAL_BLUE = "#1E40AF"
ACCENT_BLUE = "#3B82F6"
CRIMSON = "#DC2626"
GREEN = "#059669"
AMBER = "#D97706"
SLATE_DARK = "#1E293B"
SLATE_MUTED = "#64748B"
BORDER_GRAY = "#CBD5E1"
BG_LIGHT = "#F8FAFC"

def setup_mpl_style():
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "DejaVu Sans", "Arial"],
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "axes.edgecolor": BORDER_GRAY,
        "axes.linewidth": 0.8,
        "grid.color": "#E2E8F0",
        "grid.linestyle": "--",
        "grid.alpha": 0.6,
        "axes.labelcolor": SLATE_DARK,
        "xtick.color": SLATE_DARK,
        "ytick.color": SLATE_DARK,
    })

def generate_all():
    setup_mpl_style()
    print("Loading data...")
    df = pd.read_csv(OUTPUT_DIR / "data_cleaned.csv")
    total = len(df)
    n_macet = int(df["NPL_clean"].sum())
    n_lancar = total - n_macet
    pct_macet = (n_macet / total) * 100
    pct_lancar = (n_lancar / total) * 100

    # -------------------------------------------------------------
    # 1. FIG 1: DONUT CHART NPL (3.8 x 2.6 in)
    # -------------------------------------------------------------
    print("Generating Fig 1: NPL Distribution...")
    fig, ax = plt.subplots(figsize=(3.8, 2.6), dpi=300)
    sizes = [n_lancar, n_macet]
    colors = [NAVY, CRIMSON]
    explode = (0, 0.08)

    wedges, texts, autotexts = ax.pie(
        sizes,
        explode=explode,
        colors=colors,
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.76,
        wedgeprops=dict(width=0.42, edgecolor="white", linewidth=2)
    )

    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(8.5)
        at.set_weight("bold")

    # Center label
    ax.text(0, 0.08, f"TOTAL", ha="center", va="center", fontsize=8.5, weight="bold", color=SLATE_MUTED)
    ax.text(0, -0.06, f"{total:,}".replace(",", "."), ha="center", va="center", fontsize=10.5, weight="bold", color=NAVY)
    ax.text(0, -0.20, "Kontrak", ha="center", va="center", fontsize=7.5, color=SLATE_MUTED)

    # Legend at bottom
    ax.legend(
        [wedges[0], wedges[1]],
        [f"Lancar: {n_lancar:,} ({pct_lancar:.2f}%)".replace(",", "."),
         f"Macet: {n_macet:,} ({pct_macet:.2f}%)".replace(",", ".")],
        loc="lower center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=1,
        fontsize=7.5,
        frameon=False
    )
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig1_npl_distribution.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 2. FIG 2: NPL BY CATEGORIES (7.2 x 3.6 in)
    # -------------------------------------------------------------
    print("Generating Fig 2: NPL by Categories...")
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 3.6), dpi=300)

    def draw_panel(ax, col, title, bar_color, custom_labels=None):
        agg = df.groupby(col)["NPL_clean"].agg(["count", "mean"]).reset_index()
        agg["npl_pct"] = agg["mean"] * 100
        agg = agg.sort_values("npl_pct", ascending=True)

        y_labels = agg[col].astype(str)
        if custom_labels:
            y_labels = [custom_labels.get(val, val) for val in y_labels]

        bars = ax.barh(y_labels, agg["npl_pct"], color=bar_color, height=0.52, edgecolor="none")
        ax.set_title(title, fontsize=8.5, weight="bold", color=NAVY, pad=5)
        ax.set_xlabel("Tingkat NPL (%)", fontsize=7.5)
        ax.tick_params(axis="both", labelsize=7.5)
        ax.axvline(6.91, color=CRIMSON, linestyle="--", linewidth=1.0, alpha=0.8)

        max_val = max(agg["npl_pct"])
        ax.set_xlim(0, max_val * 1.35)

        for bar in bars:
            w = bar.get_width()
            ax.text(w + 0.15, bar.get_y() + bar.get_height() / 2, f"{w:.2f}%",
                    va="center", ha="left", fontsize=7.5, weight="bold", color=SLATE_DARK)

    # Panel A: STNK
    draw_panel(axes[0, 0], "kondisi_stnk", "A. Kepemilikan STNK", ROYAL_BLUE)
    # Panel B: Repeat Borrower
    draw_panel(axes[0, 1], "is_repeat_borrower", "B. Riwayat Nasabah", GREEN,
               {"0": "Nasabah Baru (0)", "1": "Repeat Borrower (1)", 0: "Nasabah Baru (0)", 1: "Repeat Borrower (1)"})
    # Panel C: Merk Motor
    draw_panel(axes[1, 0], "merk_group", "C. Merk Kendaraan Jaminan", "#8B5CF6")
    # Panel D: Skala Pinjaman
    draw_panel(axes[1, 1], "skala_pinjaman_std", "D. Skala Pinjaman Pokok Awal", AMBER)

    fig.suptitle("Perbandingan Tingkat Kredit Macet (NPL Rate %) Berdasarkan Kategori Risiko Portofolio (Garis Merah: Baseline 6,91%)",
                 fontsize=9.0, weight="bold", color=NAVY, y=1.01)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig2_npl_rate_by_categories.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 3. FIG 4: SIMPSON'S PARADOX (7.2 x 2.7 in)
    # -------------------------------------------------------------
    print("Generating Fig 4: Simpson's Paradox...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.7), dpi=300)

    # Panel 1: Aggregated
    zones = ["<=35%", "36%-40%", "41%-50%"]
    agg_ltv = df.groupby("zona_ltv_std")["NPL_clean"].mean() * 100
    vals1 = [agg_ltv.get(z, 0) for z in zones]
    bar_cols = [ROYAL_BLUE, AMBER, GREEN]
    bars1 = ax1.bar(zones, vals1, color=bar_cols, width=0.48, edgecolor="none")
    ax1.set_title("A. Tingkat NPL Agregat per Zona LTV\n(Tampak Anomali: LTV 41-50% Lebih Rendah)", fontsize=8.0, weight="bold", color=NAVY)
    ax1.set_ylabel("Tingkat NPL (%)", fontsize=7.5)
    ax1.tick_params(axis="both", labelsize=7.5)
    ax1.set_ylim(0, 10.5)
    ax1.axhline(6.91, color=CRIMSON, linestyle="--", linewidth=0.9, alpha=0.7)

    for b in bars1:
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width()/2, h + 0.25, f"{h:.2f}%",
                 ha="center", fontsize=8.0, weight="bold", color=SLATE_DARK)

    # Panel 2: Stratified by STNK
    pt = df.pivot_table(index="zona_ltv_std", columns="kondisi_stnk", values="NPL_clean", aggfunc="mean") * 100
    pt = pt.reindex(zones)
    x = np.arange(len(zones))
    w_bar = 0.30

    b2_1 = ax2.bar(x - w_bar/2, pt["A/N SENDIRI"], width=w_bar, label="STNK A/N Sendiri", color=ROYAL_BLUE)
    b2_2 = ax2.bar(x + w_bar/2, pt["A/N ORANG LAIN"], width=w_bar, label="STNK A/N Orang Lain", color=CRIMSON)

    ax2.set_title("B. Stratifikasi per Kepemilikan STNK\n(Paradoks Hilang: STNK Orang Lain Konsisten Tinggi)", fontsize=8.0, weight="bold", color=NAVY)
    ax2.set_ylabel("Tingkat NPL (%)", fontsize=7.5)
    ax2.set_xticks(x)
    ax2.set_xticklabels(zones, fontsize=7.5)
    ax2.tick_params(axis="both", labelsize=7.5)
    ax2.set_ylim(0, 11.5)
    ax2.legend(fontsize=7.2, frameon=True, loc="upper left")

    for b in list(b2_1) + list(b2_2):
        h = b.get_height()
        ax2.text(b.get_x() + b.get_width()/2, h + 0.25, f"{h:.2f}%",
                 ha="center", fontsize=7.2, weight="bold", color=SLATE_DARK)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig4_simpsons_paradox_ltv_stnk.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 4. FIG 3: VEHICLE AGE VS NPL (7.2 x 2.8 in)
    # -------------------------------------------------------------
    print("Generating Fig 3: Vehicle Age vs NPL...")
    age_agg = df.groupby("usia_kendaraan_thn")["NPL_clean"].agg(["count", "mean"]).reset_index()
    age_agg = age_agg[age_agg["count"] >= 50].sort_values("usia_kendaraan_thn")
    age_agg["npl_pct"] = age_agg["mean"] * 100

    fig, ax1 = plt.subplots(figsize=(7.2, 2.8), dpi=300)

    # Volume bar
    ax1.bar(age_agg["usia_kendaraan_thn"], age_agg["count"], color="#CBD5E1", alpha=0.55, width=0.55, label="Volume Transaksi")
    ax1.set_xlabel("Usia Kendaraan Bermotor (Tahun)", fontsize=8.0, weight="bold", color=NAVY)
    ax1.set_ylabel("Volume Transaksi Kontrak", fontsize=7.5, color=SLATE_MUTED)
    ax1.tick_params(axis="y", labelsize=7.0, labelcolor=SLATE_MUTED)
    ax1.tick_params(axis="x", labelsize=7.5)
    ax1.set_xticks(age_agg["usia_kendaraan_thn"])

    # Line for NPL rate
    ax2 = ax1.twinx()
    ax2.plot(age_agg["usia_kendaraan_thn"], age_agg["npl_pct"], marker="o", color=CRIMSON,
             linewidth=2.0, markersize=5.0, label="Tingkat NPL (%)")
    ax2.set_ylabel("Tingkat NPL (%)", fontsize=7.5, weight="bold", color=CRIMSON)
    ax2.tick_params(axis="y", labelsize=7.0, labelcolor=CRIMSON)
    ax2.set_ylim(4.0, 10.5)
    ax2.grid(False)

    for _, row in age_agg.iterrows():
        y_val = row["npl_pct"]
        ax2.annotate(f"{y_val:.1f}%",
                     (row["usia_kendaraan_thn"], y_val),
                     textcoords="offset points", xytext=(0, 6), ha="center",
                     fontsize=7.2, weight="bold", color=CRIMSON)

    ax1.set_title("Hubungan Usia Kendaraan dengan Tingkat Kredit Macet (NPL Rate %)\n(Kurva Risiko Monoton Naik Seiring Penuaan & Depresiasi Agunan)",
                  fontsize=8.5, weight="bold", color=NAVY, pad=8)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=7.2, frameon=True)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig3_vehicle_age_vs_npl.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 5 & 6. FIG 5 (ROC) & FIG 6 (CALIBRATION) (3.5 x 2.8 in each)
    # -------------------------------------------------------------
    print("Fitting models for ROC & Calibration...")
    f1 = ("NPL_clean ~ C(kondisi_stnk, Treatment(reference='A/N SENDIRI')) + "
          "C(pajak_status, Treatment(reference='Pajak Tidak Aktif')) + "
          "C(merk_group, Treatment(reference='Honda')) + usia_kendaraan_thn + pinjaman_juta")
    f2 = f1 + " + LTV_MAX"
    f4 = f2 + " + is_repeat_borrower"

    m1 = smf.logit(f1, data=df).fit(disp=False)
    m2 = smf.logit(f2, data=df).fit(disp=False)
    m4 = smf.logit(f4, data=df).fit(disp=False)

    y_true = df["NPL_clean"].values

    # Fig 5: ROC Curves
    print("Generating Fig 5: ROC Curves...")
    fig, ax = plt.subplots(figsize=(3.5, 2.8), dpi=300)
    ax.plot([0, 1], [0, 1], color="#94A3B8", linestyle=":", linewidth=1.2, label="Acak (AUC 0,5000)")

    models_info = [
        (m1, "Model 1 (Core)", "#64748B", "--", 1.4),
        (m2, "Model 2 (+LTV)", ROYAL_BLUE, "-", 1.8),
        (m4, "Model 4 (Champion)", CRIMSON, "-", 2.0)
    ]

    for m, name, col_l, ls, lw in models_info:
        y_pred = m.predict(df)
        fpr, tpr, _ = roc_curve(y_true, y_pred)
        auc = roc_auc_score(y_true, y_pred)
        ax.plot(fpr, tpr, color=col_l, linestyle=ls, linewidth=lw,
                label=f"{name}: AUC {auc:.4f}")

    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("False Positive Rate", fontsize=7.5)
    ax.set_ylabel("True Positive Rate", fontsize=7.5)
    ax.tick_params(axis="both", labelsize=7.0)
    ax.set_title("Komparasi Kurva ROC Antar Model\n(Evaluasi Daya Diskriminasi)", fontsize=8.0, weight="bold", color=NAVY)
    ax.legend(loc="lower right", fontsize=6.8, frameon=True)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig5_roc_curves_comparison.png", dpi=300)
    plt.close()

    # Fig 6: Calibration Curves
    print("Generating Fig 6: Calibration Curves...")
    fig, ax = plt.subplots(figsize=(3.5, 2.8), dpi=300)
    max_axis = 0.20
    ax.plot([0, max_axis], [0, max_axis], color="#94A3B8", linestyle=":", linewidth=1.4, label="Ideal (y = x)")
    ax.axvline(0.0691, color="#E2E8F0", linestyle="--", linewidth=0.8)
    ax.axhline(0.0691, color="#E2E8F0", linestyle="--", linewidth=0.8)

    cal_models = [
        (m1, "Model 1", "#64748B", "--^", 1.2, 4.0),
        (m2, "Model 2", ROYAL_BLUE, "-o", 1.5, 4.5),
        (m4, "Model 4", CRIMSON, "-s", 1.8, 5.0)
    ]

    for m, name, col_l, ls, lw, ms in cal_models:
        y_pred = m.predict(df)
        prob_true, prob_pred = calibration_curve(y_true, y_pred, n_bins=10, strategy="quantile")
        ax.plot(prob_pred, prob_true, ls, color=col_l, linewidth=lw, markersize=ms, label=f"Kalibrasi {name}")

    ax.set_xlim([0.0, max_axis])
    ax.set_ylim([0.0, max_axis])
    ax.set_xlabel("Rata-rata Prediksi Risiko", fontsize=7.5)
    ax.set_ylabel("Proporsi Aktual Macet", fontsize=7.5)
    ax.tick_params(axis="both", labelsize=7.0)
    ax.set_title("Kurva Kalibrasi Reliabilitas Probabilitas\n(10 Desil Populasi N = 139.493)", fontsize=8.0, weight="bold", color=NAVY)
    ax.legend(loc="upper left", fontsize=6.8, frameon=True)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig6_calibration_curves.png", dpi=300)
    plt.close()

    print("All figures successfully regenerated with crystal-clear 300 DPI layout!")

if __name__ == "__main__":
    generate_all()
