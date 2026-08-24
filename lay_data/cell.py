import csv
import os
import re
import threading

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from playwright.sync_api import sync_playwright

# 1. CẤU HÌNH DANH MỤC CELLPHONES
CATEGORY_URLS = {
    "Điện thoại": "https://cellphones.com.vn/",
    "Laptop": "https://cellphones.com.vn/laptop.html",
    "Phụ kiện": "https://cellphones.com.vn/phu-kien.html",
    "Máy tính bảng": "https://cellphones.com.vn/catalogsearch/result?q=m%C3%A1y%20t%C3%ADnh%20b%E1%BA%A3ng",
}

KNOWN_BRANDS = [
    "iPhone", "Apple", "MacBook", "iPad", "Samsung", "Xiaomi", "Redmi", "Poco", "POCO",
    "Oppo", "OPPO", "Vivo", "vivo", "Realme", "realme", "Nokia", "Asus",
    "ASUS", "Acer", "Dell", "HP", "Lenovo", "MSI", "LG", "Huawei", "Honor", "HONOR",
    "Masstel", "Itel", "Anker", "JBL", "Sony", "Canon", "Baseus", "Nubia",
    "TECNO", "Tecno", "TCL", "Kingston", "Logitech", "Razer", "TP-Link", "Ugreen",
    "Belkin", "Marshall", "Garmin", "GoPro"
]


CSV_COLUMNS = [
    "STT", "Tinh_Thanh", "Phuong_Xa", "Dia_Chi_Cu_The", 
    "Ma_San_Pham", "Ten_San_Pham", "Nhom_Hang", "So_Luong", 
    "Don_Gia", "Ty_Le_Giam_Gia", "Tien_Giam", "Tong_Hang", 
    "Tong_Thanh_Toan", "Tan_suat_mua_hang", "Thuong_Hieu", "Danh_Muc"
]

LOCATION_DATA = [
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

def _guess_brand(product_name: str) -> str:
    product_lower = product_name.lower()
    if "iphone" in product_lower: return "Apple"
    if "ipad" in product_lower: return "Apple"
    if "macbook" in product_lower: return "Apple"
    if "apple" in product_lower: return "Apple"
    if "redmi" in product_lower: return "Xiaomi"
    if "poco" in product_lower: return "Xiaomi"
    if "xiaomi" in product_lower: return "Xiaomi"
    if "oppo" in product_lower: return "Oppo"
    if "asus" in product_lower: return "Asus"
    if "honor" in product_lower: return "Honor"
    if "tecno" in product_lower: return "Tecno"

    for brand in KNOWN_BRANDS:
        if brand.lower() in product_lower:
            return brand
    return "Khác"

def _parse_price(price_text: str) -> int:
    if not price_text:
        return 0
    cleaned = price_text.replace("\xa0", " ").replace(" ", "")
    digits = re.sub(r"[^\d]", "", cleaned)
    if not digits:
        return 0
    try:
        return int(digits)
    except ValueError:
        return 0

def format_currency(amount: int) -> str:
    return f"{int(amount):,}".replace(",", ".")

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\xa0", " ").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text)
    return text.strip()

def generate_quantity(index: int, product: RawProduct) -> int:
    category_factor = {
        "Điện thoại": 2,
        "Laptop": 1,
        "Máy tính bảng": 2,
        "Phụ kiện": 3,
    }
    factor = category_factor.get(product.danh_muc, 2)
    value = (index * 7 + len(product.ten_san_pham) + len(product.thuong_hieu) + factor) % 10
    if value <= 5: return 1
    if value <= 8: return 2
    return 3

def generate_purchase_frequency(index: int, product: RawProduct) -> int:
    values = [5, 10, 15, 20, 30]
    product_score = len(product.ten_san_pham) + len(product.thuong_hieu) + len(product.danh_muc)
    position = (index * 3 + product_score) % len(values)
    return values[position]

class CellphoneSCrawler:
    def __init__(self, headless=False, max_products_per_cat=50, load_more_clicks=5, log_cb=None, stop_flag=None):
        self.headless = headless
        self.max_products_per_cat = max_products_per_cat
        self.load_more_clicks = load_more_clicks
        self.log_cb = log_cb or (lambda m: None)
        self.stop_flag = stop_flag or (lambda: False)
    def log(self, msg):
        self.log_cb(msg)
    def _auto_scroll(self, page):
        for _ in range(8):
            if self.stop_flag(): break
            page.evaluate("window.scrollBy(0, 800);")
            page.wait_for_timeout(700)
    def _extract_discount(self, text: str) -> int:
        if not text: return 0
        patterns = [r"giảm\s*(\d{1,2})\s*%", r"-\s*(\d{1,2})\s*%", r"(\d{1,2})\s*%\s*(?:giảm|off)"]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                try:
                    value = int(match.group(1))
                    if 0 <= value <= 100: return value
                except ValueError: pass
        return 0
    def _extract_card_price(self, full_text: str) -> Tuple[int, int, int]:
        text = normalize_text(full_text)
        if not text: return 0, 0, 0
        discount = self._extract_discount(text)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        price_entries = []
        for line in lines:
            lower = line.lower()
            if "trả góp" in lower or "mỗi tháng" in lower or "/tháng" in lower: continue
            if "voucher" in lower or "quà tặng" in lower: continue
            matches = re.findall(r"(?<!\d)\d{1,3}(?:[.,]\d{3})+\s*(?:₫|đ|vnđ)", line, flags=re.IGNORECASE)
            for match in matches:
                price = _parse_price(match)
                if price >= 100000:
                    price_entries.append({"line": line, "price": price})
        if not price_entries: return 0, 0, discount
        current_price = 0
        original_price = 0
        for entry in price_entries:
            if any(k in entry["line"].lower() for k in ["giá niêm yết", "giá gốc", "giá cũ"]):
                original_price = entry["price"]
                break
        for entry in price_entries:
            if any(k in entry["line"].lower() for k in ["giá bán", "giá cho bạn", "chỉ còn"]):
                current_price = entry["price"]
                break
        if current_price == 0 and len(price_entries) >= 1: current_price = price_entries[0]["price"]
        if original_price == 0 and len(price_entries) >= 2: original_price = price_entries[1]["price"]
        if len(price_entries) == 1:
            current_price = price_entries[0]["price"]
            original_price = price_entries[0]["price"]
            discount = 0
        if current_price > 0 and original_price > 0 and original_price < current_price:
            original_price, current_price = current_price, original_price
        if discount == 0 and original_price > current_price and original_price > 0:
            discount = round(((original_price - current_price) / original_price) * 100)
        return current_price, original_price, discount

    def _extract_product_name(self, text: str) -> str:
        if not text: return ""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        ignored_words = ["trả góp", "mỗi tháng", "yêu thích", "xem chi tiết", "giảm", "voucher", "quà tặng", "chỉ còn", "giá bán", "giá niêm yết"]
        
        for line in lines:
            lower = line.lower()
            if re.search(r"\d{1,3}(?:[.,]\d{3})+\s*(?:₫|đ|vnđ)", line, flags=re.IGNORECASE): continue
            if "%" in line: continue
            if lower.startswith("sku"): continue
            if any(word in lower for word in ignored_words): continue
            if len(line) >= 5: return line
        return ""

    def crawl_category(self, page, category: str) -> List[RawProduct]:
        url = CATEGORY_URLS.get(category)
        if not url: return []
        self.log(f"Mở danh mục: {category} -> {url}")
        
        try:
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
        except Exception as exc:
            self.log(f"[LỖI] Không mở được {category}: {exc}")
            return []

        page.wait_for_timeout(3000)
        self._auto_scroll(page)

        for i in range(self.load_more_clicks):
            if self.stop_flag(): break
            try:
                buttons = page.locator("button, a")
                for j in range(min(buttons.count(), 100)):
                    btn = buttons.nth(j)
                    if btn.is_visible() and "xem thêm" in btn.inner_text(timeout=300).lower():
                        btn.click(timeout=2000)
                        page.wait_for_timeout(1500)
                        self._auto_scroll(page)
                        break
            except: break
        raw_items = page.evaluate("""() => {
            const results = [];
            document.querySelectorAll('a[href]').forEach(a => {
                const href = a.href || '';
                const text = (a.innerText || a.textContent || '').trim();
                if(href.includes('cellphones.com.vn') && !href.includes('/search') && text.length > 15 && /\\d/i.test(text)){
                    results.push({text: text});
                }
            });
            return results;
        }""")

        products = []
        seen = set()
        idx = 1
        for item in raw_items or []:
            if len(products) >= self.max_products_per_cat or self.stop_flag(): break
            full_text = normalize_text(item.get("text", ""))
            if not full_text: continue
            name = self._extract_product_name(full_text)
            if not name: continue
            name_key = re.sub(r"\s+", " ", name.lower())
            if name_key in seen: continue
            seen.add(name_key)
            gia_sau_giam, don_gia_goc, ty_le_giam = self._extract_card_price(full_text)
            if gia_sau_giam <= 0: continue
            if don_gia_goc <= 0: don_gia_goc = gia_sau_giam
            if don_gia_goc < gia_sau_giam:
                don_gia_goc, gia_sau_giam = gia_sau_giam, don_gia_goc
            products.append(RawProduct(
                ma_san_pham=f"CPS{idx:04d}",
                ten_san_pham=name,
                don_gia_goc=int(don_gia_goc),
                gia_sau_giam=int(gia_sau_giam),
                ty_le_giam=int(ty_le_giam),
                danh_muc=category,
                thuong_hieu=_guess_brand(name)
            ))
            idx += 1
        self.log(f"Quét thành công {len(products)} sản phẩm thuộc '{category}'.")
        return products

class AppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CellphoneS Crawler - Xuất dữ liệu CSV chuẩn")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        self.is_running = False
        self.stop_requested = False
        self._build_ui()

    def _build_ui(self):
        config_frame = ttk.LabelFrame(self, text=" Cấu hình cào dữ liệu ", padding=10)
        config_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(config_frame, text="Danh mục:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        cat_subframe = ttk.Frame(config_frame)
        cat_subframe.grid(row=0, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        self.cat_vars = {}
        for cat in CATEGORY_URLS.keys():
            var = tk.BooleanVar(value=True)
            self.cat_vars[cat] = var
            ttk.Checkbutton(cat_subframe, text=cat, variable=var).pack(side="left", padx=5)
        ttk.Label(config_frame, text="Số SP tối đa / danh mục:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.spin_max_sp = ttk.Spinbox(config_frame, from_=5, to=500, increment=10, width=10)
        self.spin_max_sp.set(30)
        self.spin_max_sp.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(config_frame, text="Số lần bấm 'Xem thêm':").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.spin_load_more = ttk.Spinbox(config_frame, from_=0, to=20, increment=1, width=10)
        self.spin_load_more.set(3)
        self.spin_load_more.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        ttk.Label(config_frame, text="Tổng số dòng mong muốn:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.spin_total_rows = ttk.Spinbox(config_frame, from_=10, to=10000, increment=50, width=10)
        self.spin_total_rows.set(100)
        self.spin_total_rows.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.var_headless = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, text="Chạy ẩn trình duyệt", variable=self.var_headless).grid(row=2, column=2, columnspan=2, sticky="w", padx=5, pady=5)
        ttk.Label(config_frame, text="File xuất CSV:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.ent_csv_path = ttk.Entry(config_frame, width=75)
        self.ent_csv_path.insert(0, os.path.join(os.getcwd(), "cellphones_products.csv"))
        self.ent_csv_path.grid(row=3, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        ttk.Button(config_frame, text="Chọn...", command=self._browse_file).grid(row=3, column=3, sticky="w", padx=5, pady=5)
        action_frame = ttk.Frame(self)
        action_frame.pack(fill="x", padx=10, pady=5)
        self.btn_start = ttk.Button(action_frame, text="▶ Bắt đầu cào dữ liệu", command=self.start_crawling)
        self.btn_start.pack(side="left", padx=5)
        self.btn_stop = ttk.Button(action_frame, text="⏹ Dừng", command=self.stop_crawling, state="disabled")
        self.btn_stop.pack(side="left", padx=5)
        self.lbl_status = ttk.Label(action_frame, text="Sẵn sàng.", font=("Segoe UI", 9, "italic"))
        self.lbl_status.pack(side="left", padx=15)
        self.progress_bar = ttk.Progressbar(self, mode="determinate")
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        paned = ttk.PanedWindow(self, orient="vertical")
        paned.pack(fill="both", expand=True, padx=10, pady=5)
        tree_frame = ttk.LabelFrame(paned, text=" Dữ liệu đơn hàng ", padding=5)
        paned.add(tree_frame, weight=3)
        self.tree = ttk.Treeview(tree_frame, columns=CSV_COLUMNS, show="headings", selectmode="browse")
        for col in CSV_COLUMNS:
            self.tree.heading(col, text=col)
            width = 110
            if col in ("STT", "So_Luong", "Ty_Le_Giam_Gia", "Tan_suat_mua_hang"): width = 70
            elif col == "Ten_San_Pham": width = 260
            elif col == "Dia_Chi_Cu_The": width = 320
            self.tree.column(col, width=width, anchor="center" if col not in ("Ten_San_Pham", "Dia_Chi_Cu_The") else "w")
        sc_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        sc_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sc_y.set, xscrollcommand=sc_x.set)
        sc_y.pack(side="right", fill="y"); sc_x.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        log_frame = ttk.LabelFrame(paned, text=" Nhật ký xử lý ", padding=5)
        paned.add(log_frame, weight=1)
        self.txt_log = tk.Text(log_frame, height=6, bg="black", fg="lightgreen", font=("Consolas", 9))
        sc_log = ttk.Scrollbar(log_frame, orient="vertical", command=self.txt_log.yview)
        self.txt_log.configure(yscrollcommand=sc_log.set)
        sc_log.pack(side="right", fill="y")
        self.txt_log.pack(fill="both", expand=True)
    def _browse_file(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if filepath:
            self.ent_csv_path.delete(0, tk.END)
            self.ent_csv_path.insert(0, filepath)

    def log(self, message: str):
        def _append():
            ts = datetime.now().strftime("%H:%M:%S")
            self.txt_log.insert("end", f"[{ts}] {message}\n")
            self.txt_log.see("end")
        self.after(0, _append)

    def set_status(self, text: str):
        self.after(0, lambda: self.lbl_status.config(text=text))

    def add_row_to_table(self, row_dict: Dict):
        def _add():
            self.tree.insert("", "end", values=[row_dict[c] for c in CSV_COLUMNS])
            children = self.tree.get_children()
            if children: self.tree.see(children[-1])
        self.after(0, _add)

    def start_crawling(self):
        selected_cats = [cat for cat, var in self.cat_vars.items() if var.get()]
        if not selected_cats:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất 1 danh mục!")
            return
        self.is_running = True
        self.stop_requested = False
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.tree.delete(*self.tree.get_children())
        self.progress_bar["value"] = 0
        threading.Thread(target=self._run_task, args=(selected_cats,), daemon=True).start()

    def stop_crawling(self):
        if self.is_running:
            self.stop_requested = True
            self.log("Đang dừng quá trình...")

    def _run_task(self, categories: List[str]):
        try:
            max_sp = int(self.spin_max_sp.get())
            load_more = int(self.spin_load_more.get())
            target_rows = int(self.spin_total_rows.get())
            is_headless = self.var_headless.get()
            csv_path = self.ent_csv_path.get().strip()
            if not csv_path: csv_path = os.path.join(os.getcwd(), "cellphones_products.csv")
            self.log("=== BẮT ĐẦU CÀO CELLPHONES ===")
            crawler = CellphoneSCrawler(
                headless=is_headless,
                max_products_per_cat=max_sp,
                load_more_clicks=load_more,
                log_cb=self.log,
                stop_flag=lambda: self.stop_requested
            )
            all_raw_products = []
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=is_headless)
                context = browser.new_context(viewport={"width": 1280, "height": 800}, locale="vi-VN")
                page = context.new_page()

                for idx, cat in enumerate(categories):
                    if self.stop_requested: break
                    self.set_status(f"Đang cào danh mục: {cat}")
                    products = crawler.crawl_category(page, cat)
                    all_raw_products.extend(products)
                    self.progress_bar["value"] = int(((idx + 1) / len(categories)) * 50)

                browser.close()
            if not all_raw_products:
                self.log("[LỖI] Không cào được sản phẩm nào!")
                return

            self.log(f"-> Thu thập thành công {len(all_raw_products)} sản phẩm. Đang tạo đơn hàng...")
            final_rows = []
            stt = 1
            product_position = 0
            while len(final_rows) < target_rows and not self.stop_requested:
                prod = all_raw_products[product_position % len(all_raw_products)]
                so_luong = generate_quantity(stt, prod)
                tinh_thanh, phuong_xa, dia_chi_cu_the = LOCATION_DATA[(stt - 1) % len(LOCATION_DATA)]
                val_don_gia = int(prod.don_gia_goc)
                val_ty_le_giam = int(prod.ty_le_giam)
                val_tien_giam = int(prod.gia_sau_giam)
                if val_don_gia <= 0 or val_tien_giam <= 0:
                    product_position += 1
                    continue
                if val_don_gia < val_tien_giam:
                    val_don_gia, val_tien_giam = val_tien_giam, val_don_gia
                val_tong_hang = val_tien_giam * so_luong
                val_tong_thanh_toan = round(val_tong_hang * 1.1)
                tan_suat = generate_purchase_frequency(stt, prod)
                row = {
                    "STT": stt,
                    "Tinh_Thanh": tinh_thanh,
                    "Phuong_Xa": phuong_xa,
                    "Dia_Chi_Cu_The": dia_chi_cu_the,
                    "Ma_San_Pham": prod.ma_san_pham,
                    "Ten_San_Pham": prod.ten_san_pham,
                    "Nhom_Hang": "Đồ điện tử",
                    "So_Luong": so_luong,
                    "Don_Gia": format_currency(val_don_gia),
                    "Ty_Le_Giam_Gia": val_ty_le_giam,
                    "Tien_Giam": format_currency(val_tien_giam),
                    "Tong_Hang": format_currency(val_tong_hang),
                    "Tong_Thanh_Toan": format_currency(val_tong_thanh_toan),
                    "Tan_suat_mua_hang": tan_suat,
                    "Thuong_Hieu": prod.thuong_hieu,
                    "Danh_Muc": prod.danh_muc,
                }
                final_rows.append(row)
                self.add_row_to_table(row)
                stt += 1
                product_position += 1
                self.progress_bar["value"] = 50 + int((len(final_rows) / target_rows) * 50)
            if final_rows:
                os.makedirs(os.path.dirname(os.path.abspath(csv_path)), exist_ok=True)
                with open(csv_path, mode="w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
                    writer.writeheader()
                    writer.writerows(final_rows)

                self.log(f"=== HOÀN TẤT! Đã xuất {len(final_rows)} dòng vào file: {csv_path} ===")
                self.set_status("Hoàn tất.")
                self.after(0, lambda: messagebox.showinfo("Thành công", f"Đã xuất thành công {len(final_rows)} dòng ra file:\n{csv_path}"))
        except Exception as exc:
            self.log(f"[LỖI XỬ LÝ] {exc}")
            self.set_status("Có lỗi xảy ra.")
        finally:
            self.is_running = False
            self.after(0, lambda: self.btn_start.config(state="normal"))
            self.after(0, lambda: self.btn_stop.config(state="disabled"))

if __name__ == "__main__":
    app = AppGUI()
    app.mainloop()