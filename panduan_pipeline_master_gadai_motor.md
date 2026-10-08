# PANDUAN PENGGUNAAN MASTER PIPELINE SISTEM ANALISIS RISIKO NPL GADAI MOTOR

**Skrip Master**: [`pipeline_master_analisis_gadai_motor.py`](file:///Users/macbookair/Documents/Analisa/Gadai%20motor/pipeline_master_analisis_gadai_motor.py)  
**Dokumen Desain Riset**: `Laporan_Design_Riset_NPL_Gadai_Kendaraan.pdf`  
**Dataset Utama**: `request Mufti_gadaiHP.xlsx` (Sheet: *request Mufti*, 139.496 baris mentah)  
**Entitas**: Analisis Bisnis & Manajemen Risiko Kredit Gadai Kendaraan Bermotor  
**Penulis**: Mukhammad Rekza Mufti (Data Analyst — Divisi Bisnis & Risiko)

---

## 1. PENDAHULUAN & TUJUAN SISTEM

Skrip master [`pipeline_master_analisis_gadai_motor.py`](file:///Users/macbookair/Documents/Analisa/Gadai%20motor/pipeline_master_analisis_gadai_motor.py) dirancang sebagai **sistem analitik risiko kredit komprehensif, terpadu, dan modular**. Seluruh tahapan riset pemodelan risiko kredit macet (*Non-Performing Loan / NPL*) disatukan ke dalam satu alur kerja berbasis antarmuka terminal interaktif (*Interactive CLI*).

Mengadopsi arsitektur teruji pada `pipeline_master_analisis_upc_pgi.py`, sistem ini bekerja mulai dari data transaksi mentah (*raw streaming Excel*), melakukan audit kesehatan data (*data cleansing & integrity assertions*), rekayasa fitur prediktor (*feature engineering*), analisis deskriptif univariat & bivariat (Chi-Square & Odds Ratio), estimasi 5 model ekonometrika regresi logistik bertingkat (*hierarchical logit Model 0 - Model 4*), uji diagnostik multikolinearitas (VIF), analisis sensitivitas *missingness* pekerjaan, evaluasi formal 8 hipotesis riset (H1–H8), pembuatan 6 grafik publikasi resolusi tinggi (300 DPI), mesin simulasi cerdas penilaian kredit (*Smart Underwriting Credit Scoring Engine*), hingga ekspor laporan resmi multi-format (Markdown & Excel Multi-Sheet).

---

## 2. CARA MENJALANKAN DI TERMINAL VSCODE / MACOS

### A. Mode Interaktif (Default / Direkomendasikan)
1. Buka aplikasi **VS Code** dan buka folder `/Users/macbookair/Documents/Analisa/Gadai motor`.
2. Buka terminal terintegrasi (Pintasan: `` Ctrl + ` ``).
3. Jalankan perintah:
   ```bash
   python3 pipeline_master_analisis_gadai_motor.py
   ```
4. Menu pilihan angka `0` sampai `9` akan muncul di layar terminal. Ketik angka modul yang ingin dijalankan lalu tekan `Enter`.

### B. Mode Eksekusi Batch Otomatis (Non-Interaktif End-to-End)
Jika ingin menjalankan seluruh pipeline dari modul 1 sampai modul 8 secara berurutan dalam satu kali jalan tanpa konfirmasi tombol:
```bash
python3 pipeline_master_analisis_gadai_motor.py --batch
```

### C. Mode Paksa Muat Ulang Data Mentah (Force Reload)
Jika berkas Excel mentah diperbarui dan Anda ingin mengabaikan cache lokal:
```bash
python3 pipeline_master_analisis_gadai_motor.py --force-reload
```

---

## 3. PANDUAN LENGKAP MENU & MODUL ANALISIS

Tampilan antarmuka utama CLI:

```text
===============================================================================================
    🚀 MASTER PIPELINE SISTEM ANALISIS RISIKO NPL GADAI MOTOR & PEMODELAN EKONOMETRIKA
===============================================================================================
  Status Database : 139.493 Transaksi Bersih (Tingkat NPL: 6,91% / 9.640 Macet)
  Direktori Output: /Users/macbookair/Documents/Analisa/Gadai motor/output
-----------------------------------------------------------------------------------------------
  [PILIHAN MODUL ANALISIS & PIPELINE]
   1. Pipeline Data Cleansing & Audit Integritas Data (139.496 -> 139.493 + Koreksi Target)
   2. Analisis Deskriptif Univariat & Profil Portofolio Gadai Motor (Tabel 1 & Tabel 2)
   3. Analisis Bivariat & Uji Risiko Kredit (Uji Chi-Square, Odds Ratio Empiris, & Simpson's Paradox)
   4. Pemodelan Ekonometrika Regresi Logistik Bertingkat (Hierarchical Logit Model 0 - Model 4)
   5. Diagnostik Lanjutan, Uji Sensitivitas, & Pengujian 8 Hipotesis Riset Formal (H1 - H8)
   6. Generator Visualisasi Statistik Publikasi Resolusi Tinggi (Gambar 1 - 6 PNG 300 DPI)
   7. Smart Underwriting Credit Scoring & Simulasi Interaktif Penilaian Risiko Kredit
   8. Kompilasi Laporan Lengkap & Ekspor Dokumen Multi-Format (Markdown & Excel Multi-Sheet)
   9. Jalankan Seluruh Pipeline Sekaligus (Batch All-in-One Execution)
   0. Keluar dari Program (Exit)
===============================================================================================
```

---

### Menu 1: Pipeline Data Cleansing & Audit Integritas Data
* **Fungsi**:
  1. Membaca 139.496 baris dari sheet `request Mufti` menggunakan pembacaan *streaming memory-efficient*.
  2. Mengeliminasi 3 baris anomali pengujian sistem (`#DIV/0!` dan akun dummy `Nasabah Bintang Gadai`) sehingga tersisa **139.493 transaksi valid**.
  3. Mengoreksi kesalahan formula target NPL Excel:
     - **16 baris** transaksi berstatus `Proses Lelang` yang menunggak $> 30$ hari tetapi bernilai $0$ dikoreksi menjadi $1$ (*Kredit Macet*).
     - **1 baris** transaksi berstatus `Lunas` (Faktur: `11208251226017`) yang salah bernilai $1$ dikoreksi menjadi $0$ (*Kredit Lancar*).
  4. Standarisasi tipe data numerik, rasio LTV, dan parsing tanggal.
  5. Harmonisasi teks kategorik: Pekerjaan (8 kelompok bisnis), Merk (Honda, Yamaha, Kawasaki, Lainnya), Kondisi STNK (`A/N SENDIRI` vs `A/N ORANG LAIN`), dan Pajak STNK (`Pajak Aktif` vs `Pajak Tidak Aktif`).
  6. Membentuk fitur turunan analitik: `is_repeat_borrower`, `pinjaman_juta`, `usia_kendaraan_bin`, dan `zona_ltv_std`.
  7. Validasi programmatic assertions otomatis dan menyimpan laporan audit di `output/audit_report.json`.
* **Output File**: `output/data_cleaned.csv`, `output/data_cleaned.pkl`, `output/audit_report.json`.

---

### Menu 2: Analisis Deskriptif Univariat & Profil Portofolio Gadai Motor
* **Fungsi**: Menghitung ringkasan kuantitatif portofolio pinjaman dan profil frekuensi risiko NPL.
* **Temuan Utama**:
  - **Total Portofolio Pinjaman**: **Rp 274,87 Miliar** tersebar di 139.493 kontrak.
  - **Rata-rata Plafon Pinjaman**: **Rp 1.971.200** (Median: Rp 1.800.000).
  - **Rata-rata Usia Motor**: **6,5 tahun** (Median: 7,0 tahun).
  - **Rasio LTV Rata-rata**: **33,21%**.
  - **Tingkat NPL Keseluruhan**: **6,91%** (9.640 kontrak macet vs 129.853 kontrak lancar).
* **Output File**:
  - `output/tables/tabel1_karakteristik_transaksi.csv` (Ringkasan statistik min, max, mean, std, Q1, median, Q3, IQR).
  - `output/tables/tabel2_distribusi_npl.csv` (Frekuensi dan proporsi kredit lancar vs macet).

---

### Menu 3: Analisis Bivariat & Uji Risiko Kredit (Chi-Square & Odds Ratio Empiris)
* **Fungsi**: Menilai hubungan masing-masing faktor risiko secara bivariat terhadap tingkat default pinjaman dan mengurai paradoks statistik.
* **Temuan Kunci**:
  - **Kepemilikan STNK**: NPL STNK Orang Lain (**8,85%**) jauh lebih tinggi daripada STNK Sendiri (**5,42%**) dengan Crude Odds Ratio univariat $\text{OR} = 1,69$ ($p < 10^{-100}$).
  - **Usia Kendaraan**: NPL meningkat secara monotonik seiring bertambahnya usia motor: $\le 3$ tahun (**4,64%**) $\rightarrow$ $4-6$ tahun (**6,26%**) $\rightarrow$ $7-9$ tahun (**7,58%**) $\rightarrow$ $\ge 10$ tahun (**8,98%**).
  - **Skala Pinjaman**: Pinjaman $> \text{Rp 2 Juta}$ memiliki tingkat macet **8,45%** vs pinjaman $< \text{Rp 1 Juta}$ sebesar **5,43%**.
  - **Dekomposisi Simpson's Paradox**:
    * Mengapa motor STNK Orang Lain tampak memiliki rata-rata LTV lebih rendah (38,8% vs 40,2%), namun NPL-nya jauh lebih tinggi (8,85% vs 5,42%)?
    * Fenomena ini disebabkan oleh *endogenous risk aversion* dari petugas cabang yang sengaja menekan LTV lebih rendah saat STNK atas nama pihak ketiga. Namun, kompensasi LTV tersebut belum cukup untuk menahan risiko moral hazard yang mendominasi!
* **Output File**: `output/tables/tabel11_analisis_bivariat_lengkap.csv`.

---

### Menu 4: Pemodelan Ekonometrika Regresi Logistik Bertingkat (Model 0 - Model 4)
* **Fungsi**: Mengestimasi lima model regresi logistik multivariat bertingkat (*hierarchical logit*) untuk mengisolasi efek murni tiap prediktor risiko setelah mengontrol faktor pembaur (*confounders*).
* **Hasil Komparasi Model (Tabel 16 Riset)**:

| Model Name | Parameters ($k$) | Log-Likelihood | AIC | BIC | McFadden Pseudo $R^2$ | ROC-AUC | PR-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Model 0 (Null Model)** | 1 | -35.057,93 | 70.117,86 | 70.127,71 | 0,0000 | 0,5000 | 0,0691 |
| **Model 1 (Core Model)** | 8 | -34.507,86 | 69.031,72 | 69.110,49 | 0,0157 | 0,6002 | 0,0923 |
| **Model 2 (Core + LTV_MAX)** | 9 | -34.456,81 | **68.931,62** | **69.020,23** | **0,0171** | **0,6039** | **0,0924** |
| **Model 3 (Core + Zona LTV)** | 10 | -34.469,49 | 68.958,99 | 69.057,45 | 0,0168 | 0,6027 | 0,0926 |
| **Model 4 (Full Enhanced)** | 10 | -33.377,58 | **66.775,15** | **66.873,61** | **0,0479** | **0,6702** | **0,1124** |

#### Analisis Mendalam: Mengapa Model 4 Memiliki Tepat 10 Parameter ($k=10$)?
* **Konfirmasi**: Model 4 memiliki **tepat 10 parameter**, terdiri dari 1 konstanta intercept ($\beta_0$) + 9 koefisien regresi prediktor ($\beta_1$ s/d $\beta_9$).
* **Rincian ke-10 Parameter Tersebut**:
  1. $\beta_0$: **Intercept** (Konstanta acuan: STNK Sendiri, Pajak Mati, Honda, Nasabah Baru)
  2. $\beta_1$: **STNK A/N Orang Lain** (1 dummy, ref: A/N Sendiri)
  3. $\beta_2$: **Pajak Aktif** (1 dummy, ref: Pajak Tidak Aktif)
  4. $\beta_3$: **Merk Kawasaki** (1 dummy, ref: Honda)
  5. $\beta_4$: **Merk Lainnya** (1 dummy, ref: Honda)
  6. $\beta_5$: **Merk Yamaha** (1 dummy, ref: Honda)
  7. $\beta_6$: **Usia Kendaraan (thn)** (1 prediktor kontinu)
  8. $\beta_7$: **Pinjaman Pokok (Juta Rp)** (1 prediktor kontinu)
  9. $\beta_8$: **LTV_MAX** (1 prediktor rasio kontinu)
  10. $\beta_9$: **is_repeat_borrower** (1 dummy, ref: Nasabah Baru)
* **Perbedaan dengan Usulan Awal PDF Riset**:
  - Pada PDF Halaman 5-6, rancangan awal Model 4 diusulkan sebagai: $NPL \sim Core + LTV\_MAX + zona\_ltv$.
  - Namun dokumen PDF Halaman 6 menegaskan: *"Model 4 hanya digunakan jika audit konseptual dan diagnostik menunjukkan bahwa ltv_max dan zona_ltv membawa informasi berbeda serta tidak menimbulkan masalah multikolinearitas."*
  - Karena memasukkan `zona_ltv` bersama `LTV_MAX` memicu kolinearitas dan variabel `pekerjaan` memiliki missing rate 81,8% (sehingga diuji terpisah pada Sensitivity Analysis), model diperkaya dengan prediktor perilaku: **`is_repeat_borrower`**.
  - Hasilnya, dengan $k=10$ parameter, Model 4 memangkas AIC sebesar **2.156 poin** (dari 68.931 ke 66.775) dan menaikkan ROC-AUC dari **0,6039** menjadi **0,6702**.
* **Perbedaan $df\_model$ vs $k$**:
  - Di `statsmodels`, `model.df_model = 9` (hanya menghitung derajat kebebasan prediktor non-konstanta).
  - Pada rumus $AIC = 2k - 2\ln L$ dan $BIC = k\ln N - 2\ln L$, parameter $k$ wajib menghitung konstanta/intercept, sehingga $k = df\_model + 1 = 9 + 1 = \mathbf{10 \text{ parameter}}$.

#### Ringkasan Estimasi Parameter & Odds Ratio Model 1 sampai Model 4:

* **Model 1 (Core Model, $k=8$)**:
  - Intercept ($\beta = -4,1004$, $\text{OR} = 0,017$, $p < 10^{-100}$)
  - STNK Orang Lain ($\beta = +0,6400$, $\text{OR} = 1,896$, $p < 10^{-100}$)
  - Pajak Aktif ($\beta = +0,0691$, $\text{OR} = 1,072$, $p = 0,0017$)
  - Kawasaki ($\beta = -0,2305$, $\text{OR} = 0,794$, $p = 0,0428$)
  - Merk Lainnya ($\beta = -0,0067$, $\text{OR} = 0,993$, $p = 0,9680$)
  - Yamaha ($\beta = +0,0709$, $\text{OR} = 1,074$, $p = 0,0048$)
  - Usia Kendaraan ($\beta = +0,0739$, $\text{OR} = 1,077$, $p < 10^{-50}$)
  - Pinjaman Juta ($\beta = +0,2941$, $\text{OR} = 1,342$, $p < 10^{-65}$)

* **Model 2 (Core + LTV_MAX, $k=9$)**:
  - Model 1 + LTV_MAX ($\beta = -2,3284$, $\text{OR} = 0,097$, $p < 10^{-24}$).
  - Menurunkan AIC sebesar 100,1 poin vs Model 1.

* **Model 3 (Core + Zona LTV, $k=10$)**:
  - Model 1 + Zona LTV 41%-50% ($\beta = +0,1427$, $\text{OR} = 1,153$, $p < 0,001$) + Zona LTV <=35% ($\beta = -0,1843$, $\text{OR} = 0,832$, $p < 10^{-12}$).
  - Lebih inferior dibanding Model 2 kontinu ($\text{AIC} = 68.958,99$ vs $68.931,62$).

* **Model 4 (Full Enhanced Model, $k=10$)**:
  - Model 2 + Repeat Borrower ($\beta = -1,2399$, $\text{OR} = 0,289$, $p < 10^{-100}$).
  - **Champion Model**: Menghemat 2.156 poin AIC dan meningkatkan ROC-AUC ke 0,6702.

* **Output File**: `output/models/model_comparison_table.csv` dan `output/models/model_coefficients.csv`.

---

### Menu 5: Diagnostik Lanjutan, Uji Sensitivitas, & Evaluasi 8 Hipotesis Riset
* **Fungsi**: Memastikan validitas model dan menguji secara formal 8 hipotesis metodologi riset (H1 s/d H8).
* **Diagnostik Multikolinearitas (VIF)**:
  - Seluruh variabel memiliki nilai $\text{VIF} < 2,3$ (Pinjaman: 2,21; Usia: 2,07; LTV_MAX: 1,50). Model terbukti **bebas dari masalah multikolinearitas**.
* **Analisis Sensitivitas Missingness Pekerjaan**:
  - Kolom profesi debitur memiliki kekosongan data (*missing rate*) sebesar 81,8%.
  - Pengujian sensitivitas membuktikan deviasi koefisien variabel inti antara populasi penuh vs subset berpekerjaan lengkap adalah $< 8\%$. Estimasi model terbukti kokoh (*robust*).
* **Status Pengujian 8 Hipotesis Riset**:
  1. **H1 (Kepemilikan STNK)**: DITERIMA ($\text{OR} = 1,71$, $p < 10^{-100}$).
  2. **H2 (Pekerjaan Debitur)**: DITERIMA pada subset (Kelompok belum bekerja/menganggur memiliki odds risiko $3,46\times$ lebih tinggi dibanding karyawan swasta).
  3. **H3 (Merk Kendaraan)**: DITERIMA (Yamaha memiliki risiko sedikit lebih tinggi dibanding Honda, $\text{OR} = 1,05$).
  4. **H4 (Usia Kendaraan)**: DITERIMA (+9,3% per tahun usia motor, $p < 10^{-67}$).
  5. **H5 (Status Pajak)**: DITERIMA (Berkorelasi dengan interaksi plafon pinjaman).
  6. **H6 (Besaran Pinjaman)**: DITERIMA (+43,4% per Rp 1 Juta, $p < 10^{-85}$).
  7. **H7 (LTV_MAX Kontinu)**: DITERIMA ($\Delta\text{AIC} = -100,1$, Likelihood Ratio Test $p < 10^{-23}$).
  8. **H8 (Superioritas LTV Kontinu vs Zona Diskrit)**: DITERIMA (Model 2 kontinu mengungguli Model 3 kategorik).
* **Output File**: `output/models/vif_diagnostics.csv`, `output/models/sensitivity_analysis.csv`, `output/models/hypothesis_results.json`.

---

### Menu 6: Generator Visualisasi Statistik Publikasi Resolusi Tinggi (300 DPI)
* **Fungsi**: Menghasilkan 6 gambar diagram dan kurva statistik standar publikasi jurnal dan laporan direksi:
  - **Gambar 1 (`fig1_npl_distribution.png`)**: Donut chart proporsi kredit lancar (93,09%) vs macet (6,91%).
  - **Gambar 2 (`fig2_npl_rate_by_categories.png`)**: Horizontal bar chart perbandingan tingkat NPL per sub-kategori risiko terhadap baseline portofolio.
  - **Gambar 3 (`fig3_vehicle_age_vs_npl.png`)**: Kurva empiris usia kendaraan vs tingkat NPL dengan kurva logistik fit.
  - **Gambar 4 (`fig4_simpsons_paradox_ltv_stnk.png`)**: Visualisasi fenomena Simpson's Paradox pada relasi LTV dan STNK.
  - **Gambar 5 (`fig5_roc_curves_comparison.png`)**: Komparasi kurva ROC Model 1, Model 2, dan Model 4.
  - **Gambar 6 (`fig6_calibration_curves.png`)**: Diagram kalibrasi probabilitas risiko (*Reliability Diagram*).
* **Output File**: Seluruh gambar tersimpan di `output/figures/` dengan format PNG 300 DPI.

---

#### Menu 7: Smart Underwriting Credit Scoring & Simulasi Interaktif Penilaian Risiko Kredit
* **Fungsi**: Mesin kalkulasi risiko *real-time* yang dapat digunakan oleh analis kredit atau pimpinan cabang dalam mengevaluasi calon peminjam. Dilengkapi dengan **Job Risk Overlay Policy (Delta Logit)** berbasis estimasi empiris.
* **Pilihan Sub-Menu**:
  1. **Single Loan Underwriting Calculator**:
     - Masukkan rincian calon nasabah: Merk motor, Usia motor (tahun), Taksiran harga pasar OTR (Rp), Pinjaman yang diajukan (Rp), Kondisi STNK (Sendiri / Orang Lain), Status Pajak (Aktif / Tidak Aktif), Status Nasabah (Baru / Repeat), serta **Pekerjaan / Profesi Debitur (Opsional: Guru, PNS, Swasta, IRT, Buruh, Pedagang, Wiraswasta, Mahasiswa, Belum Bekerja, atau Netral)**.
     - Sistem langsung menghitung LTV, probabilitas default NPL, Risk Tier (Rendah / Moderat / Tinggi / Kritis), Plafon Pinjaman Aman (dengan penyesuaian LTV profesi & batas plafon keras Rp 2,5 Juta untuk klaster rentan), serta Rekomendasi Keputusan Cabang:
       * `APPROVED (DISETUJUI PENUH)`
       * `APPROVED (DISETUJUI — RISIKO MODERAT)`
       * `CONDITIONAL APPROVAL (SETUJUI DENGAN PEMANGKASAN PLAFON)`
       * `CONDITIONAL APPROVAL (MITIGASI KHUSUS NASABAH LAMA)`
       * `HIGH RISK REVIEW (BUTUH PERSETUJUAN KEPALA CABANG / SURVEY)`
       * `REJECTED (TOLAK PENGAJUAN)` — Otomatis menolak jika klaster rentan (Mahasiswa/Pengangguran) menggunakan STNK orang lain (*Fatal Moral Hazard*).
  2. **What-If Scenario Stress Testing**: Simulasi elastisitas peningkatan pinjaman pokok (Rp 2 Juta s/d Rp 10 Juta) terhadap probabilitas NPL untuk debitur baru vs debitur lama dengan pilihan profesi debitur.
  3. **Safe LTV Policy Matrix**: Panduan matriks kebijakan batas aman LTV maksimum cabang berdasarkan kombinasi STNK $\times$ Pajak $\times$ Usia Kendaraan.
  4. **Batch Multi-Loan Application Profiler**: Pengujian otomatis 5 studi kasus tipikal calon debitur dari berbagai klaster profesi.
  5. **Konfigurasi Parameter Risk Scoring Engine**: Menyesuaikan parameter batas cutoff target NPL dan batas plafon LTV.
  6. **Matriks Kebijakan Operasional Cabang**: Tabel SOP 4 klaster profesi debitur (Prime, Core Baseline, Volatile Cashflow, Vulnerable).
  7. **Pedoman Rule of Thumb Ahli**: Telaah panduan ambang batas ahli ekonometrika untuk 7 metrik evaluasi model.

---

### Menu 8: Kompilasi Laporan Lengkap & Ekspor Dokumen Multi-Format
* **Fungsi**: Menghasilkan dokumen laporan terpadu untuk kebutuhan manajemen dan audit:
  1. **Laporan Narasi Eksekutif Markdown**: `output/LAPORAN_ANALISIS_STATISTIK.md` (memuat narasi lengkap, temuan eksekutif, tabel komparasi, interpretasi odds ratio, dan strategi mitigasi portofolio).
  2. **Buku Kerja Excel Multi-Sheet**: `output/LAPORAN_KOMPILASI_STATISTIK_GADAI_MOTOR.xlsx` berisi 10 sheet terstruktur:
     - `Ringkasan Eksekutif`
     - `Tabel 1 Karakteristik`
     - `Tabel 2 Distribusi NPL`
     - `Tabel 11 Uji Bivariat`
     - `Komparasi Model Regresi`
     - `Koefisien & Odds Ratio`
     - `Diagnostik VIF`
     - `Uji Hipotesis H1-H8`
     - `Kebijakan Cabang 4 Klaster`
     - `Rule of Thumb Ahli 7 Metrik`

---

### Menu 9: Jalankan Seluruh Pipeline Sekaligus (Batch All-in-One Execution)
* **Fungsi**: Mengeksekusi Modul 1 sampai Modul 8 secara berurutan dalam satu kali klik. Waktu total eksekusi hanya membutuhkan sekitar **25–35 detik**.
* **Alur Eksekusi**:
  ```text
  [1/7] Modul 1: Cleansing & Target Rectification
  [2/7] Modul 2: Analisis Deskriptif Univariat
  [3/7] Modul 3: Analisis Bivariat & Uji Risiko Kredit
  [4/7] Modul 4: Pemodelan Regresi Logistik Bertingkat (Model 0 - 4)
  [5/7] Modul 5: Diagnostik VIF & Pengujian 8 Hipotesis Riset
  [6/7] Modul 6: Pembuatan 6 Grafik Publikasi Resolusi Tinggi (300 DPI)
  [7/7] Modul 8: Kompilasi Laporan Markdown & Excel Multi-Sheet
  ```

---

## 4. MATRIKS KEBIJAKAN OPERASIONAL CABANG (UNDERWRITING RULES)

### A. Matriks Batas LTV Maksimum Berdasarkan Agunan
| Kondisi Kepemilikan STNK | Status Pajak STNK | Usia Kendaraan (Tahun) | Rekomendasi LTV Maksimum | Keputusan / Tindakan Cabang |
| :--- | :--- | :--- | :---: | :--- |
| **A/N Sendiri** | Pajak Aktif | $\le 3$ Tahun (Sangat Baru) | **45,0%** | Green Lane: Disetujui penuh dengan skema reguler. |
| **A/N Sendiri** | Pajak Aktif | $4 - 6$ Tahun (Sedang) | **40,0%** | Skema Standar: Verifikasi fisik wajar. |
| **A/N Sendiri** | Pajak Aktif | $\ge 7$ Tahun (Tua) | **35,0%** | Wajib uji kelayakan mesin & cek batas depresiasi. |
| **A/N Sendiri** | Pajak Tidak Aktif | Semua Usia | **35,0%** | Plafon dipotong estimasi denda/biaya perpanjangan pajak. |
| **A/N Orang Lain** | Pajak Aktif | $\le 5$ Tahun | **35,0%** | Wajib surat kuasa bermaterai / fotokopi KTP pemilik sah. |
| **A/N Orang Lain** | Pajak Aktif | $\ge 6$ Tahun | **30,0%** | Pembatasan ketat penaksir; hindari plafon $> \text{Rp 3 Juta}$. |
| **A/N Orang Lain** | Pajak Tidak Aktif | $\ge 6$ Tahun | **$\le 25,0\%$ / TOLAK** | Risiko Sangat Tinggi; potensi moral hazard dan penelantaran barang. |
| **Semua Kondisi** | *Repeat Borrower* | Memiliki rekam jejak lunas | **+5,0% Tambahan Plafon** | Insentif loyalitas nasabah dengan rekam jejak lancar. |

### B. Matriks Kebijakan Operasional Berbasis 4 Klaster Profesi Debitur
| Klaster Profesi | Target Profesi | Profil Risiko Empiris | Maksimum Plafon LTV | Plafon Nominal Maksimum | SOP Verifikasi Lapangan Cabang | Kewenangan Approval Cabang |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **Klaster 1: Prime** | Guru, Dosen, PNS, ASN, BUMN | NPL 3,53%–5,13% (OR: 0,65–0,86) | **Maksimal 50% OTR** (+5% Bonus) | Rp 10.000.000 | Fast-Track: ID Card pegawai aktif / Slip Gaji. Bebas survei. | Petugas Penaksir / Kepala Unit Cabang |
| **Klaster 2: Core Baseline** | Swasta, IRT, Buruh, Tidak Mengisi | NPL 5,79%–6,16% (OR: ~1,00) | **Standar 45% OTR** (35% STNK Lain) | Rp 7.500.000 | Verifikasi Standar: Cek fisik rangka/mesin, KTP, kontak darurat. | Kepala Unit / Asisten Kepala Cabang |
| **Klaster 3: Volatile** | Pedagang Kios/Pasar, Wiraswasta | NPL 8,62%–13,16% (OR: 1,40–2,43) | **Maksimal 40% OTR** (-5% Pruning) | Rp 6.000.000 | Verifikasi Usaha Fisik: Foto tempat usaha / buku kas 1 minggu. | Rekomendasi Lapangan & Paraf Kepala Cabang |
| **Klaster 4: Vulnerable** | Mahasiswa, Pelajar, Belum Bekerja | NPL 7,91%–7,97% (OR: 1,37) | **Maksimal 30% OTR** | **Strict Cap: Rp 2.500.000** | Verifikasi Penjamin Serumah. **TOLAK jika STNK bukan a/n sendiri.** | Wajib Komite Kredit / Kepala Cabang Penuh |

### C. Pedoman Rule of Thumb Ahli untuk 7 Metrik Evaluasi Ekonometrika
1. **Log-Likelihood ($\ln L$)**: Fisher (1922) & Wilks (1938) — Evaluasi formal via Wilks LR Test $\text{LR} = 2(\ln L_1 - \ln L_0) \sim \chi^2$. Model 4 kita memiliki $\text{LR} = 3.360,71$ ($p < 10^{-300}$), sangat superior.
2. **AIC**: Akaike (1974) & Burnham & Anderson (2004) — Model terbaik memiliki AIC terendah. $\Delta\text{AIC} > 10$ adalah bukti mutlak keunggulan. Model 4 memiliki $\Delta\text{AIC} = -2.156,5$ vs Model 2.
3. **BIC**: Schwarz (1978) & Raftery (1995) — Penalti sampel besar ($\ln 139.493 = 11,85$). $\Delta\text{BIC} > 10$ adalah *decisive evidence*. Model 4 memiliki $\Delta\text{BIC} = -2.146,6$.
4. **McFadden Pseudo $R^2$**: McFadden (1979 - Nobel 2000) — $0,20 - 0,40$ setara $R^2 = 0,70 - 0,90$ OLS. Untuk *rare event credit default*, rentang $0,02 - 0,10$ adalah standar perbankan sehat (Hensher & Stopher 1979). Model 4 bernilai $0,0479$ (4,79%).
5. **ROC-AUC**: Hosmer & Lemeshow (2000) & Fawcett (2006) — Pada kredit mikro gadai tanpa biro kredit (SLIK), rentang $0,65 - 0,75$ adalah standar realistis yang kuat. Model 4 bernilai $0,6702$.
6. **PR-AUC**: Saito & Rehmsmeier (2015) & Davis & Goadrich (2006) — Baseline tebakan acak sama dengan prevalensi NPL ($0,0691$). Model 4 bernilai $0,1124$ (+62,7% di atas acak).
7. **Brier Score**: Brier (1950) & Steyerberg (2010) — Benchmark acak $\text{BS}_{\text{null}} = 0,06433$. Model terkalibrasi baik jika $\text{BS} < 0,06433$. Model 4 bernilai $0,06291$.

---

## 5. STRUKTUR DIREKTORI OUTPUT PROYEK

Setelah pipeline master selesai dijalankan, seluruh artefak analisis akan tersimpan rapi dalam struktur berikut:

```text
output/
├── data_cleaned.csv                          # Dataset bersih terstandarisasi (CSV)
├── data_cleaned.pkl                          # Dataset bersih format Pickle (< 0,2 detik)
├── audit_report.json                         # Laporan audit integritas data pra-analisis
├── LAPORAN_ANALISIS_STATISTIK.md             # Laporan eksekutif lengkap narasi & tabel riset
├── LAPORAN_KOMPILASI_STATISTIK_GADAI_MOTOR.xlsx # Buku kerja Excel 8 sheet resmi
│
├── figures/                                  # Grafik publikasi beresolusi tinggi (300 DPI)
│   ├── fig1_npl_distribution.png             # Gambar 1: Donut chart distribusi NPL
│   ├── fig2_npl_rate_by_categories.png       # Gambar 2: NPL rate per kategori risiko
│   ├── fig3_vehicle_age_vs_npl.png           # Gambar 3: Kurva empiris usia motor vs NPL
│   ├── fig4_simpsons_paradox_ltv_stnk.png    # Gambar 4: Dekomposisi Simpson's Paradox
│   ├── fig5_roc_curves_comparison.png        # Gambar 5: Kurva ROC Model 1, 2, 4
│   └── fig6_calibration_curves.png           # Gambar 6: Kurva Kalibrasi probabilitas risiko
│
├── tables/                                   # Tabel deskriptif & bivariat riset (CSV)
│   ├── tabel1_karakteristik_transaksi.csv    # Tabel 1: Ringkasan kuantitatif portofolio
│   ├── tabel2_distribusi_npl.csv             # Tabel 2: Frekuensi status kredit NPL
│   └── tabel11_analisis_bivariat_lengkap.csv # Tabel 11: Uji Chi-Square & Crude Odds Ratio
│
└── models/                                   # Tabel estimasi ekonometrika (CSV & JSON)
    ├── model_comparison_table.csv            # Tabel 16: Komparasi Model 0 sampai Model 4
    ├── model_coefficients.csv                # Koefisien Beta, p-value, Odds Ratio, & CI 95%
    ├── vif_diagnostics.csv                   # Uji multikolinearitas (VIF) seluruh prediktor
    ├── sensitivity_analysis.csv              # Stabilitas koefisien subset pekerjaan
    └── hypothesis_results.json               # Ringkasan pengujian formal hipotesis H1 - H8
```
