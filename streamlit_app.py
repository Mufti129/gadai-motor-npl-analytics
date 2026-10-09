#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================================================
PUSAT GADAI INDONESIA (PGI) — EXECUTIVE RISK ANALYTICS & SMART UNDERWRITING ENGINE
====================================================================================================
Penulis      : Mukhammad Rekza Mufti (Data Analyst — Divisi Bisnis & Risiko)
Dataset Acuan: 139.493 Transaksi Kredit Valid
Dokumen Acuan: Laporan_Design_Riset_NPL_Gadai_Kendaraan.pdf & README.md
Platform     : Streamlit Community Cloud (Modern Flutter-Grade Responsive Executive UI)
====================================================================================================
"""

import os
import io
import json
import zipfile
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
    page_title="PGI Risk Analytics | Smart Underwriting Engine",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Styling — Diadaptasi dari Arsitektur Visual Modern TES_CROP_HP
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Plus Jakarta Sans", sans-serif;
    }
    
    /* Hide Streamlit Brandings & Footers while preserving Sidebar Navigation */
    #MainMenu {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    [data-testid="stDecoration"] {display: none !important; visibility: hidden !important;}
    [data-testid="stStatusWidget"] {visibility: hidden !important; display: none !important;}
    .viewerBadge_container__1QSob, [class*="viewerBadge"] {display: none !important; visibility: hidden !important;}

    /* Keep Sidebar & Collapse Toggle 100% Accessible & Ultra-Visible */
    [data-testid="stHeader"] {
        background: transparent !important;
        pointer-events: none !important;
    }
    [data-testid="stHeader"] > div:not(:first-child) {
        display: none !important;
    }

    /* High Visibility Sidebar Toggle & Re-open Button */
    [data-testid="stSidebarCollapseButton"], 
    [data-testid="collapsedControl"],
    [data-testid="stHeader"] button,
    button[kind="header"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        background: #1E293B !important;
        border: 1.5px solid #6366F1 !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.45) !important;
        padding: 6px 10px !important;
        z-index: 9999999 !important;
        transition: all 0.2s ease-in-out !important;
        cursor: pointer !important;
    }

    [data-testid="stSidebarCollapseButton"]:hover, 
    [data-testid="collapsedControl"]:hover,
    button[kind="header"]:hover {
        background: #4F46E5 !important;
        border-color: #818CF8 !important;
        transform: scale(1.08) !important;
    }

    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapseButton"] svg {
        fill: #FFFFFF !important;
        stroke: #FFFFFF !important;
        width: 20px !important;
        height: 20px !important;
    }

    [data-testid="stSidebar"] {
        visibility: visible !important;
        display: block !important;
        z-index: 99999 !important;
    }
    [data-testid="stSidebarNav"] {
        display: block !important;
        visibility: visible !important;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }
    
    /* Hero AppBar Header */
    .hero-appbar {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 50%, #2563EB 100%);
        border-radius: 18px;
        padding: 24px 28px;
        color: #FFFFFF;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.3);
        margin-bottom: 22px;
        position: relative;
        overflow: hidden;
    }
    .hero-appbar::after {
        content: "";
        position: absolute;
        top: -30px;
        right: -30px;
        width: 150px;
        height: 150px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 50%;
        pointer-events: none;
    }
    .hero-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        color: #FFFFFF !important;
        line-height: 1.25;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #DBEAFE !important;
        margin-top: 6px;
        font-weight: 400;
        line-height: 1.45;
    }
    .hero-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 14px;
    }
    .hero-tag-pill {
        background: rgba(255, 255, 255, 0.16);
        backdrop-filter: blur(8px);
        padding: 4px 12px;
        border-radius: 30px;
        font-size: 0.76rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.22);
    }
    
    /* Modern Card Container */
    .modern-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px 22px;
        box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.06);
        margin-bottom: 16px;
    }
    
    /* Proportional Metric Cards — Zero Text Overflow */
    .pro-metric-card {
        background: #FFFFFF;
        border: 1.5px solid #E2E8F0;
        border-radius: 14px;
        padding: 14px 16px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-width: 0;
        box-sizing: border-box;
        margin-bottom: 10px;
    }
    .pro-metric-val {
        font-size: 1.55rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.2;
    }
    .pro-metric-label {
        font-size: 0.74rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-top: 4px;
    }
    .pro-metric-sub {
        font-size: 0.72rem;
        color: #94A3B8;
        margin-top: 2px;
    }
    
    /* Dynamic Grade Badges */
    .grade-badge-a {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: #FFFFFF !important;
        padding: 18px;
        border-radius: 14px;
        text-align: center;
        font-weight: 800;
        box-shadow: 0 6px 20px -2px rgba(16, 185, 129, 0.35);
    }
    .grade-badge-b {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: #FFFFFF !important;
        padding: 18px;
        border-radius: 14px;
        text-align: center;
        font-weight: 800;
        box-shadow: 0 6px 20px -2px rgba(245, 158, 11, 0.35);
    }
    .grade-badge-c {
        background: linear-gradient(135deg, #F97316 0%, #EA580C 100%);
        color: #FFFFFF !important;
        padding: 18px;
        border-radius: 14px;
        text-align: center;
        font-weight: 800;
        box-shadow: 0 6px 20px -2px rgba(249, 115, 22, 0.35);
    }
    .grade-badge-d {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        color: #FFFFFF !important;
        padding: 18px;
        border-radius: 14px;
        text-align: center;
        font-weight: 800;
        box-shadow: 0 6px 20px -2px rgba(239, 68, 68, 0.35);
    }
    
    /* Report & Callout Boxes */
    .report-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #2563EB;
        padding: 16px 20px;
        border-radius: 0 12px 12px 0;
        margin-top: 12px;
        margin-bottom: 14px;
        color: #0F172A;
    }
    .report-box-danger {
        background-color: #FEF2F2;
        border: 1px solid #FEE2E2;
        border-left: 5px solid #DC2626;
        padding: 16px 20px;
        border-radius: 0 12px 12px 0;
        margin-top: 12px;
        margin-bottom: 14px;
        color: #991B1B;
    }
    
    /* Driver Rows */
    .driver-item {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #0F172A;
        font-size: 0.88rem;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# PATH & PARAMETER AMBANG BATAS RISIKO (100% PERSIS DENGAN FLASK)
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
FIGURES_DIR = OUTPUT_DIR / "figures"
MODELS_DIR = OUTPUT_DIR / "models"
TABLES_DIR = OUTPUT_DIR / "tables"

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
        'policy': 'Skema Standar Cabang (LTV 45% Sendiri / 35% Orang Lain)',
        'verifikasi': 'Prosedur loket standar, cek fisik nomor rangka/mesin.'
    },
    'KARYAWAN_SWASTA': {
        'id': 'KARYAWAN_SWASTA', 'label': 'Karyawan Swasta', 'beta': 0.0, 'or': 1.000,
        'cluster': 'Klaster 2: Core Baseline', 'cluster_code': 'CORE', 'ltv_mod': 0.0,
        'policy': 'Skema Standar Cabang (Baseline Portofolio)',
        'verifikasi': 'Cek ID Card / slip gaji atau mutasi rekening jika tersedia.'
    },
    'PNS': {
        'id': 'PNS', 'label': 'PNS / ASN / Pegawai BUMN', 'beta': -0.147041, 'or': 0.863,
        'cluster': 'Klaster 1: Prime / Preferred', 'cluster_code': 'PRIME', 'ltv_mod': 0.05,
        'policy': 'Bonus LTV +5% (Maksimal 50%) & Fast-Track Approval',
        'verifikasi': 'Fast-Track: Lampirkan SK/Kartu Pegawai/Slip Gaji, tanpa survey fisik domisili.'
    },
    'GURU': {
        'id': 'GURU', 'label': 'Guru / Dosen', 'beta': -0.428912, 'or': 0.651,
        'cluster': 'Klaster 1: Prime / Preferred', 'cluster_code': 'PRIME', 'ltv_mod': 0.05,
        'policy': 'Bonus LTV +5% (Maksimal 50%) & Fast-Track Approval (Profil Paling Aman)',
        'verifikasi': 'Fast-Track: Verifikasi kartu tanda guru/dosen/NUPTK aktif.'
    },
    'IRT': {
        'id': 'IRT', 'label': 'Ibu Rumah Tangga (IRT)', 'beta': 0.002206, 'or': 1.002,
        'cluster': 'Klaster 2: Core Baseline', 'cluster_code': 'CORE', 'ltv_mod': 0.0,
        'policy': 'Skema Standar (Verifikasi Sumber Nafkah Belanja Keluarga)',
        'verifikasi': 'Konfirmasi nomor kontak suami / kepala keluarga serumah.'
    },
    'BURUH': {
        'id': 'BURUH', 'label': 'Buruh Pabrik / Bangunan', 'beta': 0.017158, 'or': 1.017,
        'cluster': 'Klaster 2: Core Baseline', 'cluster_code': 'CORE', 'ltv_mod': 0.0,
        'policy': 'Skema Standar (Upah Rutin Mingguan/Bulanan)',
        'verifikasi': 'Konfirmasi tempat kerja buruh/pabrik.'
    },
    'PEDAGANG': {
        'id': 'PEDAGANG', 'label': 'Pedagang Toko / Kios / Pasar', 'beta': 0.333499, 'or': 1.396,
        'cluster': 'Klaster 3: Arus Kas Volatil', 'cluster_code': 'VOLATILE', 'ltv_mod': -0.05,
        'policy': 'Pengetatan LTV -5% (Maksimal 40%) & Wajib Cek Nota Usaha',
        'verifikasi': 'Lampirkan foto kios/lapak dagang atau bukti nota transaksi 1 minggu terakhir.'
    },
    'WIRASWASTA': {
        'id': 'WIRASWASTA', 'label': 'Wiraswasta / Pengusaha', 'beta': 0.889340, 'or': 2.434,
        'cluster': 'Klaster 3: Arus Kas Volatil', 'cluster_code': 'VOLATILE', 'ltv_mod': -0.05,
        'policy': 'Pengetatan LTV -5% (Maksimal 40%) & Verifikasi Fisik Tempat Usaha',
        'verifikasi': 'Wajib dokumentasi tempat usaha fisik untuk mitigasi risiko volatilitas omzet modal kerja.'
    },
    'PELAJAR': {
        'id': 'PELAJAR', 'label': 'Pelajar / Mahasiswa', 'beta': 0.313070, 'or': 1.368,
        'cluster': 'Klaster 4: Rentan / Moral Hazard', 'cluster_code': 'VULNERABLE', 'ltv_mod': -0.05,
        'policy': 'Plafon Dibatasi Maksimal Rp 2.500.000 & STNK Wajib A/N Sendiri',
        'verifikasi': 'Wajib Kartu Tanda Mahasiswa (KTM) & nomor HP orang tua/wali aktif.'
    },
    'BELUM_BEKERJA': {
        'id': 'BELUM_BEKERJA', 'label': 'Belum / Tidak Bekerja (Pengangguran)', 'beta': 0.317378, 'or': 1.374,
        'cluster': 'Klaster 4: Rentan / Moral Hazard', 'cluster_code': 'VULNERABLE', 'ltv_mod': -0.10,
        'policy': 'Plafon Cap Maks Rp 2.500.000 (Pinjaman > Rp 2.5 Jt Wajib Approval Kepala Cabang)',
        'verifikasi': 'Wajib ada penjamin keluarga serumah yang bekerja & survey domisili debitur.'
    }
}

EXPERT_RULES_OF_THUMB = [
    {
        'Metrik': 'Log-Likelihood (ln L)',
        'Pakar / Referensi': 'Sir Ronald A. Fisher (1922) & Samuel S. Wilks (1938)',
        'Formula': 'ln L = Σ [ y_i ln(P_i) + (1 - y_i) ln(1 - P_i) ]',
        'Rule of Thumb': 'Semakin mendekati nol, kecocokan data semakin baik. Likelihood Ratio Test: LR = 2(ln L1 - ln L0) ~ Chi-Square(dk). Unggul signifikan jika p < 0.05.',
        'Hasil Riset': 'Model 0: -35.057,9 -> Model 2: -34.456,8 -> Model 4: -33.377,6 (LR = 3.360,71, p < 1e-300)',
        'Status': 'Sangat Superior (p < 0.0001)'
    },
    {
        'Metrik': 'Akaike Information Criterion (AIC)',
        'Pakar / Referensi': 'Hirotugu Akaike (1974) & Burnham & Anderson (2004)',
        'Formula': 'AIC = -2 ln L + 2k',
        'Rule of Thumb': 'Semakin kecil nilainya semakin baik. Delta AIC = AIC_i - AIC_min. Jika Delta > 10, model alternatif terbukti inferior secara mutlak.',
        'Hasil Riset': 'Model 0: 70.117,9 | Model 2: 68.931,6 | Model 4: 66.775,2 (Delta AIC = -2.156,5 vs Model 2)',
        'Status': 'Champion Model (Delta > 2.000)'
    },
    {
        'Metrik': 'Bayesian Information Criterion (BIC)',
        'Pakar / Referensi': 'Gideon E. Schwarz (1978) & Adrian E. Raftery (1995)',
        'Formula': 'BIC = -2 ln L + k ln(N)',
        'Rule of Thumb': 'Penalti ln(N)=11,85 per parameter. Panduan Raftery: Delta BIC > 10 menunjukkan bukti yang sangat kuat dan menentukan (decisive evidence).',
        'Hasil Riset': 'Model 0: 70.127,7 | Model 2: 69.020,2 | Model 4: 66.873,6 (Delta BIC = -2.146,6 vs Model 2)',
        'Status': 'Decisive Evidence (> 10)'
    },
    {
        'Metrik': "McFadden's Pseudo R²",
        'Pakar / Referensi': 'Daniel McFadden (1974, 1979 - Nobel Laureate 2000)',
        'Formula': 'ρ² = 1 - (ln L_model / ln L_null)',
        'Rule of Thumb': 'Nilai 0,20 - 0,40 setara dengan R² = 0,70 - 0,90 pada OLS. Untuk data rare events binary default (~6-7%), rentang 0,02 - 0,10 adalah standar industri perbankan yang sehat.',
        'Hasil Riset': 'Model 1: 1,57% | Model 2: 1,71% | Model 4: 4,79% (Peningkatan 2,8 kali lipat)',
        'Status': 'Sangat Sehat (4,79%)'
    },
    {
        'Metrik': 'ROC-AUC',
        'Pakar / Referensi': 'David W. Hosmer & Stanley Lemeshow (2000) & Tom Fawcett (2006)',
        'Formula': 'ROC-AUC = ∫ TPR(FPR) d(FPR)',
        'Rule of Thumb': '0,50 (acak), 0,60-0,70 (acceptable), 0,70-0,80 (good), >=0,80 (excellent). Pada kredit retail mikro tanpa biro kredit eksternal, 0,65 - 0,75 adalah standar yang sangat kuat.',
        'Hasil Riset': 'Model 1: 0,6002 | Model 2: 0,6039 | Model 4: 0,6702',
        'Status': 'Kuat & Mendekati 0,70'
    },
    {
        'Metrik': 'PR-AUC (Precision-Recall)',
        'Pakar / Referensi': 'Takaya Saito & Marc Rehmsmeier (2015)',
        'Formula': 'PR-AUC = ∫ Precision(Recall) d(Recall)',
        'Rule of Thumb': 'Acuan acak persis sama dengan prevalensi NPL riil = 0,0691 (6,91%). Model memiliki nilai prediktif signifikan jika PR-AUC > 0,0691.',
        'Hasil Riset': 'Model 0 (Acak): 0,0691 | Model 2: 0,0924 | Model 4: 0,1124 (+62,7% di atas acak)',
        'Status': '+62,7% Di Atas Acak'
    },
    {
        'Metrik': 'Brier Score (Probabilistic Calibration)',
        'Pakar / Referensi': 'Glenn W. Brier (1950) & Ewout W. Steyerberg (2010)',
        'Formula': 'BS = (1/N) Σ (P_i - Y_i)²',
        'Rule of Thumb': 'Mengukur deviasi probabilitas prediksi vs aktual. Rentang 0 (sempurna) s/d 1. Benchmark naif BS_null = 0,06433. Terkalibrasi baik jika BS < 0,06433.',
        'Hasil Riset': 'Model 0: 0,06433 | Model 1: 0,06385 | Model 2: 0,06383 | Model 4: 0,06291',
        'Status': 'Terkalibrasi Sempurna'
    }
]

BRANCH_OPERATIONAL_POLICIES = [
    {
        'Klaster': 'Klaster 1: Prime / Preferred',
        'Target Profesi': 'Guru, Dosen, PNS, ASN, Pegawai BUMN',
        'Risiko Empiris': 'NPL 3,53% - 5,13% | OR: 0,65 - 0,86 (Risk Reducer -35%)',
        'Maksimal LTV': '50% OTR (+5% Bonus LTV)',
        'Plafon Maksimal': 'Rp 10.000.000 (Sesuai taksiran OTR)',
        'Standar Verifikasi': 'Fast-Track Approval. Lampirkan ID Card pegawai / SK / Slip Gaji. Tidak diwajibkan survey domisili fisik.',
        'Level Otoritas': 'Petugas Penaksir / Kepala Unit Cabang'
    },
    {
        'Klaster': 'Klaster 2: Core Baseline',
        'Target Profesi': 'Karyawan Swasta, Ibu Rumah Tangga (IRT), Buruh, Tidak Mengisi',
        'Risiko Empiris': 'NPL 5,79% - 6,16% | OR: ~1,00 (Netral Baseline)',
        'Maksimal LTV': '45% (STNK Sendiri) / 35% (STNK Orang Lain / Pajak Mati)',
        'Plafon Maksimal': 'Rp 7.500.000',
        'Standar Verifikasi': 'Prosedur Standar Loket. Cek fisik nomor rangka & mesin, verifikasi KTP, konfirmasi 1 kontak darurat.',
        'Level Otoritas': 'Kepala Unit Cabang / Asisten Kepala Cabang'
    },
    {
        'Klaster': 'Klaster 3: Arus Kas Volatil',
        'Target Profesi': 'Pedagang Toko/Kios/Pasar, Wiraswasta, Pengusaha Mikro',
        'Risiko Empiris': 'NPL 8,62% - 13,16% | OR: 1,40 - 2,43 (High Variance)',
        'Maksimal LTV': '40% (STNK Sendiri) / 30% (STNK Orang Lain) [-5% LTV]',
        'Plafon Maksimal': 'Rp 6.000.000 (Kecuali omzet terbukti kuat)',
        'Standar Verifikasi': 'Verifikasi Usaha Fisik. Dokumentasikan foto kios/lapak dagang atau bukti nota transaksi 1 minggu terakhir.',
        'Level Otoritas': 'Wajib Paraf Pengawas Lapangan & Kepala Cabang'
    },
    {
        'Klaster': 'Klaster 4: Rentan & Moral Hazard',
        'Target Profesi': 'Belum/Tidak Bekerja (Pengangguran), Pelajar, Mahasiswa',
        'Risiko Empiris': 'NPL 7,91% - 7,97% | OR: 1,37 (Tanpa Penghasilan Tetap)',
        'Maksimal LTV': 'Maksimal 30% OTR | Plafon Cap Rp 2.500.000',
        'Plafon Maksimal': 'Strict Cap: Rp 2.500.000',
        'Standar Verifikasi': 'Mitigasi Moral Hazard Ketat. STNK Wajib a/n Sendiri (jika a/n orang lain -> Otomatis Ditolak). Wajib kontak penjamin aktif.',
        'Level Otoritas': 'Pinjaman > Rp 2.5 Jt Wajib Rekomendasi Tertulis & Approval Kepala Cabang'
    }
]

DATA_DICTIONARY = [
    {"Kolom": "tanggal_gadai", "Tipe": "Date", "Deskripsi": "Tanggal pencairan transaksi gadai motor."},
    {"Kolom": "Days Late", "Tipe": "Integer", "Deskripsi": "Jumlah hari keterlambatan pembayaran pasca jatuh tempo."},
    {"Kolom": "NPL_30", "Tipe": "Binary (0/1)", "Deskripsi": "Target biner status kredit macet kriteria Days Late > 30 Hari (Standar Operasional Gadai)."},
    {"Kolom": "NPL_90", "Tipe": "Binary (0/1)", "Deskripsi": "Target biner status kredit macet kriteria Days Late > 90 Hari (Standar Kolektibilitas 5 OJK / Perbankan)."},
    {"Kolom": "kategori_kolektibilitas", "Tipe": "Categorical", "Deskripsi": "Tahapan status: Lancar, DPD 1-30, NPL Transisi 31-90 Hari, NPL Berat >90 Hari."},
    {"Kolom": "merk_group", "Tipe": "Categorical", "Deskripsi": "Pengelompokan merk kendaraan utama (Honda, Yamaha, Kawasaki, Lainnya)."},
    {"Kolom": "kondisi_stnk", "Tipe": "Categorical", "Deskripsi": "Status kepemilikan dokumen STNK (A/N SENDIRI vs A/N ORANG LAIN)."},
    {"Kolom": "pajak_status", "Tipe": "Categorical", "Deskripsi": "Status masa berlaku pajak STNK (Pajak Aktif vs Pajak Tidak Aktif)."},
    {"Kolom": "usia_kendaraan_thn", "Tipe": "Numeric", "Deskripsi": "Usia kendaraan bermotor dalam satuan tahun pada saat digadaikan."},
    {"Kolom": "nilai_taksiran", "Tipe": "Numeric (Rp)", "Deskripsi": "Nilai estimasi harga pasar wajar kendaraan (OTR) oleh penaksir cabang."},
    {"Kolom": "pinjaman_pokok_efektif", "Tipe": "Numeric (Rp)", "Deskripsi": "Nominal pokok pinjaman uang yang dicairkan ke debitur."},
    {"Kolom": "LTV", "Tipe": "Float", "Deskripsi": "Rasio pinjaman terhadap nilai taksiran pasar kendaraan (Pinjaman / OTR)."},
    {"Kolom": "LTV_MAX", "Tipe": "Float", "Deskripsi": "Fitur normalisasi kontinu LTV yang dibatasi pada batas atas 1.50."},
    {"Kolom": "pekerjaan_group", "Tipe": "Categorical", "Deskripsi": "Standardisasi 10 kategori profesi/pekerjaan debitur."},
    {"Kolom": "is_repeat_borrower", "Tipe": "Binary (0/1)", "Deskripsi": "Indikator riwayat debitur (1 = Repeat Borrower, 0 = Nasabah Baru)."},
    {"Kolom": "NPL_clean", "Tipe": "Binary (0/1)", "Deskripsi": "Target biner status kredit macet default (>30 hari / NPL_30)."}
]

# ==============================================================================
# HELPER DATASET LOADING
# ==============================================================================
@st.cache_data(show_spinner="Memuat dataset portofolio 139.493 baris...")
def load_clean_dataset() -> pd.DataFrame:
    pq_path = OUTPUT_DIR / "data_cleaned.parquet"
    if pq_path.exists():
        try:
            return pd.read_parquet(pq_path)
        except Exception:
            pass
    
    zip_path = OUTPUT_DIR / "data_cleaned.zip"
    if zip_path.exists():
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                with z.open('data_cleaned.csv') as f:
                    return pd.read_csv(f, low_memory=False)
        except Exception:
            pass

    csv_path = OUTPUT_DIR / "data_cleaned.csv"
    if csv_path.exists():
        try:
            return pd.read_csv(csv_path, low_memory=False)
        except Exception:
            pass
            
    sample_path = OUTPUT_DIR / "data_cleaned_sample.csv"
    if sample_path.exists():
        return pd.read_csv(sample_path)
        
    return pd.DataFrame()

def rupiah(nilai: float) -> str:
    if pd.isna(nilai) or nilai == 0:
        return "Rp 0"
    abs_val = abs(nilai)
    if abs_val >= 1_000_000_000:
        return f"Rp {nilai / 1_000_000_000:.2f} Miliar"
    elif abs_val >= 1_000_000:
        return f"Rp {nilai / 1_000_000:.2f} Juta"
    else:
        return f"Rp {nilai:,.0f}".replace(",", ".")

def rupiah_exact(nilai: float) -> str:
    if pd.isna(nilai) or nilai == 0:
        return "Rp 0"
    return f"Rp {int(nilai):,}".replace(",", ".")

def persen(nilai: float, dec: int = 2) -> str:
    if pd.isna(nilai):
        return "0,00%"
    fmt = f"{{:.{dec}f}}%"
    return fmt.format(nilai).replace(".", ",")

def get_job_info(pekerjaan_input: str) -> Dict[str, Any]:
    if not pekerjaan_input:
        return JOB_RISK_FACTORS['TIDAK_ISI']
    clean = str(pekerjaan_input).strip().upper()
    if clean in JOB_RISK_FACTORS:
        return JOB_RISK_FACTORS[clean]
    if "GURU" in clean or "DOSEN" in clean:
        return JOB_RISK_FACTORS['GURU']
    elif "PNS" in clean or "ASN" in clean or "BUMN" in clean or "NEGERI" in clean:
        return JOB_RISK_FACTORS['PNS']
    elif "WIRA" in clean or "BISNIS" in clean:
        return JOB_RISK_FACTORS['WIRASWASTA']
    elif "DAGANG" in clean or "TOKO" in clean or "WARUNG" in clean or "KIOS" in clean:
        return JOB_RISK_FACTORS['PEDAGANG']
    elif "PELAJAR" in clean or "MAHASISWA" in clean:
        return JOB_RISK_FACTORS['PELAJAR']
    elif "BELUM" in clean or "TIDAK BEKERJA" in clean or "PENGANGGURAN" in clean or "MENGANGGUR" in clean:
        return JOB_RISK_FACTORS['BELUM_BEKERJA']
    elif "BURUH" in clean:
        return JOB_RISK_FACTORS['BURUH']
    elif "RUMAH TANGGA" in clean or "IRT" in clean:
        return JOB_RISK_FACTORS['IRT']
    elif "SWASTA" in clean or "KARYAWAN" in clean:
        return JOB_RISK_FACTORS['KARYAWAN_SWASTA']
    else:
        return JOB_RISK_FACTORS['TIDAK_ISI']

def hitung_skor_underwriting(
    merk: str,
    usia_thn: float,
    harga_taksiran_otr: float,
    pinjaman_pokok: float,
    kondisi_stnk: str,
    pajak_status: str,
    is_repeat_borrower: int = 0,
    pekerjaan: str = "TIDAK_ISI"
) -> Dict[str, Any]:
    otr = max(float(harga_taksiran_otr), 1.0)
    pinjaman = float(pinjaman_pokok)
    ltv = pinjaman / otr
    ltv_max = min(max(ltv, 0.0), 1.5)
    pinjaman_juta = pinjaman / 1_000_000.0

    merk_clean = str(merk).strip().title()
    is_yamaha = 1 if merk_clean == "Yamaha" else 0
    is_kawasaki = 1 if merk_clean == "Kawasaki" else 0
    is_lainnya = 1 if merk_clean not in ["Honda", "Yamaha", "Kawasaki"] else 0

    stnk_clean = str(kondisi_stnk).strip().upper()
    is_stnk_orang_lain = 1 if "ORANG LAIN" in stnk_clean else 0

    pajak_clean = str(pajak_status).strip().upper()
    is_pajak_aktif = 1 if "AKTIF" in pajak_clean and "TIDAK" not in pajak_clean else 0

    is_rep = 1 if int(is_repeat_borrower) == 1 else 0

    job_info = get_job_info(pekerjaan)
    delta_logit_job = job_info['beta']

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
        delta_logit_job
    )
    prob_m2_pct = (1.0 / (1.0 + np.exp(-logit_m2))) * 100.0

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
        (p4['repeat_borrower'] * is_rep) +
        delta_logit_job
    )
    prob_m4_pct = (1.0 / (1.0 + np.exp(-logit_m4))) * 100.0

    prob_final = prob_m4_pct if is_rep == 1 else prob_m2_pct

    if prob_final < CONFIG_UNDERWRITING['TARGET_NPL_CUTOFF_PCT']:
        risk_tier = "RENDAH (LOW RISK)"
        risk_grade = "Grade A"
        badge_class = "grade-badge-a"
    elif prob_final < CONFIG_UNDERWRITING['MODERATE_RISK_THRESHOLD_PCT']:
        risk_tier = "MODERAT (MEDIUM RISK)"
        risk_grade = "Grade B"
        badge_class = "grade-badge-b"
    elif prob_final < CONFIG_UNDERWRITING['HIGH_RISK_THRESHOLD_PCT']:
        risk_tier = "TINGGI (HIGH RISK)"
        risk_grade = "Grade C"
        badge_class = "grade-badge-c"
    else:
        risk_tier = "KRITIS / SANGAT TINGGI (SEVERE RISK)"
        risk_grade = "Grade D"
        badge_class = "grade-badge-d"

    if is_stnk_orang_lain:
        base_safe_ltv = CONFIG_UNDERWRITING['MAX_SAFE_LTV_ORANG_LAIN']
    elif not is_pajak_aktif or usia_thn >= 7:
        base_safe_ltv = CONFIG_UNDERWRITING['MAX_SAFE_LTV_PAJAK_MATI']
    else:
        base_safe_ltv = CONFIG_UNDERWRITING['MAX_SAFE_LTV_SENDIRI']

    safe_ltv_limit = max(0.25, min(0.50, base_safe_ltv + job_info['ltv_mod']))

    if job_info['cluster_code'] == 'VULNERABLE':
        safe_loan_limit = min(otr * safe_ltv_limit, 2_500_000.0)
    else:
        safe_loan_limit = otr * safe_ltv_limit

    reasons = []
    risk_drivers = []

    if is_stnk_orang_lain:
        msg = "STNK atas nama Orang Lain (+71% Odds NPL, Moral Hazard)"
        reasons.append(msg)
        risk_drivers.append({"faktor": "Kepemilikan STNK", "kondisi": "A/N Orang Lain", "efek": "+71% Odds Macet (Moral Hazard)", "tipe": "warning"})
    else:
        risk_drivers.append({"faktor": "Kepemilikan STNK", "kondisi": "A/N Sendiri", "efek": "Basis Aman (Dokumen Sah)", "tipe": "success"})

    if not is_pajak_aktif:
        msg = "Pajak Kendaraan Tidak Aktif (Menurunkan likuiditas penjualan barang lelang)"
        reasons.append(msg)
        risk_drivers.append({"faktor": "Pajak STNK", "kondisi": "Pajak Tidak Aktif", "efek": "Likuiditas Rendah Saat Lelang", "tipe": "warning"})
    else:
        risk_drivers.append({"faktor": "Pajak STNK", "kondisi": "Pajak Aktif", "efek": "Likuiditas Tinggi (Pajak Hidup)", "tipe": "info"})

    if usia_thn >= 8:
        msg = f"Usia motor tergolong tua ({usia_thn:.0f} tahun), depresiasi aset tinggi (+9.3%/tahun)"
        reasons.append(msg)
        risk_drivers.append({"faktor": "Usia Kendaraan", "kondisi": f"{usia_thn:.0f} Tahun", "efek": f"+{usia_thn*9.3:.1f}% Akumulasi Depresiasi", "tipe": "danger"})
    else:
        risk_drivers.append({"faktor": "Usia Kendaraan", "kondisi": f"{usia_thn:.0f} Tahun", "efek": "Depresiasi Terkendali", "tipe": "success"})

    if ltv > safe_ltv_limit:
        msg = f"Rasio LTV aktual ({ltv*100:.1f}%) melampaui batas kebijakan aman ({safe_ltv_limit*100:.0f}%)"
        reasons.append(msg)
        risk_drivers.append({"faktor": "Rasio LTV", "kondisi": f"{ltv*100:.1f}% (Over-limit)", "efek": f"Eksaserbasi Risiko ({ltv*100 - safe_ltv_limit*100:+.1f}%)", "tipe": "danger"})
    else:
        risk_drivers.append({"faktor": "Rasio LTV", "kondisi": f"{ltv*100:.1f}%", "efek": "Dalam Batas Kebijakan Aman", "tipe": "success"})

    if is_rep == 1:
        reasons.append("Status Debitur: Repeat Borrower (Memangkas risiko gagal bayar sebesar 72%)")
        risk_drivers.append({"faktor": "Histori Debitur", "kondisi": "Repeat Borrower (Nasabah Lama)", "efek": "-72% Odds Gagal Bayar (Proteksi)", "tipe": "success"})
    else:
        risk_drivers.append({"faktor": "Histori Debitur", "kondisi": "Nasabah Baru", "efek": "Profil Standar Portofolio", "tipe": "neutral"})

    if job_info['id'] != 'TIDAK_ISI':
        if job_info['or'] < 1.0:
            job_tip = 'success'
            job_effect = f"OR {job_info['or']}x (Risk Bonus -{(1-job_info['or'])*100:.0f}%)"
        elif job_info['or'] > 1.2:
            job_tip = 'danger'
            job_effect = f"OR {job_info['or']}x (Amplifier +{(job_info['or']-1)*100:.0f}%)"
        elif job_info['or'] > 1.0:
            job_tip = 'warning'
            job_effect = f"OR {job_info['or']}x (Amplifier +{(job_info['or']-1)*100:.0f}%)"
        else:
            job_tip = 'neutral'
            job_effect = "OR 1.00x (Netral)"

        reasons.append(f"Overlay Profesi ({job_info['label']}): {job_effect} — {job_info['cluster']}.")
        risk_drivers.append({"faktor": "Profesi Debitur", "kondisi": job_info['label'], "efek": job_effect, "tipe": job_tip})

    if job_info['cluster_code'] == 'VULNERABLE' and is_stnk_orang_lain:
        decision = "REJECTED (TOLAK PENGAJUAN)"
        decision_code = "REJECT"
        action_plan = "Kombinasi risiko fatal moral hazard: Debitur belum berpenghasilan mandiri menggunakan STNK a/n Orang Lain. Sangat rentan macet lelang."
    elif prob_final <= CONFIG_UNDERWRITING['TARGET_NPL_CUTOFF_PCT'] and ltv <= safe_ltv_limit:
        decision = "APPROVED (DISETUJUI PENUH)"
        decision_code = "APPROVE"
        action_plan = f"Aplikasi pinjaman {rupiah(pinjaman)} disetujui penuh dengan skema standar. {job_info['verifikasi']}"
    elif prob_final <= CONFIG_UNDERWRITING['MODERATE_RISK_THRESHOLD_PCT'] and ltv <= safe_ltv_limit:
        decision = "APPROVED (DISETUJUI — RISIKO MODERAT)"
        decision_code = "APPROVE_MODERATE"
        action_plan = f"Aplikasi pinjaman {rupiah(pinjaman)} disetujui dalam skema standar. {job_info['verifikasi']}"
    elif prob_final <= CONFIG_UNDERWRITING['HIGH_RISK_THRESHOLD_PCT'] and ltv > safe_ltv_limit:
        decision = "CONDITIONAL APPROVAL (SETUJUI DENGAN PEMANGKASAN PLAFON)"
        decision_code = "CONDITIONAL_PRUNE"
        action_plan = f"Pangkas pinjaman ke batas aman {rupiah(safe_loan_limit)} (LTV {safe_ltv_limit*100:.0f}%) untuk menekan probabilitas NPL di bawah target korporasi. {job_info['verifikasi']}"
    elif prob_final > CONFIG_UNDERWRITING['HIGH_RISK_THRESHOLD_PCT'] and is_rep == 1:
        decision = "CONDITIONAL APPROVAL (MITIGASI KHUSUS NASABAH LAMA)"
        decision_code = "CONDITIONAL_REPEAT"
        action_plan = f"Diberikan dispensasi debitur setia: Disetujui maksimal {rupiah(safe_loan_limit)} dengan syarat verifikasi fisik nomor rangka & mesin ketat di kantor cabang. {job_info['verifikasi']}"
    elif prob_final >= CONFIG_UNDERWRITING['SEVERE_RISK_THRESHOLD_PCT'] or (is_stnk_orang_lain and usia_thn >= 8 and ltv > 0.40):
        decision = "REJECTED (TOLAK PENGAJUAN)"
        decision_code = "REJECT"
        action_plan = "Kombinasi risiko kritis (STNK orang lain + kendaraan tua + LTV tinggi). Sangat rentan macet lelang."
    else:
        decision = "HIGH RISK REVIEW (BUTUH PERSETUJUAN KEPALA CABANG)"
        decision_code = "REVIEW"
        action_plan = f"Wajib survey domisili debitur oleh Kepala Cabang dan plafon maksimum dibatasi di {rupiah(safe_loan_limit)}. {job_info['verifikasi']}"

    return {
        'merk': merk_clean,
        'usia_thn': round(usia_thn, 1),
        'harga_taksiran_otr': otr,
        'harga_taksiran_otr_fmt': rupiah_exact(otr),
        'pinjaman_pokok': pinjaman,
        'pinjaman_pokok_fmt': rupiah_exact(pinjaman),
        'ltv_pct': round(ltv * 100.0, 2),
        'kondisi_stnk': "A/N ORANG LAIN" if is_stnk_orang_lain else "A/N SENDIRI",
        'pajak_status': "Pajak Aktif" if is_pajak_aktif else "Pajak Tidak Aktif",
        'is_repeat_borrower': is_rep,
        'repeat_borrower_label': "Repeat Borrower (Nasabah Lama)" if is_rep else "Nasabah Baru",
        'pekerjaan_input': pekerjaan,
        'job_id': job_info['id'],
        'job_label': job_info['label'],
        'job_cluster': job_info['cluster'],
        'job_cluster_code': job_info['cluster_code'],
        'job_odds_ratio': job_info['or'],
        'job_beta': job_info['beta'],
        'job_ltv_mod_pct': round(job_info['ltv_mod'] * 100.0, 1),
        'job_policy': job_info['policy'],
        'job_verifikasi': job_info['verifikasi'],
        'prob_npl_model2_pct': round(prob_m2_pct, 2),
        'prob_npl_model4_pct': round(prob_m4_pct, 2),
        'prob_final_pct': round(prob_final, 2),
        'target_npl_cutoff_pct': CONFIG_UNDERWRITING['TARGET_NPL_CUTOFF_PCT'],
        'npl_status_compliance': "MEMENUHI TARGET (<5%)" if prob_final <= 5.0 else f"DI ATAS TARGET (+{prob_final - 5.0:.2f}%)",
        'risk_tier': risk_tier,
        'risk_grade': risk_grade,
        'badge_class': badge_class,
        'safe_ltv_limit_pct': round(safe_ltv_limit * 100.0, 1),
        'safe_loan_limit': round(safe_loan_limit),
        'safe_loan_limit_fmt': rupiah_exact(safe_loan_limit),
        'pangkas_nominal_rp': max(0, round(pinjaman - safe_loan_limit)),
        'pangkas_nominal_fmt': rupiah_exact(max(0, round(pinjaman - safe_loan_limit))),
        'decision': decision,
        'decision_code': decision_code,
        'action_plan': action_plan,
        'reasons': reasons,
        'risk_drivers': risk_drivers
    }

# ==============================================================================
# SIDEBAR NAVIGATION & QUICK DOWNLOAD (CORP FLUTTER STYLE)
# ==============================================================================
st.sidebar.markdown("""
<div style="background: #09090B; border: 1.5px solid #27272A; border-radius: 14px; padding: 12px 14px; display: flex; align-items: center; gap: 12px; margin-bottom: 16px; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);">
    <div style="width: 42px; height: 42px; background: #18181B; border: 1px solid #3F3F46; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.5 3c-.1.2-.1.5-.1.8v5.3c0 .6.4 1 1 1h2" stroke="#38BDF8" stroke-width="2" stroke-linecap="round"/>
            <circle cx="7" cy="17" r="2" stroke="#38BDF8" stroke-width="2"/>
            <circle cx="17" cy="17" r="2" stroke="#38BDF8" stroke-width="2"/>
        </svg>
    </div>
    <div>
        <div style="font-size: 1.05rem; font-weight: 800; color: #FFFFFF !important; line-height: 1.25;">PGI Risk Analytics</div>
        <div style="font-size: 0.72rem; color: #38BDF8 !important; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;">Smart Credit Scoring</div>
    </div>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "PILIH MODUL DASHBOARD:",
    [
        "Executive Dashboard",
        "Credit Scoring Engine",
        "What-If Stress Testing",
        "Batch Loan Profiler",
        "Dataset Clean & Explorer",
        "Ekonometrika Diagnostics",
        "Matriks Kebijakan Cabang",
        "Galeri Publikasi Riset"
    ]
)

st.sidebar.divider()
st.sidebar.markdown("**PENGATURAN KRITERIA NPL:**")
npl_kriteria = st.sidebar.radio(
    "Pilih Definisi Kriteria NPL:",
    [
        "NPL > 30 Hari (Operasional Gadai)",
        "NPL > 90 Hari (Standar OJK / Kolektibilitas 5)",
        "Komparasi Dual (30 vs 90 Hari)"
    ]
)

st.sidebar.divider()
st.sidebar.markdown("**PUSAT UNDUHAN DATASET:**")

zip_file_path = OUTPUT_DIR / "data_cleaned.zip"
if zip_file_path.exists():
    with open(zip_file_path, "rb") as fz:
        st.sidebar.download_button(
            label="Unduh Full Dataset (.ZIP - 10 MB)",
            data=fz.read(),
            file_name="data_cleaned_pgi_gadai_motor.zip",
            mime="application/zip",
            use_container_width=True
        )
        
parquet_file_path = OUTPUT_DIR / "data_cleaned.parquet"
if parquet_file_path.exists():
    with open(parquet_file_path, "rb") as fp:
        st.sidebar.download_button(
            label="Unduh Parquet (.PARQUET - 8.5 MB)",
            data=fp.read(),
            file_name="data_cleaned_pgi_gadai_motor.parquet",
            mime="application/octet-stream",
            use_container_width=True
        )

st.sidebar.divider()
st.sidebar.caption("Dataset Acuan: 139.493 Transaksi Kredit Valid\nDivisi Bisnis & Risiko PGI")

# ==============================================================================
# MODUL 1: EXECUTIVE DASHBOARD
# ==============================================================================
if menu == "Executive Dashboard":
    is_90_days = "90" in npl_kriteria
    is_dual = "Dual" in npl_kriteria

    target_npl_label = "NPL > 90 Hari (OJK)" if is_90_days else ("NPL Komparatif (30 vs 90 Hari)" if is_dual else "NPL > 30 Hari (Operasional)")
    npl_rate_val = "5,56%" if is_90_days else "6,91%"
    npl_count_val = "7.756 Debitur Macet" if is_90_days else "9.640 Debitur Macet"

    st.markdown(f"""
    <div class="hero-appbar">
        <div class="hero-title">Executive Dashboard Analisis Risiko NPL Gadai Motor</div>
        <div class="hero-subtitle">Pusat Gadai Indonesia (PGI) — Ringkasan Portofolio & Model Ekonometrika 2026 ({target_npl_label})</div>
        <div class="hero-tags">
            <span class="hero-tag-pill">139.493 Transaksi Valid</span>
            <span class="hero-tag-pill">NPL >30 Hari: 6.91%</span>
            <span class="hero-tag-pill">NPL >90 Hari: 5.56%</span>
            <span class="hero-tag-pill">Champion Model 4 (ROC 0.6702)</span>
            <span class="hero-tag-pill">Target Korporasi &lt; 5.0%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class="pro-metric-card">
            <div class="pro-metric-label">Total Transaksi Kredit</div>
            <div class="pro-metric-val">139.493</div>
            <div class="pro-metric-sub">100% Data Valid Terverifikasi</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="pro-metric-card" style="border-color: #FECDD3;">
            <div class="pro-metric-label">Tingkat {target_npl_label}</div>
            <div class="pro-metric-val" style="color: #DC2626;">{npl_rate_val}</div>
            <div class="pro-metric-sub">{npl_count_val}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="pro-metric-card" style="border-color: #A7F3D0;">
            <div class="pro-metric-label">Target Toleransi Korporasi</div>
            <div class="pro-metric-val" style="color: #059669;">&lt; 5,00%</div>
            <div class="pro-metric-sub">Ambang Batas Sehat OJK</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class="pro-metric-card" style="border-color: #BFDBFE;">
            <div class="pro-metric-label">Model Champion (Model 4)</div>
            <div class="pro-metric-val" style="color: #2563EB;">67,02%</div>
            <div class="pro-metric-sub">ROC-AUC (+62.7% Precision)</div>
        </div>
        """, unsafe_allow_html=True)

    # Visual Komparasi Bucket Kolektibilitas / NPL
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.subheader("Struktur Portofolio & Komparasi Kriteria NPL (>30 Hari vs >90 Hari)")
    
    col_k1, col_k2 = st.columns([1, 1])
    with col_k1:
        df_bucket = pd.DataFrame({
            'Kategori Portofolio': [
                '1. Lancar (DPD <= 30 / Lunas)',
                '2. NPL Transisi (DPD 31-90 Hari)',
                '3. NPL Berat / Macet (DPD >90 Hari)'
            ],
            'Volume Kontrak': [129853, 1884, 7756],
            'Proporsi (%)': [93.09, 1.35, 5.56]
        })
        fig_donut = px.pie(
            df_bucket, values='Volume Kontrak', names='Kategori Portofolio',
            hole=0.55,
            color='Kategori Portofolio',
            color_discrete_map={
                '1. Lancar (DPD <= 30 / Lunas)': '#10B981',
                '2. NPL Transisi (DPD 31-90 Hari)': '#F59E0B',
                '3. NPL Berat / Macet (DPD >90 Hari)': '#DC2626'
            },
            title="Distribusi Status Kolektibilitas Portofolio"
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        fig_donut.update_layout(template="plotly_white", showlegend=False)
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_k2:
        df_comp_bar = pd.DataFrame({
            'Kriteria NPL': ['NPL > 30 Hari (Operasional)', 'NPL > 90 Hari (Standar OJK)', 'Selisih Transisi (31-90)'],
            'Tingkat NPL (%)': [6.91, 5.56, 1.35],
            'Jumlah Pinjaman': [9640, 7756, 1884]
        })
        fig_comp = px.bar(
            df_comp_bar, x='Kriteria NPL', y='Tingkat NPL (%)',
            text='Tingkat NPL (%)',
            color='Kriteria NPL',
            color_discrete_map={
                'NPL > 30 Hari (Operasional)': '#DC2626',
                'NPL > 90 Hari (Standar OJK)': '#EA580C',
                'Selisih Transisi (31-90)': '#F59E0B'
            },
            title="Perbandingan Tingkat NPL Berdasarkan Ambang Keterlambatan"
        )
        fig_comp.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig_comp.add_hline(y=5.0, line_dash="dash", line_color="#059669", annotation_text="Batas Maks 5.0%")
        fig_comp.update_layout(yaxis_title="Persentase Portofolio (%)", showlegend=False, template="plotly_white")
        st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.subheader(f"Distribusi Risiko Portofolio Agunan ({target_npl_label})")
    
    col_left, col_right = st.columns(2)
    with col_left:
        # Data STNK berdasarkan kriteria
        if is_90_days:
            stnk_sendiri_rate, stnk_lain_rate = 3.98, 6.89
        else:
            stnk_sendiri_rate, stnk_lain_rate = 4.94, 8.56

        df_stnk = pd.DataFrame({
            'Kondisi STNK': ['A/N Sendiri', 'A/N Orang Lain'],
            'Volume': [63498, 75995],
            'NPL_Rate': [stnk_sendiri_rate, stnk_lain_rate]
        })
        fig_stnk = px.bar(
            df_stnk, x='Kondisi STNK', y='NPL_Rate',
            color='Kondisi STNK',
            color_discrete_map={'A/N Sendiri': '#059669', 'A/N Orang Lain': '#DC2626'},
            text='NPL_Rate',
            title=f"Tingkat NPL berdasarkan Kepemilikan STNK ({target_npl_label})"
        )
        fig_stnk.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig_stnk.add_hline(y=5.0, line_dash="dash", line_color="#D97706", annotation_text="Target Max 5.0%")
        fig_stnk.update_layout(yaxis_title="Tingkat NPL (%)", showlegend=False, template="plotly_white")
        st.plotly_chart(fig_stnk, use_container_width=True)

    with col_right:
        if is_90_days:
            merk_rates = [5.36, 6.22, 6.62, 6.05]
        else:
            merk_rates = [6.65, 7.76, 8.15, 7.56]

        df_merk = pd.DataFrame({
            'Merk': ['Honda', 'Yamaha', 'Kawasaki', 'Lainnya'],
            'NPL_Rate': merk_rates,
            'Volume': [106611, 31236, 1117, 529]
        })
        fig_merk = px.bar(
            df_merk, x='Merk', y='NPL_Rate',
            color='Merk',
            color_discrete_sequence=['#2563EB', '#4F46E5', '#7C3AED', '#64748B'],
            text='NPL_Rate',
            title=f"Tingkat NPL berdasarkan Merk Kendaraan ({target_npl_label})"
        )
        fig_merk.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig_merk.add_hline(y=5.0, line_dash="dash", line_color="#D97706", annotation_text="Target Max 5.0%")
        fig_merk.update_layout(yaxis_title="Tingkat NPL (%)", showlegend=False, template="plotly_white")
        st.plotly_chart(fig_merk, use_container_width=True)

    st.markdown("""
    <div class="report-box">
        <strong>Temuan Kunci Divisi Risiko:</strong> Penambahan faktor jaminan (STNK a/n Orang Lain) dan riwayat nasabah berulang (Repeat Borrower) terbukti secara konsisten memangkas deviasi prediksi baik pada kriteria NPL operasional (&gt;30 hari) maupun kriteria OJK (&gt;90 hari).
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# MODUL 2: CREDIT SCORING ENGINE (PROPORTIONAL & RESPONSIVE)
# ==============================================================================
elif menu == "Credit Scoring Engine":
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">Smart Underwriting Credit Scoring Engine</div>
        <div class="hero-subtitle">Penilaian risiko kelayakan kredit calon debitur secara real-time berbasis Model 2 & Model 4</div>
        <div class="hero-tags">
            <span class="hero-tag-pill">Logit Scoring Transform</span>
            <span class="hero-tag-pill">Job Risk Overlay (N=24.857)</span>
            <span class="hero-tag-pill">Safe LTV Engine</span>
            <span class="hero-tag-pill">Branch Operational Policy</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_in, col_res = st.columns([1, 1.25])

    with col_in:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.subheader("Parameter Aplikasi Kredit")
        merk = st.selectbox("Merk Kendaraan:", ["Honda", "Yamaha", "Kawasaki", "Lainnya"])
        usia_thn = st.slider("Usia Kendaraan (Tahun):", min_value=0, max_value=20, value=4)
        otr = st.number_input("Nilai Taksiran Pasar (OTR) - Rp:", min_value=1_000_000, max_value=100_000_000, value=12_000_000, step=500_000)
        pinjaman = st.number_input("Nominal Pinjaman Diajukan - Rp:", min_value=500_000, max_value=50_000_000, value=5_000_000, step=250_000)
        
        c_r1, c_r2 = st.columns(2)
        with c_r1:
            kondisi_stnk = st.radio("Kepemilikan STNK:", ["A/N Sendiri", "A/N Orang Lain"])
        with c_r2:
            pajak_status = st.radio("Status Pajak STNK:", ["Pajak Aktif", "Pajak Tidak Aktif"])

        job_options = {k: f"{v['label']} ({v['cluster']})" for k, v in JOB_RISK_FACTORS.items()}
        job_key = st.selectbox("Profesi / Pekerjaan Debitur:", options=list(job_options.keys()), format_func=lambda x: job_options[x])
        
        is_repeat = st.checkbox("Repeat Borrower (Nasabah Lama dengan Riwayat Lunas Sempurna)", value=False)
        st.markdown('</div>', unsafe_allow_html=True)

    res = hitung_skor_underwriting(
        merk=merk,
        usia_thn=float(usia_thn),
        harga_taksiran_otr=float(otr),
        pinjaman_pokok=float(pinjaman),
        kondisi_stnk=kondisi_stnk,
        pajak_status=pajak_status,
        is_repeat_borrower=1 if is_repeat else 0,
        pekerjaan=job_key
    )

    with col_res:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.subheader("Hasil Keputusan Underwriting")
        
        # Kartu Skor Probabilitas & Badge Peringkat
        c_score1, c_score2 = st.columns([1.3, 1])
        with c_score1:
            st.markdown(f"""
            <div class="pro-metric-card" style="padding: 16px 20px;">
                <div class="pro-metric-label">Probabilitas Gagal Bayar (NPL)</div>
                <div class="pro-metric-val" style="font-size: 2.2rem; color: #0F172A;">{res['prob_final_pct']:.2f}%</div>
                <div class="pro-metric-sub" style="font-weight: 600; color: {'#DC2626' if res['prob_final_pct'] > 5.0 else '#059669'};">
                    {res['prob_final_pct'] - 5.0:+.2f}% vs Batas Toleransi 5.0%
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c_score2:
            st.markdown(f"""
            <div class="{res['badge_class']}">
                <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.9;">Peringkat Risiko</div>
                <div style="font-size: 1.7rem; font-weight: 800; margin: 2px 0;">{res['risk_grade']}</div>
                <div style="font-size: 0.72rem; opacity: 0.95;">{res['risk_tier']}</div>
            </div>
            """, unsafe_allow_html=True)

        # Kartu Banner Rekomendasi Resmi
        st.markdown(f"""
        <div style="background: #F1F5F9; border: 1.5px solid #CBD5E1; border-radius: 12px; padding: 14px 18px; margin-top: 12px; text-align: center;">
            <div style="font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">Keputusan Rekomendasi</div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #0F172A; margin-top: 4px;">{res['decision']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Kartu Instruksi Operasional Cabang
        st.markdown(f"""
        <div class="report-box">
            <div style="font-weight: 700; color: #1E3A8A; margin-bottom: 4px;">Instruksi Operasional Cabang:</div>
            <div style="font-size: 0.9rem; line-height: 1.5;">{res['action_plan']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 3 Indikator Finansial Utama
        c_k1, c_k2, c_k3 = st.columns(3)
        with c_k1:
            st.markdown(f"""
            <div class="pro-metric-card">
                <div class="pro-metric-label">LTV Diajukan</div>
                <div class="pro-metric-val">{res['ltv_pct']:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        with c_k2:
            st.markdown(f"""
            <div class="pro-metric-card">
                <div class="pro-metric-label">Batas Aman LTV</div>
                <div class="pro-metric-val">{res['safe_ltv_limit_pct']:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
        with c_k3:
            st.markdown(f"""
            <div class="pro-metric-card">
                <div class="pro-metric-label">Plafon Aman</div>
                <div class="pro-metric-val" style="font-size: 1.15rem;">{res['safe_loan_limit_fmt']}</div>
            </div>
            """, unsafe_allow_html=True)

        # Expander Summary
        with st.expander("Detail Parameter Aplikasi yang Dievaluasi", expanded=False):
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.write(f"**Agunan:** {res['merk']} ({res['usia_thn']:.0f} Tahun)")
                st.write(f"**Taksiran OTR:** {res['harga_taksiran_otr_fmt']}")
                st.write(f"**Pinjaman Diajukan:** {res['pinjaman_pokok_fmt']}")
            with col_p2:
                st.write(f"**STNK:** {res['kondisi_stnk']} ({res['pajak_status']})")
                st.write(f"**Profesi:** {res['job_label']}")
                st.write(f"**Riwayat:** {res['repeat_borrower_label']}")

        # Driver Pemicu Risiko
        st.subheader("Driver Pemicu Risiko (Risk Drivers)")
        for driver in res['risk_drivers']:
            badge_type = driver.get('tipe', 'neutral')
            if badge_type == 'success':
                border_col = "#10B981"
                text_col = "#059669"
            elif badge_type == 'warning':
                border_col = "#F59E0B"
                text_col = "#D97706"
            elif badge_type == 'danger':
                border_col = "#EF4444"
                text_col = "#DC2626"
            else:
                border_col = "#3B82F6"
                text_col = "#2563EB"

            st.markdown(f"""
            <div class="driver-item" style="border-left: 4px solid {border_col};">
                <span><strong>{driver['faktor']}:</strong> {driver['kondisi']}</span>
                <span style="color: {text_col}; font-weight: 700;">{driver['efek']}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# MODUL 3: WHAT-IF STRESS TESTING
# ==============================================================================
elif menu == "What-If Stress Testing":
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">What-If Scenario Stress Testing</div>
        <div class="hero-subtitle">Analisis kurva sensitivitas nominal pinjaman dan pengaruh faktor repeat borrower</div>
    </div>
    """, unsafe_allow_html=True)

    col_w1, col_w2 = st.columns([1, 2])
    with col_w1:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.subheader("Parameter Motor Uji")
        w_merk = st.selectbox("Merk Kendaraan:", ["Honda", "Yamaha", "Kawasaki", "Lainnya"], key="w_merk")
        w_usia = st.slider("Usia Kendaraan (Tahun):", 0, 15, 3, key="w_usia")
        w_otr = st.number_input("Harga OTR Pasar (Rp):", min_value=2_000_000, max_value=50_000_000, value=15_000_000, step=1_000_000, key="w_otr")
        w_stnk = st.selectbox("Kepemilikan STNK:", ["A/N Sendiri", "A/N Orang Lain"], key="w_stnk")
        w_pajak = st.selectbox("Status Pajak:", ["Pajak Aktif", "Pajak Tidak Aktif"], key="w_pajak")
        w_job = st.selectbox("Profesi / Pekerjaan:", list(JOB_RISK_FACTORS.keys()), key="w_job")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_w2:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        pinjaman_grid = np.linspace(1_000_000, min(float(w_otr) * 1.0, 20_000_000.0), 30)
        p_m2 = []
        p_m4 = []
        
        for p_val in pinjaman_grid:
            r_first = hitung_skor_underwriting(w_merk, float(w_usia), float(w_otr), p_val, w_stnk, w_pajak, 0, w_job)
            p_m2.append(r_first['prob_final_pct'])
            r_rep = hitung_skor_underwriting(w_merk, float(w_usia), float(w_otr), p_val, w_stnk, w_pajak, 1, w_job)
            p_m4.append(r_rep['prob_final_pct'])

        df_stress = pd.DataFrame({
            'Plafon_Juta': pinjaman_grid / 1_000_000.0,
            'NPL_Nasabah_Baru': p_m2,
            'NPL_Repeat_Borrower': p_m4
        })

        fig_stress = go.Figure()
        fig_stress.add_trace(go.Scatter(
            x=df_stress['Plafon_Juta'], y=df_stress['NPL_Nasabah_Baru'],
            mode='lines+markers', name='Nasabah Baru (Model 2 Baseline)',
            line=dict(color='#DC2626', width=3)
        ))
        fig_stress.add_trace(go.Scatter(
            x=df_stress['Plafon_Juta'], y=df_stress['NPL_Repeat_Borrower'],
            mode='lines+markers', name='Repeat Borrower (Model 4 Champion)',
            line=dict(color='#059669', width=3)
        ))
        
        fig_stress.add_hline(y=5.0, line_dash="dash", line_color="#D97706", annotation_text="Target Batas NPL 5.0%")
        fig_stress.update_layout(
            title="Kurva Sensitivitas Plafon Pinjaman terhadap NPL Rate (%)",
            xaxis_title="Nominal Pinjaman Pokok (Juta Rupiah)",
            yaxis_title="Probabilitas NPL (%)",
            hovermode="x unified",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_stress, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# MODUL 4: BATCH LOAN PROFILER
# ==============================================================================
elif menu == "Batch Loan Profiler":
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">Multi-Loan Batch Application Profiler</div>
        <div class="hero-subtitle">Evaluasi massal portofolio calon debitur sekaligus dengan format terstandarisasi</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    if st.button("Generate 10 Sample Data Aplikasi Debitur"):
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

    uploaded_file = st.file_uploader("Upload File CSV Debitur:", type=['csv'])
    if uploaded_file is not None:
        st.session_state['batch_df'] = pd.read_csv(uploaded_file)
    st.markdown('</div>', unsafe_allow_html=True)

    if 'batch_df' in st.session_state:
        df_eval = st.session_state['batch_df'].copy()
        
        results = []
        for _, row in df_eval.iterrows():
            r = hitung_skor_underwriting(
                merk=str(row['Merk']),
                usia_thn=float(row['Usia_Motor']),
                harga_taksiran_otr=float(row['Harga_OTR']),
                pinjaman_pokok=float(row['Pinjaman']),
                kondisi_stnk=str(row['STNK']),
                pajak_status=str(row['Pajak']),
                is_repeat_borrower=int(row['Repeat_Borrower']),
                pekerjaan=str(row['Pekerjaan'])
            )
            results.append({
                'Prob_NPL_%': r['prob_final_pct'],
                'Grade': r['risk_grade'],
                'Keputusan': r['decision'],
                'LTV_%': r['ltv_pct'],
                'Batas_Plafon_Aman': r['safe_loan_limit_fmt']
            })
            
        res_df = pd.concat([df_eval, pd.DataFrame(results)], axis=1)
        
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.subheader("Hasil Evaluasi Massal Portofolio")
        st.dataframe(res_df, use_container_width=True)
        
        st.subheader("Ringkasan Keputusan Evaluasi Massal")
        c_b1, c_b2, c_b3 = st.columns(3)
        with c_b1:
            st.markdown(f"""
            <div class="pro-metric-card" style="border-color: #A7F3D0;">
                <div class="pro-metric-label">Disetujui Penuh</div>
                <div class="pro-metric-val" style="color: #059669;">{len(res_df[res_df['Grade'].isin(['Grade A', 'Grade B'])])} Debitur</div>
                <div class="pro-metric-sub">Grade A & Grade B</div>
            </div>
            """, unsafe_allow_html=True)
        with c_b2:
            st.markdown(f"""
            <div class="pro-metric-card" style="border-color: #FDE68A;">
                <div class="pro-metric-label">Review / Pangkas Plafon</div>
                <div class="pro-metric-val" style="color: #D97706;">{len(res_df[res_df['Grade'] == 'Grade C'])} Debitur</div>
                <div class="pro-metric-sub">Grade C (Risiko Moderat)</div>
            </div>
            """, unsafe_allow_html=True)
        with c_b3:
            st.markdown(f"""
            <div class="pro-metric-card" style="border-color: #FECDD3;">
                <div class="pro-metric-label">Ditolak / Kritis</div>
                <div class="pro-metric-val" style="color: #DC2626;">{len(res_df[res_df['Grade'] == 'Grade D'])} Debitur</div>
                <div class="pro-metric-sub">Grade D (Severe Moral Hazard)</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# MODUL 5: DATASET CLEAN & DATA EXPLORER
# ==============================================================================
elif menu == "Dataset Clean & Explorer":
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">Dataset Clean & Data Explorer</div>
        <div class="hero-subtitle">Preview data komprehensif, ringkasan statistik deskriptif, dan pusat unduhan dataset resmi</div>
    </div>
    """, unsafe_allow_html=True)

    df_full = load_clean_dataset()

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="pro-metric-card">
            <div class="pro-metric-label">Total Baris Transaksi</div>
            <div class="pro-metric-val">{len(df_full):,}</div>
            <div class="pro-metric-sub">100% Data Valid</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="pro-metric-card">
            <div class="pro-metric-label">Total Fitur / Kolom</div>
            <div class="pro-metric-val">{df_full.shape[1]} Kolom</div>
            <div class="pro-metric-sub">Data Finansial & Agunan</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown("""
        <div class="pro-metric-card" style="border-color: #FECDD3;">
            <div class="pro-metric-label">Prevalensi NPL Riil</div>
            <div class="pro-metric-val" style="color: #DC2626;">6,91%</div>
            <div class="pro-metric-sub">9.640 Debitur Macet</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown("""
        <div class="pro-metric-card" style="border-color: #A7F3D0;">
            <div class="pro-metric-label">Penyaluran Pinjaman</div>
            <div class="pro-metric-val" style="color: #059669;">Rp 274,87 M</div>
            <div class="pro-metric-sub">Rata-rata Rp 1,97 Juta</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    tab_data1, tab_data2, tab_data3, tab_data4 = st.tabs([
        "Preview Data Interaktif",
        "Statistik Deskriptif",
        "Kamus Data & Variabel",
        "Pusat Unduhan Dataset"
    ])

    with tab_data1:
        st.subheader("Filter & Tampilkan Kolom Data")
        
        default_cols = [
            'tanggal_gadai', 'merk_group', 'kondisi_stnk', 'pajak_status',
            'usia_kendaraan_thn', 'nilai_taksiran', 'pinjaman_pokok_efektif',
            'LTV', 'LTV_MAX', 'pekerjaan_group', 'is_repeat_borrower',
            'Days Late', 'NPL_30', 'NPL_90', 'kategori_kolektibilitas', 'NPL_clean'
        ]
        available_cols = [c for c in default_cols if c in df_full.columns]
        all_cols = df_full.columns.tolist()

        col_select = st.multiselect("Pilih Kolom yang Ditampilkan:", all_cols, default=available_cols if available_cols else all_cols[:10])
        
        c_s1, c_s2 = st.columns([1, 2])
        with c_s1:
            row_limit = st.slider("Jumlah Baris Preview:", min_value=10, max_value=1000, value=50, step=10)
        with c_s2:
            search_term = st.text_input("Pencarian Teks (Merk / Profesi / STNK):", "")

        df_display = df_full[col_select] if col_select else df_full
        
        if search_term:
            mask = df_display.astype(str).apply(lambda row: row.str.contains(search_term, case=False).any(), axis=1)
            df_display = df_display[mask]

        st.dataframe(df_display.head(row_limit), use_container_width=True)
        st.caption(f"Menampilkan {min(row_limit, len(df_display))} dari total {len(df_full):,} baris data.")

    with tab_data2:
        st.subheader("Ringkasan Statistik Fitur Numerik")
        num_cols = df_full.select_dtypes(include=[np.number]).columns.tolist()
        if num_cols:
            desc_df = df_full[num_cols].describe().T
            desc_df = desc_df.rename(columns={
                'count': 'Jumlah', 'mean': 'Rata-rata', 'std': 'Standar Deviasi',
                'min': 'Minimum', '25%': 'Q1 (25%)', '50%': 'Median (50%)',
                '75%': 'Q3 (75%)', 'max': 'Maksimum'
            })
            st.dataframe(desc_df, use_container_width=True)
        else:
            st.info("Tidak ada fitur numerik yang terdeteksi.")

    with tab_data3:
        st.subheader("Kamus Data & Definisi Variabel Penelitian")
        st.dataframe(pd.DataFrame(DATA_DICTIONARY), use_container_width=True)

    with tab_data4:
        st.subheader("Pusat Unduhan Format Dataset Lengkap")
        st.write("Silakan pilih format file dataset yang sesuai dengan kebutuhan analisis Anda:")
        
        col_d1, col_d2, col_d3 = st.columns(3)
        
        with col_d1:
            st.markdown("""
            <div class="pro-metric-card">
                <div class="pro-metric-label">Dataset Penuh (CSV Zip)</div>
                <div class="pro-metric-val">10.2 MB</div>
                <div class="pro-metric-sub">139k Baris Lengkap</div>
            </div>
            """, unsafe_allow_html=True)
            if (OUTPUT_DIR / "data_cleaned.zip").exists():
                with open(OUTPUT_DIR / "data_cleaned.zip", "rb") as fz:
                    st.download_button(
                        label="Unduh CSV.ZIP",
                        data=fz.read(),
                        file_name="data_cleaned_pgi_gadai_motor.zip",
                        mime="application/zip",
                        use_container_width=True
                    )

        with col_d2:
            st.markdown("""
            <div class="pro-metric-card" style="border-color: #BFDBFE;">
                <div class="pro-metric-label">Dataset Parquet (Cepat)</div>
                <div class="pro-metric-val" style="color: #2563EB;">8.5 MB</div>
                <div class="pro-metric-sub">Format Binary Columnar</div>
            </div>
            """, unsafe_allow_html=True)
            if (OUTPUT_DIR / "data_cleaned.parquet").exists():
                with open(OUTPUT_DIR / "data_cleaned.parquet", "rb") as fp:
                    st.download_button(
                        label="Unduh Parquet",
                        data=fp.read(),
                        file_name="data_cleaned_pgi_gadai_motor.parquet",
                        mime="application/octet-stream",
                        use_container_width=True
                    )

        with col_d3:
            st.markdown("""
            <div class="pro-metric-card" style="border-color: #A7F3D0;">
                <div class="pro-metric-label">Sample Data Ringkas</div>
                <div class="pro-metric-val" style="color: #059669;">100 KB</div>
                <div class="pro-metric-sub">1.000 Baris Pertama</div>
            </div>
            """, unsafe_allow_html=True)
            if (OUTPUT_DIR / "data_cleaned_sample.csv").exists():
                with open(OUTPUT_DIR / "data_cleaned_sample.csv", "rb") as fs:
                    st.download_button(
                        label="Unduh Sample CSV",
                        data=fs.read(),
                        file_name="data_cleaned_sample_1000_rows.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# MODUL 6: EKONOMETRIKA DIAGNOSTICS
# ==============================================================================
elif menu == "Ekonometrika Diagnostics":
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">Ekonometrika & Model Diagnostics</div>
        <div class="hero-subtitle">Evaluasi Goodness-of-Fit Model 0 s/d Model 4 (NPL 30 & 90 Hari), VIF, dan Pengujian 9 Hipotesis Riset Formal</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    tab_m1, tab_m2, tab_m3 = st.tabs([
        "Perbandingan Model (30 vs 90 Hari)",
        "Pengujian Formal 9 Hipotesis (H1 - H9)",
        "Disparitas Risiko Spasial per Wilayah (H9)"
    ])

    with tab_m1:
        st.subheader("1. Tabel Komparasi Model Ekonometrika (NPL > 30 Hari vs NPL > 90 Hari)")
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            st.markdown("**Target: NPL > 30 Hari (Standar Operasional Gadai)**")
            model_30_df = pd.DataFrame([
                {"Model": "Model 0 (Null)", "Param (k)": 1, "AIC": 70117.86, "Pseudo R²": "0,00%", "ROC-AUC": "0,5000", "PR-AUC": "0,0691"},
                {"Model": "Model 1 (Core)", "Param (k)": 8, "AIC": 69031.72, "Pseudo R²": "1,57%", "ROC-AUC": "0,6002", "PR-AUC": "0,0923"},
                {"Model": "Model 2 (+ LTV_MAX)", "Param (k)": 9, "AIC": 68931.62, "Pseudo R²": "1,71%", "ROC-AUC": "0,6039", "PR-AUC": "0,0924"},
                {"Model": "Model 3 (+ Zona LTV)", "Param (k)": 10, "AIC": 68958.99, "Pseudo R²": "1,68%", "ROC-AUC": "0,6027", "PR-AUC": "0,0926"},
                {"Model": "Model 4 (Champion)", "Param (k)": 10, "AIC": 66775.15, "Pseudo R²": "4,79%", "ROC-AUC": "0,6702", "PR-AUC": "0,1124"}
            ])
            st.dataframe(model_30_df, use_container_width=True)

        with c_m2:
            st.markdown("**Target: NPL > 90 Hari (Standar Kolektibilitas OJK / Bad Debt)**")
            model_90_df = pd.DataFrame([
                {"Model": "Model 0 (Null)", "Param (k)": 1, "AIC": 59897.20, "Pseudo R²": "0,00%", "ROC-AUC": "0,5000", "PR-AUC": "0,0556"},
                {"Model": "Model 1 (Core)", "Param (k)": 8, "AIC": 58900.13, "Pseudo R²": "1,69%", "ROC-AUC": "0,6055", "PR-AUC": "0,0756"},
                {"Model": "Model 2 (+ LTV_MAX)", "Param (k)": 9, "AIC": 58814.73, "Pseudo R²": "1,83%", "ROC-AUC": "0,6093", "PR-AUC": "0,0761"},
                {"Model": "Model 3 (+ Zona LTV)", "Param (k)": 10, "AIC": 58831.00, "Pseudo R²": "1,81%", "ROC-AUC": "0,6088", "PR-AUC": "0,0756"},
                {"Model": "Model 4 (Champion)", "Param (k)": 10, "AIC": 56956.88, "Pseudo R²": "4,94%", "ROC-AUC": "0,6767", "PR-AUC": "0,0939"}
            ])
            st.dataframe(model_90_df, use_container_width=True)

    with tab_m2:
        st.subheader("2. Hasil Pengujian Formal 9 Hipotesis Riset (H1 s/d H9)")
        hyp_df = pd.DataFrame([
            {"ID": "H1", "Hipotesis": "Hubungan kepemilikan STNK dan NPL", "Odds Ratio": "1,710", "Status": "DITERIMA (Signifikan)", "Interpretasi": "STNK orang lain menaikkan odds macet +71% (p < 0.0001)"},
            {"ID": "H2", "Hipotesis": "Hubungan jenis pekerjaan dan NPL", "Odds Ratio": "3,460", "Status": "DITERIMA (Signifikan)", "Interpretasi": "Pengangguran berisiko 3.46x dibanding Karyawan Swasta"},
            {"ID": "H3", "Hipotesis": "Hubungan merk kendaraan dan NPL", "Odds Ratio": "1,050", "Status": "DITERIMA (Signifikan)", "Interpretasi": "Yamaha memiliki odds macet 5% lebih tinggi dibanding Honda"},
            {"ID": "H4", "Hipotesis": "Hubungan usia kendaraan dan NPL", "Odds Ratio": "1,093", "Status": "DITERIMA (Signifikan)", "Interpretasi": "Tiap 1 tahun usia motor menambah odds macet +9.3%"},
            {"ID": "H5", "Hipotesis": "Hubungan status pajak dan NPL", "Odds Ratio": "1,118", "Status": "DITERIMA (Signifikan)", "Interpretasi": "Pajak aktif berkorelasi dengan plafon pinjaman lebih besar"},
            {"ID": "H6", "Hipotesis": "Hubungan nominal pinjaman pokok dan NPL", "Odds Ratio": "1,434", "Status": "DITERIMA (Signifikan)", "Interpretasi": "Tiap kenaikan Rp 1 juta pinjaman menaikkan odds macet +43.4%"},
            {"ID": "H7", "Hipotesis": "Signifikansi fitur LTV_MAX", "Odds Ratio": "0,097", "Status": "DITERIMA (Signifikan)", "Interpretasi": "LTV_MAX kontinu memperbaiki AIC secara signifikan (p < 0.0001)"},
            {"ID": "H8", "Hipotesis": "Signifikansi klasifikasi Zona LTV", "Odds Ratio": "0,680", "Status": "DITERIMA (Signifikan)", "Interpretasi": "Zona LTV signifikan namun inferior dibanding LTV_MAX"},
            {"ID": "H9", "Hipotesis": "Pengaruh spasial / daerah (wilayah/cabang) terhadap NPL", "Odds Ratio": "2,276", "Status": "DITERIMA (Sangat Signifikan)", "Interpretasi": "Daerah berpengaruh sangat signifikan (LR Test p = 9.23e-60, AIC turun 296,6 poin). Nasabah di Garut, Bandung, Subang memiliki risiko 2.2x dibanding Tangerang."}
        ])
        st.dataframe(hyp_df, use_container_width=True)

    with tab_m3:
        st.subheader("3. Disparitas Risiko & Klaster Spasial per Wilayah / Kota (Hipotesis H9)")
        wilayah_csv = OUTPUT_DIR / "tables" / "tabel_analisis_wilayah_npl.csv"
        if wilayah_csv.exists():
            df_wil = pd.read_csv(wilayah_csv)
            st.dataframe(df_wil, use_container_width=True)
            
            fig_wil = px.bar(
                df_wil, x='Wilayah_Kode', y='NPL_30_Rate_Pct',
                color='Risk_Tier',
                color_discrete_map={
                    'Klaster 1: Prime Low-Risk': '#10B981',
                    'Klaster 2: Core Medium': '#F59E0B',
                    'Klaster 3: High Risk Zone': '#DC2626'
                },
                text='NPL_30_Rate_Pct',
                title="Tingkat NPL Portofolio per Wilayah Operasional"
            )
            fig_wil.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            fig_wil.add_hline(y=5.0, line_dash="dash", line_color="#059669", annotation_text="Target Sehat OJK Max 5.0%")
            fig_wil.update_layout(yaxis_title="Tingkat NPL >30 Hari (%)", template="plotly_white")
            st.plotly_chart(fig_wil, use_container_width=True)
        else:
            st.info("File tabel analisis wilayah belum tersedia.")

    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# MODUL 7: MATRIKS KEBIJAKAN CABANG
# ==============================================================================
elif menu == "Matriks Kebijakan Cabang":
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">Matriks Kebijakan Operasional & Rule of Thumb Ahli</div>
        <div class="hero-subtitle">Pedoman formal batas plafon kredit, prosedur verifikasi loket, dan metodologi internasional</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs([
        "Matriks Kebijakan 4 Klaster Pekerjaan",
        "Matriks Kebijakan 3 Klaster Wilayah",
        "Rule of Thumb Metrik Ahli"
    ])

    with tab1:
        st.dataframe(pd.DataFrame(BRANCH_OPERATIONAL_POLICIES), use_container_width=True)

    with tab2:
        df_policy_wil = pd.DataFrame([
            {"Klaster Wilayah": "Klaster 1: Prime (Low Risk)", "Wilayah / Kota": "Tangerang (TGR), Tangerang Kota (TNG), Depok (DPK), Cengkareng (CKG), Cibinong (CBI)", "NPL Rata-rata": "4,12% - 5,19%", "Odds Ratio": "1,00 - 1,28", "Kebijakan Plafon LTV": "Maksimal 45% - 50% OTR (Standar Penuh / Bonus +5%)", "Prosedur Verifikasi": "Verifikasi standar loket normal."},
            {"Klaster Wilayah": "Klaster 2: Core Baseline", "Wilayah / Kota": "Bekasi (BKS), Cikarang (CKR), Soreang (SOR), Karawang (KWG), Serang (SRG), Cianjur (CJR)", "NPL Rata-rata": "5,69% - 7,22%", "Odds Ratio": "1,45 - 1,86", "Kebijakan Plafon LTV": "Standar 45% OTR (STNK Sendiri) / 35% (STNK Orang Lain)", "Prosedur Verifikasi": "Verifikasi fisik nomor rangka/mesin & kontak darurat wajib aktif."},
            {"Klaster Wilayah": "Klaster 3: High Risk Zone", "Wilayah / Kota": "Garut (GRT), Bandung (BDG), Subang (SNG), Sukabumi (SBM)", "NPL Rata-rata": "8,88% - 9,17%", "Odds Ratio": "2,15 - 2,28", "Kebijakan Plafon LTV": "Maksimal 35% - 40% OTR (-5% s/d -10% Pruning)", "Prosedur Verifikasi": "Wajib verifikasi domisili penjamin serumah & early reminder collection DPD 7-14 hari."}
        ])
        st.dataframe(df_policy_wil, use_container_width=True)

    with tab3:
        st.dataframe(pd.DataFrame(EXPERT_RULES_OF_THUMB), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# MODUL 8: GALERI PUBLIKASI RISET
# ==============================================================================
elif menu == "Galeri Publikasi Riset":
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">Galeri Visualisasi Publikasi Riset 300 DPI</div>
        <div class="hero-subtitle">Grafik ekonometrika resmi hasil estimasi data 139.493 debitur</div>
    </div>
    """, unsafe_allow_html=True)

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
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.subheader(title)
            st.image(str(p), use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

