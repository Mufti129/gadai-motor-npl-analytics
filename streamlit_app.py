#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================================================
PUSAT GADAI INDONESIA (PGI) — EXECUTIVE RISK ANALYTICS & SMART UNDERWRITING ENGINE
====================================================================================================
Penulis      : Mukhammad Rekza Mufti (Data Analyst — Divisi Bisnis & Risiko)
Dataset Acuan: 139.493 Transaksi Kredit Valid
Dokumen Acuan: Laporan_Design_Riset_NPL_Gadai_Kendaraan.pdf & README.md
Platform     : Streamlit Community Cloud Ready (100% Logic Parity with Flask API)
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
    page_title="PGI Risk Analytics | Smart Underwriting Engine",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling — Modern, Elegant, Professional Corporate Dashboard
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .main-title {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.025em;
        margin-bottom: 0.25rem;
    }
    
    .sub-title {
        font-size: 0.95rem;
        color: #64748B;
        font-weight: 500;
        margin-bottom: 1.5rem;
    }
    
    .card-kpi {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    .card-kpi-label {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        margin-bottom: 0.4rem;
    }
    
    .card-kpi-val {
        font-size: 1.75rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.2;
    }
    
    .card-kpi-sub {
        font-size: 0.8rem;
        color: #94A3B8;
        margin-top: 0.35rem;
        font-weight: 500;
    }
    
    .decision-container {
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    .risk-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.025em;
        text-transform: uppercase;
    }
    
    .badge-grade-a { background: #DCFCE7; color: #166534; border: 1px solid #86EFAC; }
    .badge-grade-b { background: #FEF9C3; color: #854D0E; border: 1px solid #FDE047; }
    .badge-grade-c { background: #FFEDD5; color: #9A3412; border: 1px solid #FDBA74; }
    .badge-grade-d { background: #FFE4E6; color: #9F1239; border: 1px solid #FDA4AF; }
    
    .status-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .pill-success { background: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; }
    .pill-warning { background: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }
    .pill-danger { background: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }
    .pill-info { background: #EFF6FF; color: #1E40AF; border: 1px solid #BFDBFE; }
    
    .section-header {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1E293B;
        margin-top: 1rem;
        margin-bottom: 0.75rem;
        border-bottom: 2px solid #F1F5F9;
        padding-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# KONFIGURASI GLOBAL, PATH, & AMBANG BATAS RISIKO (IDENTIK 100% DENGAN FLASK)
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
FIGURES_DIR = OUTPUT_DIR / "figures"
MODELS_DIR = OUTPUT_DIR / "models"
TABLES_DIR = OUTPUT_DIR / "tables"

CONFIG_UNDERWRITING = {
    'TARGET_NPL_CUTOFF_PCT': 5.0,        # Batas toleransi NPL korporasi ideal (5,0%)
    'MODERATE_RISK_THRESHOLD_PCT': 7.0,  # Ambang batas risiko moderat (Grade B)
    'HIGH_RISK_THRESHOLD_PCT': 10.0,     # Ambang batas risiko tinggi (Grade C)
    'SEVERE_RISK_THRESHOLD_PCT': 15.0,   # Ambang batas risiko kritis / tolak mutlak (Grade D)
    'MAX_SAFE_LTV_SENDIRI': 0.45,        # Rekomendasi batas aman LTV: STNK Sendiri (45%)
    'MAX_SAFE_LTV_ORANG_LAIN': 0.35,     # Rekomendasi batas aman LTV: STNK Orang Lain (35%)
    'MAX_SAFE_LTV_PAJAK_MATI': 0.35,     # Rekomendasi batas aman LTV: Pajak Mati (35%)
    'MAX_SAFE_LTV_USIA_TUA': 0.35        # Rekomendasi batas aman LTV: Motor Tua >= 7 Thn (35%)
}

# Koefisien Resmi Model 2 (Core + LTV_MAX)
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

# Koefisien Resmi Model 4 (Full Enhanced + Repeat Borrower) — Champion Model
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
        'id': 'TIDAK_ISI',
        'label': 'Tidak Diketahui / Standar',
        'beta': 0.0,
        'or': 1.000,
        'cluster': 'Klaster 2: Core Baseline',
        'cluster_code': 'CORE',
        'ltv_mod': 0.0,
        'policy': 'Skema Standar Cabang (LTV 45% Sendiri / 35% Orang Lain)',
        'verifikasi': 'Prosedur loket standar, cek fisik no rangka/mesin.'
    },
    'KARYAWAN_SWASTA': {
        'id': 'KARYAWAN_SWASTA',
        'label': 'Karyawan Swasta',
        'beta': 0.0,
        'or': 1.000,
        'cluster': 'Klaster 2: Core Baseline',
        'cluster_code': 'CORE',
        'ltv_mod': 0.0,
        'policy': 'Skema Standar Cabang (Baseline Portofolio)',
        'verifikasi': 'Cek ID Card / slip gaji atau mutasi rekening jika tersedia.'
    },
    'PNS': {
        'id': 'PNS',
        'label': 'PNS / ASN / Pegawai BUMN',
        'beta': -0.147041,
        'or': 0.863,
        'cluster': 'Klaster 1: Prime / Preferred',
        'cluster_code': 'PRIME',
        'ltv_mod': 0.05,
        'policy': 'Bonus LTV +5% (Maksimal 50%) & Fast-Track Approval',
        'verifikasi': 'Fast-Track: Lampirkan SK/Kartu Pegawai/Slip Gaji, tanpa survey fisik domisili.'
    },
    'GURU': {
        'id': 'GURU',
        'label': 'Guru / Dosen',
        'beta': -0.428912,
        'or': 0.651,
        'cluster': 'Klaster 1: Prime / Preferred',
        'cluster_code': 'PRIME',
        'ltv_mod': 0.05,
        'policy': 'Bonus LTV +5% (Maksimal 50%) & Fast-Track Approval (Profil Paling Aman)',
        'verifikasi': 'Fast-Track: Verifikasi kartu tanda guru/dosen/NUPTK aktif.'
    },
    'IRT': {
        'id': 'IRT',
        'label': 'Ibu Rumah Tangga (IRT)',
        'beta': 0.002206,
        'or': 1.002,
        'cluster': 'Klaster 2: Core Baseline',
        'cluster_code': 'CORE',
        'ltv_mod': 0.0,
        'policy': 'Skema Standar (Verifikasi Sumber Nafkah Belanja Keluarga)',
        'verifikasi': 'Konfirmasi nomor kontak suami / kepala keluarga serumah.'
    },
    'BURUH': {
        'id': 'BURUH',
        'label': 'Buruh Pabrik / Bangunan',
        'beta': 0.017158,
        'or': 1.017,
        'cluster': 'Klaster 2: Core Baseline',
        'cluster_code': 'CORE',
        'ltv_mod': 0.0,
        'policy': 'Skema Standar (Upah Rutin Mingguan/Bulanan)',
        'verifikasi': 'Konfirmasi tempat kerja buruh/pabrik.'
    },
    'PEDAGANG': {
        'id': 'PEDAGANG',
        'label': 'Pedagang Toko / Kios / Pasar',
        'beta': 0.333499,
        'or': 1.396,
        'cluster': 'Klaster 3: Arus Kas Volatil',
        'cluster_code': 'VOLATILE',
        'ltv_mod': -0.05,
        'policy': 'Pengetatan LTV -5% (Maksimal 40%) & Wajib Cek Nota Usaha',
        'verifikasi': 'Lampirkan foto kios/lapak dagang atau bukti nota transaksi 1 minggu terakhir.'
    },
    'WIRASWASTA': {
        'id': 'WIRASWASTA',
        'label': 'Wiraswasta / Pengusaha',
        'beta': 0.889340,
        'or': 2.434,
        'cluster': 'Klaster 3: Arus Kas Volatil',
        'cluster_code': 'VOLATILE',
        'ltv_mod': -0.05,
        'policy': 'Pengetatan LTV -5% (Maksimal 40%) & Verifikasi Fisik Tempat Usaha',
        'verifikasi': 'Wajib dokumentasi tempat usaha fisik untuk mitigasi risiko volatilitas omzet modal kerja.'
    },
    'PELAJAR': {
        'id': 'PELAJAR',
        'label': 'Pelajar / Mahasiswa',
        'beta': 0.313070,
        'or': 1.368,
        'cluster': 'Klaster 4: Rentan / Moral Hazard',
        'cluster_code': 'VULNERABLE',
        'ltv_mod': -0.05,
        'policy': 'Plafon Dibatasi Maksimal Rp 2.500.000 & STNK Wajib A/N Sendiri',
        'verifikasi': 'Wajib Kartu Tanda Mahasiswa (KTM) & nomor HP orang tua/wali aktif.'
    },
    'BELUM_BEKERJA': {
        'id': 'BELUM_BEKERJA',
        'label': 'Belum / Tidak Bekerja (Pengangguran)',
        'beta': 0.317378,
        'or': 1.374,
        'cluster': 'Klaster 4: Rentan / Moral Hazard',
        'cluster_code': 'VULNERABLE',
        'ltv_mod': -0.10,
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

# ==============================================================================
# HELPER FORMATTING & ESTIMASI RISIKO (100% PERSIS DENGAN FLASK app_server_api.py)
# ==============================================================================
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
    # 1. Normalisasi dan Derivasi Fitur Agunan
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

    # 2. Faktor Risiko Pekerjaan (Delta Logit Overlay)
    job_info = get_job_info(pekerjaan)
    delta_logit_job = job_info['beta']

    # 3. Estimasi Logit Model 2 (Baseline Core + LTV_MAX + Job Delta)
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

    # 4. Estimasi Logit Model 4 (Full Enhanced + Repeat Borrower + Job Delta)
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

    # Model acuan operasional: Model 4 jika repeat borrower teridentifikasi, Model 2 jika nasabah baru
    prob_final = prob_m4_pct if is_rep == 1 else prob_m2_pct

    # 5. Penentuan Peringkat Risiko (Risk Tier & Grade)
    if prob_final < CONFIG_UNDERWRITING['TARGET_NPL_CUTOFF_PCT']:
        risk_tier = "RENDAH (LOW RISK)"
        risk_grade = "Grade A"
        color_hex = "#059669"
        badge_css = "badge-grade-a"
    elif prob_final < CONFIG_UNDERWRITING['MODERATE_RISK_THRESHOLD_PCT']:
        risk_tier = "MODERAT (MEDIUM RISK)"
        risk_grade = "Grade B"
        color_hex = "#D97706"
        badge_css = "badge-grade-b"
    elif prob_final < CONFIG_UNDERWRITING['HIGH_RISK_THRESHOLD_PCT']:
        risk_tier = "TINGGI (HIGH RISK)"
        risk_grade = "Grade C"
        color_hex = "#EA580C"
        badge_css = "badge-grade-c"
    else:
        risk_tier = "KRITIS / SANGAT TINGGI (SEVERE RISK)"
        risk_grade = "Grade D"
        color_hex = "#DC2626"
        badge_css = "badge-grade-d"

    # 6. Batas Aman Plafon dan Rasio LTV Sesuai Kebijakan Risiko + Overlay Profesi
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

    # 7. Analisis Driver Pemicu Risiko
    reasons = []
    risk_drivers = []

    if is_stnk_orang_lain:
        msg = "STNK atas nama Orang Lain (+71% Odds NPL, Moral Hazard)"
        reasons.append(msg)
        risk_drivers.append({"faktor": "Kepemilikan STNK", "kondisi": "A/N Orang Lain", "efek": "+71% Odds Macet", "tipe": "warning"})
    else:
        risk_drivers.append({"faktor": "Kepemilikan STNK", "kondisi": "A/N Sendiri", "efek": "Basis Aman", "tipe": "success"})

    if not is_pajak_aktif:
        msg = "Pajak Kendaraan Tidak Aktif (Menurunkan likuiditas penjualan barang lelang)"
        reasons.append(msg)
        risk_drivers.append({"faktor": "Pajak STNK", "kondisi": "Pajak Tidak Aktif", "efek": "Likuiditas Rendah", "tipe": "warning"})
    else:
        risk_drivers.append({"faktor": "Pajak STNK", "kondisi": "Pajak Aktif", "efek": "Likuiditas Tinggi", "tipe": "info"})

    if usia_thn >= 8:
        msg = f"Usia motor tergolong tua ({usia_thn:.0f} tahun), depresiasi aset tinggi (+9.3%/tahun)"
        reasons.append(msg)
        risk_drivers.append({"faktor": "Usia Kendaraan", "kondisi": f"{usia_thn:.0f} Tahun", "efek": f"+{usia_thn*9.3:.1f}% Akumulasi Risiko", "tipe": "danger"})
    else:
        risk_drivers.append({"faktor": "Usia Kendaraan", "kondisi": f"{usia_thn:.0f} Tahun", "efek": "Depresiasi Terkendali", "tipe": "success"})

    if ltv > safe_ltv_limit:
        msg = f"Rasio LTV aktual ({ltv*100:.1f}%) melampaui batas kebijakan aman ({safe_ltv_limit*100:.0f}%)"
        reasons.append(msg)
        risk_drivers.append({"faktor": "Rasio LTV", "kondisi": f"{ltv*100:.1f}% (Over-limit)", "efek": f"Eksaserbasi Risiko ({ltv*100 - safe_ltv_limit*100:+.1f}%)", "tipe": "danger"})
    else:
        risk_drivers.append({"faktor": "Rasio LTV", "kondisi": f"{ltv*100:.1f}%", "efek": "Dalam Batas Kebijakan", "tipe": "success"})

    if is_rep == 1:
        reasons.append("Status Debitur: Repeat Borrower (Memangkas risiko gagal bayar sebesar 72%)")
        risk_drivers.append({"faktor": "Histori Debitur", "kondisi": "Repeat Borrower (Nasabah Lama)", "efek": "-72% Odds Gagal Bayar", "tipe": "success"})
    else:
        risk_drivers.append({"faktor": "Histori Debitur", "kondisi": "Nasabah Baru", "efek": "Profil Standar", "tipe": "neutral"})

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

    # 8. Sintesis Keputusan Underwriting Cabang & Rencana Aksi (100% Identik dengan Flask)
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
        'color_hex': color_hex,
        'badge_css': badge_css,
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
# SIDEBAR NAVIGATION
# ==============================================================================
with st.sidebar:
    st.markdown("### PUSAT GADAI INDONESIA")
    st.caption("Divisi Bisnis & Manajemen Risiko Kredit")
    st.markdown("---")
    
    menu = st.radio(
        "Navigasi Modul:",
        [
            "Executive Dashboard",
            "Credit Scoring Engine",
            "What-If Stress Testing",
            "Batch Loan Profiler",
            "Ekonometrika Diagnostics",
            "Matriks Kebijakan Cabang",
            "Galeri Publikasi Riset"
        ]
    )
    
    st.markdown("---")
    st.markdown("""
    **Parameter Acuan Portofolio:**
    - Sampel Transaksi: `139.493 Valid`
    - Baseline Prevalensi: `6,91% (9.640 NPL)`
    - Model Champion: `Model 4 (AIC 66.775)`
    - Target Toleransi: `< 5,00% NPL`
    """)

# ==============================================================================
# MODUL 1: EXECUTIVE DASHBOARD
# ==============================================================================
if menu == "Executive Dashboard":
    st.markdown('<div class="main-title">Executive Dashboard Analisis Risiko NPL Gadai Motor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Pusat Gadai Indonesia (PGI) — Ringkasan Portofolio & Model Ekonometrika 2026</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class="card-kpi">
            <div class="card-kpi-label">Total Transaksi Kredit</div>
            <div class="card-kpi-val">139.493</div>
            <div class="card-kpi-sub">100% Data Valid Terverifikasi</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="card-kpi">
            <div class="card-kpi-label">Tingkat NPL Aktual</div>
            <div class="card-kpi-val" style="color: #DC2626;">6,91%</div>
            <div class="card-kpi-sub">9.640 Debitur Gagal Bayar</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="card-kpi">
            <div class="card-kpi-label">Target Toleransi Korporasi</div>
            <div class="card-kpi-val" style="color: #059669;">&lt; 5,00%</div>
            <div class="card-kpi-sub">Ambang Batas Portofolio Sehat</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class="card-kpi">
            <div class="card-kpi-label">Model Champion (Model 4)</div>
            <div class="card-kpi-val" style="color: #2563EB;">67,02%</div>
            <div class="card-kpi-sub">ROC-AUC (+62,7% Precision)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Distribusi Risiko Portofolio Agunan</div>', unsafe_allow_html=True)
    col_left, col_right = st.columns(2)

    with col_left:
        df_stnk = pd.DataFrame({
            'Kondisi STNK': ['A/N Sendiri', 'A/N Orang Lain'],
            'Volume': [63498, 75995],
            'NPL_Rate': [4.94, 8.56]
        })
        fig_stnk = px.bar(
            df_stnk, x='Kondisi STNK', y='NPL_Rate',
            color='Kondisi STNK',
            color_discrete_map={'A/N Sendiri': '#059669', 'A/N Orang Lain': '#DC2626'},
            text='NPL_Rate',
            title="Tingkat NPL berdasarkan Kepemilikan STNK (Moral Hazard +71%)"
        )
        fig_stnk.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig_stnk.add_hline(y=5.0, line_dash="dash", line_color="#D97706", annotation_text="Target Max 5.0%")
        fig_stnk.update_layout(template="plotly_white", yaxis_title="Tingkat NPL (%)", showlegend=False)
        st.plotly_chart(fig_stnk, use_container_width=True)

    with col_right:
        df_merk = pd.DataFrame({
            'Merk': ['Honda', 'Yamaha', 'Kawasaki', 'Lainnya'],
            'NPL_Rate': [6.65, 7.76, 8.15, 7.56],
            'Volume': [106611, 31236, 1117, 529]
        })
        fig_merk = px.bar(
            df_merk, x='Merk', y='NPL_Rate',
            color='Merk',
            color_discrete_sequence=['#2563EB', '#4F46E5', '#7C3AED', '#64748B'],
            text='NPL_Rate',
            title="Tingkat NPL berdasarkan Merk Kendaraan"
        )
        fig_merk.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig_merk.add_hline(y=5.0, line_dash="dash", line_color="#D97706", annotation_text="Target Max 5.0%")
        fig_merk.update_layout(template="plotly_white", yaxis_title="Tingkat NPL (%)", showlegend=False)
        st.plotly_chart(fig_merk, use_container_width=True)

# ==============================================================================
# MODUL 2: CREDIT SCORING ENGINE
# ==============================================================================
elif menu == "Credit Scoring Engine":
    st.markdown('<div class="main-title">Smart Underwriting Credit Scoring Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Penilaian risiko kelayakan kredit calon debitur secara real-time berbasis Model 2 & Model 4</div>', unsafe_allow_html=True)

    col_in, col_res = st.columns([1.1, 1.2])

    with col_in:
        st.markdown('<div class="section-header">Parameter Aplikasi Kredit</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="section-header">Hasil Keputusan Underwriting</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="decision-container" style="background: #FFFFFF; border: 2px solid {res['color_hex']};">
            <div style="font-size: 0.8rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">Probabilitas Gagal Bayar (Estimasi NPL)</div>
            <div style="font-size: 3.25rem; font-weight: 800; color: {res['color_hex']}; line-height: 1.1; margin: 8px 0;">{res['prob_final_pct']:.2f}%</div>
            <div style="margin-bottom: 14px;">
                <span class="risk-badge {res['badge_css']}">{res['risk_grade']} — {res['risk_tier']}</span>
            </div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A; border-top: 1px solid #E2E8F0; padding-top: 12px;">
                REKOMENDASI: <span style="color: {res['color_hex']};">{res['decision']}</span>
            </div>
            <div style="font-size: 0.85rem; color: #475569; margin-top: 6px; text-align: left; background: #F8FAFC; padding: 10px 14px; border-radius: 8px; border: 1px solid #E2E8F0;">
                <strong>Instruksi Operasional:</strong> {res['action_plan']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        c_k1, c_k2, c_k3 = st.columns(3)
        with c_k1:
            st.metric("Rasio LTV Diajukan", f"{res['ltv_pct']:.1f}%")
        with c_k2:
            st.metric("Batas Aman LTV", f"{res['safe_ltv_limit_pct']:.0f}%")
        with c_k3:
            st.metric("Batas Plafon Aman", res['safe_loan_limit_fmt'])

        st.markdown("##### Driver Pemicu Risiko (Risk Factors):")
        for driver in res['risk_drivers']:
            badge_type = driver.get('tipe', 'neutral')
            pill_class = 'pill-success' if badge_type == 'success' else ('pill-warning' if badge_type == 'warning' else ('pill-danger' if badge_type == 'danger' else 'pill-info'))
            st.markdown(f"- **{driver['faktor']}**: `{driver['kondisi']}` — <span class='status-pill {pill_class}'>{driver['efek']}</span>", unsafe_allow_html=True)

# ==============================================================================
# MODUL 3: WHAT-IF STRESS TESTING
# ==============================================================================
elif menu == "What-If Stress Testing":
    st.markdown('<div class="main-title">What-If Scenario Stress Testing</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Analisis kurva sensitivitas nominal pinjaman dan pengaruh faktor repeat borrower</div>', unsafe_allow_html=True)

    col_w1, col_w2 = st.columns([1, 2])
    with col_w1:
        st.markdown('<div class="section-header">Parameter Motor Uji</div>', unsafe_allow_html=True)
        w_merk = st.selectbox("Merk Kendaraan:", ["Honda", "Yamaha", "Kawasaki", "Lainnya"], key="w_merk")
        w_usia = st.slider("Usia Kendaraan (Tahun):", 0, 15, 3, key="w_usia")
        w_otr = st.number_input("Harga OTR Pasar (Rp):", min_value=2_000_000, max_value=50_000_000, value=15_000_000, step=1_000_000, key="w_otr")
        w_stnk = st.selectbox("Kepemilikan STNK:", ["A/N Sendiri", "A/N Orang Lain"], key="w_stnk")
        w_pajak = st.selectbox("Status Pajak:", ["Pajak Aktif", "Pajak Tidak Aktif"], key="w_pajak")
        w_job = st.selectbox("Profesi / Pekerjaan:", list(JOB_RISK_FACTORS.keys()), key="w_job")

    with col_w2:
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
            mode='lines', name='Nasabah Baru (Model 2 Baseline)',
            line=dict(color='#DC2626', width=3)
        ))
        fig_stress.add_trace(go.Scatter(
            x=df_stress['Plafon_Juta'], y=df_stress['NPL_Repeat_Borrower'],
            mode='lines', name='Repeat Borrower (Model 4 Champion)',
            line=dict(color='#059669', width=3)
        ))
        
        fig_stress.add_hline(y=5.0, line_dash="dash", line_color="#D97706", annotation_text="Target Batas NPL 5.0%")
        fig_stress.update_layout(
            template="plotly_white",
            title="Kurva Sensitivitas Plafon Pinjaman terhadap NPL Rate (%)",
            xaxis_title="Nominal Pinjaman Pokok (Juta Rupiah)",
            yaxis_title="Probabilitas NPL (%)",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_stress, use_container_width=True)

# ==============================================================================
# MODUL 4: BATCH LOAN PROFILER
# ==============================================================================
elif menu == "Batch Loan Profiler":
    st.markdown('<div class="main-title">Multi-Loan Batch Application Profiler</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Evaluasi massal portofolio calon debitur sekaligus dengan format terstandarisasi</div>', unsafe_allow_html=True)

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
        st.dataframe(res_df, use_container_width=True)
        
        st.markdown('<div class="section-header">Ringkasan Keputusan Evaluasi Massal</div>', unsafe_allow_html=True)
        c_b1, c_b2, c_b3 = st.columns(3)
        c_b1.metric("Disetujui Penuh", len(res_df[res_df['Grade'].isin(['Grade A', 'Grade B'])]))
        c_b2.metric("Perlu Review / Potong Plafon", len(res_df[res_df['Grade'] == 'Grade C']))
        c_b3.metric("Ditolak (Kritis)", len(res_df[res_df['Grade'] == 'Grade D']))

# ==============================================================================
# MODUL 5: EKONOMETRIKA DIAGNOSTICS
# ==============================================================================
elif menu == "Ekonometrika Diagnostics":
    st.markdown('<div class="main-title">Ekonometrika & Model Diagnostics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Evaluasi Goodness-of-Fit Model 0 s/d Model 4, VIF, dan Pengujian 8 Hipotesis Riset</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">1. Tabel Perbandingan Model Ekonometrika</div>', unsafe_allow_html=True)
    model_df = pd.DataFrame([
        {"Model": "Model 0 (Null Model)", "Param (k)": 1, "Log-Likelihood": -35057.93, "AIC": 70117.86, "BIC": 70127.71, "Pseudo R²": "0,00%", "ROC-AUC": "0,5000", "PR-AUC": "0,0691", "Brier Score": "0,06433"},
        {"Model": "Model 1 (Core Risk)", "Param (k)": 8, "Log-Likelihood": -34507.86, "AIC": 69031.72, "BIC": 69110.49, "Pseudo R²": "1,57%", "ROC-AUC": "0,6002", "PR-AUC": "0,0923", "Brier Score": "0,06385"},
        {"Model": "Model 2 (Core + LTV_MAX)", "Param (k)": 9, "Log-Likelihood": -34456.81, "AIC": 68931.62, "BIC": 69020.23, "Pseudo R²": "1,71%", "ROC-AUC": "0,6039", "PR-AUC": "0,0924", "Brier Score": "0,06383"},
        {"Model": "Model 3 (Core + Zona LTV)", "Param (k)": 10, "Log-Likelihood": -34469.49, "AIC": 68958.99, "BIC": 69057.45, "Pseudo R²": "1,68%", "ROC-AUC": "0,6027", "PR-AUC": "0,0926", "Brier Score": "0,06381"},
        {"Model": "Model 4 (Full Enhanced)", "Param (k)": 10, "Log-Likelihood": -33377.58, "AIC": 66775.15, "BIC": 66873.61, "Pseudo R²": "4,79%", "ROC-AUC": "0,6702", "PR-AUC": "0,1124", "Brier Score": "0,06291"}
    ])
    st.dataframe(model_df, use_container_width=True)

    st.markdown('<div class="section-header">2. Hasil Pengujian Formal 8 Hipotesis Riset</div>', unsafe_allow_html=True)
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
# MODUL 6: MATRIKS KEBIJAKAN CABANG
# ==============================================================================
elif menu == "Matriks Kebijakan Cabang":
    st.markdown('<div class="main-title">Matriks Kebijakan Operasional & Rule of Thumb Ahli</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Pedoman formal batas plafon kredit, prosedur verifikasi loket, dan metodologi internasional</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Matriks Kebijakan 4 Klaster Pekerjaan", "Rule of Thumb Metrik Ahli"])

    with tab1:
        st.dataframe(pd.DataFrame(BRANCH_OPERATIONAL_POLICIES), use_container_width=True)

    with tab2:
        st.dataframe(pd.DataFrame(EXPERT_RULES_OF_THUMB), use_container_width=True)

# ==============================================================================
# MODUL 7: GALERI PUBLIKASI RISET
# ==============================================================================
elif menu == "Galeri Publikasi Riset":
    st.markdown('<div class="main-title">Galeri Visualisasi Publikasi Riset 300 DPI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Grafik ekonometrika resmi hasil estimasi data 139.493 debitur</div>', unsafe_allow_html=True)

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
            st.markdown(f"#### {title}")
            st.image(str(p), use_column_width=True)
            st.markdown("---")

