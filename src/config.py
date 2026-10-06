"""
Configuration Module for Gadai Motor Pipeline.
Defines file paths, business constants, mapping rules, and econometric model specifications.
"""

from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_FILE = PROJECT_ROOT / "request Mufti_gadaiHP.xlsx"
RAW_SHEET_NAME = "request Mufti"
INFO_SHEET_NAME = "info"

# Cache & Output Paths
CACHE_DIR = PROJECT_ROOT / ".cache"
RAW_CACHE_FILE = CACHE_DIR / "raw_data_cache.pkl"

OUTPUT_DIR = PROJECT_ROOT / "output"
CLEANED_DATA_CSV = OUTPUT_DIR / "data_cleaned.csv"
CLEANED_DATA_PKL = OUTPUT_DIR / "data_cleaned.pkl"
AUDIT_REPORT_JSON = OUTPUT_DIR / "audit_report.json"
EXECUTIVE_REPORT_MD = OUTPUT_DIR / "LAPORAN_ANALISIS_STATISTIK.md"
EXCEL_COMPILATION_XLSX = OUTPUT_DIR / "LAPORAN_KOMPILASI_STATISTIK_GADAI_MOTOR.xlsx"

# Models & Statistical Output Paths
MODELS_OUTPUT_DIR = OUTPUT_DIR / "models"
MODEL_COMPARISON_CSV = MODELS_OUTPUT_DIR / "model_comparison_table.csv"
MODEL_COEFFICIENTS_CSV = MODELS_OUTPUT_DIR / "model_coefficients.csv"
VIF_DIAGNOSTICS_CSV = MODELS_OUTPUT_DIR / "vif_diagnostics.csv"
HYPOTHESIS_RESULTS_JSON = MODELS_OUTPUT_DIR / "hypothesis_results.json"
SENSITIVITY_CSV = MODELS_OUTPUT_DIR / "sensitivity_analysis.csv"
FIGURES_OUTPUT_DIR = OUTPUT_DIR / "figures"
TABLES_OUTPUT_DIR = OUTPUT_DIR / "tables"
TABEL1_CSV = TABLES_OUTPUT_DIR / "tabel1_karakteristik_transaksi.csv"
TABEL2_CSV = TABLES_OUTPUT_DIR / "tabel2_distribusi_npl.csv"
TABEL11_CSV = TABLES_OUTPUT_DIR / "tabel11_analisis_bivariat_lengkap.csv"

# Business Constants & Rules
DAYS_LATE_THRESHOLD = 30
STATUS_NPL_ACTIVE = ["Berjalan", "Proses Lelang"]
STATUS_LUNAS = "Lunas"

# Anomaly Filters
CORRUPT_NAMES_FILTER = ["Nasabah Bintang Gadai"]

# Top Vehicle Brands (rare brands < 50 loans grouped into LAINNYA)
TOP_BRANDS = ["Honda", "Yamaha", "Kawasaki"]

# Reference categories for statistical modeling
REFERENCE_CATEGORIES = {
    "kondisi_stnk": "A/N SENDIRI",
    "pajak_status": "Pajak Tidak Aktif",
    "merk_group": "Honda",
    "pekerjaan_group": "KARYAWAN SWASTA",
    "zona_ltv_std": "36%-40%",
    "skala_pinjaman_std": "Rp 1 - 2 Juta"
}

# Age Bins (in years)
AGE_BINS = [-1, 3, 6, 9, 100]
AGE_LABELS = ["0-3 thn (Sangat Baru)", "4-6 thn (Sedang)", "7-9 thn (Lama)", ">=10 thn (Tua)"]

# Loan Bins (in IDR)
LOAN_BINS = [0, 1_000_000, 2_000_000, float("inf")]
LOAN_LABELS = ["< Rp 1 Juta", "Rp 1 - 2 Juta", "> Rp 2 Juta"]

# Econometric Logistic Regression Formulas (statsmodels syntax)
FORMULA_MODEL_0 = "NPL_clean ~ 1"

FORMULA_MODEL_1 = (
    "NPL_clean ~ "
    "C(kondisi_stnk, Treatment(reference='A/N SENDIRI')) + "
    "C(pajak_status, Treatment(reference='Pajak Tidak Aktif')) + "
    "C(merk_group, Treatment(reference='Honda')) + "
    "usia_kendaraan_thn + "
    "pinjaman_juta"
)

FORMULA_MODEL_2 = FORMULA_MODEL_1 + " + LTV_MAX"

FORMULA_MODEL_3 = (
    FORMULA_MODEL_1 + " + C(zona_ltv_std, Treatment(reference='36%-40%'))"
)

FORMULA_MODEL_4 = FORMULA_MODEL_2 + " + is_repeat_borrower"

FORMULA_JOB_SUBSET = (
    "NPL_clean ~ "
    "C(kondisi_stnk, Treatment(reference='A/N SENDIRI')) + "
    "C(pajak_status, Treatment(reference='Pajak Tidak Aktif')) + "
    "C(merk_group, Treatment(reference='Honda')) + "
    "usia_kendaraan_thn + "
    "pinjaman_juta + "
    "LTV_MAX + "
    "C(pekerjaan_group, Treatment(reference='KARYAWAN SWASTA'))"
)
