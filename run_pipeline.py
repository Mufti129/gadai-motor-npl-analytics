"""
Main Entrypoint Script for Gadai Motor Data Cleansing & Preparation Pipeline.
Executes the modular end-to-end workflow and generates ready-to-analyze outputs.

Usage in Terminal / VS Code:
    python run_pipeline.py
    python run_pipeline.py --force-reload
"""

import argparse
import pickle
import time
from pathlib import Path
import pandas as pd

from src.config import (
    CLEANED_DATA_CSV,
    CLEANED_DATA_PKL,
    OUTPUT_DIR
)
from src.loader import load_raw_data
from src.cleaner import remove_anomalies, rectify_target_npl, cast_data_types
from src.normalizer import normalize_categories
from src.feature_engineering import engineer_features
from src.validator import validate_clean_dataset


def run_pipeline(force_reload: bool = False, use_cache: bool = True):
    print("=" * 70)
    print("  GADAI MOTOR DATA CLEANSING & PREPARATION PIPELINE")
    print("=" * 70)
    t_start = time.time()

    # Step 1: Loading
    print("\n[Langkah 1/6] Memuat Data Mentah...")
    df = load_raw_data(use_cache=use_cache, force_reload=force_reload)

    # Step 2: Cleaning Anomalies & Target Rectification
    print("\n[Langkah 2/6] Membersihkan Anomali & Rekonsiliasi Formula Target...")
    df, anomaly_stats = remove_anomalies(df)
    df, mismatch_stats = rectify_target_npl(df)
    df = cast_data_types(df)

    # Step 3: Normalizing Categoricals
    print("\n[Langkah 3/6] Standarisasi Variabel Kategorik & Harmonisasi Teks...")
    df = normalize_categories(df)

    # Step 4: Feature Engineering
    print("\n[Langkah 4/6] Rekayasa Fitur Analisis Risiko (Feature Engineering)...")
    df = engineer_features(df)

    # Step 5: Validation & Programmatic Assertions
    print("\n[Langkah 5/6] Validasi Integritas Data & Audit Otomatis...")
    audit_report = validate_clean_dataset(df)

    # Step 6: Exporting Outputs
    print("\n[Langkah 6/6] Mengekspor Dataset Hasil Cleansing...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Export to CSV
    t_csv = time.time()
    df.to_csv(CLEANED_DATA_CSV, index=False)
    print(f"[Export] CSV berhasil disimpan ke: {CLEANED_DATA_CSV} ({time.time() - t_csv:.2f} detik)")

    # Export to Pickle
    t_pkl = time.time()
    with open(CLEANED_DATA_PKL, "wb") as f:
        pickle.dump(df, f)
    print(f"[Export] Pickle berhasil disimpan ke: {CLEANED_DATA_PKL} ({time.time() - t_pkl:.2f} detik)")

    # Export to Parquet for fast loading
    parquet_path = OUTPUT_DIR / "data_cleaned.parquet"
    try:
        df_pq = df.copy()
        for col in df_pq.select_dtypes(include=["object"]).columns:
            df_pq[col] = df_pq[col].astype(str)
        df_pq.to_parquet(parquet_path, index=False)
        print(f"[Export] Parquet berhasil disimpan ke: {parquet_path}")
    except Exception as e:
        print(f"[Export] Catatan Parquet: {e}")

    # Export to ZIP
    zip_path = OUTPUT_DIR / "data_cleaned.zip"
    try:
        import zipfile
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(CLEANED_DATA_CSV, arcname="data_cleaned.csv")
        print(f"[Export] ZIP berhasil disimpan ke: {zip_path}")
    except Exception as e:
        print(f"[Export] Catatan ZIP: {e}")

    # Export Sample CSV (1.000 rows)
    sample_path = OUTPUT_DIR / "data_cleaned_sample.csv"
    sample_cols = [
        'tanggal_gadai', 'merk_group', 'kondisi_stnk', 'pajak_status',
        'usia_kendaraan_thn', 'nilai_taksiran', 'pinjaman_pokok_efektif',
        'LTV', 'LTV_MAX', 'pekerjaan_group', 'is_repeat_borrower',
        'Days Late', 'NPL_30', 'NPL_90', 'kategori_kolektibilitas', 'NPL_clean'
    ]
    avail_cols = [c for c in sample_cols if c in df.columns]
    df[avail_cols].head(1000).to_csv(sample_path, index=False)
    print(f"[Export] Sample CSV berhasil disimpan ke: {sample_path}")

    # Generate Publication Summary Tables (Tabel 1 & Tabel 2)
    from src.visualization.descriptive_tables import generate_table1_characteristics, generate_table2_npl_distribution
    generate_table1_characteristics(df)
    generate_table2_npl_distribution(df)

    total_time = time.time() - t_start
    print("\n" + "=" * 70)
    print(f" PIPELINE SELESAI DENGAN SUKSES DENGAN TOTAL WAKTU: {total_time:.2f} DETIK")
    print(f" - Baris Akhir Siap Analisis   : {len(df):,} baris")
    print(f" - Jumlah Kolom                : {len(df.columns)} kolom")
    print(f" - Tingkat NPL > 30 Hari       : {audit_report['target_summary']['npl_30_rate_pct']}% ({audit_report['target_summary']['npl_30_count']:,} pinjaman)")
    print(f" - Tingkat NPL > 90 Hari (OJK) : {audit_report['target_summary']['npl_90_rate_pct']}% ({audit_report['target_summary']['npl_90_count']:,} pinjaman)")
    print(f" - Transisi NPL 31-90 Hari     : {audit_report['target_summary']['transition_31_90_rate_pct']}% ({audit_report['target_summary']['transition_31_90_count']:,} pinjaman)")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gadai Motor Data Cleansing Pipeline")
    parser.add_argument("--force-reload", action="store_true", help="Abaikan cache dan baca ulang dari file Excel mentah.")
    parser.add_argument("--no-cache", action="store_true", help="Jangan gunakan cache.")
    args = parser.parse_args()

    use_cache = not args.no_cache
    run_pipeline(force_reload=args.force_reload, use_cache=use_cache)
