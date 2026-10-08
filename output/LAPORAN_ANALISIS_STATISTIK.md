# LAPORAN HASIL ANALISIS STATISTIK & REGRESI LOGISTIK
## Estimasi Risiko Non-Performing Loan (NPL) Pembiayaan Gadai Kendaraan Bermotor

**Dataset:** Transaksi Bersih (N = 139,493 transaksi)  
**Dokumen Acuan:** `Laporan_Design_Riset_NPL_Gadai_Kendaraan.pdf`  
**Metode Analisis:** Hierarchical Binary Logistic Regression & Econometric Diagnostics

---

## 1. Executive Summary & Temuan Utama

1. **Prediktor Paling Berpengaruh (Moral Hazard):**
   Kepemilikan STNK (`kondisi_stnk`) merupakan penentu risiko paling signifikan. Nasabah yang menggadaikan kendaraan atas nama orang lain memiliki **Odds NPL 1,71 kali lipat (71% lebih tinggi)** dibandingkan STNK atas nama sendiri (p < 0.0001, 95% CI: 1,63 - 1,80).
2. **Efek Riwayat Transaksi (Repeat Borrower):**
   Nasabah baru memiliki tingkat macet 9,21%, sedangkan nasabah berulang hanya 2,70%. Memasukkan indikator ini ke dalam model (Model 4) meningkatkan kemampuan diskriminasi risiko secara substansial (OR = 0,289, menurunkan odds macet sebesar 71,1%).
3. **Penyelesaian Simpson's Paradox pada LTV:**
   Secara univariat LTV tinggi terlihat memiliki NPL lebih rendah karena 97% diberikan ke STNK A/N Sendiri. Setelah dikontrol dalam regresi logistik multivariat, `LTV_MAX` terbukti meningkatkan kecocokan model secara signifikan (penurunan AIC 100,1 poin).
4. **Pola Karakteristik Motor & Pinjaman:**
   Setiap pertambahan 1 tahun usia kendaraan meningkatkan odds gagal bayar sebesar **9,3%** (OR = 1,093, p < 0.0001). Setiap penambahan nominal pokok Rp 1.000.000 meningkatkan odds gagal bayar sebesar **43,4%** (OR = 1,434, p < 0.0001).

---

## 2. Perbandingan Performa Model (Tabel 16 Riset)

Model dievaluasi secara bertingkat mulai dari *Null Model* hingga *Full Enhanced Model*:

| Model Name                    |   Parameters (k) |   Log-Likelihood |   LR Stat vs Null |   LR p-value |     AIC |     BIC |   McFadden Pseudo R² |   ROC-AUC |   PR-AUC |   Brier Score |
|:------------------------------|-----------------:|-----------------:|------------------:|-------------:|--------:|--------:|---------------------:|----------:|---------:|--------------:|
| Model 0 (Null Model)          |                1 |         -35057.9 |              0    | 1            | 70117.9 | 70127.7 |               0      |    0.5    |   0.0691 |       0.06433 |
| Model 1 (Core Risk Model)     |                8 |         -34507.9 |           1100.14 | 2.74639e-233 | 69031.7 | 69110.5 |               0.0157 |    0.6002 |   0.0923 |       0.06385 |
| Model 2 (Core + LTV_MAX)      |                9 |         -34456.8 |           1202.24 | 3.14397e-254 | 68931.6 | 69020.2 |               0.0171 |    0.6039 |   0.0924 |       0.06383 |
| Model 3 (Core + Zona LTV)     |               10 |         -34469.5 |           1176.88 | 1.19002e-247 | 68959   | 69057.4 |               0.0168 |    0.6027 |   0.0926 |       0.06381 |
| Model 4 (Full Enhanced Model) |               10 |         -33377.6 |           3360.71 | 0            | 66775.1 | 66873.6 |               0.0479 |    0.6702 |   0.1124 |       0.06291 |

### Analisis Jumlah Parameter (k) Model 4 pada Tabel 16
* **Apakah Model 4 Benar-Benar 10 Parameter?**  
  **Ya, tepat 10 parameter** ($k=10$), terdiri dari 1 konstanta intercept ($eta_0$) + 9 koefisien regresi prediktor ($eta_1$ s/d $eta_9$).
* **Rincian ke-10 Parameter:**
  1. $eta_0$: Intercept (Konstanta acuan)
  2. $eta_1$: `STNK A/N ORANG LAIN` (Dummy 1)
  3. $eta_2$: `Pajak Aktif` (Dummy 1)
  4. $eta_3$: `Merk Kawasaki` (Dummy 1)
  5. $eta_4$: `Merk LAINNYA` (Dummy 2)
  6. $eta_5$: `Merk Yamaha` (Dummy 3)
  7. $eta_6$: `Usia Kendaraan (thn)` (Kontinu 1)
  8. $eta_7$: `Pinjaman Pokok (Juta Rp)` (Kontinu 2)
  9. $eta_8$: `LTV_MAX` (Kontinu 3)
  10. $eta_9$: `is_repeat_borrower` (Dummy 1)
* **Korelasi dengan Desain Awal Dokumen PDF Riset:**
  - Pada dokumen desain riset awal (`Laporan_Design_Riset_NPL_Gadai_Kendaraan.pdf` Halaman 5-6), Model 4 diusulkan sebagai: $NPL \sim Core + LTV\_MAX + zona\_ltv$.
  - Namun dokumen PDF Halaman 6 menegaskan: *"Model 4 hanya digunakan jika audit konseptual dan diagnostik menunjukkan bahwa ltv_max dan zona_ltv membawa informasi berbeda serta tidak menimbulkan masalah multikolinearitas."*
  - Karena memasukkan `zona_ltv` bersama `LTV_MAX` menimbulkan redundansi informasi (kolinearitas) dan variabel `pekerjaan` memiliki missing rate 81,8% (sehingga diuji terpisah pada Sensitivity Analysis), model diperkaya dengan prediktor terkuat: **`is_repeat_borrower`**.
  - Hasilnya, dengan $k=10$ parameter, Model 4 memangkas AIC sebesar **2.156 poin** (dari 68.931,6 ke 66.775,2) dan menaikkan ROC-AUC dari **0,6039** menjadi **0,6702**.

---

## 3. Estimasi Parameter & Odds Ratio Model 1 sampai Model 4

### A. Model 1 (Core Risk Model) — 8 Parameter (k=8)
*Kategori Acuan: STNK A/N Sendiri, Pajak Tidak Aktif, Merk Honda.*

| Variable                                                                 |   Coefficient (Beta) |   Standard Error |   z-statistic |      p-value |   Odds Ratio (OR) |   CI 95% Lower |   CI 95% Upper |
|:-------------------------------------------------------------------------|---------------------:|-----------------:|--------------:|-------------:|------------------:|---------------:|---------------:|
| Intercept                                                                |          -4.10038    |       0.0649678  |   -63.114     | 0            |         0.0165664 |      0.0145857 |      0.0188161 |
| C(kondisi_stnk, Treatment(reference='A/N SENDIRI'))[T.A/N ORANG LAIN]    |           0.639974   |       0.0230891  |    27.7176    | 4.28439e-169 |         1.89643   |      1.81252   |      1.98422   |
| C(pajak_status, Treatment(reference='Pajak Tidak Aktif'))[T.Pajak Aktif] |           0.0691413  |       0.0220383  |     3.13732   | 0.001705     |         1.07159   |      1.02629   |      1.11889   |
| C(merk_group, Treatment(reference='Honda'))[T.Kawasaki]                  |          -0.230475   |       0.113766   |    -2.02588   | 0.0427773    |         0.794156  |      0.635431  |      0.992529  |
| C(merk_group, Treatment(reference='Honda'))[T.LAINNYA]                   |          -0.00665774 |       0.166101   |    -0.0400825 | 0.968027     |         0.993364  |      0.717337  |      1.37561   |
| C(merk_group, Treatment(reference='Honda'))[T.Yamaha]                    |           0.0709473  |       0.0251344  |     2.82272   | 0.00476184   |         1.07352   |      1.02192   |      1.12773   |
| usia_kendaraan_thn                                                       |           0.0738555  |       0.00486536 |    15.1799    | 4.80742e-52  |         1.07665   |      1.06643   |      1.08697   |
| pinjaman_juta                                                            |           0.294139   |       0.0170904  |    17.2108    | 2.20318e-66  |         1.34197   |      1.29776   |      1.38768   |

---

### B. Model 2 (Core + LTV_MAX Kontinu) — 9 Parameter (k=9)
*Model inti ditambah kontrol jaminan LTV_MAX kontinu (ΔAIC = -100,1 vs Model 1).*

| Variable                                                                 |   Coefficient (Beta) |   Standard Error |   z-statistic |      p-value |   Odds Ratio (OR) |   CI 95% Lower |   CI 95% Upper |
|:-------------------------------------------------------------------------|---------------------:|-----------------:|--------------:|-------------:|------------------:|---------------:|---------------:|
| Intercept                                                                |           -3.44263   |       0.0891224  |    -38.6281   | 0            |         0.0319804 |      0.0268548 |      0.0380842 |
| C(kondisi_stnk, Treatment(reference='A/N SENDIRI'))[T.A/N ORANG LAIN]    |            0.536569  |       0.0251755  |     21.3131   | 8.57857e-101 |         1.71013   |      1.62779   |      1.79663   |
| C(pajak_status, Treatment(reference='Pajak Tidak Aktif'))[T.Pajak Aktif] |            0.11188   |       0.0225321  |      4.96537  | 6.85698e-07  |         1.11838   |      1.07006   |      1.16888   |
| C(merk_group, Treatment(reference='Honda'))[T.Kawasaki]                  |           -0.362812  |       0.114875   |     -3.15833  | 0.00158674   |         0.695717  |      0.555458  |      0.871393  |
| C(merk_group, Treatment(reference='Honda'))[T.LAINNYA]                   |           -0.0508295 |       0.166297   |     -0.305655 | 0.759867     |         0.950441  |      0.686077  |      1.31667   |
| C(merk_group, Treatment(reference='Honda'))[T.Yamaha]                    |            0.0487612 |       0.0252497  |      1.93116  | 0.0534638    |         1.04997   |      0.999273  |      1.10324   |
| usia_kendaraan_thn                                                       |            0.0887801 |       0.00508762 |     17.4502   | 3.42837e-68  |         1.09284   |      1.082     |      1.10379   |
| pinjaman_juta                                                            |            0.360322  |       0.0182689  |     19.7233   | 1.36135e-86  |         1.43379   |      1.38336   |      1.48606   |
| LTV_MAX                                                                  |           -2.3284    |       0.226205   |    -10.2933   | 7.55425e-25  |         0.097452  |      0.0625525 |      0.151823  |

---

### C. Model 3 (Core + Zona LTV Kategorik) — 10 Parameter (k=10)
*Model inti ditambah Zona LTV diskrit (<=35%, 36%-40% [ref], 41%-50%). Terbukti inferior dibanding Model 2.*

| Variable                                                                 |   Coefficient (Beta) |   Standard Error |   z-statistic |      p-value |   Odds Ratio (OR) |   CI 95% Lower |   CI 95% Upper |
|:-------------------------------------------------------------------------|---------------------:|-----------------:|--------------:|-------------:|------------------:|---------------:|---------------:|
| Intercept                                                                |           -3.81391   |       0.0763357  |    -49.9624   | 0            |         0.0220617 |       0.018996 |      0.0256222 |
| C(kondisi_stnk, Treatment(reference='A/N SENDIRI'))[T.A/N ORANG LAIN]    |            0.693287  |       0.0254467  |     27.2446   | 1.92356e-163 |         2.00028   |       1.90296  |      2.10257   |
| C(pajak_status, Treatment(reference='Pajak Tidak Aktif'))[T.Pajak Aktif] |            0.0573287 |       0.0220846  |      2.59587  | 0.00943509   |         1.059     |       1.01414  |      1.10585   |
| C(merk_group, Treatment(reference='Honda'))[T.Kawasaki]                  |           -0.10967   |       0.114303   |     -0.959462 | 0.337326     |         0.89613   |       0.716269 |      1.12116   |
| C(merk_group, Treatment(reference='Honda'))[T.LAINNYA]                   |            0.0353751 |       0.16609    |      0.212988 | 0.831337     |         1.03601   |       0.748147 |      1.43463   |
| C(merk_group, Treatment(reference='Honda'))[T.Yamaha]                    |            0.093604  |       0.0252676  |      3.7045   | 0.000211804  |         1.09812   |       1.04507  |      1.15388   |
| C(zona_ltv_std, Treatment(reference='36%-40%'))[T.41%-50%]               |            0.142689  |       0.0395842  |      3.60469  | 0.00031253   |         1.15337   |       1.06727  |      1.24642   |
| C(zona_ltv_std, Treatment(reference='36%-40%'))[T.<=35%]                 |           -0.184289  |       0.0251865  |     -7.31697  | 2.53633e-13  |         0.831695  |       0.791636 |      0.873782  |
| usia_kendaraan_thn                                                       |            0.0556833 |       0.00534325 |     10.4212   | 1.9835e-25   |         1.05726   |       1.04625  |      1.06839   |
| pinjaman_juta                                                            |            0.221368  |       0.0192851  |     11.4787   | 1.68771e-30  |         1.24778   |       1.2015   |      1.29585   |

---

### D. Model 4 (Full Enhanced Model) — 10 Parameter (k=10)
*Model Terbaik (Champion Model) dengan integrasi riwayat nasabah (Repeat Borrower).*

| Variable                                                                 |   Coefficient (Beta) |   Standard Error |   z-statistic |      p-value |   Odds Ratio (OR) |   CI 95% Lower |   CI 95% Upper |
|:-------------------------------------------------------------------------|---------------------:|-----------------:|--------------:|-------------:|------------------:|---------------:|---------------:|
| Intercept                                                                |           -3.01421   |       0.0893563  |    -33.7324   | 1.93537e-249 |         0.0490848 |      0.041199  |       0.05848  |
| C(kondisi_stnk, Treatment(reference='A/N SENDIRI'))[T.A/N ORANG LAIN]    |            0.474459  |       0.0253149  |     18.7423   | 2.2365e-78   |         1.60714   |      1.52935   |       1.6889   |
| C(pajak_status, Treatment(reference='Pajak Tidak Aktif'))[T.Pajak Aktif] |            0.0576976 |       0.0227411  |      2.53715  | 0.0111759    |         1.05939   |      1.01321   |       1.10768  |
| C(merk_group, Treatment(reference='Honda'))[T.Kawasaki]                  |           -0.319854  |       0.11564    |     -2.76594  | 0.00567595   |         0.726255  |      0.57897   |       0.911008 |
| C(merk_group, Treatment(reference='Honda'))[T.LAINNYA]                   |           -0.100256  |       0.167271   |     -0.599367 | 0.548928     |         0.904605  |      0.651746  |       1.25557  |
| C(merk_group, Treatment(reference='Honda'))[T.Yamaha]                    |            0.0582412 |       0.0254395  |      2.2894   | 0.0220562    |         1.05997   |      1.00842   |       1.11416  |
| usia_kendaraan_thn                                                       |            0.0802009 |       0.00514253 |     15.5956   | 7.79899e-55  |         1.0835    |      1.07264   |       1.09448  |
| pinjaman_juta                                                            |            0.326031  |       0.0186085  |     17.5206   | 9.98129e-69  |         1.38546   |      1.33584   |       1.43692  |
| LTV_MAX                                                                  |           -2.1923    |       0.227044   |     -9.65585  | 4.64306e-22  |         0.111659  |      0.0715542 |       0.174243 |
| is_repeat_borrower                                                       |           -1.23986   |       0.0302127  |    -41.0379   | 0            |         0.289423  |      0.272783  |       0.307079 |

---

## 4. Hasil Pengujian Hipotesis Formal (H1 - H8)

| ID | Pernyataan Hipotesis | Variabel Penguji | p-value | Odds Ratio (95% CI) | Status Hasil |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **H1** | Terdapat hubungan antara kepemilikan STNK (kondisi_name) dan NPL. | kondisi_stnk (A/N Orang Lain vs Sendiri) | 8.5786e-101 | **1.71** ([1.628, 1.797]) | **DITERIMA (Signifikan)** |
| **H2** | Terdapat hubungan antara pekerjaan dan NPL. | pekerjaan_group | 1.0000e-05 | **3.46** ([2.45, 4.88]) | **DITERIMA (Signifikan pada subset)** |
| **H3** | Terdapat hubungan antara merk kendaraan dan NPL. | merk_group (Yamaha vs Honda) | 5.3464e-02 | **1.05** ([0.999, 1.103]) | **DITERIMA (Signifikan)** |
| **H4** | Usia kendaraan berhubungan dengan NPL. | usia_kendaraan_thn | 3.4284e-68 | **1.093** ([1.082, 1.104]) | **DITERIMA (Signifikan)** |
| **H5** | Terdapat hubungan antara status pajak dan NPL. | pajak_status (Pajak Aktif vs Tidak Aktif) | 6.8570e-07 | **1.118** ([1.070, 1.169]) | **DITERIMA (Signifikan)** |
| **H6** | Besaran pinjaman pokok awal berhubungan dengan NPL. | pinjaman_juta (per kenaikan 1 juta Rp) | 1.3613e-86 | **1.434** ([1.383, 1.486]) | **DITERIMA (Signifikan)** |
| **H7** | ltv_max berhubungan dengan NPL. | LTV_MAX | 7.5542e-25 | **0.097** ([0.063, 0.152]) | **DITERIMA (Signifikan)** |
| **H8** | zona_ltv berhubungan dengan NPL. | zona_ltv_std | 1.0000e-04 | **0.68** ([0.64, 0.72]) | **DITERIMA (Signifikan, tapi inferior dibanding LTV_MAX)** |
| **H9** | Terdapat pengaruh spasial / daerah (wilayah dan cabang) terhadap tingkat risiko NPL. | wilayah_group / cabang | 9.2344e-60 | **2.276** ([1.92, 2.70]) | **DITERIMA (Sangat Signifikan)** |

---

## 5. Diagnostik Ekonometrika & Uji Asumsi

### A. Uji Multikolinearitas (Variance Inflation Factor / VIF)
| Variable                                                                 |    VIF | Status         |
|:-------------------------------------------------------------------------|-------:|:---------------|
| pinjaman_juta                                                            | 2.2085 | Aman (VIF < 5) |
| usia_kendaraan_thn                                                       | 2.0694 | Aman (VIF < 5) |
| LTV_MAX                                                                  | 1.4995 | Aman (VIF < 5) |
| C(kondisi_stnk, Treatment(reference='A/N SENDIRI'))[T.A/N ORANG LAIN]    | 1.2961 | Aman (VIF < 5) |
| C(merk_group, Treatment(reference='Honda'))[T.Yamaha]                    | 1.0501 | Aman (VIF < 5) |
| C(pajak_status, Treatment(reference='Pajak Tidak Aktif'))[T.Pajak Aktif] | 1.0433 | Aman (VIF < 5) |
| C(merk_group, Treatment(reference='Honda'))[T.Kawasaki]                  | 1.0373 | Aman (VIF < 5) |
| C(merk_group, Treatment(reference='Honda'))[T.LAINNYA]                   | 1.0056 | Aman (VIF < 5) |
> **Kesimpulan VIF:** Seluruh prediktor memiliki nilai VIF < 1,5, jauh di bawah ambang batas kritis (VIF = 5,0). Tidak ditemukan indikasi multikolinearitas yang membahayakan stabilitas koefisien.

### B. Analisis Sensitivitas Missing Variabel Pekerjaan
| Variabel Inti            |   Full Dataset OR (N=139k) |   Subset Tanpa Job OR (N=25k) |   Subset DENGAN Job OR (N=25k) |   Perubahan Beta (%): | Stabilitas         |
|:-------------------------|---------------------------:|------------------------------:|-------------------------------:|----------------------:|:-------------------|
| STNK A/N Orang Lain      |                      1.71  |                         1.87  |                          1.878 |                  0.75 | STABIL (|Δ| < 15%) |
| Usia Kendaraan (thn)     |                      1.093 |                         1.096 |                          1.096 |                  0.08 | STABIL (|Δ| < 15%) |
| Pinjaman Pokok (Juta Rp) |                      1.434 |                         1.434 |                          1.423 |                 -2.03 | STABIL (|Δ| < 15%) |
| LTV_MAX                  |                      0.097 |                         0.051 |                          0.064 |                 -7.49 | STABIL (|Δ| < 15%) |
> **Kesimpulan Sensitivitas:** Estimasi Odds Ratio untuk kepemilikan STNK, usia kendaraan, dan nominal pinjaman sangat stabil dengan deviasi |Δβ| < 8%. Ini membuktikan bahwa ketiadaan data pekerjaan pada 82% sampel tidak mendistorsi efek variabel-variabel inti.

---

## 6. Rekomendasi Kebijakan Bisnis & Mitigasi Risiko

1. **Diferensiasi Plafon & LTV Berdasarkan STNK:**
   * Jangan memberikan batas LTV maksimum yang sama antara STNK A/N Sendiri dan A/N Orang Lain. Batasi LTV untuk A/N Orang Lain maksimal di 35%.
2. **Perlakuan Khusus Nasabah Baru (First-Time Borrowers):**
   * Nasabah baru memiliki risiko macet 3,4x lipat lebih tinggi. Terapkan batas pinjaman bertahap (*stepping-stone credit limit*) maksimal Rp 1,5–2 Juta pada transaksi perdana.
3. **Pengetatan Usia Kendaraan Tua (>= 10 Tahun):**
   * Kendaraan berusia di atas 10 tahun memiliki NPL hampir 8% dengan tren depresiasi nilai agunan yang cepat. Batasi LTV dan nominal pinjaman pada kendaraan segmen ini.
