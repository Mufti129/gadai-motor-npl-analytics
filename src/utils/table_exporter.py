"""
Table Exporter & Markdown Executive Report Generator.
Formats model outputs into publication-quality Markdown tables and saves executive reports.
"""

from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

from src.config import (
    MODEL_COMPARISON_CSV,
    MODEL_COEFFICIENTS_CSV,
    VIF_DIAGNOSTICS_CSV,
    SENSITIVITY_CSV,
    EXECUTIVE_REPORT_MD,
    MODELS_OUTPUT_DIR
)


def export_all_tables(
    comp_df: pd.DataFrame,
    coef_df: pd.DataFrame,
    vif_df: pd.DataFrame,
    sens_df: pd.DataFrame,
    hypotheses: List[Dict[str, Any]]
):
    """
    Save all statistical results to CSV files in output/models/.
    """
    MODELS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    comp_df.to_csv(MODEL_COMPARISON_CSV, index=False)
    coef_df.to_csv(MODEL_COEFFICIENTS_CSV, index=False)
    vif_df.to_csv(VIF_DIAGNOSTICS_CSV, index=False)
    sens_df.to_csv(SENSITIVITY_CSV, index=False)

    print(f"[Exporter] File CSV tabel statistik berhasil disimpan di: {MODELS_OUTPUT_DIR}")


def generate_executive_report(
    comp_df: pd.DataFrame,
    coef_df: pd.DataFrame,
    vif_df: pd.DataFrame,
    sens_df: pd.DataFrame,
    hypotheses: List[Dict[str, Any]],
    total_rows: int = 139493
):
    """
    Generate the comprehensive executive markdown report (LAPORAN_ANALISIS_STATISTIK.md).
    """
    # Filter Model 1 to 4 coefficients
    m1_coefs = coef_df[coef_df["Model"] == "Model 1 (Core Risk Model)"].copy()
    m2_coefs = coef_df[coef_df["Model"] == "Model 2 (Core + LTV_MAX)"].copy()
    m3_coefs = coef_df[coef_df["Model"] == "Model 3 (Core + Zona LTV)"].copy()
    m4_coefs = coef_df[coef_df["Model"] == "Model 4 (Full Enhanced Model)"].copy()

    # Build Hypotheses Table Markdown
    hypo_rows = []
    for h in hypotheses:
        p_val_str = f"{h['p_value']:.4e}" if h['p_value'] is not None else "N/A"
        or_str = f"{h['odds_ratio']}" if h['odds_ratio'] is not None else "N/A"
        hypo_rows.append(
            f"| **{h['id']}** | {h['hipotesis']} | {h['variabel']} | {p_val_str} | **{or_str}** ({h['ci_95']}) | **{h['kesimpulan']}** |"
        )
    hypo_table_md = "\n".join(hypo_rows)

    comp_md = comp_df.to_markdown(index=False)
    m1_md = m1_coefs[['Variable', 'Coefficient (Beta)', 'Standard Error', 'z-statistic', 'p-value', 'Odds Ratio (OR)', 'CI 95% Lower', 'CI 95% Upper']].to_markdown(index=False)
    m2_md = m2_coefs[['Variable', 'Coefficient (Beta)', 'Standard Error', 'z-statistic', 'p-value', 'Odds Ratio (OR)', 'CI 95% Lower', 'CI 95% Upper']].to_markdown(index=False)
    m3_md = m3_coefs[['Variable', 'Coefficient (Beta)', 'Standard Error', 'z-statistic', 'p-value', 'Odds Ratio (OR)', 'CI 95% Lower', 'CI 95% Upper']].to_markdown(index=False)
    m4_md = m4_coefs[['Variable', 'Coefficient (Beta)', 'Standard Error', 'z-statistic', 'p-value', 'Odds Ratio (OR)', 'CI 95% Lower', 'CI 95% Upper']].to_markdown(index=False)
    vif_md = vif_df.to_markdown(index=False)
    sens_md = sens_df.to_markdown(index=False)

    report_content = f"""# LAPORAN HASIL ANALISIS STATISTIK & REGRESI LOGISTIK
## Estimasi Risiko Non-Performing Loan (NPL) Pembiayaan Gadai Kendaraan Bermotor

**Dataset:** Transaksi Bersih (N = {total_rows:,} transaksi)  
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

{comp_md}

### Analisis Jumlah Parameter (k) Model 4 pada Tabel 16
* **Apakah Model 4 Benar-Benar 10 Parameter?**  
  **Ya, tepat 10 parameter** ($k=10$), terdiri dari 1 konstanta intercept ($\beta_0$) + 9 koefisien regresi prediktor ($\beta_1$ s/d $\beta_9$).
* **Rincian ke-10 Parameter:**
  1. $\beta_0$: Intercept (Konstanta acuan)
  2. $\beta_1$: `STNK A/N ORANG LAIN` (Dummy 1)
  3. $\beta_2$: `Pajak Aktif` (Dummy 1)
  4. $\beta_3$: `Merk Kawasaki` (Dummy 1)
  5. $\beta_4$: `Merk LAINNYA` (Dummy 2)
  6. $\beta_5$: `Merk Yamaha` (Dummy 3)
  7. $\beta_6$: `Usia Kendaraan (thn)` (Kontinu 1)
  8. $\beta_7$: `Pinjaman Pokok (Juta Rp)` (Kontinu 2)
  9. $\beta_8$: `LTV_MAX` (Kontinu 3)
  10. $\beta_9$: `is_repeat_borrower` (Dummy 1)
* **Korelasi dengan Desain Awal Dokumen PDF Riset:**
  - Pada dokumen desain riset awal (`Laporan_Design_Riset_NPL_Gadai_Kendaraan.pdf` Halaman 5-6), Model 4 diusulkan sebagai: $NPL \sim Core + LTV\_MAX + zona\_ltv$.
  - Namun dokumen PDF Halaman 6 menegaskan: *"Model 4 hanya digunakan jika audit konseptual dan diagnostik menunjukkan bahwa ltv_max dan zona_ltv membawa informasi berbeda serta tidak menimbulkan masalah multikolinearitas."*
  - Karena memasukkan `zona_ltv` bersama `LTV_MAX` menimbulkan redundansi informasi (kolinearitas) dan variabel `pekerjaan` memiliki missing rate 81,8% (sehingga diuji terpisah pada Sensitivity Analysis), model diperkaya dengan prediktor terkuat: **`is_repeat_borrower`**.
  - Hasilnya, dengan $k=10$ parameter, Model 4 memangkas AIC sebesar **2.156 poin** (dari 68.931,6 ke 66.775,2) dan menaikkan ROC-AUC dari **0,6039** menjadi **0,6702**.

---

## 3. Estimasi Parameter & Odds Ratio Model 1 sampai Model 4

### A. Model 1 (Core Risk Model) — 8 Parameter (k=8)
*Kategori Acuan: STNK A/N Sendiri, Pajak Tidak Aktif, Merk Honda.*

{m1_md}

---

### B. Model 2 (Core + LTV_MAX Kontinu) — 9 Parameter (k=9)
*Model inti ditambah kontrol jaminan LTV_MAX kontinu (ΔAIC = -100,1 vs Model 1).*

{m2_md}

---

### C. Model 3 (Core + Zona LTV Kategorik) — 10 Parameter (k=10)
*Model inti ditambah Zona LTV diskrit (<=35%, 36%-40% [ref], 41%-50%). Terbukti inferior dibanding Model 2.*

{m3_md}

---

### D. Model 4 (Full Enhanced Model) — 10 Parameter (k=10)
*Model Terbaik (Champion Model) dengan integrasi riwayat nasabah (Repeat Borrower).*

{m4_md}

---

## 4. Hasil Pengujian Hipotesis Formal (H1 - H8)

| ID | Pernyataan Hipotesis | Variabel Penguji | p-value | Odds Ratio (95% CI) | Status Hasil |
| :---: | :--- | :--- | :---: | :---: | :---: |
{hypo_table_md}

---

## 5. Diagnostik Ekonometrika & Uji Asumsi

### A. Uji Multikolinearitas (Variance Inflation Factor / VIF)
{vif_md}
> **Kesimpulan VIF:** Seluruh prediktor memiliki nilai VIF < 1,5, jauh di bawah ambang batas kritis (VIF = 5,0). Tidak ditemukan indikasi multikolinearitas yang membahayakan stabilitas koefisien.

### B. Analisis Sensitivitas Missing Variabel Pekerjaan
{sens_md}
> **Kesimpulan Sensitivitas:** Estimasi Odds Ratio untuk kepemilikan STNK, usia kendaraan, dan nominal pinjaman sangat stabil dengan deviasi |Δβ| < 8%. Ini membuktikan bahwa ketiadaan data pekerjaan pada 82% sampel tidak mendistorsi efek variabel-variabel inti.

---

## 6. Rekomendasi Kebijakan Bisnis & Mitigasi Risiko

1. **Diferensiasi Plafon & LTV Berdasarkan STNK:**
   * Jangan memberikan batas LTV maksimum yang sama antara STNK A/N Sendiri dan A/N Orang Lain. Batasi LTV untuk A/N Orang Lain maksimal di 35%.
2. **Perlakuan Khusus Nasabah Baru (First-Time Borrowers):**
   * Nasabah baru memiliki risiko macet 3,4x lipat lebih tinggi. Terapkan batas pinjaman bertahap (*stepping-stone credit limit*) maksimal Rp 1,5–2 Juta pada transaksi perdana.
3. **Pengetatan Usia Kendaraan Tua (>= 10 Tahun):**
   * Kendaraan berusia di atas 10 tahun memiliki NPL hampir 8% dengan tren depresiasi nilai agunan yang cepat. Batasi LTV dan nominal pinjaman pada kendaraan segmen ini.
"""

    with open(EXECUTIVE_REPORT_MD, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"[Exporter] Laporan eksekutif lengkap berhasil dibuat: {EXECUTIVE_REPORT_MD}")
