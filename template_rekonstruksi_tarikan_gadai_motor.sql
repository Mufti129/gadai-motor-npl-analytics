-- ============================================================================
-- TEMPLATE REKONSTRUKSI QUERY SQL TARIKAN DATA GADAI MOTOR (PT PUSAT GADAI INDONESIA)
-- ============================================================================
-- Catatan Forensik & Asal-Usul Kolom:
--   1. Pada file mentah `gadai_bpkb_motor.xlsx` & `gadai_bpkb_motor_2.xlsx`,
--      nama sheet terekam sebagai `_SELECT_g_created_at_AS_tanggal`, yang
--      membuktikan query awal di database (MySQL / phpMyAdmin / DBeaver)
--      dimulai persis dengan: `SELECT g.created_at AS tanggal_gadai, ...`
--   2. Kolom 1 s.d. 37 pada `request Mufti_gadaiHP.xlsx` adalah hasil tarikan
--      SQL mentah (ditambah `no_handphone_sekarang` pada tarikan `moto2022-2025`
--      dan `raw_emas_elek`).
--   3. Kolom 38 s.d. 52 (`LTV`, `LTV_MAX`, `Days Late`, `NPL`, dst.) adalah
--      kolom formula Excel/Google Sheets yang ditambahkan SETELAH ekspor data.
--   4. Karena skema fisik tabel pada server `database1.pusatgadai.id` tidak
--      tersimpan di lokal, nama tabel & kolom dengan tanda `<...>` perlu
--      dicocokkan terlebih dahulu dengan `SHOW TABLES` / `DESCRIBE` di server.
-- ============================================================================


-- ----------------------------------------------------------------------------
-- LANGKAH 0: QUERY PENGECEKAN NAMA TABEL & KOLOM DI SERVER (MySQL / phpMyAdmin)
-- Jalankan 2 baris berikut lebih dulu jika lupa nama tabel/relasi aslinya:
-- ----------------------------------------------------------------------------
-- SHOW TABLES;
-- SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
-- FROM INFORMATION_SCHEMA.COLUMNS
-- WHERE TABLE_SCHEMA = DATABASE()
--   AND COLUMN_NAME IN (
--       'fraktur', 'status_gadai', 'no_identitas', 'pajakstnk',
--       'nilai_taksiran', 'pinjaman_pokok_awal', 'tanggal_jatuh_tempo_sebelum',
--       'tanggal_jatuh_tempo_sekarang', 'frekuensi_cicilan_masuk'
--   )
-- ORDER BY TABLE_NAME, ORDINAL_POSITION;


-- ----------------------------------------------------------------------------
-- LANGKAH 1: REKONSTRUKSI QUERY UTAMA TARIKAN DATA MENTAH (37 + 1 KOLOM ASLI)
-- Sesuai struktur `request Mufti_gadaiHP.xlsx` (A-AK) & `moto2022-2025.xlsx`
-- ----------------------------------------------------------------------------
SELECT
    -- [1-6] Identitas Kontrak & Status Transaksi
    g.created_at                                AS tanggal_gadai,
    g.<fraktur>                                 AS fraktur,
    g.<status_gadai>                            AS status_gadai,
    k.<kondisi_name>                            AS kondisi_name,           -- Contoh: 'A/N SENDIRI', 'A/N ORANG LAIN' (hanya di request Mufti)
    b.<pajakstnk>                               AS pajakstnk,              -- Tanggal jatuh tempo pajak STNK (hanya di request Mufti)
    g.<status_pembayaran>                       AS status_pembayaran,      -- Kode 0/1/2/3

    -- [7-9] Profil Nasabah
    n.<nama_nasabah>                            AS nama_nasabah,
    n.<no_identitas>                            AS no_identitas,           -- NIK 16 digit
    -- n.<no_handphone_sekarang>                AS no_handphone_sekarang,  -- Aktifkan baris ini untuk skema moto2022-2025 / elek_emas
    p.<pekerjaan>                               AS pekerjaan,              -- Hanya di request Mufti

    -- [10-21] Spesifikasi Barang Jaminan & Referensi Harga Taksiran
    tp.<tipe_pinjaman>                          AS tipe_pinjaman,          -- 'Kendaraan'
    j.<jenis>                                   AS jenis,                  -- 'Motor'
    m.<merk>                                    AS merk,                   -- 'Honda', 'Yamaha', 'Suzuki', 'Kawasaki', dll.
    t.<tipe>                                    AS tipe,                   -- Kategori CC, misal '100cc-124cc', '>124cc-139cc'
    b.<tahun>                                   AS tahun,
    b.<harga_tipe>                              AS harga_tipe,
    b.<harga_barang_baru>                       AS harga_barang_baru,
    b.<has_tahun>                               AS has_tahun,
    b.<nilai_barang_awal>                       AS nilai_barang_awal,
    b.<harga_barang_tahun>                      AS harga_barang_tahun,
    b.<harga_bpkb>                              AS harga_bpkb,
    b.<harga_kendaraan>                         AS harga_kendaraan,

    -- [22-26] Tanggal Siklus Pinjaman & Jatuh Tempo
    DATE(g.<tgl_gadai_transaksi>)               AS tgl_gadai_transaksi,
    g.<tanggal_penarikan>                       AS tanggal_penarikan,
    g.<tanggal_jatuh_tempo_sebelum>             AS tanggal_jatuh_tempo_sebelum,
    g.<tanggal_jatuh_tempo_sekarang>            AS tanggal_jatuh_tempo_sekarang,
    g.<tanggal_pembayaran_terakhir>             AS tanggal_pembayaran_terakhir,

    -- [27-36] Nilai Pinjaman, Biaya & Agregasi Pembayaran
    g.<nilai_taksiran>                          AS nilai_taksiran,
    g.<pinjaman_maksimum>                       AS pinjaman_maksimum,
    g.<pinjaman_pokok_awal>                     AS pinjaman_pokok_awal,
    g.<pinjaman_pokok_efektif>                  AS pinjaman_pokok_efektif,
    g.<jasa_awal>                               AS jasa_awal,
    g.<biaya_asuransi>                          AS biaya_asuransi,
    g.<nilai_admin>                             AS nilai_admin,
    COALESCE(pay.<total_jasa_terbayar>, 0)      AS total_jasa_terbayar,
    COALESCE(pay.<frekuensi_cicilan_masuk>, 0)  AS frekuensi_cicilan_masuk,
    COALESCE(pay.<total_nominal_pembayaran_masuk>, 0) AS total_nominal_pembayaran_masuk,

    -- [37] Kode Cabang
    c.<kode_cabang>                             AS cabang                  -- Contoh: 'KWG030', 'CKR037', 'BKS029'

    -- ------------------------------------------------------------------------
    -- OPSIONAL: Jika ingin langsung menghitung metrik NPL di SQL (pengganti
    -- formula Excel pada kolom AL-AZ per tanggal cut-off snapshot tertentu):
    -- ------------------------------------------------------------------------
    /*
    , ROUND(g.<pinjaman_pokok_awal> / NULLIF(b.<nilai_barang_awal>, 0), 4) AS LTV
    , ROUND(g.<pinjaman_maksimum>   / NULLIF(b.<nilai_barang_awal>, 0), 4) AS LTV_MAX
    , CASE
          WHEN g.<status_gadai> = 'Lunas' OR g.<tanggal_jatuh_tempo_sekarang> IS NULL THEN 0
          ELSE GREATEST(0, DATEDIFF('2026-09-16', g.<tanggal_jatuh_tempo_sekarang>))
      END AS `Days Late`
    , CASE
          WHEN g.<status_gadai> IN ('Berjalan', 'Proses Lelang')
           AND g.<tanggal_jatuh_tempo_sekarang> IS NOT NULL
           AND DATEDIFF('2026-09-16', g.<tanggal_jatuh_tempo_sekarang>) > 30 THEN 1
          ELSE 0
      END AS NPL_30
    , CASE
          WHEN g.<status_gadai> IN ('Berjalan', 'Proses Lelang')
           AND g.<tanggal_jatuh_tempo_sekarang> IS NOT NULL
           AND DATEDIFF('2026-09-16', g.<tanggal_jatuh_tempo_sekarang>) > 90 THEN 1
          ELSE 0
      END AS NPL_90
    */

FROM `<tabel_gadai>` AS g
LEFT JOIN `<tabel_nasabah>`        AS n  ON n.id  = g.<nasabah_id>
LEFT JOIN `<tabel_pekerjaan>`      AS p  ON p.id  = n.<pekerjaan_id>       -- atau dari g.<pekerjaan_id>
LEFT JOIN `<tabel_barang_gadai>`   AS b  ON b.<gadai_id> = g.id            -- atau g.<barang_id> = b.id
LEFT JOIN `<tabel_kondisi_stnk>`   AS k  ON k.id  = b.<kondisi_id>
LEFT JOIN `<tabel_tipe_pinjaman>`  AS tp ON tp.id = g.<tipe_pinjaman_id>
LEFT JOIN `<tabel_jenis_barang>`   AS j  ON j.id  = b.<jenis_id>
LEFT JOIN `<tabel_merk>`           AS m  ON m.id  = b.<merk_id>
LEFT JOIN `<tabel_tipe_cc>`        AS t  ON t.id  = b.<tipe_id>
LEFT JOIN `<tabel_cabang>`         AS c  ON c.id  = g.<cabang_id>
LEFT JOIN (
    -- Subquery agregasi pembayaran/cicilan per transaksi gadai
    SELECT
        <gadai_id>,
        SUM(<nominal_jasa>)                     AS total_jasa_terbayar,
        COUNT(*)                                AS frekuensi_cicilan_masuk,
        SUM(<total_bayar>)                      AS total_nominal_pembayaran_masuk
    FROM `<tabel_pembayaran>`
    WHERE <status_bayar_valid> = 1              -- sesuaikan jika ada filter status pembayaran
    GROUP BY <gadai_id>
) AS pay ON pay.<gadai_id> = g.id

WHERE g.created_at BETWEEN '2025-01-01 00:00:00' AND '2025-12-31 23:59:59'
  AND tp.<tipe_pinjaman> = 'Kendaraan'
  AND j.<jenis> = 'Motor'
  -- Catatan: pada data mentah `request Mufti_gadaiHP.xlsx`, status 'Void' (509 baris)
  -- dan 'Hilang' (1 baris) masih ikut tertarik (baru difilter di Python cleaner),
  -- namun untuk tarikan baru yang bersih dapat ditambahkan filter opsional berikut:
  -- AND g.<status_gadai> NOT IN ('Void')

ORDER BY g.created_at ASC;
