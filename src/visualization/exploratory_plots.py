"""
Exploratory Data Visualizations Module (Gambar 1 - 4).
Generates publication-quality figures representing outcome distribution,
categorical risk rates, vehicle age curves, and Simpson's Paradox decomposition.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.config import FIGURES_OUTPUT_DIR
from src.visualization.style import (
    set_publication_style,
    PRIMARY_BLUE,
    DANGER_RED,
    SUCCESS_GREEN,
    PALETTE_NPL
)


def plot_fig1_npl_distribution(df: pd.DataFrame) -> Path:
    """
    Gambar 1: Distribusi Status Kredit Macet (NPL) Keseluruhan.
    Donut Chart + Summary Bar.
    """
    set_publication_style()
    FIGURES_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_OUTPUT_DIR / "fig1_npl_distribution.png"

    total = len(df)
    npl_count = int(df["NPL_clean"].sum())
    lancar_count = total - npl_count
    pct_npl = (npl_count / total) * 100
    pct_lancar = (lancar_count / total) * 100

    fig, ax = plt.subplots(figsize=(8, 6))

    labels = [f"Kredit Lancar (Non-NPL)\n{lancar_count:,} ({pct_lancar:.2f}%)",
              f"Kredit Macet (NPL)\n{npl_count:,} ({pct_npl:.2f}%)"]
    sizes = [lancar_count, npl_count]
    colors = [PALETTE_NPL[0], PALETTE_NPL[1]]
    explode = (0, 0.08)

    wedges, texts, autotexts = ax.pie(
        sizes,
        explode=explode,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.8,
        wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2)
    )

    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(12)
        at.set_weight("bold")

    for t in texts:
        t.set_fontsize(11)
        t.set_weight("semibold")

    # Center circle annotation
    ax.text(0, 0, f"TOTAL\n{total:,}\nTransaksi", ha="center", va="center",
            fontsize=13, weight="bold", color="#2c3e50")

    ax.set_title("Gambar 1: Distribusi Status Kredit Macet (NPL)\nPada Pembiayaan Gadai Kendaraan (Tahun 2025)",
                 fontsize=14, weight="bold", pad=20)

    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"[Visualisasi] Gambar 1 disimpan: {out_path.name}")
    return out_path


def plot_fig2_npl_by_categories(df: pd.DataFrame) -> Path:
    """
    Gambar 2: NPL Rate (%) Berdasarkan Kategori Risiko Kunci.
    Multi-panel horizontal comparison bar charts.
    """
    set_publication_style()
    FIGURES_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_OUTPUT_DIR / "fig2_npl_rate_by_categories.png"

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    def draw_bar(ax, group_col, title, palette_col="#2b5c8f"):
        agg = df.groupby(group_col)["NPL_clean"].agg(["count", "mean"]).reset_index()
        agg["npl_rate_pct"] = agg["mean"] * 100
        agg = agg.sort_values("npl_rate_pct", ascending=True)

        bars = ax.barh(agg[group_col].astype(str), agg["npl_rate_pct"], color=palette_col, height=0.55, edgecolor="none")
        ax.set_title(title, fontsize=12, weight="bold", pad=10)
        ax.set_xlabel("Tingkat NPL (%)", fontsize=10)
        ax.axvline(6.91, color=DANGER_RED, linestyle="--", linewidth=1.2, alpha=0.8, label="Rata-rata Nasional (6.91%)")

        for bar in bars:
            w = bar.get_width()
            ax.text(w + 0.15, bar.get_y() + bar.get_height() / 2, f"{w:.2f}%",
                    va="center", ha="left", fontsize=9.5, weight="bold", color="#2c3e50")
        
        ax.set_xlim(0, max(agg["npl_rate_pct"]) * 1.25)
        ax.legend(loc="lower right", fontsize=8.5)

    # Panel A: STNK
    draw_bar(axes[0, 0], "kondisi_stnk", "A. Kepemilikan STNK (kondisi_name)", "#34495e")
    # Panel B: Repeat Borrower
    draw_bar(axes[0, 1], "is_repeat_borrower", "B. Riwayat Nasabah (0=Baru, 1=Repeat)", "#2980b9")
    # Panel C: Merk Motor
    draw_bar(axes[1, 0], "merk_group", "C. Merk Kendaraan Jaminan", "#8e44ad")
    # Panel D: Skala Pinjaman
    draw_bar(axes[1, 1], "skala_pinjaman_std", "D. Skala Pinjaman Pokok Awal", "#d35400")

    fig.suptitle("Gambar 2: Perbandingan Tingkat Kredit Macet (NPL Rate %) Berdasarkan Kategori Risiko",
                 fontsize=15, weight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"[Visualisasi] Gambar 2 disimpan: {out_path.name}")
    return out_path


def plot_fig3_vehicle_age_curve(df: pd.DataFrame) -> Path:
    """
    Gambar 3: Kurva Hubungan Usia Kendaraan dengan Tingkat NPL.
    Empirical NPL Rate by Vehicle Age (0-13 years).
    """
    set_publication_style()
    FIGURES_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_OUTPUT_DIR / "fig3_vehicle_age_vs_npl.png"

    age_agg = df.groupby("usia_kendaraan_thn")["NPL_clean"].agg(["count", "mean"]).reset_index()
    age_agg = age_agg[age_agg["count"] >= 50].sort_values("usia_kendaraan_thn")
    age_agg["npl_rate_pct"] = age_agg["mean"] * 100

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Bar for volume
    color_bar = "#bdc3c7"
    ax1.bar(age_agg["usia_kendaraan_thn"], age_agg["count"], color=color_bar, alpha=0.4, width=0.6, label="Volume Pinjaman")
    ax1.set_xlabel("Usia Kendaraan (Tahun)", fontsize=11, weight="bold")
    ax1.set_ylabel("Volume Transaksi", fontsize=11, color="#7f8c8d")
    ax1.tick_params(axis="y", labelcolor="#7f8c8d")

    # Line for NPL Rate
    ax2 = ax1.twinx()
    ax2.plot(age_agg["usia_kendaraan_thn"], age_agg["npl_rate_pct"], marker="o", color=DANGER_RED,
             linewidth=2.5, markersize=7, label="Tingkat NPL (%)")
    ax2.set_ylabel("Tingkat NPL (%)", fontsize=11, weight="bold", color=DANGER_RED)
    ax2.tick_params(axis="y", labelcolor=DANGER_RED)
    ax2.grid(False)

    for _, row in age_agg.iterrows():
        ax2.annotate(f"{row['npl_rate_pct']:.1f}%",
                     (row["usia_kendaraan_thn"], row["npl_rate_pct"]),
                     textcoords="offset points", xytext=(0, 9), ha="center",
                     fontsize=9, weight="bold", color=DANGER_RED)

    plt.title("Gambar 3: Hubungan Usia Kendaraan dengan Tingkat Kredit Macet (NPL Rate)\n(Kurva Risiko Monoton Naik)",
              fontsize=13, weight="bold", pad=15)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"[Visualisasi] Gambar 3 disimpan: {out_path.name}")
    return out_path


def plot_fig4_simpsons_paradox(df: pd.DataFrame) -> Path:
    """
    Gambar 4: Visualisasi Dekomposisi Simpson's Paradox pada Zona LTV vs Kepemilikan STNK.
    """
    set_publication_style()
    FIGURES_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_OUTPUT_DIR / "fig4_simpsons_paradox_ltv_stnk.png"

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Panel 1: Aggregated view (Paradoxical)
    agg_ltv = df.groupby("zona_ltv_std")["NPL_clean"].mean() * 100
    zones = ["<=35%", "36%-40%", "41%-50%"]
    vals = [agg_ltv.get(z, 0) for z in zones]
    bars1 = ax1.bar(zones, vals, color=["#e74c3c", "#e67e22", "#27ae60"], width=0.5, edgecolor="none")
    ax1.set_title("A. Tingkat NPL Agregat per Zona LTV\n(Tampak Paradoks: LTV Tinggi NPL Lebih Rendah)", fontsize=11, weight="bold")
    ax1.set_ylabel("Tingkat NPL (%)", fontsize=10)
    ax1.set_ylim(0, 10)
    for b in bars1:
        ax1.text(b.get_x() + b.get_width()/2, b.get_height() + 0.2, f"{b.get_height():.2f}%",
                 ha="center", fontsize=10, weight="bold")

    # Panel 2: Stratified view by STNK
    pt = df.pivot_table(index="zona_ltv_std", columns="kondisi_stnk", values="NPL_clean", aggfunc="mean") * 100
    pt = pt.reindex(zones)
    pt.plot(kind="bar", ax=ax2, color=["#c0392b", "#2980b9"], width=0.6, edgecolor="none")
    ax2.set_title("B. Stratifikasi Berdasarkan Kepemilikan STNK\n(Paradoks Hilang: STNK A/N Orang Lain Konsisten Tinggi)", fontsize=11, weight="bold")
    ax2.set_ylabel("Tingkat NPL (%)", fontsize=10)
    ax2.set_xlabel("Zona LTV", fontsize=10)
    ax2.set_ylim(0, 11)
    ax2.legend(title="Kepemilikan STNK", fontsize=9)
    plt.xticks(rotation=0)

    fig.suptitle("Gambar 4: Analisis Simpson's Paradox — Interaksi Antara Zona LTV dan Kepemilikan STNK",
                 fontsize=14, weight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"[Visualisasi] Gambar 4 disimpan: {out_path.name}")
    return out_path
