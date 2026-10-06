#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================================================
PUSAT GADAI INDONESIA (PGI) — EXECUTIVE STREAMLIT DASHBOARD ANALISIS RISIKO NPL GADAI MOTOR
====================================================================================================
Penulis      : Mukhammad Rekza Mufti (Data Analyst — Divisi Bisnis & Risiko)
Dataset Acuan: 139.493 transaksi kredit valid
Dokumen Acuan: Laporan_Design_Riset_NPL_Gadai_Kendaraan.pdf & README.md
Platform     : Streamlit Community Cloud Ready
====================================================================================================
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==============================================================================
# KONFIGURASI HALAMAN STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="PGI - Smart Underwriting & NPL Risk Analytics",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .kpi-title {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
        margin-top: 4px;
    }
    .badge-a { background-color: #DCFCE7; color: #166534; padding: 4px 12px; border-radius: 9999px; font-weight: 600; }
    .badge-b { background-color: #FEF9C3; color: #854D0E; padding: 4px 12px; border-radius: 9999px; font-weight: 600; }
    .badge-c { background-color: #FFEDD5; color: #9A3412; padding: 4px 12px; border-radius: 9999px; font-weight: 600; }
    .badge-d { background-color: #FFE4E6; color: #9F1239; padding: 4px 12px; border-radius: 9999px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# PARAMETER MODEL & KONFIGURASI KEBIJAKAN
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
FIGURES_DIR = OUTPUT_DIR / "figures"
MODELS_DIR = OUTPUT_DIR / "models"

CONFIG_UNDERWRITING = {
    'TARGET_NPL_CUTOFF_PCT': 5.0,
    'MODERATE_RISK_THRESHOLD_PCT': 7.0,
    'HIGH_RISK_THRESHOLD_PCT': 10.0,
    'SEVERE_RISK_THRESHOLD_PCT': 15.0,
    'MAX_SAFE_LTV_SENDIRI': 0.45,
    'MAX_SAFE_LTV_ORANG_LAIN': 0.35,
    'MAX_SAFE_LTV_PAJAK_MATI': 0.35,
    'MAX_SAFE_LTV_USIA_TUA': 0.35
}

MODEL_2_PARAMS = {
    'Intercept': -3.442634,
    'stnk_orang_lain': 0.536569,
    'pajak_aktif': 0.111880,
    'merk_yamaha': 0.048761,
    'merk_kawasaki': -0.362812,
    'merk_lainnya': -0.050830,
    'usia_thn': 0.088780,
    'pinjaman_juta': 0.360322,
    'ltv_max': -2.328395
}

MODEL_4_PARAMS = {
    'Intercept': -3.109156,
    'stnk_orang_lain': 0.518621,
    'pajak_aktif': 0.089412,
    'merk_yamaha': 0.042180,
    'merk_kawasaki': -0.355120,
    'merk_lainnya': -0.048910,
    'usia_thn': 0.085140,
    'pinjaman_juta': 0.341200,
    'ltv_max': -2.189500,
    'repeat_borrower': -1.265430
}

JOB_RISK_FACTORS = {
    'TIDAK_ISI': {
        'id': 'TIDAK_ISI', 'label': 'Tidak Diketahui / Standar', 'beta': 0.0, 'or': 1.000,
        'cluster': 'Klaster 2: Core Baseline', 'cluster_code': 'CORE', 'ltv_mod': 0.0,
        'policy': 'Skema Standar Cabang (LTV 45% Sendiri / 35% Orang Lain)'
    },
    'KARYAWAN_SWASTA': {
        'id': 'KARYAWAN_SWASTA', 'label': 'Karyawan Swasta', 'beta': 0.0, 'or': 1.000,
        'cluster': 'Klaster 2: Core Baseline', 'cluster_code': 'CORE', 'ltv_mod': 0.0,
        'policy': 'Skema Standar Cabang (Baseline Portofolio)'
    },
    'PNS': {
        'id': 'PNS', 'label': 'PNS / ASN / Pegawai BUMN', 'beta': -0.147041, 'or': 0.863,
        'cluster': 'Klaster 1: Prime / Preferred', 'cluster_code': 'PRIME', 'ltv_mod': 0.05,
        'policy': 'Bonus LTV +5% (Maksimal 50%) & Fast-Track Approval'
    },
    'GURU': {
        'id': 'GURU', 'label': 'Guru / Dosen', 'beta': -0.428912, 'or': 0.651,
        'cluster': 'Klaster 1: Prime / Preferred', 'cluster_code': 'PRIME', 'ltv_mod': 0.05,
        'policy': 'Bonus LTV +5% (Maksimal 50%) & Fast-Track Approval (Profil Paling Aman)'
    },
    'IRT': {
        'id': 'IRT', 'label': 'Ibu Rumah Tangga (IRT)', 'beta': 0.002206, 'or': 1.002,
        'cluster': 'Klaster 2: Core Baseline', 'cluster_code': 'CORE', 'ltv_mod': 0.0,
        'policy': 'Skema Standar (Verifikasi Sumber Nafkah Belanja Keluarga)'
    },
    'BURUH': {
        'id': 'BURUH', 'label': 'Buruh Pabrik / Bangunan', 'beta': 0.017158, 'or': 1.017,
        'cluster': 'Klaster 2: Core Baseline', 'cluster_code': 'CORE', 'ltv_mod': 0.0,
        'policy': 'Skema Standar (Upah Rutin Mingguan/Bulanan)'
    },
    'PEDAGANG': {
        'id': 'PEDAGANG', 'label': 'Pedagang Toko / Kios / Pasar', 'beta': 0.333499, 'or': 1.396,
        'cluster': 'Klaster 3: Arus Kas Volatil', 'cluster_code': 'VOLATILE', 'ltv_mod': -0.05,
        'policy': 'Pengetatan LTV -5% (Maksimal 40%) & Wajib Cek Nota Usaha'
    },
    'WIRASWASTA': {
        'id': 'WIRASWASTA', 'label': 'Wiraswasta / Pengusaha', 'beta': 0.889340, 'or': 2.434,
        'cluster': 'Klaster 3: Arus Kas Volatil', 'cluster_code': 'VOLATILE', 'ltv_mod': -0.05,
        'policy': 'Pengetatan LTV -5% (Maksimal 40%) & Verifikasi Fisik Tempat Usaha'
    },
    'PELAJAR': {
        'id': 'PELAJAR', 'label': 'Pelajar / Mahasiswa', 'beta': 0.313070, 'or': 1.368,
        'cluster': 'Klaster 4: Rentan / Moral Hazard', 'cluster_code': 'VULNERABLE', 'ltv_mod': -0.05,
        'policy': 'Plafon Dibatasi Maksimal Rp 2.500.000 & STNK Wajib A/N Sendiri'
    },
    'BELUM_BEKERJA': {
        'id': 'BELUM_BEKERJA', 'label': 'Belum / Tidak Bekerja (Pengangguran)', 'beta': 0.317378, 'or': 1.374,
        'cluster': 'Klaster 4: Rentan / Moral Hazard', 'cluster_code': 'VULNERABLE', 'ltv_mod': -0.10,
        'policy': 'Plafon Cap Maks Rp 2.500.000 (Pinjaman > Rp 2.5 Jt Wajib Approval Kepala Cabang)'
    }
}

EXPERT_RULES_OF_THUMB = [
    {
        'Metric': 'Log-Likelihood (ln L)',
        'Pakar / Referensi': 'Sir Ronald A. Fisher (1922) & Samuel S. Wilks (1938)',
        'Rumus': 'ln L = Σ [ y_i ln(P_i) + (1 - y_i) ln(1 - P_i) ]',
        'Rule of Thumb': 'Semakin mendekati nol, kecocokan model semakin baik. Evaluasi LR Test p < 0.05.',
        'Hasil Portofolio': 'Model 0: -35.057,9 ➔ Model 2: -34.456,8 ➔ Model 4: -33.377,6 (LR = 3.360,71, p < 1e-300)',
        'Status': 'Sangat Superior'
    },
    {
        'Metric': 'AIC (Akaike Info Criterion)',
        'Pakar / Referensi': 'Hirotugu Akaike (1974) & Burnham & Anderson (2004)',
        'Rumus': 'AIC = -2 ln L + 2k',
        'Rule of Thumb': 'Semakin kecil semakin baik. Selisih Delta AIC > 10 membuktikan keunggulan mutlak.',
        'Hasil Portofolio': 'Model 2: 68.931,6 ➔ Model 4: 66.775,2 (Delta AIC = -2.156,5 vs Model 2)',
        'Status': 'Champion Model'
    },
    {
        'Metric': 'BIC (Bayesian Info Criterion)',
        'Pakar / Referensi': 'Gideon E. Schwarz (1978) & Adrian E. Raftery (1995)',
        'Rumus': 'BIC = -2 ln L + k ln(N)',
        'Rule of Thumb': 'Penalti ln(N)=11,85 per parameter. Delta BIC > 10 mengonfirmasi bukti menentukan.',
        'Hasil Portofolio': 'Model 2: 69.020,2 ➔ Model 4: 66.873,6 (Delta BIC = -2.146,6)',
        'Status': 'Decisive Evidence'
    },
    {
        'Metric': "McFadden's Pseudo R²",
        'Pakar / Referensi': 'Daniel McFadden (1974, 1979 - Nobel 2000)',
        'Rumus': 'ρ² = 1 - (ln L_model / ln L_null)',
        'Rule of Thumb': '0,02 - 0,10 adalah standar industri perbankan yang sehat untuk binary rare events.',
        'Hasil Portofolio': 'Model 1: 1,57% ➔ Model 2: 1,71% ➔ Model 4: 4,79% (Lonjakan 2,8x lipat)',
        'Status': 'Sangat Sehat'
    },
    {
        'Metric': 'ROC-AUC',
        'Pakar / Referensi': 'Hosmer & Lemeshow (2000) & Tom Fawcett (2006)',
        'Rumus': 'ROC-AUC = ∫ TPR(FPR) d(FPR)',
        'Rule of Thumb': '0,65 - 0,75 adalah batas standar realistis & kuat pada mikro kredit tanpa SLIK.',
        'Hasil Portofolio': 'Model 1: 0,6002 ➔ Model 2: 0,6039 ➔ Model 4: 0,6702',
        'Status': 'Kuat & Mendekati 0,70'
    },
    {
        'Metric': 'PR-AUC',
        'Pakar / Referensi': 'Takaya Saito & Marc Rehmsmeier (2015)',
        'Rumus': 'PR-AUC = ∫ Precision(Recall) d(Recall)',
        'Rule of Thumb': 'Acuan acak = 0,0691 (6,91%). Model memiliki daya presisi jika PR-AUC > 0,0691.',
        'Hasil Portofolio': 'Model 0: 0,0691 ➔ Model 2: 0,0924 ➔ Model 4: 0,1124 (+62,7% di atas acak)',
        'Status': '+62,7% Di Atas Acak'
    },
    {
        'Metric': 'Brier Score Calibration',
        'Pakar / Referensi': 'Glenn W. Brier (1950) & Ewout W. Steyerberg (2010)',
        'Rumus': 'BS = (1/N) Σ (P_i - Y_i)²',
        'Rule of Thumb': 'Benchmark Naif = 0,06433. Model terkalibrasi baik jika BS < 0,06433.',
        'Hasil Portofolio': 'Model 0: 0,06433 ➔ Model 2: 0,06383 ➔ Model 4: 0,06291',
        'Status': 'Terkalibrasi Sempurna'
    }
]

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def rupiah(nilai: float) -> str:
    if pd.isna(nilai) or nilai == 0:
        return "Rp 0"
    return f"Rp {int(nilai):,}".replace(",", ".")

def persen(nilai: float, dec: int = 2) -> str:
    if pd.isna(nilai):
        return "0,00%"
    fmt = f"{{:.{dec}f}}%"
    return fmt.format(nilai).replace(".", ",")

def hitung_skor(merk, usia_thn, otr, pinjaman, kondisi_stnk, pajak_status, is_rep, job_key):
    otr = max(float(otr), 1.0)
    pinjaman = float(pinjaman)
    ltv = pinjaman / otr
    ltv_max = min(max(ltv, 0.0), 1.5)
    pinjaman_juta = pinjaman / 1_000_000.0

    is_yamaha = 1 if merk == "Yamaha" else 0
    is_kawasaki = 1 if merk == "Kawasaki" else 0
    is_lainnya = 1 if merk not in ["Honda", "Yamaha", "Kawasaki"] else 0

    is_stnk_orang_lain = 1 if "ORANG LAIN" in kondisi_stnk.upper() else 0
    is_pajak_aktif = 1 if "AKTIF" in pajak_status.upper() and "TIDAK" not in pajak_status.upper() else 0
    is_repeat = 1 if is_rep else 0

    job_info = JOB_RISK_FACTORS.get(job_key, JOB_RISK_FACTORS['TIDAK_ISI'])
    delta_job = job_info['beta']

    # Model 2
    p2 = MODEL_2_PARAMS
    logit_m2 = (
        p2['Intercept'] +
        (p2['stnk_orang_lain'] * is_stnk_orang_lain) +
        (p2['pajak_aktif'] * is_pajak_aktif) +
        (p2['merk_yamaha'] * is_yamaha) +
        (p2['merk_kawasaki'] * is_kawasaki) +
        (p2['merk_lainnya'] * is_lainnya) +
        (p2['usia_thn'] * usia_thn) +
        (p2['pinjaman_juta'] * pinjaman_juta) +
        (p2['ltv_max'] * ltv_max) +
        delta_job
    )
    prob_m2 = (1.0 / (1.0 + np.exp(-logit_m2))) * 100.0

    # Model 4
    p4 = MODEL_4_PARAMS
    logit_m4 = (
        p4['Intercept'] +
        (p4['stnk_orang_lain'] * is_stnk_orang_lain) +
        (p4['pajak_aktif'] * is_pajak_aktif) +
        (p4['merk_yamaha'] * is_yamaha) +
        (p4['merk_kawasaki'] * is_kawasaki) +
        (p4['merk_lainnya'] * is_lainnya) +
        (p4['usia_thn'] * usia_thn) +
        (p4['pinjaman_juta'] * pinjaman_juta) +
        (p4['ltv_max'] * ltv_max) +
        (p4['repeat_borrower'] * is_repeat) +
        delta_job
    )
    prob_m4 = (1.0 / (1.0 + np.exp(-logit_m4))) * 100.0

    prob_final = prob_m4 if is_repeat else prob_m2

    # Tier & Grade
    if prob_final < 5.0:
        grade = "Grade A"
        tier = "RENDAH (LOW RISK)"
        badge_class = "badge-a"
        rekom = "DISETUJUI (FAST-TRACK)"
        color = "#10B981"
    elif prob_final < 7.0:
        grade = "Grade B"
        tier = "MODERAT (MEDIUM RISK)"
        badge_class = "badge-b"
        rekom = "DISETUJUI (STANDAR PROSEDUR)"
        color = "#F59E0B"
    elif prob_final < 10.0:
        grade = "Grade C"
        tier = "TINGGI (HIGH RISK)"
        badge_class = "badge-c"
        rekom = "REVIEW MANUAL / POTONG PLAFON"
        color = "#EA580C"
    else:
        grade = "Grade D"
        tier = "KRITIS / SANGAT TINGGI"
        badge_class = "badge-d"
        rekom = "DITOLAK / WAJIB APPROVAL BM"
        color = "#E11D48"

    # Safe LTV & Limit
    if is_stnk_orang_lain:
        base_safe_ltv = 0.35
    elif not is_pajak_aktif or usia_thn >= 7:
        base_safe_ltv = 0.35
    else:
        base_safe_ltv = 0.45

    safe_ltv = max(0.25, min(0.50, base_safe_ltv + job_info['ltv_mod']))
    if job_info['cluster_code'] == 'VULNERABLE':
        safe_loan = min(otr * safe_ltv, 2_500_000.0)
    else:
        safe_loan = otr * safe_ltv

    return {
        'prob_final': prob_final,
        'prob_m2': prob_m2,
        'prob_m4': prob_m4,
        'grade': grade,
        'tier': tier,
        'badge_class': badge_class,
        'rekom': rekom,
        'color': color,
        'ltv': ltv,
        'safe_ltv': safe_ltv,
        'safe_loan': safe_loan,
        'job_info': job_info
    }

# ==============================================================================
# SIDEBAR NAVIGATION
# ==============================================================================
with st.sidebar:
    st.image("https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Python-Dark.svg", width=40)
    st.title("PGI Analytics")
    st.caption("Sistem Penilaian Risiko Kredit NPL")
    
    menu = st.radio(
        "Pilih Modul:",
        [
            "📊 Executive Dashboard",
            "🧮 Single Loan Scoring Engine",
            "📈 What-If Stress Testing",
            "📑 Multi-Loan Batch Profiler",
            "🔬 Ekonometrika & Model Diagnostics",
            "📋 Matriks Kebijakan & Rule Ahli",
            "🖼️ Galeri Visualisasi Riset"
        ]
    )
    
    st.divider()
    st.markdown("""
    **Dataset Portofolio**:
    - Total Data: `139.493 Transaksi`
    - Prevalensi NPL: `6,91% (9.640 Kasus)`
    - Model Champion: `Model 4 (AIC 66.775)`
    - Target Korporasi: `< 5,00% NPL`
    """)

# ==============================================================================
# MODUL 1: EXECUTIVE DASHBOARD
# ==============================================================================
if menu == "📊 Executive Dashboard":
    st.markdown('<div class="main-header">Executive Dashboard Analisis Risiko NPL</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Pusat Gadai Indonesia (PGI) — Ringkasan Portofolio & Kebijakan Underwriting 2026</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Total Transaksi Kredit</div>
            <div class="kpi-value">139.493</div>
            <span style="color: #64748B; font-size: 0.8rem;">100% Data Valid Terverifikasi</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Tingkat NPL Aktual</div>
            <div class="kpi-value" style="color: #E11D48;">6,91%</div>
            <span style="color: #64748B; font-size: 0.8rem;">9.640 Debitur Macet</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Target Toleransi NPL</div>
            <div class="kpi-value" style="color: #10B981;">&lt; 5,00%</div>
            <span style="color: #64748B; font-size: 0.8rem;">Ambang Batas Sehat OJK</span>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Model Champion (M4)</div>
            <div class="kpi-value" style="color: #2563EB;">67,02%</div>
            <span style="color: #64748B; font-size: 0.8rem;">ROC-AUC (+62,7% Precision)</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Ringkasan Distribusi Risiko Agunan & Portofolio")
    col_left, col_right = st.columns(2)

    with col_left:
        # Chart STNK
        df_stnk = pd.DataFrame({
            'Kondisi STNK': ['A/N Sendiri', 'A/N Orang Lain'],
            'Volume': [63498, 75995],
            'NPL_Rate': [4.94, 8.56]
        })
        fig_stnk = px.bar(
            df_stnk, x='Kondisi STNK', y='NPL_Rate',
            color='Kondisi STNK',
            color_discrete_map={'A/N Sendiri': '#10B981', 'A/N Orang Lain': '#EF4444'},
            text='NPL_Rate',
            title="Tingkat NPL berdasarkan Kepemilikan STNK (Moral Hazard +71%)"
        )
        fig_stnk.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig_stnk.add_hline(y=5.0, line_dash="dash", line_color="orange", annotation_text="Target Max 5%")
        st.plotly_chart(fig_stnk, use_container_width=True)

    with col_right:
        # Chart Merk
        df_merk = pd.DataFrame({
            'Merk': ['Honda', 'Yamaha', 'Kawasaki', 'Lainnya'],
            'NPL_Rate': [6.65, 7.76, 8.15, 7.56],
            'Total': [106611, 31236, 1117, 529]
        })
        fig_merk = px.bar(
            df_merk, x='Merk', y='NPL_Rate',
            color='Merk',
            text='NPL_Rate',
            title="Tingkat NPL berdasarkan Merk Kendaraan"
        )
        fig_merk.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig_merk.add_hline(y=5.0, line_dash="dash", line_color="orange", annotation_text="Target Max 5%")
        st.plotly_chart(fig_merk, use_container_width=True)

# ==============================================================================
# MODUL 2: SINGLE LOAN SCORING ENGINE
# ==============================================================================
elif menu == "🧮 Single Loan Scoring Engine":
    st.markdown('<div class="main-header">Smart Underwriting Credit Scoring Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Evaluasi kelayakan pinjaman debitur tunggal secara presisi & real-time</div>', unsafe_allow_html=True)

    col_in, col_res = st.columns([1, 1])

    with col_in:
        st.subheader("1. Form Parameter Aplikasi Kredit")
        merk = st.selectbox("Merk Kendaraan:", ["Honda", "Yamaha", "Kawasaki", "Lainnya"])
        usia_thn = st.slider("Usia Kendaraan (Tahun):", min_value=0, max_value=20, value=4)
        otr = st.number_input("Harga Taksiran Pasar (OTR) - Rp:", min_value=1_000_000, max_value=100_000_000, value=12_000_000, step=500_000)
        pinjaman = st.number_input("Nominal Pengajuan Pinjaman - Rp:", min_value=500_000, max_value=50_000_000, value=5_000_000, step=250_000)
        kondisi_stnk = st.radio("Kepemilikan Dokumen STNK:", ["A/N Sendiri", "A/N Orang Lain"], horizontal=True)
        pajak_status = st.radio("Status Pajak STNK:", ["Pajak Aktif", "Pajak Tidak Aktif (Mati)"], horizontal=True)
        
        job_options = {k: f"{v['label']} ({v['cluster']})" for k, v in JOB_RISK_FACTORS.items()}
        job_key = st.selectbox("Profesi / Pekerjaan Calon Debitur:", options=list(job_options.keys()), format_func=lambda x: job_options[x])
        
        is_repeat = st.checkbox("Debitur Berulang (Repeat Borrower - Riwayat Lunas Sempurna)", value=False)

    res = hitung_skor(merk, usia_thn, otr, pinjaman, kondisi_stnk, pajak_status, is_repeat, job_key)

    with col_res:
        st.subheader("2. Hasil Keputusan Underwriting")
        
        st.markdown(f"""
        <div style="background-color: #F8FAFC; border: 2px solid {res['color']}; border-radius: 12px; padding: 20px; text-align: center;">
            <div style="font-size: 0.9rem; color: #64748B; font-weight: 600;">PROBABILITAS GAGAL BAYAR (ESTIMASI NPL)</div>
            <div style="font-size: 3rem; font-weight: 800; color: {res['color']};">{res['prob_final']:.2f}%</div>
            <div style="margin-top: 8px;">
                <span class="{res['badge_class']}" style="font-size: 1.1rem; padding: 6px 16px;">{res['grade']} — {res['tier']}</span>
            </div>
            <div style="margin-top: 16px; font-weight: 700; font-size: 1.15rem; color: #0F172A;">
                REKOMENDASI: <span style="color: {res['color']};">{res['rekom']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Rasio LTV Diajukan", f"{res['ltv']*100:.1f}%")
        with col_m2:
            st.metric("Batas Aman LTV Kebijakan", f"{res['safe_ltv']*100:.0f}%")

        st.metric("Batas Maksimal Plafon Aman", rupiah(res['safe_loan']), delta=f"{rupiah(res['safe_loan'] - pinjaman)} vs Diajukan")

        st.info(f"💡 **Kebijakan Klaster Profesi ({res['job_info']['cluster']}):**\n{res['job_info']['policy']}")

# ==============================================================================
# MODUL 3: WHAT-IF STRESS TESTING
# ==============================================================================
elif menu == "📈 What-If Stress Testing":
    st.markdown('<div class="main-header">What-If Scenario Stress Testing</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Analisis sensitivitas risiko NPL terhadap variasi plafon pinjaman dan LTV</div>', unsafe_allow_html=True)

    col_w1, col_w2 = st.columns([1, 2])
    with col_w1:
        st.subheader("Parameter Motor Uji")
        w_merk = st.selectbox("Merk Kendaraan:", ["Honda", "Yamaha", "Kawasaki", "Lainnya"], key="w_merk")
        w_usia = st.slider("Usia Motor (Thn):", 0, 15, 3, key="w_usia")
        w_otr = st.number_input("Harga OTR (Rp):", min_value=2_000_000, max_value=50_000_000, value=15_000_000, step=1_000_000, key="w_otr")
        w_stnk = st.selectbox("STNK:", ["A/N Sendiri", "A/N Orang Lain"], key="w_stnk")
        w_pajak = st.selectbox("Status Pajak:", ["Pajak Aktif", "Pajak Tidak Aktif"], key="w_pajak")
        w_job = st.selectbox("Profesi:", list(JOB_RISK_FACTORS.keys()), key="w_job")

    with col_w2:
        # Generate curve
        pinjaman_range = np.linspace(1_000_000, min(w_otr * 1.0, 20_000_000), 25)
        probs_m2 = []
        probs_m4 = []
        
        for p_val in pinjaman_range:
            r_new = hitung_skor(w_merk, w_usia, w_otr, p_val, w_stnk, w_pajak, False, w_job)
            probs_m2.append(r_new['prob_m2'])
            r_rep = hitung_skor(w_merk, w_usia, w_otr, p_val, w_stnk, w_pajak, True, w_job)
            probs_m4.append(r_rep['prob_m4'])

        df_curve = pd.DataFrame({
            'Plafon_Juta': pinjaman_range / 1_000_000,
            'NPL_M2_FirstTimer': probs_m2,
            'NPL_M4_RepeatBorrower': probs_m4
        })

        fig_stress = go.Figure()
        fig_stress.add_trace(go.Scatter(x=df_curve['Plafon_Juta'], y=df_curve['NPL_M2_FirstTimer'], mode='lines+markers', name='Debitur Baru (Model 2)', line=dict(color='#EF4444', width=3)))
        fig_stress.add_trace(go.Scatter(x=df_curve['Plafon_Juta'], y=df_curve['NPL_M4_RepeatBorrower'], mode='lines+markers', name='Repeat Borrower (Model 4)', line=dict(color='#10B981', width=3)))
        
        fig_stress.add_hline(y=5.0, line_dash="dash", line_color="orange", annotation_text="Target Batas NPL 5%")
        fig_stress.update_layout(
            title="Kurva Sensitivitas Plafon Pinjaman terhadap NPL",
            xaxis_title="Nominal Pinjaman Pokok (Juta Rupiah)",
            yaxis_title="Probabilitas Gagal Bayar (%)",
            hovermode="x unified"
        )
        st.plotly_chart(fig_stress, use_container_width=True)

# ==============================================================================
# MODUL 4: MULTI-LOAN BATCH PROFILER
# ==============================================================================
elif menu == "📑 Multi-Loan Batch Profiler":
    st.markdown('<div class="main-header">Multi-Loan Batch Application Profiler</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Evaluasi dan scoring portofolio calon debitur massal sekaligus</div>', unsafe_allow_html=True)

    st.write("Upload file CSV calon debitur atau gunakan data simulasi bawaan:")

    # Generate Dummy Data Button
    if st.button("🎲 Generate 10 Sample Data Aplikasi Debitur"):
        sample_data = pd.DataFrame({
            'Nama_Debitur': [f'Debitur_{i+1}' for i in range(10)],
            'Merk': ['Honda', 'Yamaha', 'Honda', 'Kawasaki', 'Honda', 'Yamaha', 'Honda', 'Yamaha', 'Honda', 'Lainnya'],
            'Usia_Motor': [2, 5, 8, 1, 3, 10, 4, 6, 2, 7],
            'Harga_OTR': [15000000, 12000000, 8000000, 25000000, 14000000, 6000000, 16000000, 11000000, 18000000, 7000000],
            'Pinjaman': [6000000, 5000000, 4500000, 8000000, 5500000, 3500000, 6500000, 5000000, 7000000, 3500000],
            'STNK': ['A/N Sendiri', 'A/N Orang Lain', 'A/N Orang Lain', 'A/N Sendiri', 'A/N Sendiri', 'A/N Orang Lain', 'A/N Sendiri', 'A/N Orang Lain', 'A/N Sendiri', 'A/N Orang Lain'],
            'Pajak': ['Pajak Aktif', 'Pajak Aktif', 'Pajak Tidak Aktif', 'Pajak Aktif', 'Pajak Aktif', 'Pajak Tidak Aktif', 'Pajak Aktif', 'Pajak Tidak Aktif', 'Pajak Aktif', 'Pajak Tidak Aktif'],
            'Pekerjaan': ['PNS', 'KARYAWAN_SWASTA', 'WIRASWASTA', 'PNS', 'GURU', 'BELUM_BEKERJA', 'PEDAGANG', 'BURUH', 'KARYAWAN_SWASTA', 'PELAJAR'],
            'Repeat_Borrower': [1, 0, 0, 1, 1, 0, 0, 0, 1, 0]
        })
        st.session_state['batch_df'] = sample_data

    uploaded_file = st.file_uploader("Upload CSV Debitur:", type=['csv'])
    if uploaded_file is not None:
        st.session_state['batch_df'] = pd.read_csv(uploaded_file)

    if 'batch_df' in st.session_state:
        df_eval = st.session_state['batch_df'].copy()
        
        results = []
        for _, row in df_eval.iterrows():
            r = hitung_skor(
                row['Merk'], row['Usia_Motor'], row['Harga_OTR'], row['Pinjaman'],
                row['STNK'], row['Pajak'], bool(row['Repeat_Borrower']), row['Pekerjaan']
            )
            results.append({
                'Prob_NPL_%': round(r['prob_final'], 2),
                'Grade': r['grade'],
                'Keputusan': r['rekom'],
                'LTV_%': round(r['ltv'] * 100, 1),
                'Plafon_Aman_Rp': int(r['safe_loan'])
            })
            
        res_df = pd.concat([df_eval, pd.DataFrame(results)], axis=1)
        st.dataframe(res_df, use_container_width=True)
        
        # Ringkasan Keputusan
        st.markdown("### Ringkasan Keputusan Batch")
        c_b1, c_b2, c_b3 = st.columns(3)
        c_b1.metric("Total Debitur Disetujui", len(res_df[res_df['Grade'].isin(['Grade A', 'Grade B'])]))
        c_b2.metric("Total Perlu Review / Potong Plafon", len(res_df[res_df['Grade'] == 'Grade C']))
        c_b3.metric("Total Ditolak", len(res_df[res_df['Grade'] == 'Grade D']))

# ==============================================================================
# MODUL 5: EKONOMETRIKA & MODEL DIAGNOSTICS
# ==============================================================================
elif menu == "🔬 Ekonometrika & Model Diagnostics":
    st.markdown('<div class="main-header">Ekonometrika & Model Diagnostics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Evaluasi komprehensif Model 0 s/d Model 4, VIF, dan 8 Hipotesis Empiris</div>', unsafe_allow_html=True)

    st.subheader("1. Tabel Perbandingan Model Ekonometrika")
    model_df = pd.DataFrame([
        {"Model": "Model 0 (Null Model)", "Param (k)": 1, "Log-Likelihood": -35057.93, "AIC": 70117.86, "BIC": 70127.71, "Pseudo R²": "0,00%", "ROC-AUC": "0,5000", "PR-AUC": "0,0691", "Brier Score": "0,06433"},
        {"Model": "Model 1 (Core Risk)", "Param (k)": 8, "Log-Likelihood": -34507.86, "AIC": 69031.72, "BIC": 69110.49, "Pseudo R²": "1,57%", "ROC-AUC": "0,6002", "PR-AUC": "0,0923", "Brier Score": "0,06385"},
        {"Model": "Model 2 (Core + LTV_MAX)", "Param (k)": 9, "Log-Likelihood": -34456.81, "AIC": 68931.62, "BIC": 69020.23, "Pseudo R²": "1,71%", "ROC-AUC": "0,6039", "PR-AUC": "0,0924", "Brier Score": "0,06383"},
        {"Model": "Model 3 (Core + Zona LTV)", "Param (k)": 10, "Log-Likelihood": -34469.49, "AIC": 68958.99, "BIC": 69057.45, "Pseudo R²": "1,68%", "ROC-AUC": "0,6027", "PR-AUC": "0,0926", "Brier Score": "0,06381"},
        {"Model": "Model 4 (Full Enhanced)", "Param (k)": 10, "Log-Likelihood": -33377.58, "AIC": 66775.15, "BIC": 66873.61, "Pseudo R²": "4,79%", "ROC-AUC": "0,6702", "PR-AUC": "0,1124", "Brier Score": "0,06291"}
    ])
    st.dataframe(model_df, use_container_width=True)

    st.subheader("2. Hasil Pengujian 8 Hipotesis Riset")
    hyp_df = pd.DataFrame([
        {"ID": "H1", "Hipotesis": "Hubungan kepemilikan STNK dan NPL", "Odds Ratio": "1,710", "Status": "DITERIMA", "Interpretasi": "STNK orang lain menaikkan odds macet +71% (p < 0.0001)"},
        {"ID": "H2", "Hipotesis": "Hubungan jenis pekerjaan dan NPL", "Odds Ratio": "3,460", "Status": "DITERIMA", "Interpretasi": "Pengangguran berisiko 3.46x dibanding Karyawan Swasta"},
        {"ID": "H3", "Hipotesis": "Hubungan merk kendaraan dan NPL", "Odds Ratio": "1,050", "Status": "DITERIMA", "Interpretasi": "Yamaha memiliki odds macet 5% lebih tinggi dibanding Honda"},
        {"ID": "H4", "Hipotesis": "Hubungan usia kendaraan dan NPL", "Odds Ratio": "1,093", "Status": "DITERIMA", "Interpretasi": "Tiap 1 tahun usia motor menambah odds macet +9.3%"},
        {"ID": "H5", "Hipotesis": "Hubungan status pajak dan NPL", "Odds Ratio": "1,118", "Status": "DITERIMA", "Interpretasi": "Pajak aktif berkorelasi dengan plafon pinjaman lebih besar"},
        {"ID": "H6", "Hipotesis": "Hubungan nominal pinjaman pokok dan NPL", "Odds Ratio": "1,434", "Status": "DITERIMA", "Interpretasi": "Tiap kenaikan Rp 1 juta pinjaman menaikkan odds macet +43.4%"},
        {"ID": "H7", "Hipotesis": "Signifikansi fitur LTV_MAX", "Odds Ratio": "0,097", "Status": "DITERIMA", "Interpretasi": "LTV_MAX kontinu memperbaiki AIC secara signifikan"},
        {"ID": "H8", "Hipotesis": "Signifikansi klasifikasi Zona LTV", "Odds Ratio": "0,680", "Status": "DITERIMA", "Interpretasi": "Zona LTV terbukti signifikan namun inferior dibanding LTV_MAX"}
    ])
    st.dataframe(hyp_df, use_container_width=True)

# ==============================================================================
# MODUL 6: MATRIKS KEBIJAKAN & RULE OF THUMB AHLI
# ==============================================================================
elif menu == "📋 Matriks Kebijakan & Rule Ahli":
    st.markdown('<div class="main-header">Matriks Kebijakan Operasional & Rule of Thumb Ahli</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Pedoman eksekutif dan metodologi statistik internasional</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏛️ Matriks Kebijakan 4 Klaster Pekerjaan", "📚 Rule of Thumb Ahli Dunia"])

    with tab1:
        st.markdown("""
        | Klaster | Target Profesi | Risiko NPL Empiris | Batas Max LTV | Plafon Max | Standar Verifikasi |
        | :--- | :--- | :--- | :--- | :--- | :--- |
        | **Klaster 1: Prime** | Guru, Dosen, PNS, ASN, BUMN | 3,53% - 5,13% | 50% OTR (+5% Bonus) | Rp 10.000.000 | Fast-Track Approval, slip gaji / SK aktif |
        | **Klaster 2: Core** | Karyawan Swasta, IRT, Buruh | 5,79% - 6,16% | 45% (Sendiri) / 35% (Orang Lain) | Rp 7.500.000 | Prosedur Standar Loket & cek fisik agunan |
        | **Klaster 3: Volatil** | Pedagang, Wiraswasta | 8,62% - 13,16% | 40% (Sendiri) / 30% (Orang Lain) | Rp 6.000.000 | Wajib Cek Nota & foto tempat usaha |
        | **Klaster 4: Rentan** | Pengangguran, Pelajar | 7,91% - 7,97% | Maksimal 30% OTR | **Cap Rp 2.500.000** | STNK Wajib A/N Sendiri & Penjamin Aktif |
        """)

    with tab2:
        st.dataframe(pd.DataFrame(EXPERT_RULES_OF_THUMB), use_container_width=True)

# ==============================================================================
# MODUL 7: GALERI VISUALISASI RISET
# ==============================================================================
elif menu == "🖼️ Galeri Visualisasi Riset":
    st.markdown('<div class="main-header">Galeri Publikasi Gambar Riset 300 DPI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Visualisasi empiris ekonometrika Model 0 s/d Model 4</div>', unsafe_allow_html=True)

    figures = [
        ("Gambar 1: Distribusi Risiko STNK & Merk", "output/figures/gambar_1_distribusi_risiko_stnk_merk.png"),
        ("Gambar 2: Kurva Sensitivitas Plafon & LTV", "output/figures/gambar_2_kurva_sensitivitas_plafon_ltv.png"),
        ("Gambar 3: Heatmap Matriks Risiko Bivariat", "output/figures/gambar_3_heatmap_matriks_risiko.png"),
        ("Gambar 4: Evaluasi ROC & PR-AUC Model", "output/figures/gambar_4_evaluasi_roc_pr_auc.png"),
        ("Gambar 5: Forest Plot Odds Ratio Ekonometrika", "output/figures/gambar_5_forest_plot_odds_ratio.png"),
        ("Gambar 6: Kalibrasi Probabilitas Brier Score", "output/figures/gambar_6_kalibrasi_probabilitas.png")
    ]

    for title, path_str in figures:
        p = BASE_DIR / path_str
        if p.exists():
            st.subheader(title)
            st.image(str(p), use_column_width=True)
            st.divider()

