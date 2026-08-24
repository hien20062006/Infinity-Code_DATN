# ============================================================
# THẾ GIỚI DI ĐỘNG CRAWLER
#
# CÀO SẢN PHẨM + TẠO DATASET ĐƠN HÀNG
#
# WEBSITE:
# https://www.thegioididong.com
#
# QUY TẮC GIÁ:
#
# Don_Gia       = Giá gốc trên website
# Ty_Le_Giam    = % giảm trên website
# Tien_Giam     = Giá bán thực tế sau giảm trên website
# Tong_Hang     = Tien_Giam × So_Luong
# Tong_Thanh_Toan = Tong_Hang × 1.1
#
# KHÔNG SỬ DỤNG GIÁ TRỊ NGẪU NHIÊN
# ============================================================


import csv
import os
import re
import threading
from dataclasses import dataclass
from datetime import datetime
import tkinter as tk

from tkinter import (
    filedialog,
    messagebox,
    ttk
)

from typing import Dict, List

from playwright.sync_api import sync_playwright


# ============================================================
# 1. CẤU HÌNH DANH MỤC THẾ GIỚI DI ĐỘNG
# ============================================================

CATEGORY_URLS = {

    "Điện thoại":
        "https://www.thegioididong.com/dtdd",

    "Laptop":
        "https://www.thegioididong.com/laptop",

    "Máy tính bảng":
        "https://www.thegioididong.com/may-tinh-bang",

    "Phụ kiện":
        "https://www.thegioididong.com/phu-kien",
}


# ============================================================
# 2. DANH SÁCH THƯƠNG HIỆU
# ============================================================

KNOWN_BRANDS = [
    "iPhone", "Apple", "MacBook", "iPad", "Samsung", "Xiaomi", "Redmi", "Poco", "POCO",
    "Oppo", "OPPO", "Vivo", "vivo", "Realme", "realme", "Nokia", "Asus",
    "ASUS", "Acer", "Dell", "HP", "Lenovo", "MSI", "LG", "Huawei", "Honor", "HONOR",
    "Masstel", "Itel", "Anker", "JBL", "Sony", "Canon", "Baseus", "Nubia",
    "TECNO", "Tecno", "TCL", "Kingston", "Logitech", "Razer", "TP-Link", "Ugreen",
    "Belkin", "Marshall", "Garmin", "GoPro"
]


# ============================================================
# 3. ĐỊA CHỈ THẾ GIỚI DI ĐỘNG
#
# CHỈ DÙNG CỬA HÀNG THẾ GIỚI DI ĐỘNG
#
# KHÔNG ĐƯA ĐIỆN MÁY XANH VÀO
# ============================================================

TGDD_ADDRESSES = [

       ("TP. Hồ Chí Minh", "P. Tân Định", "128 Trần Quang Khải (Thế Giới Di Động)"),
    ("TP. Hồ Chí Minh", "P. Bến Thành", "136 Nguyễn Thái Học (Thế Giới Di Động)"),
    ("TP. Hồ Chí Minh", "P. Hòa Hưng", "228A–230 Đường 3 Tháng 2 (Thế Giới Di Động)"),
    ("TP. Hồ Chí Minh", "P. Tân Sơn Nhì", "455 Tân Kỳ Tân Quý (Thế Giới Di Động)"),
    ("TP. Hồ Chí Minh", "P. Thạnh Mỹ Tây", "602/1 Điện Biên Phủ (Thế Giới Di Động)"),
    ("TP. Hồ Chí Minh", "P. Thạnh Mỹ Tây", "820 Xô Viết Nghệ Tĩnh (Thế Giới Di Động)"),
    ("TP. Hồ Chí Minh", "P. Thới An", "354 Lê Văn Khương (Thế Giới Di Động)"),
    ("TP. Hồ Chí Minh", "P. Thông Tây Hội", "154–156 Lê Văn Thọ (Thế Giới Di Động)"),
    ("TP. Hồ Chí Minh", "P. Tăng Nhơn Phú", "159–161 Lê Văn Việt (Thế Giới Di Động)"),
    ("TP. Hồ Chí Minh", "X. Củ Chi", "01 Lê Minh Nhựt (Thế Giới Di Động)"),
    ("TP. Hồ Chí Minh", "P. Trung Mỹ Tây", "55A Nguyễn Ảnh Thủ (Thế Giới Di Động)"),
    ("TP. Hồ Chí Minh", "X. Bà Điểm", "1/1A Vạn Hạnh 3 (Thế Giới Di Động)"),
    ("TP. Hồ Chí Minh", "P. Gò Vấp", "Nguyễn Oanh – Nguyễn Văn Lượng (Thế Giới Di Động)"),
    ("TP. Hồ Chí Minh", "P. Tân Định", "218–220 Trần Quang Khải (Thế Giới Di Động)"),
    ("TP. Hồ Chí Minh", "P. Phan Đăng Lưu", "114 Phan Đăng Lưu (Thế Giới Di Động)"),
    ("TP. Hồ Chí Minh", "P. Phạm Ngũ Lão", "157–159 Nguyễn Thị Minh Khai (Thế Giới Di Động)"),
    ("TP. Hồ Chí Minh", "P. Khánh Hội", "177 Khánh Hội (Thế Giới Di Động)"),
    ("TP. Hồ Chí Minh", "P. Bình An", "139 Trần Não (Thế Giới Di Động)"),
    ("TP. Hồ Chí Minh", "P. Tân Quy", "248 Nguyễn Thị Thập (Thế Giới Di Động)"),
    ("TP. Hồ Chí Minh", "P. Phú Thạnh", "161 Nguyễn Sơn (Thế Giới Di Động)"),

    # Đồng Nai (20 địa chỉ)
    ("Đồng Nai", "P. Tam Hiệp", "QL1A/06/1B, Tổ 1, KP. 1 (Thế Giới Di Động)"),
    ("Đồng Nai", "P. Trấn Biên", "282B Võ Thị Sáu (Thế Giới Di Động)"),
    ("Đồng Nai", "P. Long Bình", "194 Nguyễn Ái Quốc (Thế Giới Di Động)"),
    ("Đồng Nai", "P. Trảng Dài", "Bùi Trọng Nghĩa/2, Tổ 31, KP. 3A (Thế Giới Di Động)"),
    ("Đồng Nai", "P. Phước Tân", "QL51/08, Tổ 07, Ấp Tân Mai 2 (Thế Giới Di Động)"),
    ("Đồng Nai", "P. Tam Phước", "301 Quốc lộ 51 (Thế Giới Di Động)"),
    ("Đồng Nai", "P. Hố Nai", "419–420, Tổ 29, Xóm 4, Ấp Thái Hòa (Thế Giới Di Động)"),
    ("Đồng Nai", "P. Phước Bình", "1910, Tổ 1, Ấp 1C (Thế Giới Di Động)"),
    ("Đồng Nai", "P. Long Thành", "702 Phạm Văn Đồng, Tổ 5, Khu Cầu Xéo (Thế Giới Di Động)"),
    ("Đồng Nai", "P. Long Thành", "486 Lê Duẩn, Khu Phước Thuận (Thế Giới Di Động)"),
    ("Đồng Nai", "P. Nhơn Trạch", "340 Lý Thái Tổ, Bến Cam (Thế Giới Di Động)"),
    ("Đồng Nai", "P. Phước An", "808 Hùng Vương, Ấp 1 (Thế Giới Di Động)"),
    ("Đồng Nai", "X. Thống Nhất", "26 Khu dân cư 4, Ấp Cây Xăng (Thế Giới Di Động)"),
    ("Đồng Nai", "X. Xuân Lộc", "398 Trần Phú, Khu 3 (Thế Giới Di Động)"),
    ("Đồng Nai", "X. Hưng Thịnh", "555 Quốc lộ 1A (Thế Giới Di Động)"),
    ("Đồng Nai", "X. Dầu Giây", "Ấp Trần Cao Vân (Thế Giới Di Động)"),
    ("Đồng Nai", "X. Bù Đăng", "112–114 Quốc lộ 14 (Thế Giới Di Động)"),
    ("Đồng Nai", "X. Thống Nhất", "26 Khu dân cư 4, Ấp Cây Xăng (Thế Giới Di Động)"),
    ("Đồng Nai", "P. Long Bình", "Ngã Ba Phát Triển, 94 Quốc lộ 1A, KP. 8A (Thế Giới Di Động)"),
    ("Đồng Nai", "X. Phước Thái", "1910, Tổ 1, Ấp 1C (Thế Giới Di Động)"),

    # Tây Ninh (4 địa chỉ)
    ("Tây Ninh", "P. Tân Ninh", "583 Cách Mạng Tháng 8 (Thế Giới Di Động)"),
    ("Tây Ninh", "P. Tân Ninh", "1197 Cách Mạng Tháng 8 (Thế Giới Di Động)"),
    ("Tây Ninh", "P. Long Hoa", "14 Phạm Hùng (Thế Giới Di Động)"),
    ("Tây Ninh", "P. Tân Ninh", "229 Cách Mạng Tháng 8 (Thế Giới Di Động)"),

    # Đồng Tháp (20 địa chỉ)
    ("Đồng Tháp", "P. Cao Lãnh", "83 Nguyễn Huệ (Thế Giới Di Động)"),
    ("Đồng Tháp", "P. Cao Lãnh", "178 Nguyễn Huệ (Thế Giới Di Động)"),
    ("Đồng Tháp", "P. Cao Lãnh", "72 Phạm Hữu Lầu (Thế Giới Di Động)"),
    ("Đồng Tháp", "P. Cao Lãnh", "329 Đường 30 Tháng 4 (Thế Giới Di Động)"),
    ("Đồng Tháp", "P. Sa Đéc", "Đường Nguyễn Sinh Sắc (Thế Giới Di Động)"),
    ("Đồng Tháp", "P. Sa Đéc", "Đường Nguyễn Tất Thành (Thế Giới Di Động)"),
    ("Đồng Tháp", "P. Tháp Mười", "119 Hùng Vương, Khóm 4 (Thế Giới Di Động)"),
    ("Đồng Tháp", "P. Hồng Ngự", "Đường Hùng Vương, Khóm 3 (Thế Giới Di Động)"),
    ("Đồng Tháp", "X. Lấp Vò", "280/1 Quốc lộ 80, Khóm Bình Thạnh 1 (Thế Giới Di Động)"),
    ("Đồng Tháp", "X. Tân Hồng", "50 Nguyễn Huệ (Thế Giới Di Động)"),
    ("Đồng Tháp", "X. Tràm Chim", "Khu vực Tràm Chim (Thế Giới Di Động)"),
    ("Đồng Tháp", "X. Mỹ Hiệp", "Ấp 02 (Thế Giới Di Động)"),
    ("Đồng Tháp", "X. Mỹ Hiệp", "Khu vực Mỹ Hiệp (Thế Giới Di Động)"),
    ("Đồng Tháp", "X. Cái Tàu Hạ", "83C Quốc lộ 80 (Thế Giới Di Động)"),
    ("Đồng Tháp", "X. Trường Xuân", "Ấp 5A (Thế Giới Di Động)"),
    ("Đồng Tháp", "X. Mỹ Ngãi", "Chợ Trần Quốc Toản (Thế Giới Di Động)"),
    ("Đồng Tháp", "X. Trung An", "132A Cầu Trung Lương, Khu phố 2 (Thế Giới Di Động)"),
    ("Đồng Tháp", "X. Đạo Thạnh", "49/2 Đường Ấp Bắc (Thế Giới Di Động)"),
    ("Đồng Tháp", "X. Đạo Thạnh", "25–26 Ấp Bắc (Thế Giới Di Động)"),
    ("Đồng Tháp", "X. Đạo Thạnh", "920 Lý Thường Kiệt (Thế Giới Di Động)"),

    # Vĩnh Long (20 địa chỉ)
    ("Vĩnh Long", "P. Long Châu", "93B Đường 2 Tháng 9, Khóm Hưng Đạo Vương (Thế Giới Di Động)"),
    ("Vĩnh Long", "P. Phước Hậu", "550 Phạm Thái Bường, Khóm 5 (Thế Giới Di Động)"),
    ("Vĩnh Long", "P. Bình Minh", "Tổ 21, Khóm 5 (Thế Giới Di Động)"),
    ("Vĩnh Long", "X. Càng Long", "248–250–252 Quốc lộ 53, Khóm 3 (Thế Giới Di Động)"),
    ("Vĩnh Long", "P. An Hội", "174A Đoàn Hoàng Minh (Thế Giới Di Động)"),
    ("Vĩnh Long", "P. Long Châu", "210 Lê Thái Tổ (Thế Giới Di Động)"),
    ("Vĩnh Long", "P. Long Đức", "20 Hùng Vương (Thế Giới Di Động)"),
    ("Vĩnh Long", "P. Phú Khương", "112B Đại lộ Đồng Khởi, Khóm 5 (Thế Giới Di Động)"),
    ("Vĩnh Long", "P. Long Châu", "56G Phạm Hùng (Thế Giới Di Động)"),
    ("Vĩnh Long", "P. Tân Hạnh", "14D–14E Đinh Tiên Hoàng, Khóm 4 (Thế Giới Di Động)"),
    ("Vĩnh Long", "X. Trung Thành", "Khóm 1 (Thế Giới Di Động)"),
    ("Vĩnh Long", "X. Long Hồ", "339 Quốc lộ 53, Khóm 1 (Thế Giới Di Động)"),
    ("Vĩnh Long", "X. Nguyệt Hóa", "181 Võ Nguyên Giáp, Khóm 6 (Thế Giới Di Động)"),
    ("Vĩnh Long", "X. Hiếu Phụng", "Ấp Nhơn Ngãi (Thế Giới Di Động)"),
    ("Vĩnh Long", "P. Trà Vinh", "474B Nguyễn Đáng, Khóm 3 (Thế Giới Di Động)"),
    ("Vĩnh Long", "X. Tam Bình", "Phan Văn Đáng, Khóm 3 (Thế Giới Di Động)"),
    ("Vĩnh Long", "X. Phú Quới", "197C/17 Quốc lộ 1A, Ấp Phước Yên (Thế Giới Di Động)"),
    ("Vĩnh Long", "X. Trà Ôn", "Quốc lộ 54, Khu 7 (Thế Giới Di Động)"),
    ("Vĩnh Long", "X. Chợ Lách", "278/18B1, Khu phố 2 (Thế Giới Di Động)"),
    ("Vĩnh Long", "X. Tiểu Cần", "Khóm 2 (Thế Giới Di Động)"),

    # Cần Thơ (20 địa chỉ)
    ("Cần Thơ", "P. Ninh Kiều", "86A–86–86B Đường 30 Tháng 4 (Thế Giới Di Động)"),
    ("Cần Thơ", "P. Cái Khế", "405 Nguyễn Văn Cừ (Thế Giới Di Động)"),
    ("Cần Thơ", "P. Cái Khế", "35B Cách Mạng Tháng 8 (Thế Giới Di Động)"),
    ("Cần Thơ", "P. Tân An", "217 Nguyễn Văn Linh / Đường 3 Tháng 2 (Thế Giới Di Động)"),
    ("Cần Thơ", "P. Phú Lợi", "50–52 Hai Bà Trưng (Thế Giới Di Động)"),
    ("Cần Thơ", "X. Cờ Đỏ", "Ấp Thới Hòa (Thế Giới Di Động)"),
    ("Cần Thơ", "P. Tân An", "305V Nguyễn Văn Linh, Khu vực 3 (Thế Giới Di Động)"),
    ("Cần Thơ", "P. Long Mỹ", "30 Nguyễn Huệ (Thế Giới Di Động)"),
    ("Cần Thơ", "P. Thới An Đông", "30A7 Khu Công nghiệp Trà Nóc (Thế Giới Di Động)"),
    ("Cần Thơ", "X. Thới Lai", "21 ĐT922, Ấp Thới Thuận A (Thế Giới Di Động)"),
    ("Cần Thơ", "X. Tân Bình", "954 Ấp Cầu Xáng (Thế Giới Di Động)"),
    ("Cần Thơ", "X. Phong Điền", "168–169–170 Ấp Thị Tứ (Thế Giới Di Động)"),
    ("Cần Thơ", "P. Bình Thủy", "26B/9 Lê Hồng Phong (Thế Giới Di Động)"),
    ("Cần Thơ", "P. Thốt Nốt", "17 Quốc lộ 91 (Thế Giới Di Động)"),
    ("Cần Thơ", "P. Vị Thanh", "Đường Trần Hưng Đạo, Khu vực 2 (Thế Giới Di Động)"),
    ("Cần Thơ", "P. Ngã Năm", "Khóm 1 (Thế Giới Di Động)"),
    ("Cần Thơ", "X. Châu Thành", "Tỉnh lộ 925, Ấp Thị Trấn (Thế Giới Di Động)"),
    ("Cần Thơ", "P. Vị Tân", "01 Ngô Quốc Trị (Thế Giới Di Động)"),
    ("Cần Thơ", "P. Ô Môn", "6 Quốc lộ 91, Khu vực 5 (Thế Giới Di Động)"),
    ("Cần Thơ", "P. Tân Bình", "52 Quốc lộ 61 (Thế Giới Di Động)"),

    # An Giang (20 địa chỉ)
    ("An Giang", "P. Long Xuyên", "170A Trần Hưng Đạo (Thế Giới Di Động)"),
    ("An Giang", "P. Long Xuyên", "820 Hà Hoàng Hổ (Thế Giới Di Động)"),
    ("An Giang", "P. Châu Đốc", "Tổ 1, Khóm Châu (Thế Giới Di Động)"),
    ("An Giang", "P. Châu Đốc", "104 Thủ Khoa Nghĩa (Thế Giới Di Động)"),
    ("An Giang", "P. Tân Châu", "7 Nguyễn Văn Linh (Thế Giới Di Động)"),
    ("An Giang", "P. Tân Châu", "1 Trần Hưng Đạo, Khóm Long (Thế Giới Di Động)"),
    ("An Giang", "P. An Châu", "391 Quốc lộ 91, Ấp Hòa Long 1 (Thế Giới Di Động)"),
    ("An Giang", "P. Châu Phú", "Quốc lộ 91, Ấp Bình Hòa (Thế Giới Di Động)"),
    ("An Giang", "P. Chợ Mới", "Nguyễn Hữu Cảnh, Ấp Long Hòa (Thế Giới Di Động)"),
    ("An Giang", "P. Bình Hòa", "Tổ 39, Ấp Bình Phú 1 (Thế Giới Di Động)"),
    ("An Giang", "X. Phú Tân", "181 Phú Mỹ (Thế Giới Di Động)"),
    ("An Giang", "X. Phú Tân", "Đường Tôn Đức Thắng (Thế Giới Di Động)"),
    ("An Giang", "X. Mỹ Thuận", "Khu phố Thị Tứ (Thế Giới Di Động)"),
    ("An Giang", "X. Long Điền", "191–193 ĐT942, Ấp Thị 2 (Thế Giới Di Động)"),
    ("An Giang", "X. Tri Tôn", "79 Trần Hưng Đạo, Khóm 2 (Thế Giới Di Động)"),
    ("An Giang", "X. Châu Thành", "607 Quốc lộ 61, KP. Minh Phú (Thế Giới Di Động)"),
    ("An Giang", "X. An Minh", "Khu phố 3 (Thế Giới Di Động)"),
    ("An Giang", "X. Hòn Đất", "Khu phố Đường Hòn (Thế Giới Di Động)"),
    ("An Giang", "Đặc khu Phú Quốc", "Nguyễn Trung Trực (Thế Giới Di Động)"),
    ("An Giang", "X. Óc Eo", "483 Nguyễn Thị Hạnh, Ấp Tân Hiệp A (Thế Giới Di Động)"),

    # Cà Mau (20 địa chỉ)
    ("Cà Mau", "P. Tân Thành", "2A Trần Hưng Đạo, Khóm 6 (Thế Giới Di Động)"),
    ("Cà Mau", "P. Lý Văn Lâm", "125B–127 Nguyễn Tất Thành, Khóm 7 (Thế Giới Di Động)"),
    ("Cà Mau", "P. Lý Văn Lâm", "155A Nguyễn Tất Thành (Thế Giới Di Động)"),
    ("Cà Mau", "P. An Xuyên", "18 Ngô Quyền (Thế Giới Di Động)"),
    ("Cà Mau", "P. Tân Thành", "255 Quốc lộ 1A, Ấp 3 (Thế Giới Di Động)"),
    ("Cà Mau", "X. Trần Văn Thời", "Khóm 7 (Thế Giới Di Động)"),
    ("Cà Mau", "X. Nguyễn Phích", "Khóm 1 (Thế Giới Di Động)"),
    ("Cà Mau", "X. Đầm Dơi", "57 Dương Thị Cẩm Vân, Vùng 4 (Thế Giới Di Động)"),
    ("Cà Mau", "X. Thới Bình", "Khóm 8 (Thế Giới Di Động)"),
    ("Cà Mau", "X. Hồng Dân", "Ấp Nội Ô (Thế Giới Di Động)"),
    ("Cà Mau", "X. Hòa Bình", "03 Quốc lộ 1A (Thế Giới Di Động)"),
    ("Cà Mau", "X. Năm Căn", "92 Nguyễn Tất Thành, Khóm 4 (Thế Giới Di Động)"),
    ("Cà Mau", "X. Năm Căn", "Khu vực 1/Số 00780 Nguyễn Tất Thành, Khóm 2 (Thế Giới Di Động)"),
    ("Cà Mau", "X. Gành Hào", "78 Ấp 3, Ngã 4 chợ (Thế Giới Di Động)"),
    ("Cà Mau", "X. Giá Rai", "148B Quốc lộ 1A, Ấp 2 (Thế Giới Di Động)"),
    ("Cà Mau", "P. Bạc Liêu", "C1B Trần Phú (Thế Giới Di Động)"),
    ("Cà Mau", "X. Đông Hải", "Khu vực trung tâm Đông Hải (Thế Giới Di Động)"),
    ("Cà Mau", "X. Vĩnh Lợi", "Khu vực trung tâm Vĩnh Lợi (Thế Giới Di Động)"),
    ("Cà Mau", "X. Hòa Bình", "Khu vực trung tâm Hòa Bình (Thế Giới Di Động)"),
    ("Cà Mau", "X. Phong Thạnh", "Khu vực trung tâm Phong Thạnh (Thế Giới Di Động)"),

]


# ============================================================
# 4. CỘT CSV
# ============================================================

CSV_COLUMNS = [
    "STT", "Tinh_Thanh", "Phuong_Xa", "Dia_Chi_Cu_The", 
    "Ma_San_Pham", "Ten_San_Pham", "Nhom_Hang", "So_Luong", 
    "Don_Gia", "Ty_Le_Giam_Gia", "Tien_Giam", "Tong_Hang", 
    "Tong_Thanh_Toan", "Tan_suat_mua_hang", "Thuong_Hieu", "Danh_Muc"
]

# ============================================================
# 5. DATA MODEL
# ============================================================

@dataclass
class RawProduct:

    ma_san_pham: str

    ten_san_pham: str

    don_gia_goc: int

    gia_sau_giam: int

    ty_le_giam: int

    danh_muc: str

    thuong_hieu: str


# ============================================================
# 6. XỬ LÝ THƯƠNG HIỆU
# ============================================================

def guess_brand(product_name: str) -> str:

    product_lower = product_name.lower()

    # Kiểm tra thương hiệu dài trước
    brands = sorted(
        KNOWN_BRANDS,
        key=lambda x: len(x),
        reverse=True
    )

    for brand in brands:

        if brand.lower() in product_lower:

            if brand in (
                "iPhone",
                "MacBook",
                "iPad"
            ):

                return "Apple"

            if brand in (
                "Redmi",
                "Poco"
            ):

                return "Xiaomi"

            return brand

    return "Khác"


# ============================================================
# 7. ĐỌC GIÁ
# ============================================================

def parse_price(price_text: str) -> int:

    if not price_text:

        return 0

    cleaned = price_text.replace(
        "\xa0",
        " "
    )

    digits = re.sub(
        r"[^\d]",
        "",
        cleaned
    )

    if not digits:

        return 0

    try:

        return int(digits)

    except ValueError:

        return 0


# ============================================================
# 8. FORMAT TIỀN
# ============================================================

def format_currency(amount: int) -> str:

    return f"{int(amount):,}".replace(
        ",",
        "."
    )


# ============================================================
# 9. LẤY ĐỊA CHỈ
# ============================================================

def get_tgdd_address(index: int):

    if not TGDD_ADDRESSES:

        return "", "", ""

    position = (
        (index - 1)
        % len(TGDD_ADDRESSES)
    )

    return TGDD_ADDRESSES[position]


# ============================================================
# 10. TẠO SỐ LƯỢNG
#
# DÙNG CÔNG THỨC CỐ ĐỊNH
# ============================================================

def generate_quantity(
    index: int,
    product: RawProduct
) -> int:

    category_factor = {

        "Điện thoại": 2,

        "Laptop": 1,

        "Máy tính bảng": 2,

        "Phụ kiện": 3,
    }

    factor = category_factor.get(
        product.danh_muc,
        2
    )

    value = (

        (
            index * 7
            + len(product.ten_san_pham)
            + factor
        )

        % 10
    ) + 1

    if value <= 6:

        return 1

    if value <= 8:

        return 2

    return 3


# ============================================================
# 11. TẠO TẦN SUẤT MUA HÀNG
#
# DÙNG CÔNG THỨC CỐ ĐỊNH
# ============================================================

def generate_purchase_frequency(
    index: int,
    product: RawProduct
) -> int:

    values = [

        5,
        10,
        15,
        20,
        30,
    ]

    product_score = (

        len(product.ten_san_pham)

        + len(product.thuong_hieu)

        + len(product.danh_muc)
    )

    position = (

        index * 3
        + product_score

    ) % len(values)

    return values[position]


# ============================================================
# 12. CRAWLER THẾ GIỚI DI ĐỘNG
# ============================================================

class TGDDCrawler:

    def __init__(
        self,
        headless=False,
        max_products_per_cat=50,
        load_more_clicks=5,
        log_cb=None,
        stop_flag=None
    ):

        self.headless = headless

        self.max_products_per_cat = (
            max_products_per_cat
        )

        self.load_more_clicks = (
            load_more_clicks
        )

        self.log_cb = (
            log_cb
            or (lambda m: None)
        )

        self.stop_flag = (
            stop_flag
            or (lambda: False)
        )


    # ========================================================
    # LOG
    # ========================================================

    def log(self, msg):

        self.log_cb(msg)


    # ========================================================
    # SCROLL
    # ========================================================

    def auto_scroll(self, page):

        for _ in range(8):

            if self.stop_flag():

                break

            page.evaluate(
                """
                window.scrollBy(
                    0,
                    700
                );
                """
            )

            page.wait_for_timeout(
                700
            )


    # ========================================================
    # LẤY % GIẢM
    # ========================================================

    def extract_discount(
        self,
        text: str
    ) -> int:

        if not text:

            return 0

        patterns = [

            r"-\s*(\d{1,2})\s*%",

            r"giảm\s*(\d{1,2})\s*%",

            r"(\d{1,2})\s*%",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            if match:

                try:

                    value = int(
                        match.group(1)
                    )

                    if 0 <= value <= 100:

                        return value

                except ValueError:

                    pass

        return 0


    # ========================================================
    # LẤY GIÁ TRONG MỘT ELEMENT
    #
    # QUAN TRỌNG:
    #
    # Không lấy min()
    # Không lấy max()
    #
    # Thứ tự ưu tiên:
    #
    # 1. Giá bán hiện tại
    # 2. Giá gốc
    # ========================================================

    def extract_prices_from_card(
        self,
        card
    ):

        current_price = 0

        old_price = 0

        discount = 0


        # ====================================================
        # 1. TÌM GIÁ BÁN HIỆN TẠI
        # ====================================================

        current_selectors = [

            ".price",

            ".price-current",

            ".box-price",

            ".item-price",

            "[class*='price-current']",

            "[class*='current-price']",

            "[class*='price']",
        ]


        for selector in current_selectors:

            try:

                elements = card.locator(
                    selector
                )

                count = min(
                    elements.count(),
                    10
                )

                for i in range(count):

                    try:

                        element = (
                            elements.nth(i)
                        )

                        text = (
                            element
                            .inner_text(
                                timeout=500
                            )
                            .strip()
                        )

                        matches = re.findall(

                            r"(?<!\d)"
                            r"(\d{1,3}"
                            r"(?:[.,]\d{3})+)"
                            r"\s*(?:đ|₫|vnđ)"
                            r"(?!\w)",

                            text,

                            flags=re.IGNORECASE
                        )

                        if matches:

                            price = parse_price(
                                matches[0]
                            )

                            if price >= 100000:

                                current_price = price

                                break

                    except Exception:

                        continue

                if current_price:

                    break

            except Exception:

                continue


        # ====================================================
        # 2. TÌM GIÁ GỐC BỊ GẠCH
        #
        # TGDD thường dùng:
        #
        # .price-old
        # .price-old
        # text-decoration
        # ====================================================

        old_selectors = [

            ".price-old",

            ".old-price",

            "[class*='price-old']",

            "[class*='old-price']",

            "del",

            "s",
        ]


        for selector in old_selectors:

            try:

                elements = card.locator(
                    selector
                )

                count = min(
                    elements.count(),
                    10
                )

                for i in range(count):

                    try:

                        element = (
                            elements.nth(i)
                        )

                        text = (
                            element
                            .inner_text(
                                timeout=500
                            )
                            .strip()
                        )

                        matches = re.findall(

                            r"(?<!\d)"
                            r"(\d{1,3}"
                            r"(?:[.,]\d{3})+)"
                            r"\s*(?:đ|₫|vnđ)"
                            r"(?!\w)",

                            text,

                            flags=re.IGNORECASE
                        )

                        if matches:

                            price = parse_price(
                                matches[0]
                            )

                            if price >= 100000:

                                old_price = price

                                break

                    except Exception:

                        continue

                if old_price:

                    break

            except Exception:

                continue


        # ====================================================
        # 3. TÌM % GIẢM
        # ====================================================

        try:

            card_text = (
                card
                .inner_text(
                    timeout=1000
                )
            )

            discount = (
                self.extract_discount(
                    card_text
                )
            )

        except Exception:

            discount = 0


        # ====================================================
        # 4. FALLBACK
        #
        # Nếu selector giá không bắt được,
        # đọc các số tiền trong card.
        #
        # KHÔNG dùng min/max.
        # ====================================================

        if not current_price or not old_price:

            try:

                card_text = (
                    card
                    .inner_text(
                        timeout=1000
                    )
                )

                lines = [

                    line.strip()

                    for line
                    in card_text.splitlines()

                    if line.strip()
                ]


                price_candidates = []


                for line in lines:

                    lower = (
                        line.lower()
                    )

                    if (

                        "trả góp"
                        in lower

                        or "mỗi tháng"
                        in lower

                        or "/tháng"
                        in lower

                    ):

                        continue


                    matches = re.findall(

                        r"(?<!\d)"
                        r"(\d{1,3}"
                        r"(?:[.,]\d{3})+)"
                        r"\s*(?:đ|₫|vnđ)"
                        r"(?!\w)",

                        line,

                        flags=re.IGNORECASE
                    )


                    for value in matches:

                        price = parse_price(
                            value
                        )

                        if price >= 100000:

                            price_candidates.append(
                                price
                            )


                # Loại trùng nhưng giữ nguyên thứ tự
                unique_prices = []

                for price in price_candidates:

                    if price not in unique_prices:

                        unique_prices.append(
                            price
                        )


                if unique_prices:

                    if not current_price:

                        current_price = (
                            unique_prices[0]
                        )

                    if (
                        not old_price
                        and len(unique_prices) >= 2
                    ):

                        old_price = (
                            unique_prices[1]
                        )

            except Exception:

                pass


        # ====================================================
        # 5. NẾU GIÁ ĐANG ĐỌC BỊ NGƯỢC
        #
        # Ví dụ:
        #
        # current = 13.990.000
        # old     = 12.290.000
        #
        # thì đổi lại.
        # ====================================================

        if (

            current_price
            and old_price
            and old_price < current_price

        ):

            old_price, current_price = (

                current_price,
                old_price
            )


        # ====================================================
        # 6. CHỈ CÓ MỘT GIÁ
        # ====================================================

        if current_price and not old_price:

            old_price = current_price

            discount = 0


        # ====================================================
        # 7. NẾU CÓ 2 GIÁ NHƯNG WEB KHÔNG HIỂN THỊ %
        # ====================================================

        if (

            discount == 0

            and old_price > current_price

            and old_price > 0

        ):

            discount = round(

                (

                    (
                        old_price
                        - current_price
                    )

                    / old_price

                )

                * 100
            )


        return (

            old_price,

            current_price,

            discount
        )


    # ========================================================
    # LẤY TÊN SẢN PHẨM
    # ========================================================

    def extract_product_name(
        self,
        card
    ) -> str:

        selectors = [

            "h3",

            "h2",

            ".item-name",

            ".product-name",

            "[class*='product-name']",

            "[class*='item-name']",

            "a",
        ]


        for selector in selectors:

            try:

                elements = card.locator(
                    selector
                )

                count = min(
                    elements.count(),
                    10
                )

                for i in range(count):

                    try:

                        text = (
                            elements
                            .nth(i)
                            .inner_text(
                                timeout=500
                            )
                            .strip()
                        )

                        text = re.sub(
                            r"\s+",
                            " ",
                            text
                        ).strip()


                        if len(text) < 5:

                            continue


                        lower = (
                            text.lower()
                        )


                        if (

                            "mua ngay"
                            in lower

                            or "xem chi tiết"
                            in lower

                            or "trả góp"
                            in lower

                        ):

                            continue


                        # Không lấy text chỉ chứa giá
                        if re.fullmatch(

                            r"[\d\.,\sđ₫]+",

                            text,

                            flags=re.IGNORECASE
                        ):

                            continue


                        return text

                    except Exception:

                        continue

            except Exception:

                continue


        return ""


    # ========================================================
    # LẤY SKU / MÃ SẢN PHẨM
    # ========================================================

    def extract_sku(
        self,
        card,
        fallback_index: int
    ) -> str:

        try:

            card_text = (
                card
                .inner_text(
                    timeout=1000
                )
            )

            patterns = [

                r"SKU\s*[:\-]?\s*([A-Za-z0-9\-_]+)",

                r"Mã\s*(?:SP|sản phẩm)"
                r"\s*[:\-]?\s*([A-Za-z0-9\-_]+)",
            ]


            for pattern in patterns:

                match = re.search(
                    pattern,
                    card_text,
                    flags=re.IGNORECASE
                )

                if match:

                    return (
                        match.group(1)
                        .strip()
                    )

        except Exception:

            pass


        # Nếu card không có SKU,
        # tạo mã theo vị trí sản phẩm.
        return f"TGDD{fallback_index:05d}"


    # ========================================================
    # CRAWL CATEGORY
    # ========================================================

    def crawl_category(
        self,
        page,
        category: str
    ) -> List[RawProduct]:

        url = CATEGORY_URLS.get(
            category
        )


        if not url:

            return []


        self.log(
            f"Mở danh mục: {category}"
        )

        self.log(
            f"URL: {url}"
        )


        # ====================================================
        # MỞ TRANG
        # ====================================================

        try:

            page.goto(

                url,

                timeout=60000,

                wait_until="domcontentloaded"
            )

        except Exception as exc:

            self.log(
                f"[LỖI] Không mở được "
                f"{category}: {exc}"
            )

            return []


        page.wait_for_timeout(
            4000
        )


        # ====================================================
        # SCROLL
        # ====================================================

        self.auto_scroll(
            page
        )


        # ====================================================
        # BẤM XEM THÊM
        # ====================================================

        for i in range(
            self.load_more_clicks
        ):

            if self.stop_flag():

                break


            clicked = False


            try:

                page.evaluate(
                    """
                    window.scrollTo(
                        0,
                        document.body.scrollHeight
                    );
                    """
                )


                page.wait_for_timeout(
                    1000
                )


                buttons = page.locator(
                    "a, button"
                )


                count = min(
                    buttons.count(),
                    150
                )


                for j in range(count):

                    try:

                        element = (
                            buttons.nth(j)
                        )


                        if not element.is_visible():

                            continue


                        text = (
                            element
                            .inner_text(
                                timeout=500
                            )
                            .strip()
                        )


                        if not text:

                            continue


                        lower = (
                            text.lower()
                        )


                        if (

                            "xem thêm"
                            in lower

                            or "xem thêm sản phẩm"
                            in lower

                        ):

                            element.click(
                                timeout=3000
                            )


                            self.log(
                                f" -> Nhấn "
                                f"'Xem thêm' "
                                f"lần {i + 1}"
                            )


                            page.wait_for_timeout(
                                1800
                            )


                            self.auto_scroll(
                                page
                            )


                            clicked = True

                            break


                    except Exception:

                        continue


            except Exception:

                pass


            if not clicked:

                break


        # ====================================================
        # TÌM PRODUCT CARD
        #
        # TGDD có thể thay đổi class theo thời điểm.
        #
        # Ta thử nhiều selector.
        # ====================================================

        card_selectors = [

            "li.item",

            "li.item-2020",

            "li[class*='item']",

            "div[class*='item']",

            "div[class*='product']",

            "a[href*='/dtdd/']",

            "a[href*='/laptop/']",

            "a[href*='/may-tinh-bang/']",

            "a[href*='/phu-kien/']",
        ]


        cards = None


        for selector in card_selectors:

            try:

                locator = page.locator(
                    selector
                )

                count = locator.count()


                if count >= 3:

                    cards = locator

                    self.log(
                        f" -> Tìm thấy "
                        f"{count} phần tử "
                        f"theo selector: "
                        f"{selector}"
                    )

                    break

            except Exception:

                continue


        if cards is None:

            self.log(
                f"[CẢNH BÁO] "
                f"Không tìm thấy product card "
                f"ở danh mục {category}."
            )

            return []


        # ====================================================
        # XỬ LÝ SẢN PHẨM
        # ====================================================

        products = []

        seen_names = set()

        seen_skus = set()


        count = min(

            cards.count(),

            self.max_products_per_cat * 3
        )


        for i in range(count):

            if self.stop_flag():

                break


            if len(products) >= (
                self.max_products_per_cat
            ):

                break


            try:

                card = cards.nth(i)


                # =================================================
                # TÊN
                # =================================================

                name = (
                    self.extract_product_name(
                        card
                    )
                )


                if not name:

                    continue


                name_key = re.sub(
                    r"\s+",
                    " ",
                    name.lower()
                ).strip()


                if name_key in seen_names:

                    continue


                # =================================================
                # SKU
                # =================================================

                sku = (
                    self.extract_sku(
                        card,
                        i + 1
                    )
                )


                if sku in seen_skus:

                    continue


                # =================================================
                # GIÁ
                # =================================================

                (
                    don_gia_goc,
                    gia_sau_giam,
                    ty_le_giam
                ) = (
                    self.extract_prices_from_card(
                        card
                    )
                )


                # Không có giá thì bỏ
                if gia_sau_giam <= 0:

                    continue


                # =================================================
                # BRAND
                # =================================================

                brand = guess_brand(
                    name
                )


                # =================================================
                # PRODUCT
                # =================================================

                product = RawProduct(

                    ma_san_pham=sku,

                    ten_san_pham=name,

                    don_gia_goc=int(
                        don_gia_goc
                    ),

                    gia_sau_giam=int(
                        gia_sau_giam
                    ),

                    ty_le_giam=int(
                        ty_le_giam
                    ),

                    danh_muc=category,

                    thuong_hieu=brand,
                )


                products.append(
                    product
                )


                seen_names.add(
                    name_key
                )

                seen_skus.add(
                    sku
                )


                self.log(
                    f"    + {len(products)}. "
                    f"{name} | "
                    f"{format_currency(gia_sau_giam)}"
                )


            except Exception as exc:

                self.log(
                    f"[BỎ QUA] "
                    f"Sản phẩm {i + 1}: "
                    f"{exc}"
                )

                continue


        self.log(
            f"Quét thành công "
            f"{len(products)} sản phẩm "
            f"thuộc '{category}'."
        )


        return products


# ============================================================
# 13. GIAO DIỆN
# ============================================================

class AppGUI(tk.Tk):


    def __init__(self):

        super().__init__()


        self.title(
            "Thế Giới Di Động Crawler - "
            "Xuất dữ liệu CSV chuẩn"
        )


        self.geometry(
            "1200x750"
        )


        self.minsize(
            1000,
            650
        )


        self.is_running = False

        self.stop_requested = False


        self.build_ui()


    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):


        config_frame = ttk.LabelFrame(

            self,

            text=" Cấu hình cào dữ liệu ",

            padding=10
        )


        config_frame.pack(

            fill="x",

            padx=10,

            pady=5
        )


        # ====================================================
        # DANH MỤC
        # ====================================================

        ttk.Label(

            config_frame,

            text="Danh mục:"
        ).grid(

            row=0,

            column=0,

            sticky="w",

            padx=5,

            pady=5
        )


        cat_subframe = ttk.Frame(
            config_frame
        )


        cat_subframe.grid(

            row=0,

            column=1,

            columnspan=3,

            sticky="w",

            padx=5,

            pady=5
        )


        self.cat_vars = {}


        for cat in CATEGORY_URLS.keys():

            var = tk.BooleanVar(
                value=True
            )


            self.cat_vars[cat] = var


            cb = ttk.Checkbutton(

                cat_subframe,

                text=cat,

                variable=var
            )


            cb.pack(

                side="left",

                padx=5
            )


        # ====================================================
        # MAX SP
        # ====================================================

        ttk.Label(

            config_frame,

            text="Số SP tối đa / danh mục:"
        ).grid(

            row=1,

            column=0,

            sticky="w",

            padx=5,

            pady=5
        )


        self.spin_max_sp = ttk.Spinbox(

            config_frame,

            from_=5,

            to=500,

            increment=10,

            width=10
        )


        self.spin_max_sp.set(
            50
        )


        self.spin_max_sp.grid(

            row=1,

            column=1,

            sticky="w",

            padx=5,

            pady=5
        )


        # ====================================================
        # LOAD MORE
        # ====================================================

        ttk.Label(

            config_frame,

            text="Số lần bấm 'Xem thêm':"
        ).grid(

            row=1,

            column=2,

            sticky="w",

            padx=5,

            pady=5
        )


        self.spin_load_more = ttk.Spinbox(

            config_frame,

            from_=0,

            to=20,

            increment=1,

            width=10
        )


        self.spin_load_more.set(
            5
        )


        self.spin_load_more.grid(

            row=1,

            column=3,

            sticky="w",

            padx=5,

            pady=5
        )


        # ====================================================
        # TỔNG DÒNG
        # ====================================================

        ttk.Label(

            config_frame,

            text="Tổng số dòng mong muốn:"
        ).grid(

            row=2,

            column=0,

            sticky="w",

            padx=5,

            pady=5
        )


        self.spin_total_rows = ttk.Spinbox(

            config_frame,

            from_=10,

            to=10000,

            increment=50,

            width=10
        )


        self.spin_total_rows.set(
            100
        )


        self.spin_total_rows.grid(

            row=2,

            column=1,

            sticky="w",

            padx=5,

            pady=5
        )


        # ====================================================
        # HEADLESS
        # ====================================================

        self.var_headless = tk.BooleanVar(
            value=False
        )


        cb_headless = ttk.Checkbutton(

            config_frame,

            text="Chạy ẩn trình duyệt",

            variable=self.var_headless
        )


        cb_headless.grid(

            row=2,

            column=2,

            columnspan=2,

            sticky="w",

            padx=5,

            pady=5
        )


        # ====================================================
        # FILE CSV
        # ====================================================

        ttk.Label(

            config_frame,

            text="File xuất CSV:"
        ).grid(

            row=3,

            column=0,

            sticky="w",

            padx=5,

            pady=5
        )


        self.ent_csv_path = ttk.Entry(

            config_frame,

            width=75
        )


        default_path = os.path.join(

            os.getcwd(),

            "thegioididong_products.csv"
        )


        self.ent_csv_path.insert(

            0,

            default_path
        )


        self.ent_csv_path.grid(

            row=3,

            column=1,

            columnspan=2,

            sticky="ew",

            padx=5,

            pady=5
        )


        btn_browse = ttk.Button(

            config_frame,

            text="Chọn...",

            command=self.browse_file
        )


        btn_browse.grid(

            row=3,

            column=3,

            sticky="w",

            padx=5,

            pady=5
        )


        # ====================================================
        # ACTION
        # ====================================================

        action_frame = ttk.Frame(
            self
        )


        action_frame.pack(

            fill="x",

            padx=10,

            pady=5
        )


        self.btn_start = ttk.Button(

            action_frame,

            text="▶ Bắt đầu cào dữ liệu",

            command=self.start_crawling
        )


        self.btn_start.pack(

            side="left",

            padx=5
        )


        self.btn_stop = ttk.Button(

            action_frame,

            text="⏹ Dừng",

            command=self.stop_crawling,

            state="disabled"
        )


        self.btn_stop.pack(

            side="left",

            padx=5
        )


        self.lbl_status = ttk.Label(

            action_frame,

            text="Sẵn sàng.",

            font=(

                "Segoe UI",

                9,

                "italic"
            )
        )


        self.lbl_status.pack(

            side="left",

            padx=15
        )


        # ====================================================
        # PROGRESS
        # ====================================================

        self.progress_bar = ttk.Progressbar(

            self,

            mode="determinate"
        )


        self.progress_bar.pack(

            fill="x",

            padx=10,

            pady=5
        )


        # ====================================================
        # PANED
        # ====================================================

        paned = ttk.PanedWindow(

            self,

            orient="vertical"
        )


        paned.pack(

            fill="both",

            expand=True,

            padx=10,

            pady=5
        )


        # ====================================================
        # TREE
        # ====================================================

        tree_frame = ttk.LabelFrame(

            paned,

            text=" Dữ liệu đơn hàng ",

            padding=5
        )


        paned.add(

            tree_frame,

            weight=3
        )


        self.tree = ttk.Treeview(

            tree_frame,

            columns=CSV_COLUMNS,

            show="headings",

            selectmode="browse"
        )


        for col in CSV_COLUMNS:

            self.tree.heading(

                col,

                text=col
            )


            width = 110


            if col in (

                "STT",

                "So_Luong",

                "Ty_Le_Giam_Gia",

                "Tan_suat_mua_hang"

            ):

                width = 75


            elif col == "Ten_San_Pham":

                width = 250


            elif col == "Dia_Chi_Cu_The":

                width = 300


            elif col == "Ma_San_Pham":

                width = 120


            self.tree.column(

                col,

                width=width,

                anchor=(

                    "center"

                    if col not in (

                        "Ten_San_Pham",

                        "Dia_Chi_Cu_The"

                    )

                    else "w"
                )
            )


        sc_y = ttk.Scrollbar(

            tree_frame,

            orient="vertical",

            command=self.tree.yview
        )


        sc_x = ttk.Scrollbar(

            tree_frame,

            orient="horizontal",

            command=self.tree.xview
        )


        self.tree.configure(

            yscrollcommand=sc_y.set,

            xscrollcommand=sc_x.set
        )


        sc_y.pack(

            side="right",

            fill="y"
        )


        sc_x.pack(

            side="bottom",

            fill="x"
        )


        self.tree.pack(

            fill="both",

            expand=True
        )


        # ====================================================
        # LOG
        # ====================================================

        log_frame = ttk.LabelFrame(

            paned,

            text=" Nhật ký xử lý ",

            padding=5
        )


        paned.add(

            log_frame,

            weight=1
        )


        self.txt_log = tk.Text(

            log_frame,

            height=6,

            bg="black",

            fg="lightgreen",

            font=(

                "Consolas",

                9
            )
        )


        sc_log = ttk.Scrollbar(

            log_frame,

            orient="vertical",

            command=self.txt_log.yview
        )


        self.txt_log.configure(

            yscrollcommand=sc_log.set
        )


        sc_log.pack(

            side="right",

            fill="y"
        )


        self.txt_log.pack(

            fill="both",

            expand=True
        )


    # ========================================================
    # CHỌN FILE
    # ========================================================

    def browse_file(self):

        filepath = filedialog.asksaveasfilename(

            defaultextension=".csv",

            filetypes=[

                (
                    "CSV files",

                    "*.csv"
                ),

                (
                    "All files",

                    "*.*"
                ),
            ],

            title="Chọn nơi lưu file CSV"
        )


        if filepath:

            self.ent_csv_path.delete(

                0,

                tk.END
            )


            self.ent_csv_path.insert(

                0,

                filepath
            )


    # ========================================================
    # LOG
    # ========================================================

    def log(
        self,
        message: str
    ):

        def append():

            ts = datetime.now().strftime(
                "%H:%M:%S"
            )


            self.txt_log.insert(

                "end",

                f"[{ts}] {message}\n"
            )


            self.txt_log.see(
                "end"
            )


        self.after(
            0,
            append
        )


    # ========================================================
    # STATUS
    # ========================================================

    def set_status(
        self,
        text: str
    ):

        self.after(

            0,

            lambda:
                self.lbl_status.config(
                    text=text
                )
        )


    # ========================================================
    # ADD ROW
    # ========================================================

    def add_row_to_table(
        self,
        row_dict: Dict
    ):

        def add():

            self.tree.insert(

                "",

                "end",

                values=[

                    row_dict[c]

                    for c in CSV_COLUMNS
                ]
            )


            children = (
                self.tree
                .get_children()
            )


            if children:

                self.tree.see(
                    children[-1]
                )


        self.after(
            0,
            add
        )


    # ========================================================
    # START
    # ========================================================

    def start_crawling(self):

        selected_cats = [

            cat

            for cat, var
            in self.cat_vars.items()

            if var.get()
        ]


        if not selected_cats:

            messagebox.showwarning(

                "Cảnh báo",

                "Vui lòng chọn ít nhất 1 danh mục!"
            )

            return


        self.is_running = True

        self.stop_requested = False


        self.btn_start.config(

            state="disabled"
        )


        self.btn_stop.config(

            state="normal"
        )


        self.tree.delete(

            *self.tree.get_children()
        )


        self.progress_bar["value"] = 0


        threading.Thread(

            target=self.run_task,

            args=(selected_cats,),

            daemon=True

        ).start()


    # ========================================================
    # STOP
    # ========================================================

    def stop_crawling(self):

        if self.is_running:

            self.stop_requested = True

            self.log(
                "Đang dừng quá trình..."
            )


    # ========================================================
    # RUN TASK
    # ========================================================

    def run_task(
        self,
        categories: List[str]
    ):

        try:

            max_sp = int(
                self.spin_max_sp.get()
            )


            load_more = int(
                self.spin_load_more.get()
            )


            target_rows = int(
                self.spin_total_rows.get()
            )


            is_headless = (
                self.var_headless.get()
            )


            csv_path = (
                self.ent_csv_path
                .get()
                .strip()
            )


            if not csv_path:

                csv_path = os.path.join(

                    os.getcwd(),

                    "thegioididong_products.csv"
                )


            self.log(
                "================================================"
            )


            self.log(
                "BẮT ĐẦU CÀO DỮ LIỆU THẾ GIỚI DI ĐỘNG"
            )


            self.log(
                "Giá được lấy trực tiếp từ từng product card."
            )


            self.log(
                "Giá gốc = giá bị gạch trên website."
            )


            self.log(
                "Giá bán = giá hiện tại trên website."
            )


            self.log(
                "================================================"
            )


            # =================================================
            # CRAWLER
            # =================================================

            crawler = TGDDCrawler(

                headless=is_headless,

                max_products_per_cat=max_sp,

                load_more_clicks=load_more,

                log_cb=self.log,

                stop_flag=lambda:
                    self.stop_requested
            )


            all_raw_products = []


            # =================================================
            # PLAYWRIGHT
            # =================================================

            with sync_playwright() as pw:

                browser = pw.chromium.launch(

                    headless=is_headless
                )


                context = (
                    browser.new_context(

                        viewport={

                            "width": 1366,

                            "height": 900
                        },

                        locale="vi-VN",

                        user_agent=(

                            "Mozilla/5.0 "
                            "(Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 "
                            "(KHTML, like Gecko) "
                            "Chrome/131.0.0.0 "
                            "Safari/537.36"
                        )
                    )
                )


                page = (
                    context.new_page()
                )


                for idx, cat in enumerate(
                    categories
                ):


                    if self.stop_requested:

                        break


                    self.set_status(

                        f"Đang cào: {cat}"
                    )


                    products = (

                        crawler
                        .crawl_category(

                            page,

                            cat
                        )
                    )


                    all_raw_products.extend(
                        products
                    )


                    progress = int(

                        (

                            (idx + 1)

                            / len(categories)

                        )

                        * 50
                    )


                    self.progress_bar[
                        "value"
                    ] = progress


                browser.close()


            # =================================================
            # KIỂM TRA
            # =================================================

            if not all_raw_products:

                self.log(
                    "[LỖI] Không cào được sản phẩm nào!"
                )

                self.after(

                    0,

                    lambda:
                        messagebox.showerror(

                            "Lỗi",

                            "Không lấy được sản phẩm "
                            "từ Thế Giới Di Động.\n\n"
                            "Bạn kiểm tra Internet hoặc "
                            "website có thay đổi giao diện."
                        )
                )

                return


            self.log(

                f"-> Thu thập thành công "
                f"{len(all_raw_products)} sản phẩm."
            )


            self.log(
                "-> Bắt đầu tạo dữ liệu đơn hàng..."
            )


            # =================================================
            # TẠO FINAL DATA
            # =================================================

            final_rows = []


            stt = 1


            product_position = 0


            while (

                len(final_rows)
                < target_rows

                and not self.stop_requested
            ):


                prod = (

                    all_raw_products[

                        product_position
                        % len(all_raw_products)
                    ]
                )


                # =============================================
                # SỐ LƯỢNG
                # =============================================

                so_luong = (

                    generate_quantity(

                        stt,

                        prod
                    )
                )


                # =============================================
                # ĐỊA CHỈ
                # =============================================

                (
                    tinh_thanh,

                    phuong_xa,

                    dia_chi_cu_the

                ) = get_tgdd_address(
                    stt
                )


                # =============================================
                # GIÁ GỐC
                # =============================================

                val_don_gia = int(

                    prod.don_gia_goc
                )


                # =============================================
                # % GIẢM
                # =============================================

                val_ty_le_giam = int(

                    prod.ty_le_giam
                )


                # =============================================
                # GIÁ BÁN THỰC TẾ
                # =============================================

                val_tien_giam = int(

                    prod.gia_sau_giam
                )


                # =============================================
                # TỔNG HÀNG
                # =============================================

                val_tong_hang = (

                    val_tien_giam
                    * so_luong
                )


                # =============================================
                # TỔNG THANH TOÁN
                #
                # TỔNG HÀNG + 10%
                # =============================================

                val_tong_thanh_toan = round(

                    val_tong_hang
                    * 1.1
                )


                # =============================================
                # TẦN SUẤT
                # =============================================

                tan_suat = (

                    generate_purchase_frequency(

                        stt,

                        prod
                    )
                )


                # =============================================
                # ROW
                # =============================================

                row = {

                    "STT":
                        stt,

                    "Tinh_Thanh":
                        tinh_thanh,

                    "Phuong_Xa":
                        phuong_xa,

                    "Dia_Chi_Cu_The":
                        dia_chi_cu_the,

                    "Ma_San_Pham":
                        prod.ma_san_pham,

                    "Ten_San_Pham":
                        prod.ten_san_pham,

                    "Nhom_Hang":
                        "Đồ điện tử",

                    "So_Luong":
                        so_luong,

                    "Don_Gia":
                        format_currency(
                            val_don_gia
                        ),

                    "Ty_Le_Giam_Gia":
                        val_ty_le_giam,

                    "Tien_Giam":
                        format_currency(
                            val_tien_giam
                        ),

                    "Tong_Hang":
                        format_currency(
                            val_tong_hang
                        ),

                    "Tong_Thanh_Toan":
                        format_currency(
                            val_tong_thanh_toan
                        ),

                    "Tan_suat_mua_hang":
                        tan_suat,

                    "Thuong_Hieu":
                        prod.thuong_hieu,

                    "Danh_Muc":
                        prod.danh_muc,
                }


                final_rows.append(
                    row
                )


                self.add_row_to_table(
                    row
                )


                stt += 1

                product_position += 1


                # =============================================
                # PROGRESS
                # =============================================

                self.progress_bar[
                    "value"
                ] = (

                    50

                    + int(

                        (

                            len(final_rows)
                            / target_rows

                        )

                        * 50
                    )
                )


            # =================================================
            # XUẤT CSV
            # =================================================

            if final_rows:

                save_path = csv_path


                # =============================================
                # KIỂM TRA FILE ĐANG MỞ
                # =============================================

                try:

                    if os.path.exists(
                        save_path
                    ):

                        with open(

                            save_path,

                            "a",

                            encoding="utf-8"

                        ):

                            pass


                except PermissionError:

                    timestamp = (

                        datetime.now()
                        .strftime(
                            "%H%M%S"
                        )
                    )


                    base, ext = (

                        os.path.splitext(
                            save_path
                        )
                    )


                    save_path = (

                        f"{base}_new_"
                        f"{timestamp}"
                        f"{ext}"
                    )


                    self.log(
                        "[CẢNH BÁO] "
                        "File cũ đang mở."
                    )


                    self.log(

                        "Đã đổi tên file xuất thành: "

                        f"{os.path.basename(save_path)}"
                    )


                # =============================================
                # TẠO THƯ MỤC
                # =============================================

                folder = os.path.dirname(

                    os.path.abspath(
                        save_path
                    )
                )


                os.makedirs(

                    folder,

                    exist_ok=True
                )


                # =============================================
                # GHI CSV
                # =============================================

                with open(

                    save_path,

                    mode="w",

                    newline="",

                    encoding="utf-8-sig"

                ) as f:


                    writer = csv.DictWriter(

                        f,

                        fieldnames=CSV_COLUMNS
                    )


                    writer.writeheader()


                    writer.writerows(
                        final_rows
                    )


                # =============================================
                # HOÀN TẤT
                # =============================================

                self.log(
                    "================================================"
                )


                self.log(

                    f"HOÀN TẤT! "
                    f"Đã xuất "
                    f"{len(final_rows)} dòng."
                )


                self.log(

                    f"File: {save_path}"
                )


                self.log(
                    "================================================"
                )


                self.set_status(

                    f"Hoàn tất. "
                    f"Đã xuất "
                    f"{len(final_rows)} dòng."
                )


                self.progress_bar[
                    "value"
                ] = 100


                self.after(

                    0,

                    lambda:
                        messagebox.showinfo(

                            "Thành công",

                            "Đã xuất thành công "
                            f"{len(final_rows)} dòng "
                            "ra file:\n"
                            f"{save_path}"
                        )
                )


        except Exception as exc:

            self.log(
                f"[LỖI XỬ LÝ] {exc}"
            )


            self.after(

                0,

                lambda:
                    messagebox.showerror(

                        "Lỗi",

                        "Quá trình xử lý gặp lỗi:\n"
                        f"{exc}"
                    )
            )


        finally:

            self.is_running = False


            self.after(

                0,

                lambda:
                    self.btn_start.config(

                        state="normal"
                    )
            )


            self.after(

                0,

                lambda:
                    self.btn_stop.config(

                        state="disabled"
                    )
            )


# ============================================================
# 14. CHẠY CHƯƠNG TRÌNH
# ============================================================

if __name__ == "__main__":

    app = AppGUI()

    app.mainloop()