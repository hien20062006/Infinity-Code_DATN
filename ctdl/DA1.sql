/* =========================================================================
   STAR SCHEMA CHO D? LI?U XU?T NH?P KH?U
   Ngu?n d? li?u: [DA1].[dbo].[du_lieu_nhap_khau_da_dich]  (dã có s?n d? li?u)
   Dialect: SQL SERVER (T-SQL)
   Ch?ng trùng d? li?u b?ng UNIQUE constraint + WHERE NOT EXISTS khi insert
   ========================================================================= */

USE DA1;
GO

-- Xoá fact tru?c (n?u dã t?n t?i) vì có FK tr? t?i các b?ng Dim
IF OBJECT_ID('fact_thuong_mai', 'U') IS NOT NULL DROP TABLE fact_thuong_mai;
GO

/* =========================================================================
   1. DIM_QUOC_GIA_BAO_CAO (nu?c báo cáo)
   ========================================================================= */
IF OBJECT_ID('dim_quoc_gia_bao_cao', 'U') IS NOT NULL DROP TABLE dim_quoc_gia_bao_cao;
CREATE TABLE dim_quoc_gia_bao_cao (
    quoc_gia_bao_cao_key   INT IDENTITY(1,1) PRIMARY KEY,
    ten_nuoc_bao_cao       NVARCHAR(100) NOT NULL UNIQUE
);

INSERT INTO dim_quoc_gia_bao_cao (ten_nuoc_bao_cao)
SELECT DISTINCT s.Ten_nuoc_bao_cao
FROM [dbo].[du_lieu_nhap_khau_da_dich] s
WHERE NOT EXISTS (
    SELECT 1 FROM dim_quoc_gia_bao_cao d WHERE d.ten_nuoc_bao_cao = s.Ten_nuoc_bao_cao
);

/* =========================================================================
   2. DIM_QUOC_GIA_DOI_TAC (nu?c d?i tác)
   ========================================================================= */
IF OBJECT_ID('dim_quoc_gia_doi_tac', 'U') IS NOT NULL DROP TABLE dim_quoc_gia_doi_tac;
CREATE TABLE dim_quoc_gia_doi_tac (
    quoc_gia_doi_tac_key   INT IDENTITY(1,1) PRIMARY KEY,
    ten_nuoc_doi_tac       NVARCHAR(100) NOT NULL UNIQUE
);

INSERT INTO dim_quoc_gia_doi_tac (ten_nuoc_doi_tac)
SELECT DISTINCT s.[Tên_nuoc_doi_tac]
FROM [dbo].[du_lieu_nhap_khau_da_dich] s
WHERE NOT EXISTS (
    SELECT 1 FROM dim_quoc_gia_doi_tac d WHERE d.ten_nuoc_doi_tac = s.[Tên_nuoc_doi_tac]
);

/* =========================================================================
   3. DIM_LOAI_HINH_THUONG_MAI (mã lu?ng + lo?i hình: Nh?p kh?u/Xu?t kh?u...)
   ========================================================================= */
IF OBJECT_ID('dim_loai_hinh_thuong_mai', 'U') IS NOT NULL DROP TABLE dim_loai_hinh_thuong_mai;
CREATE TABLE dim_loai_hinh_thuong_mai (
    loai_hinh_tm_key       INT IDENTITY(1,1) PRIMARY KEY,
    ma_luong_thuong_mai    NVARCHAR(10) NOT NULL UNIQUE,
    loai_hinh_thuong_mai   NVARCHAR(100)
);

INSERT INTO dim_loai_hinh_thuong_mai (ma_luong_thuong_mai, loai_hinh_thuong_mai)
SELECT DISTINCT s.Ma_luong_thuong_mai, s.Loai_hinh_thuong_mai
FROM [dbo].[du_lieu_nhap_khau_da_dich] s
WHERE NOT EXISTS (
    SELECT 1 FROM dim_loai_hinh_thuong_mai d WHERE d.ma_luong_thuong_mai = s.Ma_luong_thuong_mai
);

/* =========================================================================
   4. DIM_HANG_HOA (mã hàng hóa + mô t?)
   ========================================================================= */
IF OBJECT_ID('dim_hang_hoa', 'U') IS NOT NULL DROP TABLE dim_hang_hoa;
CREATE TABLE dim_hang_hoa (
    hang_hoa_key      INT IDENTITY(1,1) PRIMARY KEY,
    ma_hang_hoa       INT NOT NULL UNIQUE,
    mo_ta_hang_hoa    NVARCHAR(1000),
    cap_do_tong_hop   INT
);

INSERT INTO dim_hang_hoa (ma_hang_hoa, mo_ta_hang_hoa, cap_do_tong_hop)
SELECT DISTINCT s.Ma_hang_hoa, r.Mo_ta_hang_hoa, s.Cap_do_tong_hop
FROM [dbo].[du_lieu_nhap_khau_da_dich] s
CROSS APPLY (
    SELECT TOP 1 x.Mo_ta_hang_hoa
    FROM [dbo].[du_lieu_nhap_khau_da_dich] x
    WHERE x.Ma_hang_hoa = s.Ma_hang_hoa
    ORDER BY x.STT ASC
) r
WHERE NOT EXISTS (
    SELECT 1 FROM dim_hang_hoa d WHERE d.ma_hang_hoa = s.Ma_hang_hoa
);

/* =========================================================================
   5. DIM_DON_VI_TINH (don v? s? lu?ng)
   ========================================================================= */
IF OBJECT_ID('dim_don_vi_tinh', 'U') IS NOT NULL DROP TABLE dim_don_vi_tinh;
CREATE TABLE dim_don_vi_tinh (
    don_vi_tinh_key   INT IDENTITY(1,1) PRIMARY KEY,
    don_vi_so_luong   NVARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO dim_don_vi_tinh (don_vi_so_luong)
SELECT DISTINCT ISNULL(s.Don_vi_so_luong, N'Không xác d?nh')
FROM [dbo].[du_lieu_nhap_khau_da_dich] s
WHERE NOT EXISTS (
    SELECT 1 FROM dim_don_vi_tinh d
    WHERE d.don_vi_so_luong = ISNULL(s.Don_vi_so_luong, N'Không xác d?nh')
);

/* =========================================================================
   6. DIM_KY_BAO_CAO (th?i gian báo cáo: nam/k?/tháng)
   ========================================================================= */
IF OBJECT_ID('dim_ky_bao_cao', 'U') IS NOT NULL DROP TABLE dim_ky_bao_cao;
CREATE TABLE dim_ky_bao_cao (
    ky_bao_cao_key    INT IDENTITY(1,1) PRIMARY KEY,
    nam_bao_cao       INT NOT NULL,
    thang_bao_cao     INT,
    ky_bao_cao        INT,
    CONSTRAINT uq_ky_bao_cao UNIQUE (nam_bao_cao, thang_bao_cao, ky_bao_cao)
);

INSERT INTO dim_ky_bao_cao (nam_bao_cao, thang_bao_cao, ky_bao_cao)
SELECT DISTINCT s.Nam_bao_cao, CAST(s.Thang_bao_cao AS INT), s.Ky_bao_cao
FROM [dbo].[du_lieu_nhap_khau_da_dich] s
WHERE NOT EXISTS (
    SELECT 1 FROM dim_ky_bao_cao d
    WHERE d.nam_bao_cao = s.Nam_bao_cao
      AND ISNULL(d.thang_bao_cao,-1) = ISNULL(CAST(s.Thang_bao_cao AS INT),-1)
      AND d.ky_bao_cao = s.Ky_bao_cao
);

/* =========================================================================
   7. FACT_THUONG_MAI (b?ng s? ki?n - m?i dòng = 1 b?n ghi thuong m?i)
   ========================================================================= */
CREATE TABLE fact_thuong_mai (
    stt                     INT PRIMARY KEY,
    quoc_gia_bao_cao_key    INT REFERENCES dim_quoc_gia_bao_cao(quoc_gia_bao_cao_key),
    quoc_gia_doi_tac_key    INT REFERENCES dim_quoc_gia_doi_tac(quoc_gia_doi_tac_key),
    loai_hinh_tm_key        INT REFERENCES dim_loai_hinh_thuong_mai(loai_hinh_tm_key),
    hang_hoa_key            INT REFERENCES dim_hang_hoa(hang_hoa_key),
    don_vi_tinh_key         INT REFERENCES dim_don_vi_tinh(don_vi_tinh_key),
    ky_bao_cao_key          INT REFERENCES dim_ky_bao_cao(ky_bao_cao_key),

    so_luong                DECIMAL(18,2),
    trong_luong_tinh        DECIMAL(18,2),
    gia_tri_cif             DECIMAL(18,2),
    gia_tri_fob             DECIMAL(18,2),
    gia_tri_giao_dich       DECIMAL(18,2)
);

INSERT INTO fact_thuong_mai (
    stt, quoc_gia_bao_cao_key, quoc_gia_doi_tac_key, loai_hinh_tm_key,
    hang_hoa_key, don_vi_tinh_key, ky_bao_cao_key,
    so_luong, trong_luong_tinh, gia_tri_cif, gia_tri_fob, gia_tri_giao_dich
)
SELECT
    s.STT,
    qb.quoc_gia_bao_cao_key,
    qd.quoc_gia_doi_tac_key,
    lh.loai_hinh_tm_key,
    hh.hang_hoa_key,
    dv.don_vi_tinh_key,
    kb.ky_bao_cao_key,
    s.So_luong,
    s.Trong_luong_tinh,
    s.Gia_tri_CIF_USD,
    s.Gia_tri_FOB_USD,
    s.Gia_tri_giao_dich_USD
FROM [dbo].[du_lieu_nhap_khau_da_dich] s
JOIN dim_quoc_gia_bao_cao qb ON qb.ten_nuoc_bao_cao = s.Ten_nuoc_bao_cao
JOIN dim_quoc_gia_doi_tac qd ON qd.ten_nuoc_doi_tac = s.[Tên_nuoc_doi_tac]
JOIN dim_loai_hinh_thuong_mai lh ON lh.ma_luong_thuong_mai = s.Ma_luong_thuong_mai
JOIN dim_hang_hoa hh ON hh.ma_hang_hoa = s.Ma_hang_hoa
JOIN dim_don_vi_tinh dv ON dv.don_vi_so_luong = ISNULL(s.Don_vi_so_luong, N'Không xác d?nh')
JOIN dim_ky_bao_cao kb
     ON kb.nam_bao_cao = s.Nam_bao_cao
    AND ISNULL(kb.thang_bao_cao,-1) = ISNULL(CAST(s.Thang_bao_cao AS INT),-1)
    AND kb.ky_bao_cao = s.Ky_bao_cao
WHERE NOT EXISTS (
    SELECT 1 FROM fact_thuong_mai f WHERE f.stt = s.STT
);