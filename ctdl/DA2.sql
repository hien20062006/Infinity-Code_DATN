/* =========================================================================
   STAR SCHEMA CHO DỮ LIỆU BÁN HÀNG (goc_da_thay_doi.csv)
   Dialect: SQL SERVER (T-SQL)
   Chống trùng dữ liệu bằng UNIQUE constraint + WHERE NOT EXISTS khi insert
   ========================================================================= */

USE DA2;
GO

-- Xoá fact trước (nếu đã tồn tại) vì có FK trỏ tới các bảng Dim
IF OBJECT_ID('fact_don_hang', 'U') IS NOT NULL DROP TABLE fact_don_hang;
GO

/* =========================================================================
   1. DIM_SAN_PHAM
   ========================================================================= */
IF OBJECT_ID('dim_san_pham', 'U') IS NOT NULL DROP TABLE dim_san_pham;
CREATE TABLE dim_san_pham (
    san_pham_key    INT IDENTITY(1,1) PRIMARY KEY,
    ma_san_pham     NVARCHAR(20) NOT NULL UNIQUE,
    ten_san_pham    NVARCHAR(200),
    nhom_hang       NVARCHAR(100),
    thuong_hieu     NVARCHAR(100),
    danh_muc        NVARCHAR(100)
);

INSERT INTO dim_san_pham (ma_san_pham, ten_san_pham, nhom_hang, thuong_hieu, danh_muc)
SELECT DISTINCT s.Ma_San_Pham, s.Ten_San_Pham, s.Nhom_Hang, s.Thuong_Hieu, s.Danh_Muc
FROM [dbo].[goc_da_thay_doi] s
WHERE NOT EXISTS (
    SELECT 1 FROM dim_san_pham d WHERE d.ma_san_pham = s.Ma_San_Pham
);

/* =========================================================================
   2. DIM_DIA_DIEM (Tỉnh/Thành + Phường/Xã)
   ========================================================================= */
IF OBJECT_ID('dim_dia_diem', 'U') IS NOT NULL DROP TABLE dim_dia_diem;
CREATE TABLE dim_dia_diem (
    dia_diem_key   INT IDENTITY(1,1) PRIMARY KEY,
    tinh_thanh     NVARCHAR(100) NOT NULL,
    phuong_xa      NVARCHAR(100) NOT NULL,
    CONSTRAINT uq_dia_diem UNIQUE (tinh_thanh, phuong_xa)
);

INSERT INTO dim_dia_diem (tinh_thanh, phuong_xa)
SELECT DISTINCT s.Tinh_Thanh, s.Phuong_Xa
FROM [dbo].[goc_da_thay_doi] s
WHERE NOT EXISTS (
    SELECT 1 FROM dim_dia_diem d
    WHERE d.tinh_thanh = s.Tinh_Thanh AND d.phuong_xa = s.Phuong_Xa
);

/* =========================================================================
   3. FACT_DON_HANG (bảng sự kiện - mỗi dòng = 1 đơn hàng)
   ========================================================================= */
CREATE TABLE fact_don_hang (
    stt                  INT PRIMARY KEY,
    dia_diem_key         INT REFERENCES dim_dia_diem(dia_diem_key),
    san_pham_key         INT REFERENCES dim_san_pham(san_pham_key),
    dia_chi_cu_the       NVARCHAR(300),

    so_luong             INT,
    don_gia              DECIMAL(15,2),
    ty_le_giam_gia       DECIMAL(5,4),
    tien_giam            DECIMAL(15,2),
    tong_hang            DECIMAL(15,2),
    tong_thanh_toan      DECIMAL(15,2),
    tan_suat_mua_hang    INT
);

INSERT INTO fact_don_hang (
    stt, dia_diem_key, san_pham_key, dia_chi_cu_the,
    so_luong, don_gia, ty_le_giam_gia, tien_giam, tong_hang, tong_thanh_toan, tan_suat_mua_hang
)
SELECT
    s.STT,
    dd.dia_diem_key,
    sp.san_pham_key,
    s.Dia_Chi_Cu_The,
    s.So_Luong,
    ISNULL(TRY_CAST(REPLACE(REPLACE(REPLACE(LTRIM(RTRIM(s.Don_Gia)), N'₫',''), ',',''), ' ','') AS DECIMAL(15,2)), 0),
    s.Ty_Le_Giam_Gia,
    ISNULL(TRY_CAST(REPLACE(REPLACE(REPLACE(LTRIM(RTRIM(s.Tien_Giam)), N'₫',''), ',',''), ' ','') AS DECIMAL(15,2)), 0),
    ISNULL(TRY_CAST(REPLACE(REPLACE(REPLACE(LTRIM(RTRIM(s.Tong_Hang)), N'₫',''), ',',''), ' ','') AS DECIMAL(15,2)), 0),
    ISNULL(TRY_CAST(REPLACE(REPLACE(REPLACE(LTRIM(RTRIM(s.Tong_Thanh_Toan)), N'₫',''), ',',''), ' ','') AS DECIMAL(15,2)), 0),
    s.Tan_suat_mua_hang
FROM [dbo].[goc_da_thay_doi] s
JOIN dim_dia_diem dd ON dd.tinh_thanh = s.Tinh_Thanh AND dd.phuong_xa = s.Phuong_Xa
JOIN dim_san_pham sp ON sp.ma_san_pham = s.Ma_San_Pham
WHERE NOT EXISTS (
    SELECT 1 FROM fact_don_hang f WHERE f.stt = s.STT
);