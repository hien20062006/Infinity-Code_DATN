
import csv
import os
import re
import threading
from dataclasses import dataclass
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Dict, List

from playwright.sync_api import sync_playwright


# ============================================================
# 1. CẤU HÌNH DANH MỤC
# ============================================================

CATEGORY_URLS = {
    "Điện thoại":
        "https://fptshop.com.vn/dien-thoai",

    "Laptop":
        "https://fptshop.com.vn/may-tinh-xach-tay",

    "Máy tính bảng":
        "https://fptshop.com.vn/may-tinh-bang",

    "Phụ kiện":
        "https://fptshop.com.vn/phu-kien",
}


# ============================================================
# 2. DANH SÁCH THƯƠNG HIỆU
# ============================================================

KNOWN_BRANDS = ["iPhone","Apple","MacBook","iPad","Samsung","Xiaomi","Redmi","Poco","Oppo","Vivo","Realme","Nokia","Asus","Acer",
                "Dell","HP","Lenovo","MSI","LG","Huawei","Honor","Masstel","Itel","Anker","JBL","Sony","Canon","Baseus","Nubia",
]


# ============================================================
# 3. 20 ĐỊA CHỈ FPT SHOP
#
# Đây là danh sách địa điểm thực tế dùng cho dataset.
# Không coi đây là thứ hạng doanh số chính thức.
# ============================================================

FPT_ADDRESSES = [

# --------------------------------------------------------
# HÀ NỘI
# --------------------------------------------------------

(
    "Hà Nội",
    "P. Đống Đa",
    "45 Thái Hà (Gần bể bơi Thái Hà) (FPT Shop)"
),

(
    "Hà Nội",
    "P. Phú Diễn",
    "24 Hồ Tùng Mậu (Đối diện đường Trần Bình) (FPT Shop)"
),

(
    "Hà Nội",
    "P. Hai Bà Trưng",
    "325 Phố Huế (Đầu chợ Giời) (FPT Shop)"
),

(
    "Hà Nội",
    "P. Cầu Giấy",
    "109 Hồ Tùng Mậu (FPT Shop)"
),

# --------------------------------------------------------
# HỒ CHÍ MINH
# --------------------------------------------------------

(
    "Hồ Chí Minh",
    "P. Bến Thành",
    "29-31 Nguyễn Thị Minh Khai (FPT Shop)"
),

(
    "Hồ Chí Minh",
    "P. Tân Sơn Nhất",
    "2A Phan Đăng Lưu (FPT Shop)"
),

(
    "Hồ Chí Minh",
    "P. Vĩnh Hội",
    "261-263 Khánh Hội (FPT Shop)"
),

(
    "Hồ Chí Minh",
    "P. Tân Bình",
    "202 Hoàng Văn Thụ (FPT Shop)"
),

# --------------------------------------------------------
# ĐÀ NẴNG
# --------------------------------------------------------

(
    "Đà Nẵng",
    "P. Thanh Khê",
    "318 Lê Duẩn (FPT Shop)"
),

(
    "Đà Nẵng",
    "P. Hải Châu",
    "Lô A1 Nguyễn Văn Linh nối dài (FPT Shop)"
),

# --------------------------------------------------------
# CẦN THƠ
# --------------------------------------------------------

(
    "Cần Thơ",
    "P. Ninh Kiều",
    "83 Trần Hưng Đạo (Ngã ba Lý Tự Trọng) (FPT Shop)"
),

(
    "Cần Thơ",
    "P. Ninh Kiều",
    "52-54-56 Đường 30/4 (FPT Shop)"
),

(
    "Cần Thơ",
    "P. Thốt Nốt",
    "314 Quốc Lộ 91 (FPT Shop)"
),

# --------------------------------------------------------
# HẢI PHÒNG
# --------------------------------------------------------

(
    "Hải Phòng",
    "X. Vĩnh Bảo",
    "238-240 Phố Đông Thái (Cổng chợ Vĩnh Bảo)((FPT Shop))"
),

(
    "Hải Phòng",
    "X. Tiên Lãng",
    "42 Minh Đức, Tỉnh lộ 354, Khu 2 (FPT Shop)"
),

(
    "Đồng Nai",
    "P. Long Khánh",
    "Đường Hùng Vương (FPT Shop)"
),

(
    "Bình Dương",
    "P. Thủ Dầu Một",
    "Đại lộ Bình Dương (FPT Shop)"
),

(
    "Bà Rịa - Vũng Tàu",
    "P. Phước Trung",
    "Đường 30/4 (FPT Shop)"
),

(
    "Khánh Hòa",
    "P. Nha Trang",
    "Đường Thái Nguyên (FPT Shop)"
),

(
    "Nghệ An",
    "P. Vinh",
    "Đường Lê Duẩn (FPT Shop)"
),

]


# ============================================================
# 4. CỘT CSV
# ============================================================

CSV_COLUMNS = [
    "STT",
    "Tinh_Thanh",
    "Phuong_Xa",
    "Dia_Chi_Cu_The",
    "Ma_San_Pham",
    "Ten_San_Pham",
    "Nhom_Hang",
    "So_Luong",
    "Don_Gia",
    "Ty_Le_Giam_Gia",
    "Tien_Giam",
    "Tong_Hang",
    "Tong_Thanh_Toan",
    "Tan_suat_mua_hang",
    "Thuong_Hieu",
    "Danh_Muc",
]


# ============================================================
# 5. DATA MODEL
# ============================================================

@dataclass
class RawProduct:

    ma_san_pham: str

    ten_san_pham: str

    # Giá gốc trên website
    don_gia_goc: int

    # Giá bán hiện tại trên website
    gia_sau_giam: int

    # Phần trăm giảm trên website
    ty_le_giam: int

    danh_muc: str

    thuong_hieu: str


# ============================================================
# 6. XỬ LÝ THƯƠNG HIỆU
# ============================================================

def _guess_brand(product_name: str) -> str:

    product_lower = product_name.lower()

    for brand in KNOWN_BRANDS:

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

def _parse_price(price_text: str) -> int:

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

def get_fpt_address(index: int):

    if not FPT_ADDRESSES:
        return "", "", ""

    position = (
        index - 1
    ) % len(FPT_ADDRESSES)

    tinh, phuong_xa, dia_chi = (
        FPT_ADDRESSES[position]
    )

    return (
        tinh,
        phuong_xa,
        dia_chi
    )


# ============================================================
# 10. TẠO SỐ LƯỢNG
#
# KHÔNG DÙNG RANDOM
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
# KHÔNG DÙNG RANDOM
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
        30
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
# 12. CRAWLER FPT SHOP
# ============================================================

class FPTShopCrawler:

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
    # AUTO SCROLL
    # ========================================================

    def _auto_scroll(self, page):

        for _ in range(5):

            if self.stop_flag():
                break

            page.evaluate(
                "window.scrollBy(0, 700);"
            )

            page.wait_for_timeout(
                700
            )

    # ========================================================
    # LẤY GIÁ
    #
    # QUAN TRỌNG:
    # KHÔNG DÙNG MIN / MAX
    # ========================================================

    def _extract_prices_from_text(
        self,
        text: str
    ) -> List[int]:

        if not text:
            return []

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        prices = []

        pattern = re.compile(
            r"(?<!\d)"
            r"(\d{1,3}(?:[.,]\d{3})+)"
            r"\s*(?:₫|đ|VNĐ)"
            r"(?!\w)",
            re.IGNORECASE
        )

        for line in lines:

            lower = line.lower()

            # ------------------------------------------------
            # BỎ GIÁ TRẢ GÓP
            # ------------------------------------------------

            if (
                "trả góp" in lower
                or "mỗi tháng" in lower
                or "/tháng" in lower
            ):
                continue

            # ------------------------------------------------
            # BỎ QUÀ TẶNG / VOUCHER
            # ------------------------------------------------

            if (
                "quà tặng" in lower
                or "voucher" in lower
            ):
                continue

            matches = pattern.findall(
                line
            )

            for value in matches:

                price = _parse_price(
                    value
                )

                if price >= 100000:

                    if price not in prices:

                        prices.append(
                            price
                        )

        return prices

    # ========================================================
    # LẤY % GIẢM
    # ========================================================

    def _extract_discount(
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
            f"Mở danh mục: {category} -> {url}"
        )

        try:

            page.goto(
                url,
                timeout=60000,
                wait_until="domcontentloaded"
            )

        except Exception as exc:

            self.log(
                f"[LỖI] Không mở được {category}: {exc}"
            )

            return []

        page.wait_for_timeout(
            3000
        )

        self._auto_scroll(
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

            try:

                page.evaluate(
                    """
                    window.scrollTo(
                        0,
                        document.body.scrollHeight - 700
                    )
                    """
                )

                page.wait_for_timeout(
                    1200
                )

                buttons = page.locator(
                    "a, button"
                )

                clicked = False

                count = min(
                    buttons.count(),
                    100
                )

                for j in range(
                    count
                ):

                    try:

                        element = (
                            buttons.nth(j)
                        )

                        text = (
                            element
                            .inner_text(
                                timeout=500
                            )
                            .strip()
                        )

                        if (
                            "Xem thêm"
                            in text
                        ):

                            if element.is_visible():

                                element.click(
                                    timeout=3000
                                )

                                self.log(
                                    f" -> [{category}] "
                                    f"Nhấn 'Xem thêm' "
                                    f"lần {i + 1}"
                                )

                                page.wait_for_timeout(
                                    1800
                                )

                                self._auto_scroll(
                                    page
                                )

                                clicked = True

                                break

                    except Exception:

                        continue

                if not clicked:
                    break

            except Exception:

                break

        # ====================================================
        # LẤY PRODUCT CARD
        # ====================================================

        raw_items = page.evaluate(
            """
            () => {

                const results = [];

                const links = Array.from(
                    document.querySelectorAll(
                        'a[href]'
                    )
                );

                links.forEach(a => {

                    const text = (
                        a.innerText ||
                        a.textContent ||
                        ''
                    ).trim();

                    if (!text) {
                        return;
                    }

                    const hasPrice =
                        /\\d[\\d\\.\\,]*\\s*(₫|đ|VNĐ)/i
                        .test(text);

                    if (!hasPrice) {
                        return;
                    }

                    const lines = text
                        .split('\\n')
                        .map(x => x.trim())
                        .filter(
                            x => x.length > 0
                        );

                    let name = '';

                    for (
                        const line of lines
                    ) {

                        const lower =
                            line.toLowerCase();

                        if (
                            line.length >= 8 &&
                            !/\\d[\\d\\.\\,]*\\s*(₫|đ|vnđ)/i.test(line) &&
                            !/%/.test(line) &&
                            !lower.includes(
                                'trả góp'
                            ) &&
                            !lower.includes(
                                'mỗi tháng'
                            ) &&
                            !lower.includes(
                                'xem chi tiết'
                            )
                        ) {

                            name = line;

                            break;
                        }
                    }

                    if (name) {

                        results.push({
                            name: name,
                            full_text: text
                        });

                    }

                });

                return results;
            }
            """
        )

        products = []

        seen_names = set()

        idx = 1

        # ====================================================
        # XỬ LÝ SẢN PHẨM
        # ====================================================

        for item in raw_items:

            if (
                len(products)
                >= self.max_products_per_cat
                or self.stop_flag()
            ):
                break

            name = (
                item
                .get(
                    "name",
                    ""
                )
                .strip()
            )

            full_text = (
                item
                .get(
                    "full_text",
                    ""
                )
                .strip()
            )

            if not name:
                continue

            # ------------------------------------------------
            # CHỐNG TRÙNG
            # ------------------------------------------------

            name_key = re.sub(
                r"\s+",
                " ",
                name.lower()
            )

            if name_key in seen_names:
                continue

            seen_names.add(
                name_key
            )

            # =================================================
            # LẤY GIÁ
            # =================================================

            all_prices = (
                self._extract_prices_from_text(
                    full_text
                )
            )

            if not all_prices:
                continue

            # =================================================
            # LẤY % GIẢM TRÊN WEB
            # =================================================

            ty_le_giam = (
                self._extract_discount(
                    full_text
                )
            )

            # =================================================
            # XÁC ĐỊNH GIÁ
            #
            # Không dùng min()
            # Không dùng max()
            # =================================================

            if len(all_prices) >= 2:

                # ---------------------------------------------
                # GIÁ HIỆN TẠI
                # ---------------------------------------------

                gia_sau_giam = (
                    all_prices[0]
                )

                # ---------------------------------------------
                # GIÁ GỐC
                # ---------------------------------------------

                don_gia_goc = (
                    all_prices[1]
                )

                # ---------------------------------------------
                # Nếu thứ tự trên card ngược lại
                # thì đổi vị trí
                # ---------------------------------------------

                if (
                    don_gia_goc
                    < gia_sau_giam
                ):

                    don_gia_goc, gia_sau_giam = (
                        gia_sau_giam,
                        don_gia_goc
                    )

            else:

                # ---------------------------------------------
                # Chỉ có một giá
                # ---------------------------------------------

                don_gia_goc = (
                    all_prices[0]
                )

                gia_sau_giam = (
                    all_prices[0]
                )

                ty_le_giam = 0

            # =================================================
            # NẾU WEB KHÔNG CÓ %
            #
            # Chỉ khi không có % mới tính từ 2 giá web.
            # =================================================

            if ty_le_giam == 0:

                if (
                    don_gia_goc
                    > gia_sau_giam
                    and don_gia_goc > 0
                ):

                    ty_le_giam = round(
                        (
                            (
                                don_gia_goc
                                - gia_sau_giam
                            )
                            / don_gia_goc
                        )
                        * 100
                    )

            # =================================================
            # TẠO PRODUCT
            # =================================================

            product = RawProduct(

                ma_san_pham=
                    f"SP{idx:04d}",

                ten_san_pham=
                    name,

                don_gia_goc=
                    int(don_gia_goc),

                gia_sau_giam=
                    int(gia_sau_giam),

                ty_le_giam=
                    int(ty_le_giam),

                danh_muc=
                    category,

                thuong_hieu=
                    _guess_brand(name),
            )

            products.append(
                product
            )

            idx += 1

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
            "FPTShop Crawler - Xuất dữ liệu CSV chuẩn"
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

        self._build_ui()

    # ========================================================
    # BUILD UI
    # ========================================================

    def _build_ui(self):

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

            self.cat_vars[
                cat
            ] = var

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
            "fptshop_products.csv"
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
            command=self._browse_file
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
        # PANED WINDOW
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

                width = 70

            elif col == "Ten_San_Pham":

                width = 230

            elif col == "Dia_Chi_Cu_The":

                width = 300

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

    def _browse_file(self):

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
                )
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

        def _append():

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
            _append
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
    # THÊM ROW VÀO GUI
    # ========================================================

    def add_row_to_table(
        self,
        row_dict: Dict
    ):

        def _add():

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
            _add
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

        self.progress_bar[
            "value"
        ] = 0

        threading.Thread(

            target=self._run_task,

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

    def _run_task(
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
                    "fptshop_products.csv"
                )

            self.log(
                "=== BẮT ĐẦU CÀO DỮ LIỆU ==="
            )

            self.log(
                "Giá bán và giá gốc "
                "được lấy từ dữ liệu trên web."
            )

            self.log(
                "Tien_Giam = giá bán thực tế sau giảm."
            )

            self.log(
                "Địa chỉ sử dụng 20 cửa hàng FPT Shop."
            )

            # =================================================
            # CRAWLER
            # =================================================

            crawler = FPTShopCrawler(

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
                            "width": 1280,
                            "height": 800
                        },

                        locale="vi-VN"
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
                        f"Đang cào danh mục: {cat}"
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

                # ==========================================
                # SỐ LƯỢNG
                # ==========================================

                so_luong = (
                    generate_quantity(
                        stt,
                        prod
                    )
                )

                # ==========================================
                # ĐỊA CHỈ
                # ==========================================

                (
                    tinh_thanh,
                    phuong_xa,
                    dia_chi_cu_the
                ) = get_fpt_address(
                    stt
                )

                # ==========================================
                # GIÁ GỐC
                # ==========================================

                val_don_gia = int(
                    prod.don_gia_goc
                )

                # ==========================================
                # % GIẢM
                # ==========================================

                val_ty_le_giam = int(
                    prod.ty_le_giam
                )

                # ==========================================
                # TIEN_GIAM
                #
                # CỰC KỲ QUAN TRỌNG:
                #
                # Đây là GIÁ BÁN THỰC TẾ trên web.
                #
                # Ví dụ:
                #
                # 3.390.000
                #       ↓
                #      15%
                #       ↓
                # 2.890.000
                #
                # Tien_Giam = 2.890.000
                # ==========================================

                val_tien_giam = int(
                    prod.gia_sau_giam
                )

                # ==========================================
                # TỔNG HÀNG
                #
                # GIÁ BÁN × SỐ LƯỢNG
                # ==========================================

                val_tong_hang = (

                    val_tien_giam
                    * so_luong
                )

                # ==========================================
                # TỔNG THANH TOÁN
                #
                # TỔNG HÀNG + 10%
                # ==========================================

                val_tong_thanh_toan = round(

                    val_tong_hang
                    * 1.1
                )

                # ==========================================
                # TẦN SUẤT MUA HÀNG
                # ==========================================

                tan_suat = (
                    generate_purchase_frequency(
                        stt,
                        prod
                    )
                )

                # ==========================================
                # TẠO ROW
                # ==========================================

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

                # ==========================================
                # PROGRESS
                # ==========================================

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

                # ==========================================
                # KIỂM TRA FILE BỊ KHÓA
                # ==========================================

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

                # ==========================================
                # TẠO THƯ MỤC
                # ==========================================

                folder = os.path.dirname(
                    os.path.abspath(
                        save_path
                    )
                )

                os.makedirs(
                    folder,
                    exist_ok=True
                )

                # ==========================================
                # GHI CSV
                # ==========================================

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

                # ==========================================
                # HOÀN TẤT
                # ==========================================

                self.log(
                    f"HOÀN TẤT! "
                    f"Đã xuất "
                    f"{len(final_rows)} dòng."
                )

                self.log(
                    f"File: {save_path}"
                )

                self.set_status(
                    f"Hoàn tất. "
                    f"Đã xuất "
                    f"{len(final_rows)} dòng."
                )

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
