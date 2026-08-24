# ============================================================
# PHONG VŨ CRAWLER
#
# CÀO SẢN PHẨM + TẠO DATASET ĐƠN HÀNG
#
# QUY TẮC GIÁ:
#
# Don_Gia       = GIÁ GỐC trên website
# Ty_Le_Giam    = % GIẢM trên website
# Tien_Giam     = GIÁ BÁN THỰC TẾ sau giảm trên website
# Tong_Hang     = Tien_Giam × So_Luong
# Tong_Thanh_Toan = Tong_Hang × 1.1
#
# LƯU Ý:
# - Không lấy giá theo vị trí cố định all_prices[0], all_prices[1]
# - Bỏ giá COMBO / TIẾT KIỆM / QUÀ TẶNG / TRẢ GÓP
# - Hỗ trợ cả cấu trúc giá ở trang danh mục
# - Hỗ trợ cả cấu trúc giá ở trang chi tiết
# - Không dùng dữ liệu ngẫu nhiên
# ============================================================

import csv
import os
import re
import threading

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from playwright.sync_api import sync_playwright


# ============================================================
# 1. CẤU HÌNH DANH MỤC PHONG VŨ
# ============================================================

CATEGORY_URLS = {

    "Điện thoại":
        "https://phongvu.vn/c/phone-dien-thoai",

    "Laptop":
        "https://phongvu.vn/c/laptop",

    "Máy tính bảng":
        "https://phongvu.vn/c/may-tinh-bang",

    "Phụ kiện":
        "https://phongvu.vn/c/phu-kien-chung",
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
# 3. 20 ĐỊA CHỈ PHONG VŨ
#
# Dùng để gán địa điểm cố định cho dataset đơn hàng.
# Không dùng để thể hiện thứ hạng doanh số.
# ============================================================

PHONGVU_ADDRESSES = [

    # TP. Hồ Chí Minh
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
    
        # Đồng Nai
        ("Đồng Nai", "P. Long Bình", "37 Bùi Văn Hòa, Khu phố 4 (Phong Vũ)"),
    
        # Tây Ninh
        ("Tây Ninh", "P. Tân Ninh", "969 Cách Mạng Tháng 8 (Phong Vũ)"),
        ("Tây Ninh", "P. Long An", "Số 2 Châu Văn Giác (Phong Vũ)"),
    
        # Đồng Tháp
        ("Đồng Tháp", "P. Cao Lãnh", "37–39 Lý Thường Kiệt (Phong Vũ)"),
        ("Đồng Tháp", "P. Trung An", "225 Ấp Bắc, Khu phố 3 (Phong Vũ)"),
    
        # Vĩnh Long
        ("Vĩnh Long", "P. Phú Tân", "207A6 Đại Lộ Đồng Khởi (Phong Vũ)"),
    
        # Cần Thơ
        ("Cần Thơ", "P. Tân An", "178 Đường 3 Tháng 2 (Phong Vũ)"),
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
# 6. ĐOÁN THƯƠNG HIỆU
# ============================================================

def _guess_brand(product_name: str) -> str:

    product_lower = product_name.lower()

    # Kiểm tra thương hiệu dài trước
    brands_sorted = sorted(
        KNOWN_BRANDS,
        key=len,
        reverse=True
    )

    for brand in brands_sorted:

        if brand.lower() in product_lower:

            if brand in (
                "iPhone",
                "MacBook",
                "iPad",
            ):
                return "Apple"

            if brand in (
                "Redmi",
                "Poco",
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

    cleaned = (
        price_text
        .replace("\xa0", " ")
        .replace(",", "")
        .replace(".", "")
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

def get_phongvu_address(index: int):

    if not PHONGVU_ADDRESSES:

        return "", "", ""

    position = (
        index - 1
    ) % len(PHONGVU_ADDRESSES)

    tinh, phuong_xa, dia_chi = (
        PHONGVU_ADDRESSES[position]
    )

    return (
        tinh,
        phuong_xa,
        dia_chi
    )


# ============================================================
# 10. TẠO SỐ LƯỢNG
#
# Giá trị được tạo theo quy tắc cố định dựa trên:
# - STT
# - tên sản phẩm
# - danh mục
#
# Không phụ thuộc thời điểm chạy chương trình.
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
# 12. PHONG VŨ CRAWLER
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

    def log(
        self,
        msg: str
    ):

        self.log_cb(msg)


    # ========================================================
    # AUTO SCROLL
    # ========================================================

    def _auto_scroll(
        self,
        page
    ):

        for _ in range(6):

            if self.stop_flag():

                break

            page.evaluate(
                """
                window.scrollBy(
                    0,
                    800
                );
                """
            )

            page.wait_for_timeout(
                700
            )


    # ========================================================
    # CLICK XEM THÊM
    # ========================================================

    def _click_load_more(
        self,
        page,
        category: str
    ):

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
                        document.body.scrollHeight - 600
                    );
                    """
                )

                page.wait_for_timeout(
                    1000
                )

                buttons = page.locator(
                    "button, a"
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
                            .lower()
                        )

                        if (
                            "xem thêm sản phẩm"
                            in text
                            or text == "xem thêm"
                            or "xem thêm" in text
                        ):

                            element.click(
                                timeout=3000
                            )

                            self.log(
                                f"[{category}] "
                                f"Nhấn Xem thêm "
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


    # ========================================================
    # LẤY PRODUCT CARD TỪ DOM
    #
    # Không lấy toàn bộ <a> như code cũ.
    #
    # Ưu tiên:
    # h2 / h3
    #     ↓
    # tìm ancestor có giá
    #     ↓
    # lấy text của card
    # ========================================================

    def _extract_product_cards(
        self,
        page
    ) -> List[Dict]:

        result = page.evaluate(
            """
            () => {

                const output = [];

                const pricePattern =
                    /\\d{1,3}(?:[.,]\\d{3})+(?:\\s*-\\s*\\d{1,3}(?:[.,]\\d{3})+)?\\s*(?:₫|đ|VNĐ)/i;

                const headings = Array.from(
                    document.querySelectorAll(
                        "h2, h3"
                    )
                );

                headings.forEach(
                    heading => {

                        const name = (
                            heading.innerText ||
                            heading.textContent ||
                            ""
                        ).trim();

                        if (!name) {
                            return;
                        }

                        if (name.length < 8) {
                            return;
                        }

                        let card = null;

                        let current =
                            heading;

                        // --------------------------------
                        // Tìm ancestor chứa giá
                        // --------------------------------

                        for (
                            let i = 0;
                            i < 8 && current;
                            i++
                        ) {

                            const text = (
                                current.innerText ||
                                current.textContent ||
                                ""
                            ).trim();

                            if (
                                text &&
                                pricePattern.test(text)
                            ) {

                                card = current;

                                break;
                            }

                            current =
                                current.parentElement;
                        }

                        if (!card) {
                            return;
                        }

                        const fullText = (
                            card.innerText ||
                            card.textContent ||
                            ""
                        ).trim();

                        if (!fullText) {
                            return;
                        }

                        if (
                            !pricePattern.test(
                                fullText
                            )
                        ) {
                            return;
                        }

                        // --------------------------------
                        // Tìm link sản phẩm
                        // --------------------------------

                        let productLink = "";

                        const directLink =
                            heading.closest(
                                "a[href]"
                            );

                        if (directLink) {

                            productLink =
                                directLink.href;
                        }

                        if (!productLink) {

                            const links =
                                Array.from(
                                    card.querySelectorAll(
                                        "a[href]"
                                    )
                                );

                            for (
                                const link
                                of links
                            ) {

                                const href =
                                    link.href || "";

                                const linkText = (
                                    link.innerText ||
                                    link.textContent ||
                                    ""
                                ).trim();

                                if (
                                    href &&
                                    linkText &&
                                    linkText.length >= 8
                                ) {

                                    productLink =
                                        href;

                                    break;
                                }
                            }
                        }

                        output.push({

                            name: name,

                            full_text:
                                fullText,

                            href:
                                productLink,
                        });
                    }
                );

                return output;
            }
            """
        )

        return result or []


    # ========================================================
    # LẤY TOKEN GIÁ
    #
    # Ví dụ:
    #
    # 10.790.000 ₫
    #
    # 8.990.000 ₫
    #
    # 43.990.000 - 44.990.000 ₫
    #
    # Không lấy các số không có đơn vị tiền.
    # ========================================================

    def _extract_price_tokens(
        self,
        text: str
    ) -> List[Dict]:

        if not text:

            return []

        pattern = re.compile(
            r"(?<!\d)"
            r"(\d{1,3}(?:[.,]\d{3})+)"
            r"(?:\s*-\s*(\d{1,3}(?:[.,]\d{3})+))?"
            r"\s*(?:₫|đ|VNĐ)"
            r"(?!\w)",
            re.IGNORECASE
        )

        tokens = []

        for match in pattern.finditer(text):

            first_price = _parse_price(
                match.group(1)
            )

            second_price = None

            if match.group(2):

                second_price = _parse_price(
                    match.group(2)
                )

            if first_price < 1000:

                continue

            # --------------------------------------------
            # Lấy dòng chứa giá
            # --------------------------------------------

            line_start = (
                text.rfind(
                    "\n",
                    0,
                    match.start()
                ) + 1
            )

            line_end = text.find(
                "\n",
                match.end()
            )

            if line_end == -1:

                line_end = len(text)

            line_text = (
                text[
                    line_start:line_end
                ]
                .strip()
            )

            tokens.append({

                "value":
                    first_price,

                "range_second":
                    second_price,

                "start":
                    match.start(),

                "end":
                    match.end(),

                "line":
                    line_text,
            })

        return tokens


    # ========================================================
    # KIỂM TRA GIÁ KHÔNG PHẢI GIÁ SẢN PHẨM
    # ========================================================

    def _is_excluded_price_line(
        self,
        line: str
    ) -> bool:

        if not line:

            return True

        lower = (
            line
            .lower()
            .replace(
                "\xa0",
                " "
            )
        )

        excluded_words = [

            "quà tặng",

            "voucher",

            "combo giảm",

            "tiết kiệm",

            "trả góp",

            "mỗi tháng",

            "/tháng",

            "coupon",

            "mã giảm",

            "giảm thêm",

            "nhận được",

        ]

        for word in excluded_words:

            if word in lower:

                return True

        return False


    # ========================================================
    # LẤY % GIẢM
    # ========================================================

    def _extract_discount(
        self,
        text: str
    ) -> Tuple[int, Optional[int]]:

        if not text:

            return 0, None

        patterns = [

            r"[-−]\s*(\d{1,2}(?:[.,]\d+)?)\s*%",

            r"giảm\s*(\d{1,2}(?:[.,]\d+)?)\s*%",

            r"(\d{1,2}(?:[.,]\d+)?)\s*%",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            if not match:

                continue

            try:

                value = float(
                    match.group(1)
                    .replace(",", ".")
                )

                if 0 <= value <= 100:

                    return (
                        int(round(value)),
                        match.start()
                    )

            except ValueError:

                continue

        return 0, None


    # ========================================================
    # LẤY GIÁ SẢN PHẨM
    #
    # HỖ TRỢ 2 DẠNG:
    #
    # DẠNG 1 - TRANG CHI TIẾT:
    #
    # 10.790.000 ₫ -17%
    # 8.990.000 ₫
    #
    # => old = 10.790.000
    # => new = 8.990.000
    #
    #
    # DẠNG 2 - TRANG DANH MỤC:
    #
    # 8.990.000 ₫
    # 10.790.000 ₫
    # -17%
    #
    # => new = 8.990.000
    # => old = 10.790.000
    # ========================================================

    def _extract_product_prices(
        self,
        text: str
    ) -> Optional[Tuple[int, int, int]]:

        if not text:

            return None

        tokens = (
            self._extract_price_tokens(
                text
            )
        )

        # --------------------------------------------
        # Chỉ giữ giá thuộc dòng sản phẩm
        # --------------------------------------------

        valid_tokens = [

            token

            for token in tokens

            if not self._is_excluded_price_line(
                token["line"]
            )
        ]

        if not valid_tokens:

            return None

        # --------------------------------------------
        # Lấy % giảm
        # --------------------------------------------

        discount, discount_pos = (
            self._extract_discount(
                text
            )
        )

        # ====================================================
        # CÓ % GIẢM
        # ====================================================

        if (
            discount > 0
            and discount_pos is not None
        ):

            before = [

                token

                for token
                in valid_tokens

                if token["end"]
                <= discount_pos
            ]

            after = [

                token

                for token
                in valid_tokens

                if token["start"]
                >= discount_pos
            ]

            # ------------------------------------------------
            # TRƯỜNG HỢP TRANG CHI TIẾT
            #
            # 10.790.000 -17%
            # 8.990.000
            #
            # Có 1 giá trước %
            # Có 1 giá sau %
            # ------------------------------------------------

            if before and after:

                old_price = (
                    before[-1]["value"]
                )

                new_price = (
                    after[0]["value"]
                )

                if (
                    old_price > 0
                    and new_price > 0
                ):

                    if (
                        old_price
                        >= new_price
                    ):

                        return (
                            old_price,
                            new_price,
                            discount
                        )

            # ------------------------------------------------
            # TRƯỜNG HỢP TRANG DANH MỤC
            #
            # 8.990.000
            # 10.790.000
            # -17%
            #
            # Có ít nhất 2 giá trước %
            # ------------------------------------------------

            if len(before) >= 2:

                new_price = (
                    before[-2]["value"]
                )

                old_price = (
                    before[-1]["value"]
                )

                if (
                    old_price >= new_price
                    and new_price > 0
                ):

                    return (
                        old_price,
                        new_price,
                        discount
                    )

            # ------------------------------------------------
            # Trường hợp % nằm trước giá
            #
            # -17%
            # 8.990.000
            #
            # Nếu có giá sau nhưng không có giá gốc
            # thì không tự tạo giá gốc.
            # ------------------------------------------------

            if after:

                new_price = (
                    after[0]["value"]
                )

                # Nếu có giá trước đó trong card
                # thì dùng giá gần nhất làm giá gốc.
                if before:

                    old_price = (
                        before[-1]["value"]
                    )

                    if (
                        old_price
                        >= new_price
                    ):

                        return (
                            old_price,
                            new_price,
                            discount
                        )

                # Không đủ dữ liệu giá gốc
                # => coi giá hiện tại là giá gốc
                # nhưng vẫn giữ % website.
                return (
                    new_price,
                    new_price,
                    discount
                )

        # ====================================================
        # KHÔNG CÓ % GIẢM
        # ====================================================

        if len(valid_tokens) == 1:

            price = (
                valid_tokens[0]["value"]
            )

            return (
                price,
                price,
                0
            )

        # ----------------------------------------------------
        # Có nhiều giá nhưng không có %
        #
        # Dùng cặp giá gần cuối.
        # ----------------------------------------------------

        first = valid_tokens[-2]
        second = valid_tokens[-1]

        price_a = first["value"]
        price_b = second["value"]

        if (
            price_a > 0
            and price_b > 0
            and price_b > price_a
        ):

            calculated_discount = round(

                (
                    (
                        price_b
                        - price_a
                    )
                    / price_b
                )
                * 100
            )

            return (
                price_b,
                price_a,
                calculated_discount
            )

        # ----------------------------------------------------
        # Nếu không xác định được cặp giá
        # lấy giá cuối cùng làm giá hiện tại.
        # ----------------------------------------------------

        price = (
            valid_tokens[-1]["value"]
        )

        return (
            price,
            price,
            0
        )


    # ========================================================
    # LẤY SKU
    # ========================================================

    def _extract_sku(
        self,
        text: str
    ) -> str:

        if not text:

            return ""

        patterns = [

            r"SKU\s*:\s*([A-Za-z0-9_-]+)",

            r"SKU\s+([A-Za-z0-9_-]+)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            if match:

                return (
                    match.group(1)
                    .strip()
                )

        return ""


    # ========================================================
    # LẤY TÊN SẢN PHẨM
    # ========================================================

    def _clean_product_name(
        self,
        name: str
    ) -> str:

        if not name:

            return ""

        name = re.sub(
            r"\s+",
            " ",
            name
        ).strip()

        return name


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
            f"Mở danh mục: "
            f"{category}"
        )

        self.log(
            f"URL: {url}"
        )

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
            3500
        )

        # --------------------------------------------
        # Cuộn trang
        # --------------------------------------------

        self._auto_scroll(
            page
        )

        # --------------------------------------------
        # Xem thêm
        # --------------------------------------------

        self._click_load_more(
            page,
            category
        )

        # --------------------------------------------
        # Lấy card
        # --------------------------------------------

        raw_items = (
            self._extract_product_cards(
                page
            )
        )

        self.log(
            f"[{category}] "
            f"Tìm thấy {len(raw_items)} card."
        )

        products = []

        seen_names = set()

        idx = 1

        # ====================================================
        # XỬ LÝ CARD
        # ====================================================

        for item in raw_items:

            if self.stop_flag():

                break

            if (
                len(products)
                >= self.max_products_per_cat
            ):

                break

            name = self._clean_product_name(

                item.get(
                    "name",
                    ""
                )
            )

            full_text = (
                item.get(
                    "full_text",
                    ""
                )
                .strip()
            )

            if not name:

                continue

            # --------------------------------------------
            # Loại các heading không phải sản phẩm
            # --------------------------------------------

            name_lower = (
                name.lower()
            )

            bad_names = [

                "sản phẩm điện thoại nổi bật",

                "sản phẩm laptop nổi bật",

                "sản phẩm phụ kiện nổi bật",

                "sản phẩm máy tính bảng nổi bật",

                "sắp xếp theo",

                "xem thêm sản phẩm",
            ]

            if any(
                bad in name_lower
                for bad in bad_names
            ):

                continue

            # --------------------------------------------
            # Chống trùng tên
            # --------------------------------------------

            name_key = re.sub(
                r"\s+",
                " ",
                name.lower()
            )

            if name_key in seen_names:

                continue

            # --------------------------------------------
            # Lấy giá
            # --------------------------------------------

            price_data = (
                self._extract_product_prices(
                    full_text
                )
            )

            if not price_data:

                self.log(
                    f"[BỎ] Không xác định được "
                    f"giá: {name[:70]}"
                )

                continue

            (
                don_gia_goc,
                gia_sau_giam,
                ty_le_giam
            ) = price_data

            # --------------------------------------------
            # Kiểm tra giá
            # --------------------------------------------

            if don_gia_goc <= 0:

                continue

            if gia_sau_giam <= 0:

                continue

            if (
                gia_sau_giam
                > don_gia_goc
            ):

                self.log(
                    f"[BỎ] Giá bán > giá gốc: "
                    f"{name[:60]}"
                )

                continue

            # --------------------------------------------
            # SKU nếu có
            # --------------------------------------------

            sku = (
                self._extract_sku(
                    full_text
                )
            )

            if not sku:

                sku = (
                    f"SP{idx:04d}"
                )

            # --------------------------------------------
            # Thương hiệu
            # --------------------------------------------

            brand = _guess_brand(
                name
            )

            # --------------------------------------------
            # Tạo product
            # --------------------------------------------

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

            self.log(
                f"[OK] {product.ten_san_pham[:60]}"
            )

            self.log(
                f"     Giá gốc: "
                f"{format_currency(product.don_gia_goc)}"
            )

            self.log(
                f"     Giảm: "
                f"{product.ty_le_giam}%"
            )

            self.log(
                f"     Giá bán: "
                f"{format_currency(product.gia_sau_giam)}"
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
            "Phong Vũ Crawler - Xuất dữ liệu CSV chuẩn"
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
            "phongvu_products.csv"
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

                width = 300

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
    # PROGRESS
    # ========================================================

    def set_progress(
        self,
        value: float
    ):

        self.after(
            0,
            lambda:
                self.progress_bar.configure(
                    value=value
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

        self.txt_log.delete(
            "1.0",
            tk.END
        )

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

            self.set_status(
                "Đang dừng..."
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
                    "phongvu_products.csv"
                )

            # =================================================
            # BẮT ĐẦU
            # =================================================

            self.log(
                "================================================"
            )

            self.log(
                "BẮT ĐẦU CÀO DỮ LIỆU PHONG VŨ"
            )

            self.log(
                "================================================"
            )

            self.log(
                "Thuật toán giá mới:"
            )

            self.log(
                "Don_Gia = giá gốc"
            )

            self.log(
                "Ty_Le_Giam_Gia = % giảm trên website"
            )

            self.log(
                "Tien_Giam = giá bán thực tế"
            )

            self.log(
                "Tong_Hang = giá bán × số lượng"
            )

            self.log(
                "Tong_Thanh_Toan = Tổng hàng × 1.1"
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

                total_categories = len(
                    categories
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

                    progress = (

                        (
                            (idx + 1)
                            / total_categories
                        )
                        * 50
                    )

                    self.set_progress(
                        progress
                    )

                browser.close()

            # =================================================
            # KIỂM TRA
            # =================================================

            if not all_raw_products:

                self.log(
                    "[LỖI] Không cào được sản phẩm nào!"
                )

                self.set_status(
                    "Không có dữ liệu."
                )

                return

            self.log(
                f"Tổng sản phẩm thu thập được: "
                f"{len(all_raw_products)}"
            )

            self.log(
                "Bắt đầu tạo dữ liệu đơn hàng..."
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
                ) = get_phongvu_address(
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
                # GIÁ BÁN THỰC TẾ
                # ==========================================

                val_tien_giam = int(
                    prod.gia_sau_giam
                )

                # ==========================================
                # TỔNG HÀNG
                # ==========================================

                val_tong_hang = (

                    val_tien_giam
                    * so_luong
                )

                # ==========================================
                # TỔNG THANH TOÁN
                # ==========================================

                val_tong_thanh_toan = round(

                    val_tong_hang
                    * 1.1
                )

                # ==========================================
                # TẦN SUẤT
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

                progress = (

                    50

                    + (

                        (
                            len(final_rows)
                            / target_rows
                        )
                        * 50
                    )
                )

                self.set_progress(
                    progress
                )

            # =================================================
            # NẾU DỪNG
            # =================================================

            if self.stop_requested:

                self.log(
                    "Quá trình đã được dừng."
                )

                self.set_status(
                    "Đã dừng."
                )

            # =================================================
            # XUẤT CSV
            # =================================================

            if final_rows:

                save_path = csv_path

                # =============================================
                # KIỂM TRA FILE BỊ KHÓA
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
                        "Đổi tên file xuất thành: "
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
                    f"Đã xuất {len(final_rows)} dòng."
                )

                self.log(
                    f"File: {save_path}"
                )

                self.log(
                    "================================================"
                )

                self.set_progress(
                    100
                )

                self.set_status(
                    f"Hoàn tất. "
                    f"Đã xuất {len(final_rows)} dòng."
                )

                if not self.stop_requested:

                    self.after(

                        0,

                        lambda path=save_path,
                        count=len(final_rows):

                            messagebox.showinfo(

                                "Thành công",

                                "Đã xuất thành công "
                                f"{count} dòng "
                                "ra file:\n"
                                f"{path}"
                            )
                    )

        except Exception as exc:

            error_text = str(exc)

            self.log(
                f"[LỖI XỬ LÝ] {error_text}"
            )

            self.set_status(
                "Có lỗi xảy ra."
            )

            self.after(

                0,

                lambda text=error_text:

                    messagebox.showerror(

                        "Lỗi",

                        "Quá trình xử lý gặp lỗi:\n"
                        f"{text}"
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