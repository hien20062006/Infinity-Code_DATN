SELECT
    -- =========================
    -- THÔNG TIN ĐƠN HÀNG - FACT
    -- =========================
    f.ma_don,
    
    -- =========================
    -- KHÁCH HÀNG
    -- =========================
    kh.ma_khach_hang,
    kh.so_dien_thoai,

    -- =========================
    -- SẢN PHẨM
    -- =========================
    sp.ma_san_pham,
    sp.ten_san_pham,
    sp.nhom_hang,
    sp.thuong_hieu,
    sp.danh_muc,

    -- =========================
    -- ĐỊA ĐIỂM
    -- =========================
    dd.tinh_thanh,

    -- =========================
    -- KÊNH BÁN
    -- =========================
    kb.kenh_ban,

    -- =========================
    -- ĐƠN VỊ GIAO
    -- =========================
    dv.don_vi_giao,

    -- =========================
    -- THANH TOÁN
    -- =========================
    tt.phuong_thuc_thanh_toan,

    -- =========================
    -- TRẠNG THÁI ĐƠN HÀNG
    -- =========================
    tr.trang_thai,

    -- =========================
    -- NGÀY ĐẶT HÀNG
    -- =========================
    tg_dat.ngay AS ngay_dat,
    tg_dat.ngay_trong_thang AS ngay_dat_trong_thang,
    tg_dat.thang AS thang_dat,
    tg_dat.quy AS quy_dat,
    tg_dat.nam AS nam_dat,
    tg_dat.thu_trong_tuan AS thu_trong_tuan_dat,

    -- =========================
    -- NGÀY GIAO DỰ KIẾN
    -- =========================
    tg_giao.ngay AS ngay_giao_du_kien,
    tg_giao.ngay_trong_thang AS ngay_giao_du_kien_trong_thang,
    tg_giao.thang AS thang_giao_du_kien,
    tg_giao.quy AS quy_giao_du_kien,
    tg_giao.nam AS nam_giao_du_kien,
    tg_giao.thu_trong_tuan AS thu_trong_tuan_giao_du_kien,

    -- =========================
    -- CHỈ SỐ ĐƠN HÀNG
    -- =========================
    f.so_luong,
    f.don_gia,
    f.ty_le_giam_gia,
    f.tien_giam,
    f.tong_hang,
    f.vat_10,
    f.phi_van_chuyen,
    f.tong_thanh_toan,
    f.so_lan_khach_quay_lai

FROM fact_don_hang AS f

-- =========================
-- JOIN KHÁCH HÀNG
-- =========================
LEFT JOIN dim_khach_hang AS kh
    ON f.khach_hang_key = kh.khach_hang_key

-- =========================
-- JOIN SẢN PHẨM
-- =========================
LEFT JOIN dim_san_pham AS sp
    ON f.san_pham_key = sp.san_pham_key

-- =========================
-- JOIN ĐỊA ĐIỂM
-- =========================
LEFT JOIN dim_dia_diem AS dd
    ON f.dia_diem_key = dd.dia_diem_key

-- =========================
-- JOIN ĐƠN VỊ GIAO
-- =========================
LEFT JOIN dim_don_vi_giao AS dv
    ON f.don_vi_giao_key = dv.don_vi_giao_key

-- =========================
-- JOIN THANH TOÁN
-- =========================
LEFT JOIN dim_thanh_toan AS tt
    ON f.thanh_toan_key = tt.thanh_toan_key

-- =========================
-- JOIN KÊNH BÁN
-- =========================
LEFT JOIN dim_kenh_ban AS kb
    ON f.kenh_ban_key = kb.kenh_ban_key

-- =========================
-- JOIN TRẠNG THÁI
-- =========================
LEFT JOIN dim_trang_thai AS tr
    ON f.trang_thai_key = tr.trang_thai_key

-- =========================
-- JOIN NGÀY ĐẶT
-- =========================
LEFT JOIN dim_thoi_gian AS tg_dat
    ON f.ngay_dat_key = tg_dat.thoi_gian_key

-- =========================
-- JOIN NGÀY GIAO DỰ KIẾN
-- =========================
LEFT JOIN dim_thoi_gian AS tg_giao
    ON f.ngay_giao_du_kien_key = tg_giao.thoi_gian_key;