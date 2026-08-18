USE [DA1];
GO

-- 1. Dim Thời Gian
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dim_thoi_gian')
CREATE TABLE [dbo].[dim_thoi_gian] (
    [thoi_gian_key] INT IDENTITY(1,1) PRIMARY KEY,
    [ma_ky_bao_cao] NVARCHAR(50),
    [nam_bao_cao] INT,
    [tuan_bao_cao] INT
);

-- 2. Dim Đối Tác
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dim_doi_tac')
CREATE TABLE [dbo].[dim_doi_tac] (
    [doi_tac_key] INT IDENTITY(1,1) PRIMARY KEY,
    [ten_nuoc_doi_tac] NVARCHAR(255)
);

-- 3. Dim Loại Luồng
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dim_loai_luong')
CREATE TABLE [dbo].[dim_loai_luong] (
    [loai_luong_key] INT IDENTITY(1,1) PRIMARY KEY,
    [loai_luong_xnk] NVARCHAR(100)
);

-- 4. Dim Hàng Hóa
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dim_hang_hoa')
CREATE TABLE [dbo].[dim_hang_hoa] (
    [hang_hoa_key] INT IDENTITY(1,1) PRIMARY KEY,
    [mo_hang_hoa] NVARCHAR(MAX)
);

-- 5. Dim Đơn Vị
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dim_don_vi')
CREATE TABLE [dbo].[dim_don_vi] (
    [don_vi_key] INT IDENTITY(1,1) PRIMARY KEY,
    [don_vi_so_luong] NVARCHAR(50)
);

-- 6. Bảng Fact
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'fact_thuong_mai')
CREATE TABLE [dbo].[fact_thuong_mai] (
    [fact_key] INT IDENTITY(1,1) PRIMARY KEY,
    [stt] INT,
    [thoi_gian_key] INT FOREIGN KEY REFERENCES [dim_thoi_gian]([thoi_gian_key]),
    [doi_tac_key] INT FOREIGN KEY REFERENCES [dim_doi_tac]([doi_tac_key]),
    [loai_luong_key] INT FOREIGN KEY REFERENCES [dim_loai_luong]([loai_luong_key]),
    [hang_hoa_key] INT FOREIGN KEY REFERENCES [dim_hang_hoa]([hang_hoa_key]),
    [don_vi_key] INT FOREIGN KEY REFERENCES [dim_don_vi]([don_vi_key]),
    [so_luong] FLOAT,
    [so_luong_thay_the] FLOAT,
    [trong_luong_tinh_kg] FLOAT,
    [gia_tri_cif_usd] FLOAT,
    [gia_tri_fob_usd] FLOAT,
    [gia_tri_chinh_usd] FLOAT
);
GO







SELECT TOP (1000)
    f.[stt] AS [STT],
    tg.[ma_ky_bao_cao] AS [Ma_ky_bao_cao],
    tg.[nam_bao_cao] AS [Nam_bao_cao],
    tg.[tuan_bao_cao] AS [Tuan_bao_cao],
    ll.[loai_luong_xnk] AS [Loai_luong_XNK],
    dt.[ten_nuoc_doi_tac] AS [Ten_nuoc_doi_tac],
    hh.[mo_hang_hoa] AS [Mo_hang_hoa],
    dv.[don_vi_so_luong] AS [Don_vi_so_luong],
    f.[so_luong] AS [So_luong],
    f.[so_luong_thay_the] AS [So_luong_thay_the],
    f.[trong_luong_tinh_kg] AS [Trong_luong_tinh_kg],
    f.[gia_tri_cif_usd] AS [Gia_tri_CIF_USD],
    f.[gia_tri_fob_usd] AS [Gia_tri_FOB_USD],
    f.[gia_tri_chinh_usd] AS [Gia_tri_chinh_USD]
FROM [DA1].[dbo].[fact_thuong_mai] f
LEFT JOIN [DA1].[dbo].[dim_thoi_gian] tg ON f.[thoi_gian_key] = tg.[thoi_gian_key]
LEFT JOIN [DA1].[dbo].[dim_loai_luong] ll ON f.[loai_luong_key] = ll.[loai_luong_key]
LEFT JOIN [DA1].[dbo].[dim_doi_tac] dt ON f.[doi_tac_key] = dt.[doi_tac_key]
LEFT JOIN [DA1].[dbo].[dim_hang_hoa] hh ON f.[hang_hoa_key] = hh.[hang_hoa_key]
LEFT JOIN [DA1].[dbo].[dim_don_vi] dv ON f.[don_vi_key] = dv.[don_vi_key];



USE [DA1];
GO

-- 1. Nạp bảng Dim Thời Gian
INSERT INTO [dbo].[dim_thoi_gian] ([ma_ky_bao_cao], [nam_bao_cao], [tuan_bao_cao])
SELECT DISTINCT [Ma_ky_bao_cao], [Nam_bao_cao], [Tuan_bao_cao]
FROM [dbo].[Data_XNK_goc_hoan_chinh_csv]
WHERE [Ma_ky_bao_cao] IS NOT NULL;

-- 2. Nạp bảng Dim Đối Tác
INSERT INTO [dbo].[dim_doi_tac] ([ten_nuoc_doi_tac])
SELECT DISTINCT [Ten_nuoc_doi_tac]
FROM [dbo].[Data_XNK_goc_hoan_chinh_csv]
WHERE [Ten_nuoc_doi_tac] IS NOT NULL;

-- 3. Nạp bảng Dim Loại Luồng
INSERT INTO [dbo].[dim_loai_luong] ([loai_luong_xnk])
SELECT DISTINCT [Loai_luong_XNK]
FROM [dbo].[Data_XNK_goc_hoan_chinh_csv]
WHERE [Loai_luong_XNK] IS NOT NULL;

-- 4. Nạp bảng Dim Hàng Hóa
INSERT INTO [dbo].[dim_hang_hoa] ([mo_hang_hoa])
SELECT DISTINCT [Mo_hang_hoa]
FROM [dbo].[Data_XNK_goc_hoan_chinh_csv]
WHERE [Mo_hang_hoa] IS NOT NULL;

-- 5. Nạp bảng Dim Đơn Vị
INSERT INTO [dbo].[dim_don_vi] ([don_vi_so_luong])
SELECT DISTINCT [Don_vi_so_luong]
FROM [dbo].[Data_XNK_goc_hoan_chinh_csv]
WHERE [Don_vi_so_luong] IS NOT NULL;
GO




USE [DA1];
GO

INSERT INTO [dbo].[fact_thuong_mai] (
    [stt],
    [thoi_gian_key],
    [doi_tac_key],
    [loai_luong_key],
    [hang_hoa_key],
    [don_vi_key],
    [so_luong],
    [so_luong_thay_the],
    [trong_luong_tinh_kg],
    [gia_tri_cif_usd],
    [gia_tri_fob_usd],
    [gia_tri_chinh_usd]
)
SELECT 
    g.[STT],
    tg.[thoi_gian_key],
    dt.[doi_tac_key],
    ll.[loai_luong_key],
    hh.[hang_hoa_key],
    dv.[don_vi_key],
    g.[So_luong],
    g.[So_luong_thay_the],
    g.[Trong_luong_tinh_kg],
    g.[Gia_tri_CIF_USD],
    g.[Gia_tri_FOB_USD],
    g.[Gia_tri_chinh_USD]
FROM [dbo].[Data_XNK_goc_hoan_chinh_csv] g
LEFT JOIN [dbo].[dim_thoi_gian] tg 
    ON ISNULL(g.[Ma_ky_bao_cao], '') = ISNULL(tg.[ma_ky_bao_cao], '')
   AND ISNULL(g.[Nam_bao_cao], 0) = ISNULL(tg.[nam_bao_cao], 0)
   AND ISNULL(g.[Tuan_bao_cao], 0) = ISNULL(tg.[tuan_bao_cao], 0)
LEFT JOIN [dbo].[dim_doi_tac] dt 
    ON ISNULL(g.[Ten_nuoc_doi_tac], '') = ISNULL(dt.[ten_nuoc_doi_tac], '')
LEFT JOIN [dbo].[dim_loai_luong] ll 
    ON ISNULL(g.[Loai_luong_XNK], '') = ISNULL(ll.[loai_luong_xnk], '')
LEFT JOIN [dbo].[dim_hang_hoa] hh 
    ON ISNULL(g.[Mo_hang_hoa], '') = ISNULL(hh.[mo_hang_hoa], '')
LEFT JOIN [dbo].[dim_don_vi] dv 
    ON ISNULL(g.[Don_vi_so_luong], '') = ISNULL(dv.[don_vi_so_luong], '');
GO