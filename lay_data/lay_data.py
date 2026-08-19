import csv
import os
import random
import re
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from playwright.sync_api import sync_playwright

ALL_SITE_URLS = {
    "Phong Vũ": {
        "Điện thoại": "https://phongvu.vn/c/phone-dien-thoai",
        "Laptop": "https://phongvu.vn/c/laptop",
        "Máy tính bảng": "https://phongvu.vn/c/may-tinh-bang",
        "Phụ kiện": "https://phongvu.vn/c/phu-kien-chung",
        "Tivi": "https://phongvu.vn/c/tivi",
    },
    "FPT Shop": {
        "Điện thoại": "https://fptshop.com.vn/dien-thoai",
        "Laptop": "https://fptshop.com.vn/may-tinh-xach-tay",
        "Máy tính bảng": "https://fptshop.com.vn/may-tinh-bang",
        "Phụ kiện": "https://fptshop.com.vn/phu-kien",
        "Tivi": "https://fptshop.com.vn/tivi",
    },
    "Thế Giới Di Động": {
        "Điện thoại": "https://www.thegioididong.com/dtdd",
        "Laptop": "https://www.thegioididong.com/laptop",
        "Máy tính bảng": "https://www.thegioididong.com/may-tinh-bang",
        "Phụ kiện": "https://www.thegioididong.com/phu-kien",
        "Tivi": "https://fptshop.com.vn/tivi",
    },
    "CellphoneS": {
        "Điện thoại": "https://cellphones.com.vn/",
        "Laptop": "https://cellphones.com.vn/laptop.html",
        "Máy tính bảng": "https://cellphones.com.vn/catalogsearch/result?q=m%C3%A1y%20t%C3%ADnh%20b%E1%BA%A3ng",
        "Phụ kiện": "https://cellphones.com.vn/phu-kien.html",
        "Tivi": "https://cellphones.com.vn/dien-may.html",
    }
}

KNOWN_BRANDS = [
    "iPhone", "Apple", "MacBook", "iPad", "Samsung", "Xiaomi", "Redmi", "Poco", "POCO",
    "Oppo", "OPPO", "Vivo", "vivo", "Realme", "realme", "Nokia", "Asus", "ASUS", "Acer",
    "Dell", "HP", "Lenovo", "MSI", "LG", "Huawei", "Honor", "HONOR", "Masstel", "Itel",
    "Anker", "JBL", "Sony", "Canon", "Baseus", "Nubia", "TECNO", "Tecno", "TCL",
    "Kingston", "Logitech", "Razer", "Corsair", "SanDisk", "Lexar", "Ugreen", "Belkin",
    "TP-Link", "Havit", "Boya", "Sennheiser", "Epson", "Brother", "Marshall", "Garmin",
    "GoPro", "Coocaa", "Sharp", "Casper", "Toshiba", "Panasonic"
]

CSV_COLUMNS = [
    "STT", "Nguon_Trang", "Tinh_Thanh", "Phuong_Xa", "Dia_Chi_Cu_The", "Ma_San_Pham", "Ten_San_Pham", 
    "Nhom_Hang", "So_Luong", "Don_Gia", "Ty_Le_Giam_Gia", "Tien_Giam", "Tong_Hang", 
    "Tong_Thanh_Toan", "Tan_suat_mua_hang", "Thuong_Hieu", "Danh_Muc"
]

ALL_ADDRESSES = [
    ("TP. Hồ Chí Minh", "P. Vĩnh Hội", "261–263 Khánh Hội (FPT Shop)"),
    ("TP. Hồ Chí Minh", "P. Hạnh Thông", "418 Nguyễn Văn Nghi (FPT Shop)"),
    ("TP. Hồ Chí Minh", "P. Hòa Bình", "176 Ông Ích Khiêm (FPT Shop)"),
    ("TP. Hồ Chí Minh", "P. Bàn Cờ", "149 Cách Mạng Tháng 8 (FPT Shop)"),
    ("TP. Hồ Chí Minh", "P. Tân Thuận", "489–491 Huỳnh Tấn Phát (FPT Shop)"),
    ("TP. Hồ Chí Minh", "P. Hiệp Bình", "30 Hiệp Bình, Khu phố 8 (FPT Shop)"),
    ("TP. Hồ Chí Minh", "P. Minh Phụng", "1215 Đường Ba Tháng Hai (FPT Shop)"),
    ("TP. Hồ Chí Minh", "P. Phú Thọ", "07 Lê Đại Hành (FPT Shop)"),
    ("TP. Hồ Chí Minh", "X. Tân An Hội", "705 Phan Bội Châu (Quốc lộ 22) (FPT Shop)"),
    ("TP. Hồ Chí Minh", "P. Bến Thành", "121 Lê Lợi (FPT Shop)"),
    ("TP. Hồ Chí Minh", "P. Chợ Quán", "608–610 Trần Hưng Đạo (FPT Shop)"),
    ("TP. Hồ Chí Minh", "P. Tân Bình", "306A Trường Chinh (FPT Shop)"),
    ("TP. Hồ Chí Minh", "P. Hòa Hưng", "305 Tô Hiến Thành (FPT Shop)"),
    ("TP. Hồ Chí Minh", "P. Bình Trưng", "192A Nguyễn Thị Định (FPT Shop)"),
    ("TP. Hồ Chí Minh", "P. Tân Hưng", "376A Nguyễn Thị Thập (FPT Shop)"),
    ("TP. Hồ Chí Minh", "P. Thạnh Mỹ Tây", "538 Xô Viết Nghệ Tĩnh (FPT Shop)"),
    ("TP. Hồ Chí Minh", "P. Bình Tân", "229 Nguyễn Thị Tú (FPT Shop)"),
    ("TP. Hồ Chí Minh", "P. Tăng Nhơn Phú", "157 Lê Văn Việt (FPT Shop)"),
    ("TP. Hồ Chí Minh", "P. Bình Trưng", "358 Nguyễn Duy Trinh (FPT Shop)"),
    ("TP. Hồ Chí Minh", "P. Vườn Lài", "256 Nguyễn Tri Phương (FPT Shop)"),
    ("Đồng Nai", "P. Trấn Biên", "282 Phạm Văn Thuận (Đối diện Vincom Biên Hòa) (FPT Shop)"),
    ("Đồng Nai", "P. Long Hưng", "24/11 KP Long Điềm (Ngã ba Long Bình Tân) (FPT Shop)"),
    ("Đồng Nai", "P. Bình Long", "109 Nguyễn Huệ (Vòng xoay Bình Long) (FPT Shop)"),
    ("Đồng Nai", "X. Gia Kiệm", "04/N Phúc Nhạc 2 (Đối diện chợ Phúc Nhạc) (FPT Shop)"),
    ("Đồng Nai", "P. Tam Hiệp", "6/1A Khu phố 1 (Cổng chào Biên Hòa) (FPT Shop)"),
    ("Đồng Nai", "P. Tam Hiệp", "660 Đồng Khởi (Ngã tư Amata), Khu phố 4 (FPT Shop)"),
    ("Đồng Nai", "X. Bình Minh", "07 Tây Lạc (Ngã ba Trị An) (FPT Shop)"),
    ("Đồng Nai", "P. Long Hưng", "353 Bùi Văn Hòa (FPT Shop)"),
    ("Đồng Nai", "P. Trảng Dài", "02 Bùi Trọng Nghĩa, Tổ 31, Khu phố 3A (FPT Shop)"),
    ("Đồng Nai", "Long Thành", "491 Lê Duẩn, Tổ 32 (FPT Shop)"),
    ("Đồng Nai", "P. Long Khánh", "1 Khổng Tử, Khu phố 1 (FPT Shop)"),
    ("Đồng Nai", "P. Long Khánh", "7 Hùng Vương (Ngã ba Khổng Tử) (FPT Shop)"),
    ("Đồng Nai", "X. Phú Lâm", "2248 Ấp Phương Mai 1 (FPT Shop)"),
    ("Đồng Nai", "X. Xuân Tâm", "2150 Quốc lộ 1A, Ấp 4 (FPT Shop)"),
    ("Đồng Nai", "X. Xuân Lộc", "246 Hùng Vương (FPT Shop)"),
    ("Đồng Nai", "P. Trấn Biên", "26/6 Cách Mạng Tháng 8, KP3 (FPT Shop)"),
    ("Đồng Nai", "X. An Phước", "Khu 465 (Ngã ba Dân Chủ), Khu 4, Ấp 8 (FPT Shop)"),
    ("Đồng Nai", "X. Phước Thái", "1912, Tổ 1, Ấp 1C (FPT Shop)"),
    ("Đồng Nai", "X. Hiệp Phước", "394–396–398 Hùng Vương, Ấp 3 (FPT Shop)"),
    ("Đồng Nai", "X. Định Quán", "62A Tổ 2, Khu phố 11 (FPT Shop)"),
    ("Tây Ninh", "P. Long An", "02 Ngô Quyền (Gần cầu Đúc) (FPT Shop)"),
    ("Tây Ninh", "X. Bến Lức", "21 Nguyễn Hữu Thọ (Cạnh phòng khám Phú Khang) (FPT Shop)"),
    ("Tây Ninh", "P. An Tịnh", "3427 Quốc Lộ 22, Ấp Suối Sâu (Đối diện chợ Suối Sâu) (FPT Shop)"),
    ("Tây Ninh", "X. Cần Giuộc", "02 Nguyễn Thái Bình, Tổ 8, Khu phố 4 (Ngã 5 Mũi Tàu) (FPT Shop)"),
    ("Tây Ninh", "P. Trảng Bàng", "200–202 Quốc Lộ 22 (Đối diện chợ Trảng Bàng) (FPT Shop)"),
    ("Tây Ninh", "P. Long Hoa", "127–129–131 Phạm Văn Đồng, Khu phố 2 (FPT Shop)"),
    ("Tây Ninh", "X. Tân Châu", "116–118 Khu phố 1 (Đối diện chợ Tân Châu) (FPT Shop)"),
    ("Tây Ninh", "P. Gia Lộc", "247 Đường 782, Ấp Phước Đức A (Ngã tư Nông Trường) (FPT Shop)"),
    ("Tây Ninh", "P. Gò Dầu", "2/227 Khu phố Thanh Hà (FPT Shop)"),
    ("Tây Ninh", "P. Tân Ninh", "1089–1091 Cách Mạng Tháng 8, Khu phố Hiệp Bình (FPT Shop)"),
    ("Tây Ninh", "P. Tân Ninh", "619 Cách Mạng Tháng 8, Khu phố 2 (FPT Shop)"),
    ("Tây Ninh", "P. Tân Ninh", "867 Cách Mạng Tháng 8 (Ngã ba Nguyễn Trãi) (FPT Shop)"),
    ("Tây Ninh", "P. Long An", "68 Hùng Vương (Ngã tư Bến xe) (FPT Shop)"),
    ("Tây Ninh", "X. Mỹ Yên", "02C ĐT835, Ấp 5 (FPT Shop)"),
    ("Tây Ninh", "X. Cần Đước", "01 Trần Hưng Đạo (FPT Shop)"),
    ("Đồng Tháp", "P. Cao Lãnh", "162–164 Nguyễn Huệ (FPT Shop)"),
    ("Đồng Tháp", "P. Cao Lãnh", "50–52 Phạm Hữu Lầu (FPT Shop)"),
    ("Đồng Tháp", "P. Cao Lãnh", "218 Đường 30/4 (FPT Shop)"),
    ("Đồng Tháp", "P. Hồng Ngự", "72–74 Hùng Vương (FPT Shop)"),
    ("Đồng Tháp", "P. Sa Đéc", "205 Nguyễn Sinh Sắc (FPT Shop)"),
    ("Đồng Tháp", "P. Sa Đéc", "1B Đường ĐT852 (FPT Shop)"),
    ("Đồng Tháp", "X. Mỹ Hiệp", "Tổ 24, Ấp 2 (FPT Shop)"),
    ("Đồng Tháp", "X. Tháp Mười", "133/D Hùng Vương (FPT Shop)"),
    ("Đồng Tháp", "P. Cai Lậy", "365–366 Quốc lộ 1A (FPT Shop)"),
    ("Đồng Tháp", "P. Mỹ Phước Tây", "Ấp Kinh 12 (FPT Shop)"),
    ("Đồng Tháp", "X. Châu Thành", "4/4 Ấp Rẫy (FPT Shop)"),
    ("Đồng Tháp", "P. Thới Sơn", "152 Lý Thường Kiệt (FPT Shop)"),
    ("Đồng Tháp", "P. Thới Sơn", "12/4B Lê Thị Hồng Gấm (FPT Shop)"),
    ("Vĩnh Long", "P. Long Châu", "139–139C Lê Thái Tổ (FPT Shop)"),
    ("Vĩnh Long", "P. Tân Hạnh", "14A–14B–14C Đinh Tiên Hoàng (FPT Shop)"),
    ("Vĩnh Long", "X. Phú Quới", "Thửa đất 218, Tờ bản đồ 34, Quốc lộ 1A, Tổ 9, Ấp Thạnh Hưng (FPT Shop)"),
    ("Vĩnh Long", "P. Trà Vinh", "27A Điện Biên Phủ, Khu phố 4 (FPT Shop)"),
    ("Vĩnh Long", "P. Nguyệt Hóa", "289 Nguyễn Đáng, Khóm 6 (FPT Shop)"),
    ("Vĩnh Long", "P. Phú Khương", "77C Đại lộ Đồng Khởi, Khu phố 6 (FPT Shop)"),
    ("Vĩnh Long", "P. Bình Minh", "Tổ 3, Khóm 5 (FPT Shop)"),
    ("Vĩnh Long", "X. Giao Long", "376 ĐT883, Ấp 4 (FPT Shop)"),
    ("Cần Thơ", "P. Sóc Trăng", "89–91 Hùng Vương (FPT Shop)"),
    ("Cần Thơ", "P. Ninh Kiều", "83 Trần Hưng Đạo (FPT Shop)"),
    ("Cần Thơ", "P. Vị Tân", "2 Ngô Quốc Trị (FPT Shop)"),
    ("Cần Thơ", "P. Ninh Kiều", "52–54–56 Đường 30/4 (FPT Shop)"),
    ("Cần Thơ", "P. Thốt Nốt", "314 Quốc lộ 91 (FPT Shop)"),
    ("Cần Thơ", "P. Tân An", "198B Đường 3/2 (FPT Shop)"),
    ("Cần Thơ", "P. Tân An", "289 Nguyễn Văn Cừ (FPT Shop)"),
    ("Cần Thơ", "P. Cái Răng", "166 Phạm Hùng (FPT Shop)"),
    ("Cần Thơ", "X. Phong Điền", "146 Phan Văn Trị, Ấp Thị Tứ (FPT Shop)"),
    ("Cần Thơ", "P. Ô Môn", "1255 Tôn Đức Thắng, Khu vực 5 (FPT Shop)"),
    ("Cần Thơ", "P. Sóc Trăng", "Cửa hàng FPT Shop (FPT Shop)"),
    ("An Giang", "P. Long Xuyên", "311/2B Trần Hưng Đạo, Khóm 7 (FPT Shop)"),
    ("An Giang", "P. Long Xuyên", "361 Trần Hưng Đạo (FPT Shop)"),
    ("An Giang", "P. Bình Đức", "244 Trần Hưng Đạo (FPT Shop)"),
    ("An Giang", "P. Châu Đốc", "243–245 Lê Lợi (FPT Shop)"),
    ("An Giang", "P. Châu Đốc", "30–32 Nguyễn Văn Thoại (FPT Shop)"),
    ("An Giang", "P. Tân Châu", "188 Tôn Đức Thắng (FPT Shop)"),
    ("An Giang", "X. An Phú", "17 Nguyễn Hữu Cảnh (FPT Shop)"),
    ("An Giang", "X. Cần Đăng", "Thửa đất 218, Tờ bản đồ 34, Ấp Cần Thạnh (FPT Shop)"),
    ("An Giang", "P. Thới Sơn", "318 Khóm Thới Hòa (FPT Shop)"),
    ("An Giang", "X. Phú Tân", "455 Đường Tỉnh lộ 954, Ấp Thượng 2, Tổ 8 (FPT Shop)"),
    ("An Giang", "X. Thoại Sơn", "305 Nguyễn Huệ (FPT Shop)"),
    ("An Giang", "P. Rạch Giá", "159 Trần Phú (FPT Shop)"),
    ("An Giang", "P. Rạch Giá", "02 Nguyễn Chí Thanh (FPT Shop)"),
    ("An Giang", "P. Rạch Giá", "136 Nguyễn Trung Trực (FPT Shop)"),
    ("An Giang", "P. Hà Tiên", "156 Mạc Thiên Tích (FPT Shop)"),
    ("An Giang", "P. Kiên Lương", "12 Quốc lộ 80 (FPT Shop)"),
    ("An Giang", "X. Tri Tôn", "92 Trần Hưng Đạo, Khóm 6 (FPT Shop)"),
    ("An Giang", "X. Giồng Riềng", "605 Hùng Vương (FPT Shop)"),
    ("An Giang", "Đặc khu Phú Quốc", "1 Hùng Vương (FPT Shop)"),
    ("An Giang", "X. Châu Phú", "134 Quốc lộ 91 (FPT Shop)"),
    ("Cà Mau", "P. Bạc Liêu", "66 Hòa Bình (Vòng xoay Ngã Tư Quốc Tế) (FPT Shop)"),
    ("Cà Mau", "P. Giá Rai", "148 Quốc Lộ 1A (148 Hộ Phòng) (FPT Shop)"),
    ("Cà Mau", "P. Bạc Liêu", "89 Hai Bà Trưng (FPT Shop)"),
    ("Cà Mau", "P. Bạc Liêu", "35 Trần Huỳnh, Khóm 2 (FPT Shop)"),
    ("Cà Mau", "P. Lý Văn Lâm", "149 Nguyễn Tất Thành (FPT Shop)"),
    ("Cà Mau", "P. Tân Thành", "11 Trần Hưng Đạo, Khu phố 6 (FPT Shop)"),
    ("Cà Mau", "X. Thới Bình", "23 Khóm 8 (FPT Shop)"),
    ("Cà Mau", "X. Trần Văn Thời", "Đường 30/4, Khóm 7 (FPT Shop)"),
    ("Cà Mau", "X. Sông Đốc", "Khóm 7 (FPT Shop)"),
    ("Cà Mau", "X. Đầm Dơi", "65 Dương Thị Cẩm Vân, Khóm 4 (FPT Shop)"),
    ("Cà Mau", "X. Phước Long", "Ấp Long Thành (FPT Shop)"),
    ("TP. Hồ Chí Minh", "P. Tân Định", "218–220 Trần Quang Khải (CellphoneS)"),
    ("TP. Hồ Chí Minh", "P. Tân Định", "55B Trần Quang Khải (CellphoneS)"),
    ("TP. Hồ Chí Minh", "P. Phan Đăng Lưu", "114 Phan Đăng Lưu (CellphoneS)"),
    ("TP. Hồ Chí Minh", "P. Phạm Ngũ Lão", "157–159 Nguyễn Thị Minh Khai (CellphoneS)"),
    ("TP. Hồ Chí Minh", "P. Phạm Ngũ Lão", "134 Nguyễn Thái Học (CellphoneS)"),
    ("TP. Hồ Chí Minh", "P. Bình Thạnh", "377–379 Điện Biên Phủ (CellphoneS)"),
    ("TP. Hồ Chí Minh", "P. Hòa Hưng", "296 Đường 3 Tháng 2 (CellphoneS)"),
    ("TP. Hồ Chí Minh", "P. Hạnh Thông", "567 Lê Quang Định (CellphoneS)"),
    ("TP. Hồ Chí Minh", "P. Tân Bình", "190B Hoàng Văn Thụ (CellphoneS)"),
    ("TP. Hồ Chí Minh", "P. Bình Thạnh", "536 Xô Viết Nghệ Tĩnh (CellphoneS)"),
    ("TP. Hồ Chí Minh", "P. Diên Hồng", "347 Nguyễn Tri Phương (CellphoneS)"),
    ("TP. Hồ Chí Minh", "P. Chợ Quán", "785 Trần Hưng Đạo (CellphoneS)"),
    ("TP. Hồ Chí Minh", "P. Vĩnh Hội", "177 Khánh Hội (CellphoneS)"),
    ("TP. Hồ Chí Minh", "P. Gò Vấp", "59 Quang Trung (CellphoneS)"),
    ("TP. Hồ Chí Minh", "P. Phú Thạnh", "161 Nguyễn Sơn (CellphoneS)"),
    ("TP. Hồ Chí Minh", "P. Bình An", "139 Trần Não (CellphoneS)"),
    ("TP. Hồ Chí Minh", "P. Tân Bình", "672–674 Âu Cơ (CellphoneS)"),
    ("TP. Hồ Chí Minh", "P. Tân Bình", "359 Cộng Hòa (CellphoneS)"),
    ("TP. Hồ Chí Minh", "P. Gò Vấp", "525 Quang Trung (CellphoneS)"),
    ("TP. Hồ Chí Minh", "P. Tân Quy", "248 Nguyễn Thị Thập (CellphoneS)"),
    ("Đồng Nai", "P. Long Khánh", "175 Hùng Vương (CellphoneS)"),
    ("Đồng Nai", "P. Tam Hiệp", "57 Phạm Văn Thuận (CellphoneS)"),
    ("Đồng Nai", "P. Long Bình", "7–9–11 Bùi Văn Hòa (CellphoneS)"),
    ("Đồng Nai", "P. Tam Hiệp", "F1 Đường Đồng Khởi, Khu phố 14 (CellphoneS)"),
    ("Đồng Nai", "P. Nhơn Trạch", "237 Lý Thái Tổ (CellphoneS)"),
    ("Đồng Nai", "X. Long Thành", "307 Lê Duẩn (CellphoneS)"),
    ("Đồng Nai", "X. Trảng Bom", "58 Đường 30/4 (CellphoneS)"),
    ("Đồng Nai", "P. Tân Biên", "44/2 Nguyễn Ái Quốc (CellphoneS)"),
    ("Tây Ninh", "P. Trảng Bàng", "214 Quốc Lộ 22 (CellphoneS)"),
    ("Tây Ninh", "P. Tân Ninh", "855 Cách Mạng Tháng 8 (CellphoneS)"),
    ("Tây Ninh", "P. Long An", "122 Hùng Vương (CellphoneS)"),
    ("Tây Ninh", "X. Bến Lức", "82–84 Nguyễn Hữu Thọ (CellphoneS)"),
    ("Đồng Tháp", "P. Cao Lãnh", "81 Nguyễn Huệ (CellphoneS)"),
    ("Đồng Tháp", "P. Sa Đéc", "103–105 Hùng Vương (CellphoneS)"),
    ("Vĩnh Long", "P. Phước Hậu", "56D Phạm Thái Bường, Khóm 1 (CellphoneS)"),
    ("Vĩnh Long", "P. Long Châu", "Số 4–6 đường Lê Thái Tổ, Khóm 2 (CellphoneS)"),
    ("Vĩnh Long", "P. Phú Khương", "300A Đoàn Hoàng Minh (CellphoneS)"),
    ("Cần Thơ", "P. Ninh Kiều", "131A–133 Cách Mạng Tháng 8 (CellphoneS)"),
    ("Cần Thơ", "P. Tân An", "141 Nguyễn Văn Cừ (CellphoneS)"),
    ("Cần Thơ", "P. Tân An", "272 Đường 30 Tháng 4 (CellphoneS)"),
    ("Cần Thơ", "P. Vị Thanh", "78 Nguyễn Công Trứ (CellphoneS)"),
    ("An Giang", "P. Mỹ Long", "1393 Trần Hưng Đạo (CellphoneS)"),
    ("An Giang", "P. Bình Đức", "912–915 Trần Hưng Đạo (CellphoneS)"),
    ("An Giang", "P. Châu Đốc", "272 Lê Lợi (CellphoneS)"),
    ("An Giang", "P. Rạch Giá", "405 Nguyễn Trung Trực (CellphoneS)"),
    ("An Giang", "P. Rạch Giá", "117–119 Nguyễn Trung Trực (CellphoneS)"),
    ("An Giang", "Đặc khu Phú Quốc", "35 Hùng Vương (CellphoneS)"),
    ("Cà Mau", "P. Bạc Liêu", "66 Hòa Bình (Vòng xoay Ngã Tư Quốc Tế) (CellphoneS)"),
    ("Cà Mau", "P. Giá Rai", "148 Quốc Lộ 1A (148 Hộ Phòng) (CellphoneS)"),
    ("Cà Mau", "P. Bạc Liêu", "89 Hai Bà Trưng (CellphoneS)"),
    ("Cà Mau", "P. Bạc Liêu", "35 Trần Huỳnh, Khóm 2 (CellphoneS)"),
    ("Cà Mau", "P. Lý Văn Lâm", "149 Nguyễn Tất Thành (CellphoneS)"),
    ("Cà Mau", "P. Tân Thành", "11 Trần Hưng Đạo, Khu phố 6 (CellphoneS)"),
    ("Cà Mau", "X. Thới Bình", "23 Khóm 8 (CellphoneS)"),
    ("Cà Mau", "X. Trần Văn Thời", "Đường 30/4, Khóm 7 (CellphoneS)"),
    ("Cà Mau", "X. Sông Đốc", "Khóm 7 (CellphoneS)"),
    ("Cà Mau", "X. Đầm Dơi", "65 Dương Thị Cẩm Vân, Khóm 4 (CellphoneS)"),
    ("Cà Mau", "X. Phước Long", "Ấp Long Thành (CellphoneS)"),
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
    ("Tây Ninh", "P. Tân Ninh", "583 Cách Mạng Tháng 8 (Thế Giới Di Động)"),
    ("Tây Ninh", "P. Tân Ninh", "1197 Cách Mạng Tháng 8 (Thế Giới Di Động)"),
    ("Tây Ninh", "P. Long Hoa", "14 Phạm Hùng (Thế Giới Di Động)"),
    ("Tây Ninh", "P. Tân Ninh", "229 Cách Mạng Tháng 8 (Thế Giới Di Động)"),
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
    ("TP. Hồ Chí Minh", "P. Xuân Hòa", "262A–262B–264–264A–264B Nguyễn Thị Minh Khai (Phong Vũ)"),
    ("TP. Hồ Chí Minh", "P. Nhiêu Lộc", "132E Cách Mạng Tháng Tám (Phong Vũ)"),
    ("TP. Hồ Chí Minh", "P. Gia Định", "26B Phan Đăng Lưu (Phong Vũ)"),
    ("TP. Hồ Chí Minh", "P. Bảy Hiền", "02 Hoàng Hoa Thám (Phong Vũ)"),
    ("TP. Hồ Chí Minh", "P. Bình Phú", "1081A–1081C Hậu Giang (Phong Vũ)"),
    ("TP. Hồ Chí Minh", "P. Tăng Nhơn Phú", "164 Lê Văn Việt (Phong Vũ)"),
    ("TP. Hồ Chí Minh", "P. Thủ Đức", "269–271 Võ Văn Ngân (Phong Vũ)"),
    ("TP. Hồ Chí Minh", "P. Tân Mỹ", "9–11 Nguyễn Thị Thập (Phong Vũ)"),
    ("TP. Hồ Chí Minh", "P. Hạnh Thông", "2A Nguyễn Oanh (Phong Vũ)"),
    ("TP. Hồ Chí Minh", "P. Trung Mỹ Tây", "38M Nguyễn Ảnh Thủ (Phong Vũ)"),
    ("TP. Hồ Chí Minh", "P. Khánh Hội", "162–164 Khánh Hội (Phong Vũ)"),
    ("Đồng Nai", "P. Long Bình", "37 Bùi Văn Hòa, Khu phố 4 (Phong Vũ)"),
    ("Tây Ninh", "P. Tân Ninh", "969 Cách Mạng Tháng 8 (Phong Vũ)"),
    ("Tây Ninh", "P. Long An", "Số 2 Châu Văn Giác (Phong Vũ)"),
    ("Đồng Tháp", "P. Cao Lãnh", "37–39 Lý Thường Kiệt (Phong Vũ)"),
    ("Đồng Tháp", "P. Trung An", "225 Ấp Bắc, Khu phố 3 (Phong Vũ)"),
    ("Vĩnh Long", "P. Phú Tân", "207A6 Đại Lộ Đồng Khởi (Phong Vũ)"),
    ("Cần Thơ", "P. Tân An", "178 Đường 3 Tháng 2 (Phong Vũ)"),
]

@dataclass
class RawProduct:
    ma_san_pham: str
    ten_san_pham: str
    don_gia_goc: int
    gia_sau_giam: int
    ty_le_giam: int
    danh_muc: str
    thuong_hieu: str
    nguon: str

def guess_brand(name: str) -> str:
    n_lower = name.lower()
    for b in sorted(KNOWN_BRANDS, key=len, reverse=True):
        if b.lower() in n_lower:
            if b.lower() in ("iphone", "macbook", "ipad"): return "Apple"
            if b.lower() in ("redmi", "poco"): return "Xiaomi"
            return b
    return "Khác"

def parse_price(txt: str) -> int:
    if not txt: return 0
    digits = re.sub(r"[^\d]", "", str(txt))
    return int(digits) if digits else 0

def format_currency(amt: int) -> str:
    return f"{int(amt):,}".replace(",", ".")

def get_address(idx: int):
    return ALL_ADDRESSES[(idx - 1) % len(ALL_ADDRESSES)]

def crawl_site(page, site_name, category, url, max_sp, load_more, log_fn, stop_fn):
    log_fn(f"[{site_name}] Đang cào danh mục: {category}")
    products = []
    try:
        page.goto(url, timeout=60000, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        
        for _ in range(6):
            if stop_fn(): break
            page.evaluate("window.scrollBy(0, 800);")
            page.wait_for_timeout(600)

        for i in range(load_more):
            if stop_fn(): break
            try:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight - 500);")
                page.wait_for_timeout(1000)
                btn = page.locator("button:has-text('Xem thêm'), a:has-text('Xem thêm')").first
                if btn.is_visible():
                    btn.click(timeout=2000)
                    page.wait_for_timeout(1500)
                else: break
            except: break

        raw_items = page.evaluate("""() => {
            const res = [];
            document.querySelectorAll('a[href]').forEach(a => {
                const text = (a.innerText || a.textContent || '').trim();
                if ((text.includes('đ') || text.includes('₫')) && text.length > 15) {
                    res.push({ text: text });
                }
            });
            return res;
        }""")

        seen = set()
        for idx, item in enumerate(raw_items or []):
            if len(products) >= max_sp or stop_fn(): break
            text = item["text"]
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            name = next((l for l in lines if len(l) > 5 and not re.search(r'\d.*đ', l) and '%' not in l), None)
            if not name or name.lower() in seen: continue
            prices = [parse_price(p) for p in re.findall(r"\d{1,3}(?:[.,]\d{3})+\s*(?:₫|đ)", text)]
            prices = [p for p in prices if p >= 100000]
            if not prices: continue
            gia_ban = min(prices)
            gia_goc = max(prices) if len(prices) > 1 else gia_ban
            if gia_goc < gia_ban: gia_goc, gia_ban = gia_ban, gia_goc
            pct = re.search(r"(\d{1,2})\s*%", text)
            ty_le = int(pct.group(1)) if pct else int(((gia_goc - gia_ban)/gia_goc)*100) if gia_goc > gia_ban else 0
            products.append(RawProduct(
                ma_san_pham=f"{site_name[:3].upper()}{idx:03d}",
                ten_san_pham=name,
                don_gia_goc=int(gia_goc),
                gia_sau_giam=int(gia_ban),
                ty_le_giam=int(ty_le),
                danh_muc=category,
                thuong_hieu=guess_brand(name),
                nguon=site_name
            ))
            seen.add(name.lower())
        log_fn(f"[{site_name}] Hoàn tất {category}: lấy được {len(products)} sản phẩm.")
    except Exception as e:
        log_fn(f"[{site_name}] Lỗi danh mục {category}: {e}")
    return products

class UnifiedCrawlerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("All-In-One Unified Crawler")
        self.geometry("1250x750")
        self.is_running = False
        self.stop_signal = False
        self.build_ui()

    def build_ui(self):
        frm = ttk.LabelFrame(self, text=" Cấu hình cào dữ liệu tổng hợp ", padding=10)
        frm.pack(fill="x", padx=10, pady=5)

        ttk.Label(frm, text="Danh mục sản phẩm:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        f_cat = ttk.Frame(frm)
        f_cat.grid(row=0, column=1, columnspan=3, sticky="w")
        self.cats = {}
        for c in ["Điện thoại", "Laptop", "Máy tính bảng", "Phụ kiện", "Tivi"]:
            v = tk.BooleanVar(value=True)
            self.cats[c] = v
            ttk.Checkbutton(f_cat, text=c, variable=v).pack(side="left", padx=5)
        ttk.Label(frm, text="Số SP tối đa / danh mục:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.spin_max = ttk.Spinbox(frm, from_=5, to=300, width=8)
        self.spin_max.set(20)
        self.spin_max.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(frm, text="Số lần click 'Xem thêm':").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.spin_load = ttk.Spinbox(frm, from_=0, to=15, width=8)
        self.spin_load.set(2)
        self.spin_load.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        ttk.Label(frm, text="Tổng dòng Dataset:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.spin_rows = ttk.Spinbox(frm, from_=10, to=10000, increment=50, width=8)
        self.spin_rows.set(100)
        self.spin_rows.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.chk_head = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="Chạy ẩn trình duyệt (Headless)", variable=self.chk_head).grid(row=2, column=2, columnspan=2, sticky="w", padx=5)
        ttk.Label(frm, text="Lưu file CSV tổng hợp:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.ent_file = ttk.Entry(frm, width=65)
        self.ent_file.insert(0, os.path.join(os.getcwd(), "dataset_tong_hop.csv"))
        self.ent_file.grid(row=3, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        ttk.Button(frm, text="Chọn...", command=self.select_file).grid(row=3, column=3, sticky="w", padx=5)
        f_act = ttk.Frame(self)
        f_act.pack(fill="x", padx=10, pady=5)
        self.btn_start = ttk.Button(f_act, text="BẮT ĐẦU CÀO ", command=self.start)
        self.btn_start.pack(side="left", padx=5)
        self.btn_stop = ttk.Button(f_act, text="DỪNG LẠI", command=self.stop, state="disabled")
        self.btn_stop.pack(side="left", padx=5)
        self.lbl_stt = ttk.Label(f_act, text="Trạng thái: Sẵn sàng.", font=("Segoe UI", 9, "italic"))
        self.lbl_stt.pack(side="left", padx=15)
        self.pbar = ttk.Progressbar(self, mode="determinate")
        self.pbar.pack(fill="x", padx=10, pady=5)
        pane = ttk.PanedWindow(self, orient="vertical")
        pane.pack(fill="both", expand=True, padx=10, pady=5)
        f_t = ttk.LabelFrame(pane, text=" Bảng dữ liệu thời gian thực ", padding=5)
        pane.add(f_t, weight=3)
        self.tree = ttk.Treeview(f_t, columns=CSV_COLUMNS, show="headings")
        for col in CSV_COLUMNS:
            self.tree.heading(col, text=col)
            w = 70 if col in ("STT", "So_Luong", "Ty_Le_Giam_Gia", "Tan_suat_mua_hang") else (200 if col == "Ten_San_Pham" else 110)
            self.tree.column(col, width=w, anchor="center" if w < 100 else "w")
        sy = ttk.Scrollbar(f_t, orient="vertical", command=self.tree.yview)
        sx = ttk.Scrollbar(f_t, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side="right", fill="y"); sx.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        f_l = ttk.LabelFrame(pane, text=" Nhật ký hệ thống (Log) ", padding=5)
        pane.add(f_l, weight=1)
        self.log_area = tk.Text(f_l, height=6, bg="black", fg="#00FF00", font=("Consolas", 9))
        sl = ttk.Scrollbar(f_l, orient="vertical", command=self.log_area.yview)
        self.log_area.configure(yscrollcommand=sl.set)
        sl.pack(side="right", fill="y")
        self.log_area.pack(fill="both", expand=True)

    def select_file(self):
        f = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if f:
            self.ent_file.delete(0, tk.END)
            self.ent_file.insert(0, f)

    def log(self, text):
        def _do():
            ts = datetime.now().strftime("%H:%M:%S")
            self.log_area.insert("end", f"[{ts}] {text}\n")
            self.log_area.see("end")
        self.after(0, _do)

    def status(self, text):
        self.after(0, lambda: self.lbl_stt.config(text=f"Trạng thái: {text}"))

    def add_row(self, row):
        def _do():
            self.tree.insert("", "end", values=[row[c] for c in CSV_COLUMNS])
            kids = self.tree.get_children()
            if kids: self.tree.see(kids[-1])
        self.after(0, _do)

    def start(self):
        selected_cats = [c for c, v in self.cats.items() if v.get()]
        if not selected_cats:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất 1 danh mục!")
            return

        self.is_running = True
        self.stop_signal = False
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.tree.delete(*self.tree.get_children())
        self.pbar["value"] = 0

        threading.Thread(target=self.run_task, args=(selected_cats,), daemon=True).start()

    def stop(self):
        if self.is_running:
            self.stop_signal = True
            self.log("Đã phát tín hiệu dừng chương trình...")

    def run_task(self, selected_cats):
        try:
            max_p = int(self.spin_max.get())
            load_c = int(self.spin_load.get())
            total_r = int(self.spin_rows.get())
            headless = self.chk_head.get()
            out_path = self.ent_file.get().strip()  # Đã sửa đúng thuộc tính ent_file
            if not out_path: out_path = os.path.join(os.getcwd(), "dataset_tong_hop.csv")
            self.log("=== BẮT ĐẦU CÀO DỮ LIỆU ===")
            master_raw_products = []
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=headless)
                context = browser.new_context(viewport={"width": 1280, "height": 800}, locale="vi-VN")
                page = context.new_page()
                total_jobs = len(ALL_SITE_URLS) * len(selected_cats)
                done_jobs = 0

                for site_name, cat_dict in ALL_SITE_URLS.items():
                    if self.stop_signal: break
                    for cat in selected_cats:
                        if self.stop_signal: break
                        if cat not in cat_dict:
                            done_jobs += 1
                            continue
                        url = cat_dict[cat]
                        self.status(f"Đang cào {site_name} - {cat}")
                        prods = crawl_site(page, site_name, cat, url, max_p, load_c, self.log, lambda: self.stop_signal)
                        master_raw_products.extend(prods)
                        done_jobs += 1
                        self.pbar["value"] = (done_jobs / max(total_jobs, 1)) * 50
                browser.close()

            if not master_raw_products:
                self.log("[LỖI] Không thu thập được sản phẩm nào từ các trang web!")
                return
            self.log(f"-> Tổng hợp thành công {len(master_raw_products)} sản phẩm thô. Đang tạo đơn hàng...")
            final_rows = []
            stt = 1
            pos = 0
            while len(final_rows) < total_r and not self.stop_signal:
                p = master_raw_products[pos % len(master_raw_products)]
                tinh, phuong, dc = get_address(stt)
                category_factor = {"Điện thoại": 2, "Laptop": 1, "Máy tính bảng": 2, "Phụ kiện": 3, "Tivi": 2}
                factor = category_factor.get(p.danh_muc, 2)
                val_q = (stt * 7 + len(p.ten_san_pham) + len(p.thuong_hieu) + factor) % 10
                so_luong = 1 if val_q <= 5 else (2 if val_q <= 8 else 3)
                val_goc = p.don_gia_goc
                val_ban = p.gia_sau_giam
                if val_goc < val_ban: val_goc, val_ban = val_ban, val_goc
                tong_hang = val_ban * so_luong
                tong_tt = round(tong_hang * 1.1)
                freq_vals = [5, 10, 15, 20, 30]
                score = len(p.ten_san_pham) + len(p.thuong_hieu) + len(p.danh_muc)
                tan_suat = freq_vals[(stt * 3 + score) % len(freq_vals)]
                row = {
                    "STT": stt,
                    "Nguon_Trang": p.nguon,
                    "Tinh_Thanh": tinh,
                    "Phuong_Xa": phuong,
                    "Dia_Chi_Cu_The": dc,
                    "Ma_San_Pham": p.ma_san_pham,
                    "Ten_San_Pham": p.ten_san_pham,
                    "Nhom_Hang": "Đồ điện tử",
                    "So_Luong": so_luong,
                    "Don_Gia": format_currency(val_goc),
                    "Ty_Le_Giam_Gia": p.ty_le_giam,
                    "Tien_Giam": format_currency(val_ban),
                    "Tong_Hang": format_currency(tong_hang),
                    "Tong_Thanh_Toan": format_currency(tong_tt),
                    "Tan_suat_mua_hang": tan_suat,
                    "Thuong_Hieu": p.thuong_hieu,
                    "Danh_Muc": p.danh_muc
                }
                final_rows.append(row)
                self.add_row(row)
                stt += 1
                pos += 1
                self.pbar["value"] = 50 + ((len(final_rows) / total_r) * 50)

            if final_rows:
                os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
                with open(out_path, mode="w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
                    writer.writeheader()
                    writer.writerows(final_rows)
                self.log(f"=== HOÀN TẤT XUẤT 1 FILE DUY NHẤT: {out_path} ({len(final_rows)} dòng) ===")
                self.status("Hoàn tất.")
                self.after(0, lambda: messagebox.showinfo("Thành công", f"Đã cào toàn bộ và xuất thành công 1 file duy nhất:\n{out_path}"))
        except Exception as ex:
            self.log(f"[LỖI TRẦM TRỌNG]: {ex}")
            self.status("Gặp lỗi khi chạy.")
        finally:
            self.is_running = False
            self.after(0, lambda: self.btn_start.config(state="normal"))
            self.after(0, lambda: self.btn_stop.config(state="disabled"))

if __name__ == "__main__":
    app = UnifiedCrawlerApp()
    app.mainloop()