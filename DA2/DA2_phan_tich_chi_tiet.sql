USE [DA2];
GO

-- ============================================================================
-- BƯỚC 1: TẠO CẤU TRÚC CÁC BẢNG DIM VÀ FACT
-- ============================================================================

-- 1.1 Dim Địa Chỉ
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dim_khach_hang_dia_chi')
CREATE TABLE [dbo].[dim_khach_hang_dia_chi] (
    [dia_chi_key] INT IDENTITY(1,1) PRIMARY KEY,
    [tinh_thanh] NVARCHAR(50),
    [phuong_xa] NVARCHAR(50),
    [dia_chi_cu_the] NVARCHAR(100)
);

-- 1.2 Dim Sản Phẩm
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dim_san_pham')
CREATE TABLE [dbo].[dim_san_pham] (
    [san_pham_key] INT IDENTITY(1,1) PRIMARY KEY,
    [ma_san_pham] NVARCHAR(50),
    [ten_san_pham] NVARCHAR(100),
    [nhom_hang] NVARCHAR(50),
    [thuong_hieu] NVARCHAR(50),
    [danh_muc] NVARCHAR(50)
);

-- 1.3 Fact Bán Hàng
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'fact_ban_hang')
CREATE TABLE [dbo].[fact_ban_hang] (
    [fact_key] INT IDENTITY(1,1) PRIMARY KEY,
    [stt] INT,
    [dia_chi_key] INT FOREIGN KEY REFERENCES [dim_khach_hang_dia_chi]([dia_chi_key]),
    [san_pham_key] INT FOREIGN KEY REFERENCES [dim_san_pham]([san_pham_key]),
    [so_luong] TINYINT,
    [don_gia] MONEY,
    [ty_le_giam_gia] FLOAT,
    [tien_giam] MONEY,
    [tong_hang] MONEY,
    [tong_thanh_toan] MONEY,
    [tan_suat_mua_hang] TINYINT
);
GO


-- ============================================================================
-- BƯỚC 2: NẠP DỮ LIỆU VÀO BẢNG DIM (TỪ BẢNG Dien_tu_goc_da_thay_doi_csv TRONG DA2)
-- ============================================================================

-- 2.1 Nạp Dim Địa Chỉ
INSERT INTO [dbo].[dim_khach_hang_dia_chi] ([tinh_thanh], [phuong_xa], [dia_chi_cu_the])
SELECT DISTINCT [Tinh_Thanh], [Phuong_Xa], [Dia_Chi_Cu_The]
FROM [dbo].[Dien_tu_goc_da_thay_doi_csv]
WHERE [Dia_Chi_Cu_The] IS NOT NULL;

-- 2.2 Nạp Dim Sản Phẩm
INSERT INTO [dbo].[dim_san_pham] ([ma_san_pham], [ten_san_pham], [nhom_hang], [thuong_hieu], [danh_muc])
SELECT DISTINCT [Ma_San_Pham], [Ten_San_Pham], [Nhom_Hang], [Thuong_Hieu], [Danh_Muc]
FROM [dbo].[Dien_tu_goc_da_thay_doi_csv]
WHERE [Ma_San_Pham] IS NOT NULL;
GO


-- ============================================================================
-- BƯỚC 3: NẠP DỮ LIỆU VÀO BẢNG FACT
-- ============================================================================

INSERT INTO [dbo].[fact_ban_hang] (
    [stt],
    [dia_chi_key],
    [san_pham_key],
    [so_luong],
    [don_gia],
    [ty_le_giam_gia],
    [tien_giam],
    [tong_hang],
    [tong_thanh_toan],
    [tan_suat_mua_hang]
)
SELECT 
    g.[STT],
    dc.[dia_chi_key],
    sp.[san_pham_key],
    g.[So_Luong],
    g.[Don_Gia],
    g.[Ty_Le_Giam_Gia],
    g.[Tien_Giam],
    g.[Tong_Hang],
    g.[Tong_Thanh_Toan],
    g.[Tan_suat_mua_hang]
FROM [dbo].[Dien_tu_goc_da_thay_doi_csv] g
LEFT JOIN [dbo].[dim_khach_hang_dia_chi] dc 
    ON ISNULL(g.[Tinh_Thanh], '') = ISNULL(dc.[tinh_thanh], '')
   AND ISNULL(g.[Phuong_Xa], '') = ISNULL(dc.[phuong_xa], '')
   AND ISNULL(g.[Dia_Chi_Cu_The], '') = ISNULL(dc.[dia_chi_cu_the], '')
LEFT JOIN [dbo].[dim_san_pham] sp 
    ON ISNULL(g.[Ma_San_Pham], '') = ISNULL(sp.[ma_san_pham], '');
GO


-- ============================================================================
-- BƯỚC 4: XEM KẾT QUẢ
-- ============================================================================

SELECT TOP (1000)
    f.[stt] AS [STT],
    dc.[tinh_thanh] AS [Tinh_Thanh],
    dc.[phuong_xa] AS [Phuong_Xa],
    dc.[dia_chi_cu_the] AS [Dia_Chi_Cu_The],
    sp.[ma_san_pham] AS [Ma_San_Pham],
    sp.[ten_san_pham] AS [Ten_San_Pham],
    sp.[nhom_hang] AS [Nhom_Hang],
    sp.[thuong_hieu] AS [Thuong_Hieu],
    sp.[danh_muc] AS [Danh_Muc],
    f.[so_luong] AS [So_Luong],
    f.[don_gia] AS [Don_Gia],
    f.[ty_le_giam_gia] AS [Ty_Le_Giam_Gia],
    f.[tien_giam] AS [Tien_Giam],
    f.[tong_hang] AS [Tong_Hang],
    f.[tong_thanh_toan] AS [Tong_Thanh_Toan],
    f.[tan_suat_mua_hang] AS [Tan_Suat_Mua_Hang]
FROM [dbo].[fact_ban_hang] f
LEFT JOIN [dbo].[dim_khach_hang_dia_chi] dc ON f.[dia_chi_key] = dc.[dia_chi_key]
LEFT JOIN [dbo].[dim_san_pham] sp ON f.[san_pham_key] = sp.[san_pham_key];