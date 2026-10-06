"""
Data Loading & Caching Module.
Handles memory-efficient streaming of raw Excel records and local disk caching.
"""

import pickle
import time
from pathlib import Path
import pandas as pd
import openpyxl

from src.config import RAW_DATA_FILE, RAW_SHEET_NAME, RAW_CACHE_FILE, CACHE_DIR


def load_raw_data(use_cache: bool = True, force_reload: bool = False) -> pd.DataFrame:
    """
    Load raw transaction dataset from Excel or local cache.

    Parameters:
    -----------
    use_cache : bool, default True
        If True, attempts to load from cached .pkl file.
    force_reload : bool, default False
        If True, ignores existing cache and reloads from Excel file.

    Returns:
    --------
    pd.DataFrame
        Raw transactions DataFrame.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if use_cache and not force_reload and RAW_CACHE_FILE.exists():
        t0 = time.time()
        print(f"[Loader] Memuat data mentah dari cache: {RAW_CACHE_FILE.name} ...")
        with open(RAW_CACHE_FILE, "rb") as f:
            df = pickle.load(f)
        print(f"[Loader] Selesai dimuat dalam {time.time() - t0:.2f} detik. Total: {len(df):,} baris × {len(df.columns)} kolom.")
        return df

    if not RAW_DATA_FILE.exists():
        raise FileNotFoundError(f"File data mentah tidak ditemukan: {RAW_DATA_FILE}")

    print(f"[Loader] Membaca file Excel mentah: {RAW_DATA_FILE.name} (Sheet: {RAW_SHEET_NAME}) ...")
    t0 = time.time()

    # Streaming row-by-row using read_only=True for speed and memory efficiency
    wb = openpyxl.load_workbook(str(RAW_DATA_FILE), read_only=True, data_only=True)
    ws = wb[RAW_SHEET_NAME]
    rows = ws.iter_rows(values_only=True)
    headers = next(rows)

    data = list(rows)
    df = pd.DataFrame(data, columns=headers)

    load_time = time.time() - t0
    print(f"[Loader] Pembacaan Excel selesai dalam {load_time:.2f} detik. Total: {len(df):,} baris.")

    # Save to cache
    t_save = time.time()
    with open(RAW_CACHE_FILE, "wb") as f:
        pickle.dump(df, f)
    print(f"[Loader] Cache disimpan ke {RAW_CACHE_FILE} ({time.time() - t_save:.2f} detik).")

    return df
