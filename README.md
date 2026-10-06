# Repositori Analisis Risiko NPL Gadai Motor

Repositori ini memuat rancangan riset terpadu, pipeline pembersihan data (*data cleansing*), rekayasa fitur (*feature engineering*), pemodelan ekonometrika regresi logistik bertingkat (*hierarchical binary logistic regression*), dan modul visualisasi statistik publikasi (*publication figures*) untuk analisis risiko kredit macet (NPL) pembiayaan gadai motor.

Seluruh arsitektur dibangun mengacu pada standar metodologis formal di `Laporan_Design_Riset_NPL_Gadai_Kendaraan.pdf`.

---

## 📁 Struktur Direktori Proyek

```text
Gadai motor/
├── Laporan_Design_Riset_NPL_Gadai_Kendaraan.pdf   # Dokumen metodologi riset formal
├── request Mufti_gadaiHP.xlsx                     # Dataset transaksi mentah (35 MB, 139k baris)
├── requirements.txt                              # Dependensi pustaka Python
├── README.md                                     # Dokumentasi teknis & panduan VS Code
│
├── run_pipeline.py                               # [Tahap 1] CLI: Cleansing & feature engineering
├── run_analysis.py                               # [Tahap 2] CLI: Estimasi model regresi & uji hipotesis
├── run_visualization.py                          # [Tahap 3] CLI: Pembuat grafik publikasi & tabel riset
│
├── src/                                          # Modul kode modular
│   ├── __init__.py                               # Package init
│   ├── config.py                                 # Konfigurasi path, parameter bisnis, & rumus model
│   ├── loader.py                                 # Pemuatan data streaming & auto-caching disk
│   ├── cleaner.py                                # Eliminasi anomali #DIV/0! & koreksi formula NPL
│   ├── normalizer.py                             # Harmonisasi teks (pekerjaan, merk, STNK, pajak)
│   ├── feature_engineering.py                    # Rekayasa fitur risiko (repeat borrower, age bin, dll)
│   ├── validator.py                              # Pengujian integritas data otomatis (assertions)
│   ├── models/                                   # Sub-package pemodelan statistik
│   │   ├── __init__.py
│   │   ├── logistic_regression.py                # Estimasi Model 0 - Model 4 (statsmodels)
│   │   ├── diagnostics.py                        # LR-Test, AIC/BIC, Pseudo R2, ROC/PR AUC, Brier, VIF
│   │   ├── sensitivity.py                        # Sensitivity analysis pada subset pekerjaan
│   │   └── hypothesis_tester.py                  # Pengujian formal hipotesis H1 - H8
│   ├── visualization/                            # Sub-package visualisasi & pelaporan grafis
│   │   ├── __init__.py
│   │   ├── style.py                              # Konfigurasi tema estetika (300 DPI, modern palette)
│   │   ├── exploratory_plots.py                  # Pembuat Gambar 1, 2, 3, 4
│   │   ├── model_plots.py                        # Pembuat Gambar 5 (ROC Curve) & Gambar 6 (Kalibrasi)
│   │   └── descriptive_tables.py                 # Generator Tabel 1, 2, 11 (Univariat & Bivariat)
│   └── utils/                                    # Sub-package utilitas
│       ├── __init__.py
│       └── table_exporter.py                     # Generator tabel CSV & laporan narasi Markdown
│
├── .cache/                                       # Cache lokal data mentah (otomatis dibuat)
│   └── raw_data_cache.pkl
│
└── output/                                       # Direktori hasil pemrosesan & analisis
    ├── data_cleaned.csv                          # Dataset bersih siap analisis (CSV)
    ├── data_cleaned.pkl                          # Dataset bersih format Pickle (buka < 0,2 detik)
    ├── audit_report.json                         # Laporan audit integritas data pra-analisis
    ├── LAPORAN_ANALISIS_STATISTIK.md             # Laporan eksekutif lengkap narasi & tabel riset
    ├── figures/                                  # Gambar grafik beresolusi tinggi (PNG, 300 DPI)
    │   ├── fig1_npl_distribution.png             # Gambar 1: Distribusi NPL (Donut Chart)
    │   ├── fig2_npl_rate_by_categories.png       # Gambar 2: NPL Rate per kategori risiko
    │   ├── fig3_vehicle_age_vs_npl.png           # Gambar 3: Kurva empiris usia motor vs NPL
    │   ├── fig4_simpsons_paradox_ltv_stnk.png    # Gambar 4: Dekomposisi Simpson's Paradox LTV vs STNK
    │   ├── fig5_roc_curves_comparison.png        # Gambar 5: Kurva ROC Model 1, 2, 4
    │   └── fig6_calibration_curves.png           # Gambar 6: Kurva Kalibrasi probabilitas risiko
    ├── tables/                                   # Tabel deskriptif & bivariat riset (CSV)
    │   ├── tabel1_karakteristik_transaksi.csv    # Tabel 1 di PDF (Ringkasan kuantitatif)
    │   ├── tabel2_distribusi_npl.csv             # Tabel 2 di PDF (Frekuensi & % NPL)
    │   └── tabel11_analisis_bivariat_lengkap.csv # Tabel 11 di PDF (Uji Chi-Square, OR 95% CI)
    └── models/                                   # Tabel hasil estimasi statistik (CSV & JSON)
        ├── model_comparison_table.csv            # Tabel 16 di PDF (Perbandingan performa Model 0-4)
        ├── model_coefficients.csv                # Koefisien, p-value, & Odds Ratio seluruh model
        ├── vif_diagnostics.csv                   # Uji multikolinearitas (VIF)
        ├── sensitivity_analysis.csv              # Stabilitas koefisien subset pekerjaan
        └── hypothesis_results.json               # Status & interpretasi hipotesis H1 - H8
```

---

## 🚀 Panduan Menjalankan di VS Code (Step-by-Step)

### 1. Buka Folder di VS Code
1. Buka aplikasi **VS Code**.
2. Pilih menu **File** > **Open Folder...** (atau tekan `Cmd + O` di Mac).
3. Pilih direktori: `/Users/macbookair/Documents/Analisa/Gadai motor`.

### 2. Buka Terminal VS Code
* Tekan shortcut ``Ctrl + ` `` (atau menu **Terminal** > **New Terminal**).

### 3. Install Dependensi Pustaka
```bash
pip install -r requirements.txt
```

---

### 4. Menjalankan 3 Tahapan Analisis (CLI Scripts)

#### Tahap 1: Pembersihan & Rekayasa Fitur Data
```bash
python run_pipeline.py
```
* **Fungsi:** Mengambil data mentah riil `request Mufti_gadaiHP.xlsx` (139.496 baris), mengeliminasi 3 baris anomali sistem (`#DIV/0!` dan akun pengujian IT `Nasabah Bintang Gadai`) menyisakan 139.493 transaksi riil valid, mengoreksi formula NPL (16 baris *Proses Lelang* $\rightarrow$ 1, 1 baris *Lunas* $\rightarrow$ 0), standarisasi kategori, membentuk fitur analitik, dan mengekspor `output/data_cleaned.csv`.
* **Kecepatan:** ~25 detik (pertama kali); ~2,8 detik (selanjutnya via cache).

#### Tahap 2: Pemodelan Statistik Regresi Logistik & Ekonometrika
```bash
python run_analysis.py
```
* **Fungsi:** 
  - Mengestimasi **Model 0 (Null)**, **Model 1 (Core)**, **Model 2 (+ LTV_MAX)**, **Model 3 (+ Zona LTV)**, dan **Model 4 (+ Repeat Borrower)**.
  - Menghitung metrik performa komparatif: Log-Likelihood, Likelihood Ratio Test, AIC, BIC, McFadden Pseudo $R^2$, ROC-AUC, PR-AUC, dan Brier Score.
  - Menghitung uji multikolinearitas (**VIF**) dan analisis sensitivitas (*pekerjaan*).
  - Menguji 8 hipotesis riset (**H1 – H8**) secara formal.
  - Mengekspor seluruh tabel CSV ke `output/models/` dan laporan narasi lengkap ke `output/LAPORAN_ANALISIS_STATISTIK.md`.
* **Kecepatan:** ~7,8 detik.

#### Tahap 3: Pembuatan Grafik Publikasi (300 DPI) & Tabel Riset
```bash
python run_visualization.py
```
* **Fungsi:**
  - Menghasilkan 6 gambar publikasi berkualitas tinggi di `output/figures/` (Gambar 1–6 di Bab 17 PDF).
  - Menghasilkan tabel deskriptif univariat & bivariat (Tabel 1, 2, 11) di `output/tables/`.
* **Kecepatan:** ~6,3 detik.

---

## 📊 Ringkasan Hasil Pemodelan (Tabel 16 Riset)

| Model Name | Parameters ($k$) | AIC | BIC | McFadden Pseudo $R^2$ | ROC-AUC | PR-AUC | Catatan Riset |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Model 0 (Null Model)** | 1 | 70.117,9 | 70.127,7 | 0,0000 | 0,5000 | 0,0691 | Baseline tanpa prediktor |
| **Model 1 (Core Risk Model)** | 8 | 69.031,7 | 69.110,5 | 0,0157 | 0,6002 | 0,0923 | STNK, Pajak, Merk, Usia, Pinjaman |
| **Model 2 (Core + LTV_MAX)** | 9 | **68.931,6** | **69.020,2** | **0,0171** | **0,6039** | **0,0924** | Mengungguli Model 1 ($\Delta\text{AIC} = -100,1$) |
| **Model 3 (Core + Zona LTV)** | 10 | 68.959,0 | 69.057,5 | 0,0168 | 0,6027 | 0,0926 | Lebih inferior dibanding LTV_MAX kontinu |
| **Model 4 (Full Enhanced)** | 10 | **66.775,2** | **66.873,6** | **0,0479** | **0,6702** | **0,1124** | **Model Terbaik:** Integrasi *Repeat Borrower* |

---

## 🔍 Temuan Kunci & Efek Ukuran (Odds Ratio Model 2)

* **Kepemilikan STNK (H1):** STNK atas nama orang lain meningkatkan odds kredit macet sebesar **71%** ($\text{OR} = 1,71$, 95% CI: 1,63–1,80, $p < 10^{-100}$).
* **Nominal Pinjaman (H6):** Setiap kenaikan Rp 1.000.000 nominal pinjaman pokok meningkatkan odds kredit macet sebesar **43,4%** ($\text{OR} = 1,43$, $p < 10^{-85}$).
* **Usia Kendaraan (H4):** Setiap penambahan 1 tahun umur motor meningkatkan odds kredit macet sebesar **9,3%** ($\text{OR} = 1,093$, $p < 10^{-67}$).
* **Efek Repeat Borrower (Model 4):** Nasabah yang pernah bertransaksi sebelumnya memiliki odds macet **72% lebih rendah** ($\text{OR} = 0,28$) dibanding nasabah baru (NPL Rate 2,7% vs 9,2%).
* **Diagnostik Multikolinearitas (VIF):** Seluruh variabel memiliki nilai $\text{VIF} < 2,3$ (aman dari multikolinearitas).
* **Uji Sensitivitas Pekerjaan:** Deviasi koefisien variabel inti pada subset pekerjaan $< 8\%$ (estimasi terbukti stabil dan tidak mengalami distorsi akibat 82% *missingness*).
