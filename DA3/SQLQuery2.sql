CREATE TABLE dbo.Dim_Thoi_Gian_Thi_Phan
(
    Ma_Thoi_Gian INT IDENTITY(1,1) NOT NULL,
    Ngay DATE NOT NULL,
    Nam INT NOT NULL,
    Thang INT NOT NULL,
    Quy INT NOT NULL,

    CONSTRAINT PK_Dim_Thoi_Gian_Thi_Phan
        PRIMARY KEY (Ma_Thoi_Gian)
);
GO


INSERT INTO dbo.Dim_Thoi_Gian_Thi_Phan
(
    Ngay,
    Nam,
    Thang,
    Quy
)
SELECT DISTINCT
    CAST([Date] AS DATE),
    CAST([Year] AS INT),
    CAST([Month] AS INT),
    DATEPART(QUARTER, CAST([Date] AS DATE))
FROM dbo.hang_viet_nam_csv
WHERE [Date] IS NOT NULL;
GO


INSERT INTO dbo.Dim_Thoi_Gian_Thi_Phan
(
    Ngay,
    Nam,
    Thang,
    Quy
)
SELECT DISTINCT
    CAST([Date] AS DATE),
    CAST([Year] AS INT),
    CAST([Month] AS INT),
    DATEPART(QUARTER, CAST([Date] AS DATE))
FROM dbo.hang_viet_nam_csv
WHERE [Date] IS NOT NULL;
GO



SELECT *
FROM dbo.Dim_Thoi_Gian_Thi_Phan
ORDER BY Nam, Thang;



CREATE TABLE dbo.Dim_Thuong_Hieu_Thi_Phan
(
    Ma_Thuong_Hieu INT IDENTITY(1,1) NOT NULL,
    Ten_Thuong_Hieu NVARCHAR(100) NOT NULL,

    CONSTRAINT PK_Dim_Thuong_Hieu_Thi_Phan
        PRIMARY KEY (Ma_Thuong_Hieu),

    CONSTRAINT UQ_Dim_Thuong_Hieu_Thi_Phan
        UNIQUE (Ten_Thuong_Hieu)
);
GO


INSERT INTO dbo.Dim_Thuong_Hieu_Thi_Phan
(
    Ten_Thuong_Hieu
)
VALUES
(N'Apple'),
(N'Samsung'),
(N'Oppo'),
(N'Xiaomi'),
(N'Vivo'),
(N'Nokia'),
(N'Realme'),
(N'Unknown'),
(N'Huawei'),
(N'Sony'),
(N'Vsmart'),
(N'LG'),
(N'Asus'),
(N'HTC'),
(N'Lenovo'),
(N'Google'),
(N'Tecno'),
(N'RIM'),
(N'Motorola'),
(N'BBK'),
(N'Itel'),
(N'Mobicel'),
(N'Pantech'),
(N'Honor'),
(N'OnePlus'),
(N'ZTE'),
(N'Wiko'),
(N'Infinix'),
(N'Alcatel'),
(N'Sharp'),
(N'Acer'),
(N'Meizu'),
(N'Coolpad'),
(N'Other');
GO




CREATE TABLE dbo.Fact_Thi_Phan_Thuong_Hieu
(
    Ma_Fact INT IDENTITY(1,1) NOT NULL,

    Ma_Thoi_Gian INT NOT NULL,
    Ma_Thuong_Hieu INT NOT NULL,

    Thi_Phan DECIMAL(10,2) NULL,

    CONSTRAINT PK_Fact_Thi_Phan_Thuong_Hieu
        PRIMARY KEY (Ma_Fact),

    CONSTRAINT FK_Fact_Thi_Phan_Thoi_Gian
        FOREIGN KEY (Ma_Thoi_Gian)
        REFERENCES dbo.Dim_Thoi_Gian_Thi_Phan(Ma_Thoi_Gian),

    CONSTRAINT FK_Fact_Thi_Phan_Thuong_Hieu
        FOREIGN KEY (Ma_Thuong_Hieu)
        REFERENCES dbo.Dim_Thuong_Hieu_Thi_Phan(Ma_Thuong_Hieu)
);
GO





INSERT INTO dbo.Fact_Thi_Phan_Thuong_Hieu
(
    Ma_Thoi_Gian,
    Ma_Thuong_Hieu,
    Thi_Phan
)
SELECT
    tg.Ma_Thoi_Gian,
    th.Ma_Thuong_Hieu,
    CAST(u.Thi_Phan AS DECIMAL(10,2))
FROM dbo.hang_viet_nam_csv h

CROSS APPLY
(
    VALUES
    (N'Apple', h.Apple),
    (N'Samsung', h.Samsung),
    (N'Oppo', h.Oppo),
    (N'Xiaomi', h.Xiaomi),
    (N'Vivo', h.Vivo),
    (N'Nokia', h.Nokia),
    (N'Realme', h.Realme),
    (N'Unknown', h.Unknown),
    (N'Huawei', h.Huawei),
    (N'Sony', h.Sony),
    (N'Vsmart', h.Vsmart),
    (N'LG', h.LG),
    (N'Asus', h.Asus),
    (N'HTC', h.HTC),
    (N'Lenovo', h.Lenovo),
    (N'Google', h.Google),
    (N'Tecno', h.Tecno),
    (N'RIM', h.RIM),
    (N'Motorola', h.Motorola),
    (N'BBK', h.BBK),
    (N'Itel', h.Itel),
    (N'Mobicel', h.Mobicel),
    (N'Pantech', h.Pantech),
    (N'Honor', h.Honor),
    (N'OnePlus', h.OnePlus),
    (N'ZTE', h.ZTE),
    (N'Wiko', h.Wiko),
    (N'Infinix', h.Infinix),
    (N'Alcatel', h.Alcatel),
    (N'Sharp', h.Sharp),
    (N'Acer', h.Acer),
    (N'Meizu', h.Meizu),
    (N'Coolpad', h.Coolpad),
    (N'Other', h.Other)
) u(Ten_Thuong_Hieu, Thi_Phan)

INNER JOIN dbo.Dim_Thoi_Gian_Thi_Phan tg
    ON tg.Ngay = CAST(h.[Date] AS DATE)

INNER JOIN dbo.Dim_Thuong_Hieu_Thi_Phan th
    ON th.Ten_Thuong_Hieu = u.Ten_Thuong_Hieu;
GO



SELECT
    tg.Nam,
    tg.Thang,
    th.Ten_Thuong_Hieu,
    f.Thi_Phan
FROM dbo.Fact_Thi_Phan_Thuong_Hieu f
JOIN dbo.Dim_Thoi_Gian_Thi_Phan tg
    ON f.Ma_Thoi_Gian = tg.Ma_Thoi_Gian
JOIN dbo.Dim_Thuong_Hieu_Thi_Phan th
    ON f.Ma_Thuong_Hieu = th.Ma_Thuong_Hieu
ORDER BY
    tg.Nam,
    tg.Thang,
    th.Ten_Thuong_Hieu;