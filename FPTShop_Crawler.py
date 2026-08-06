# -*- coding: utf-8 -*-
"""
FPTShop_Crawler.py
================
BẢN GỘP 1 FILE DUY NHẤT của project FPTShop_Crawler (gộp từ main.py, crawler.py,
generator.py, exporter.py) - giữ nguyên toàn bộ chức năng:

    - Cào dữ liệu sản phẩm thật từ FPT Shop (fptshop.com.vn) bằng Playwright
      (Điện thoại, Laptop, Máy tính bảng, Phụ kiện).
    - Sinh dữ liệu đơn hàng/khách hàng giả lập (synthetic) theo quy tắc
      nghiệp vụ hợp lý (không random tuỳ tiện) vì các thông tin này không
      tồn tại công khai trên website.
    - Xuất kết quả ra products.csv (24 cột theo yêu cầu).
    - Giao diện đồ hoạ Tkinter: chọn danh mục, Progress Bar, Log, bảng dữ
      liệu hiển thị theo thời gian thực, chạy trên Thread riêng để không
      treo giao diện.

Cách chạy:
    pip install -r requirements.txt
    playwright install chromium
    python FPTShop_Crawler.py

File được tổ chức thành 4 phần theo đúng thứ tự phụ thuộc:
    PHẦN 1 - CRAWLER   : cào dữ liệu sản phẩm (Playwright)
    PHẦN 2 - GENERATOR : sinh dữ liệu đơn hàng/khách hàng
    PHẦN 3 - EXPORTER  : xuất ra file CSV
    PHẦN 4 - MAIN (GUI): giao diện Tkinter + quản lý Thread + hàm main()
"""



# ============================================================================
# PHẦN 1 - CRAWLER: Cào dữ liệu sản phẩm thật từ FPT Shop (Playwright)
# ============================================================================

import re
import time
import unicodedata
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


# ---------------------------------------------------------------------------
# Cấu hình danh mục
# ---------------------------------------------------------------------------

CATEGORY_URLS = {
    "Điện thoại": "https://fptshop.com.vn/dien-thoai",
    "Laptop": "https://fptshop.com.vn/may-tinh-xach-tay",
    "Máy tính bảng": "https://fptshop.com.vn/may-tinh-bang",
    "Phụ kiện": "https://fptshop.com.vn/phu-kien",
}

# Danh sách selector CSS khả dĩ cho từng "ô sản phẩm" trên trang danh mục.
# Website có thể đổi class theo thời gian nên ta thử lần lượt. FPT Shop là
# ứng dụng SPA (Vue/Nuxt) nên tên class có thể thay đổi giữa các bản deploy;
# nếu không selector nào khớp, _extract_products_from_page sẽ tự động dùng
# phương án dự phòng "smart fallback" (xem hàm _js_fallback_find_product_cards).
PRODUCT_CARD_SELECTORS = [
    # Phát hiện qua DevTools thực tế trên fptshop.com.vn (7/2026): mỗi ô sản
    # phẩm là 1 thẻ <a> có thuộc tính title="Tên sản phẩm sạch" + href dẫn
    # tới trang chi tiết, class là chuỗi Tailwind sinh tự động (không ổn
    # định để bám vào). Do đó selector "a[title]" là lựa chọn ưu tiên hàng
    # đầu — vừa xác định đúng ô sản phẩm vừa cho tên sạch qua attribute,
    # không cần phải "dọn rác" từ text như các trang khác.
    "a[title][href]",
    "div.cdt-product",
    "a.cdt-product",
    "div[class*='cdt-product']",
    "div.product-item",
    "a.product-item",
    "div[class*='product-item']",
    "div[class*='ProductItem']",
    "li.product",
    "div.product",
]

# Selector cho nút "Xem thêm sản phẩm". "text=" là cú pháp selector đặc biệt
# của Playwright, cho phép tìm phần tử theo nội dung chữ hiển thị — hữu ích
# khi không biết trước tên class của nút trên FPT Shop.
LOAD_MORE_SELECTORS = [
    "a.view-more",
    "button.view-more",
    "div.view-more a",
    "button[class*='view-more']",
    "button[class*='load-more']",
    "text=Xem thêm",
]

# Danh sách thương hiệu phổ biến để suy luận "thuong_hieu" từ tên sản phẩm
# khi trang không có sẵn cột thương hiệu riêng biệt.
KNOWN_BRANDS = [
    "iPhone", "Apple", "MacBook", "iPad",
    "Samsung", "Xiaomi", "Redmi", "Poco",
    "Oppo", "Vivo", "Realme", "Nokia",
    "Asus", "Acer", "Dell", "HP", "Lenovo", "MSI", "LG",
    "Huawei", "Honor", "Masstel", "Itel", "Mobell", "Benco",
    "Anker", "Baseus", "JBL", "Sony", "Logitech", "Xperia",
]


@dataclass
class RawProduct:
    """Đại diện cho một sản phẩm cào được (dữ liệu thô, chưa sinh đơn hàng)."""
    ma_san_pham: str
    ten_san_pham: str
    don_gia: int
    danh_muc: str
    thuong_hieu: str
    url: str = ""


def _slugify_code(name: str, index: int, prefix: str) -> str:
    """Sinh mã sản phẩm ổn định (deterministic) từ tên sản phẩm, không random.

    Ví dụ: "iPhone 15 Pro Max 256GB" -> "DT-IPHONE15PROMAX256GB-014"
    Nếu 2 sản phẩm trùng tên (hiếm khi xảy ra) mã vẫn khác nhau nhờ index.
    """
    normalized = unicodedata.normalize("NFKD", name)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_name = re.sub(r"[^A-Za-z0-9]+", "", ascii_name).upper()
    ascii_name = ascii_name[:24] if ascii_name else "SP"
    return f"{prefix}-{ascii_name}-{index:04d}"


def _category_prefix(category: str) -> str:
    mapping = {
        "Điện thoại": "DT",
        "Laptop": "LT",
        "Máy tính bảng": "TB",
        "Phụ kiện": "PK",
    }
    return mapping.get(category, "SP")


def _guess_brand(product_name: str) -> str:
    """Suy luận thương hiệu từ tên sản phẩm bằng cách so khớp từ khóa.

    Đây KHÔNG phải là random: quy tắc cố định, nếu không khớp thương hiệu
    nào sẽ trả về "Khác" (Other) một cách nhất quán.
    """
    lower_name = product_name.lower()
    for brand in KNOWN_BRANDS:
        if brand.lower() in lower_name:
            # Chuẩn hoá một vài trường hợp đặc biệt
            if brand in ("iPhone", "MacBook", "iPad"):
                return "Apple"
            if brand == "Xperia":
                return "Sony"
            if brand in ("Redmi", "Poco"):
                return "Xiaomi"
            return brand
    return "Khác"


_BADGE_PHRASES = [
    "mẫu mới", "trả chậm", "trả góp 0%", "ngày siêu sale", "mã giảm",
    "hàng sắp về", "hàng có sẵn", "quà ", "online giá rẻ", "giá rẻ quá",
    "freeship", "km chính hãng", "sale sốc", "flash sale", "giảm thêm",
    "ưu đãi", "khuyến mãi", "giá tốt", "trả góp", "voucher",
    "giảm ", "cho đơn", "thanh toán qua", "ví trả sau", "zalopay", "momo",
    "kredivo", "tặng ", "km khác", "áp dụng", "mua kèm", "trả trước",
    "lãi suất", "kỳ hạn", "phụ phí", "còn 00 ngày", "đơn từ", "combo",
]

_SPEC_PREFIXES = [
    "ram ", "ssd ", "retina", "oled", "amoled", "qxga", "ips ", "lcd ",
    "fhd", "hd+", "wqhd", "chip ", "cpu ", "gpu ", "pin ", "camera sau",
    "camera trước", "màn hình", "độ phân giải", "super amoled",
]

_CURRENCY_RE = re.compile(r"^-?[\d\.,]+\s*(₫|đ|vnđ|vnd)$", re.IGNORECASE)
_PERCENT_RE = re.compile(r"^-?\d+(\.\d+)?%$")
_CAPACITY_RE = re.compile(r"^\d+\s*(gb|tb|mb)(\s*-\s*\d+\s*(gb|tb|mb))*$", re.IGNORECASE)
_UNIT_VALUE_RE = re.compile(r'^[\d\.,]+\s*(ghz|hz|mah|inch|mm|kg|g|"|cm)$', re.IGNORECASE)


def _clean_product_name(raw: str) -> str:
    """Làm sạch tên sản phẩm cào được.

    Trên trang danh mục, đôi khi ô sản phẩm chứa nhiều dòng text gộp chung
    (badge khuyến mãi, thông số kỹ thuật, giá...) thay vì chỉ riêng tên sản
    phẩm, ví dụ:
        "Mẫu mới\\n\\nSamsung Galaxy Z Fold8 Ultra 12GB/256GB\\n\\nQXGA+\\n\\n
         Hàng sắp về\\n\\n52.990.000₫"
    Hàm này tách theo từng dòng, loại bỏ các dòng là: giá tiền, phần trăm
    giảm giá, dung lượng bộ nhớ đơn lẻ, thông số kỹ thuật, badge/khuyến mãi
    đã biết — rồi chọn dòng còn lại dài nhất (thường là tên sản phẩm đầy đủ
    nhất) làm kết quả.
    """
    if not raw:
        return raw
    lines = [l.strip() for l in re.split(r"[\r\n]+", raw)]
    lines = [l for l in lines if l]

    candidates = []
    for line in lines:
        low = line.lower()
        if _CURRENCY_RE.match(line):
            continue
        if _PERCENT_RE.match(line):
            continue
        if _CAPACITY_RE.match(line):
            continue
        if _UNIT_VALUE_RE.match(line):
            continue
        if any(phrase in low for phrase in _BADGE_PHRASES):
            continue
        if any(low.startswith(prefix) for prefix in _SPEC_PREFIXES):
            continue
        candidates.append(line)

    if not candidates:
        candidates = lines
    if not candidates:
        return raw.strip()

    # Ưu tiên dòng có chứa một thương hiệu đã biết (vd "Laptop Acer...",
    # "iPhone...") vì tên sản phẩm thật hầu như luôn chứa thương hiệu, trong
    # khi các câu quảng cáo/khuyến mãi còn sót lại thường thì không.
    branded = [c for c in candidates if any(b.lower() in c.lower() for b in KNOWN_BRANDS)]
    pool = branded if branded else candidates

    best = max(pool, key=len)
    return re.sub(r"\s{2,}", " ", best).strip()


def _extract_lowest_standalone_price(text: str) -> int:
    """Quét toàn bộ text của 1 ô sản phẩm, tìm các DÒNG chỉ chứa giá tiền
    (không lẫn chữ khác, vd "13.590.000đ") và trả về giá trị NHỎ NHẤT.

    Lý do lấy giá nhỏ nhất: khi có khuyến mãi, trang luôn hiển thị giá gốc
    (gạch ngang, cao hơn) và giá sau giảm (thấp hơn) là 2 dòng đứng riêng;
    giá sau giảm mới là giá bán thực tế mà khách phải trả. Các dòng kiểu
    "Giảm 200.000đ" (số tiền được giảm) đã bị loại vì có thêm chữ "Giảm "
    nên không khớp regex "chỉ chứa giá tiền".
    """
    if not text:
        return 0
    prices = []
    for line in re.split(r"[\r\n]+", text):
        line = line.strip()
        if _CURRENCY_RE.match(line):
            value = _parse_price(line)
            if value > 0:
                prices.append(value)
    return min(prices) if prices else 0


def _parse_price(price_text: str) -> int:
    """Chuyển chuỗi giá tiếng Việt (vd '25.990.000₫', '25.990.000 đ') thành int.

    Nếu không parse được, trả về 0 để nơi gọi tự quyết định cách xử lý
    (ví dụ sinh giá theo quy tắc danh mục thay vì random vô lý).
    """
    if not price_text:
        return 0
    digits = re.sub(r"[^\d]", "", price_text)
    if not digits:
        return 0
    try:
        return int(digits)
    except ValueError:
        return 0


class FPTShopCrawler:
    """Bộ cào dữ liệu sản phẩm FPT Shop sử dụng Playwright (Chromium headless)."""

    def __init__(
        self,
        headless: bool = True,
        max_products_per_category: int = 40,
        load_more_clicks: int = 3,
        request_delay_seconds: float = 1.0,
        log_callback: Optional[Callable[[str], None]] = None,
        stop_flag: Optional[Callable[[], bool]] = None,
    ):
        """
        Args:
            headless: chạy trình duyệt ẩn (không hiện cửa sổ) hay không.
            max_products_per_category: giới hạn số sản phẩm cào mỗi danh mục
                để tránh cào quá nhiều và giảm tải cho server đích.
            load_more_clicks: số lần bấm nút "Xem thêm" trước khi dừng lại.
            request_delay_seconds: thời gian chờ (giây) giữa các thao tác để
                tránh gửi request dồn dập.
            log_callback: hàm nhận vào 1 chuỗi log, dùng để đẩy log lên GUI.
            stop_flag: hàm trả về True nếu người dùng yêu cầu dừng giữa chừng.
        """
        self.headless = headless
        self.max_products_per_category = max_products_per_category
        self.load_more_clicks = load_more_clicks
        self.request_delay_seconds = request_delay_seconds
        self.log_callback = log_callback or (lambda msg: None)
        self.stop_flag = stop_flag or (lambda: False)

    def _log(self, message: str) -> None:
        self.log_callback(message)

    def _should_stop(self) -> bool:
        try:
            return bool(self.stop_flag())
        except Exception:
            return False

    def crawl_categories(
        self,
        categories: List[str],
        on_product_found: Optional[Callable[[RawProduct], None]] = None,
        on_category_progress: Optional[Callable[[str, int, int], None]] = None,
    ) -> List[RawProduct]:
        """Cào toàn bộ danh sách danh mục được chọn.

        Args:
            categories: danh sách tên danh mục, vd ["Điện thoại", "Laptop"]
            on_product_found: callback gọi ngay khi 1 sản phẩm được cào xong,
                dùng để hiển thị dữ liệu theo thời gian thực lên GUI.
            on_category_progress: callback (category, current_index, total)
                để cập nhật thanh Progress Bar.

        Returns:
            Danh sách toàn bộ RawProduct cào được.
        """
        all_products: List[RawProduct] = []

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=self.headless)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                locale="vi-VN",
            )
            page = context.new_page()

            for category in categories:
                if self._should_stop():
                    self._log("Đã nhận lệnh dừng, ngừng cào dữ liệu.")
                    break

                url = CATEGORY_URLS.get(category)
                if not url:
                    self._log(f"[Bỏ qua] Không tìm thấy URL cho danh mục '{category}'.")
                    continue

                self._log(f"Đang mở danh mục '{category}' ({url}) ...")
                try:
                    page.goto(url, timeout=30000, wait_until="domcontentloaded")
                except PlaywrightTimeoutError:
                    self._log(f"[Lỗi] Timeout khi mở trang danh mục '{category}'.")
                    continue
                except Exception as exc:
                    self._log(f"[Lỗi] Không thể mở trang '{category}': {exc}")
                    continue

                time.sleep(self.request_delay_seconds)

                # Bấm "Xem thêm" một số lần để tải thêm sản phẩm
                for click_index in range(self.load_more_clicks):
                    if self._should_stop():
                        break
                    clicked = self._try_click_load_more(page)
                    if not clicked:
                        break
                    time.sleep(self.request_delay_seconds)

                products = self._extract_products_from_page(page, category)
                total = min(len(products), self.max_products_per_category)
                self._log(f"Tìm thấy {len(products)} sản phẩm trong '{category}', "
                           f"sẽ lấy {total} sản phẩm.")

                for index, raw in enumerate(products[:total], start=1):
                    if self._should_stop():
                        self._log("Đã nhận lệnh dừng, ngừng cào dữ liệu.")
                        break
                    all_products.append(raw)
                    if on_product_found:
                        on_product_found(raw)
                    if on_category_progress:
                        on_category_progress(category, index, total)
                    time.sleep(0.02)  # nhường CPU cho luồng GUI

            context.close()
            browser.close()

        self._log(f"Hoàn tất cào dữ liệu. Tổng số sản phẩm: {len(all_products)}.")
        return all_products

    # -- Các hàm nội bộ -----------------------------------------------------

    def _try_click_load_more(self, page) -> bool:
        for selector in LOAD_MORE_SELECTORS:
            try:
                locator = page.locator(selector)
                if locator.count() > 0 and locator.first.is_visible():
                    locator.first.click(timeout=3000)
                    self._log("  -> Đã bấm 'Xem thêm sản phẩm'.")
                    return True
            except Exception:
                continue
        return False

    def _extract_products_from_page(self, page, category: str) -> List[RawProduct]:
        cards = []
        for selector in PRODUCT_CARD_SELECTORS:
            try:
                locator = page.locator(selector)
                count = locator.count()
                if count > 0:
                    cards = [locator.nth(i) for i in range(count)]
                    self._log(f"  -> Dùng selector '{selector}', tìm thấy {count} thẻ sản phẩm.")
                    break
            except Exception:
                continue

        products: List[RawProduct] = []
        prefix = _category_prefix(category)

        if not cards:
            # Không selector CSS tĩnh nào khớp (thường do site là SPA và đổi
            # tên class giữa các bản deploy) -> dùng phương án dự phòng:
            # quét toàn bộ thẻ <a> có kèm theo giá tiền dạng "...đ"/"...₫".
            self._log("  -> Không khớp selector tĩnh nào, dùng smart fallback (quét theo mẫu giá tiền).")
            fallback_items = self._js_fallback_find_product_cards(page)
            for index, item in enumerate(fallback_items, start=1):
                raw_name = item.get("name", "")
                href = item.get("href", "")
                name = _clean_product_name(raw_name.strip())
                if not name:
                    continue
                # Ưu tiên quét toàn bộ text gốc (raw_name = innerText đầy đủ
                # của thẻ <a>) để tìm dòng giá thấp nhất (giá sau giảm);
                # nếu không tìm được dòng "chỉ chứa giá" nào, dùng price_text
                # đã bắt được từ regex trong JS làm phương án 2.
                price = _extract_lowest_standalone_price(raw_name)
                if price <= 0:
                    price = _parse_price(item.get("price_text", ""))
                if price <= 0:
                    price = self._fallback_price_by_category(category)
                brand = _guess_brand(name)
                code = _slugify_code(name, index, prefix)
                url = href if href.startswith("http") else (
                    f"https://fptshop.com.vn{href}" if href else ""
                )
                products.append(RawProduct(
                    ma_san_pham=code, ten_san_pham=name, don_gia=price,
                    danh_muc=category, thuong_hieu=brand, url=url,
                ))
            return products

        for index, card in enumerate(cards, start=1):
            try:
                # Ưu tiên #1: thuộc tính title trên chính thẻ <a> (đã xác
                # nhận qua DevTools là tên sản phẩm sạch, không lẫn badge/
                # giá). Nếu không có (card không phải <a> hoặc site đổi
                # cấu trúc), fallback về cách dò qua text như cũ.
                name = (card.get_attribute("title", timeout=1000) or "").strip()
                if not name:
                    name = self._extract_text(card, [
                        "h3", "h3 a", ".product-name", "h3.product-name",
                        "div[class*='product-name']", "a",
                    ])

                # href: nếu card chính là thẻ <a> thì lấy trực tiếp, nếu
                # không thì tìm thẻ <a> con như cũ.
                href = card.get_attribute("href", timeout=1000) or ""
                if not href:
                    href = self._extract_attr(card, "a", "href")

                if not name:
                    continue

                # Làm sạch tên sản phẩm: loại bỏ badge khuyến mãi, thông số
                # kỹ thuật, giá tiền lẫn vào cùng khối text (xem _clean_product_name)
                name = _clean_product_name(name.strip())
                if not name:
                    continue

                # Lấy giá: quét toàn bộ text trong card, tìm các dòng CHỈ
                # chứa giá tiền (vd "13.590.000đ"), rồi lấy giá trị NHỎ NHẤT
                # trong số đó — vì khi có khuyến mãi, trang luôn hiển thị
                # giá gốc (gạch ngang, cao hơn) và giá sau giảm (thấp hơn)
                # là 2 dòng riêng biệt; giá sau giảm mới là giá bán thực tế.
                try:
                    full_text = card.inner_text(timeout=1500)
                except Exception:
                    full_text = ""
                price = _extract_lowest_standalone_price(full_text)
                if price <= 0:
                    # Website không hiển thị giá rõ ràng (vd sản phẩm liên hệ).
                    # Sinh giá tham khảo theo quy tắc cố định dựa trên danh
                    # mục thay vì bỏ qua sản phẩm hoặc random vô căn cứ.
                    price = self._fallback_price_by_category(category)

                brand = _guess_brand(name)
                code = _slugify_code(name, index, prefix)
                url = href if href and href.startswith("http") else (
                    f"https://fptshop.com.vn{href}" if href else ""
                )

                products.append(RawProduct(
                    ma_san_pham=code,
                    ten_san_pham=name,
                    don_gia=price,
                    danh_muc=category,
                    thuong_hieu=brand,
                    url=url,
                ))
            except Exception as exc:
                self._log(f"  [Cảnh báo] Bỏ qua 1 thẻ sản phẩm lỗi: {exc}")
                continue

        return products

    @staticmethod
    def _extract_text(card, selectors: List[str]) -> str:
        for sel in selectors:
            try:
                locator = card.locator(sel)
                if locator.count() > 0:
                    text = locator.first.inner_text(timeout=1500).strip()
                    if text:
                        return text
            except Exception:
                continue
        return ""

    @staticmethod
    def _extract_attr(card, selector: str, attr: str) -> str:
        try:
            locator = card.locator(selector)
            if locator.count() > 0:
                value = locator.first.get_attribute(attr, timeout=1500)
                return value or ""
        except Exception:
            pass
        return ""

    @staticmethod
    def _js_fallback_find_product_cards(page) -> list:
        """Phương án dự phòng khi không selector CSS tĩnh nào khớp (thường
        gặp ở các trang SPA như FPT Shop, nơi tên class có thể đổi giữa các
        bản deploy).

        Ý tưởng: một "ô sản phẩm" trên trang danh mục luôn là 1 thẻ <a> có
        href dẫn tới trang chi tiết, và bên trong luôn chứa một chuỗi giá
        tiền dạng "12.990.000đ" hoặc "12.990.000₫". Ta quét toàn bộ thẻ <a>
        trên trang, giữ lại những thẻ thoả điều kiện trên, rồi coi dòng
        text đầu tiên (dài nhất) không phải giá tiền là tên sản phẩm — phần
        làm sạch chi tiết hơn được xử lý tiếp bởi _clean_product_name.
        """
        try:
            return page.evaluate(
                """
                () => {
                    const priceRe = /[\\d\\.]{4,}\\s*(đ|₫)/;
                    const anchors = Array.from(document.querySelectorAll('a[href]'));
                    const seen = new Set();
                    const results = [];
                    for (const a of anchors) {
                        const text = (a.innerText || '').trim();
                        if (!text) continue;
                        const match = text.match(priceRe);
                        if (!match) continue;
                        const href = a.getAttribute('href') || '';
                        if (!href || seen.has(href)) continue;
                        // Bỏ qua các thẻ quá ngắn (chỉ có giá, không có tên)
                        // hoặc quá dài (khả năng là khối chứa nhiều sản phẩm)
                        if (text.length < 8 || text.length > 400) continue;
                        seen.add(href);
                        results.push({ name: text, price_text: match[0], href: href });
                        if (results.length >= 200) break;
                    }
                    return results;
                }
                """
            ) or []
        except Exception:
            return []

    @staticmethod
    def _fallback_price_by_category(category: str) -> int:
        """Giá tham khảo hợp lý theo danh mục khi website không hiển thị giá.

        Đây là quy tắc cố định (không random), dựa trên mặt bằng giá trung
        bình phổ biến của từng danh mục sản phẩm tại thời điểm viết code.
        """
        base_price = {
            "Điện thoại": 5_990_000,
            "Laptop": 15_990_000,
            "Máy tính bảng": 6_990_000,
            "Phụ kiện": 490_000,
        }
        return base_price.get(category, 1_000_000)


# ============================================================================
# PHẦN 2 - GENERATOR: Sinh dữ liệu đơn hàng/khách hàng theo quy tắc hợp lý
# ============================================================================

import random
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Callable, Dict, List, Optional


# ---------------------------------------------------------------------------
# Danh mục dữ liệu tham chiếu (dùng để sinh dữ liệu hợp lý, có căn cứ)
# ---------------------------------------------------------------------------

# 63 tỉnh/thành Việt Nam (rút gọn danh sách phổ biến để tính toán vận chuyển,
# có thể mở rộng thêm nếu cần).
PROVINCES = [
    "TP. Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Hải Phòng", "Cần Thơ",
    "Bình Dương", "Đồng Nai", "Khánh Hoà", "An Giang", "Bà Rịa - Vũng Tàu",
    "Bắc Ninh", "Nghệ An", "Thanh Hoá", "Lâm Đồng", "Quảng Ninh",
    "Kiên Giang", "Long An", "Tiền Giang", "Huế", "Gia Lai",
]

# Tỉnh/thành lớn -> giao nhanh (1-2 ngày). Còn lại giao 3-5 ngày.
FAST_SHIPPING_PROVINCES = {"TP. Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Bình Dương", "Đồng Nai"}

# Đầu số điện thoại di động thực tế tại Việt Nam theo nhà mạng
MOBILE_PREFIXES = [
    "090", "091", "092", "093", "094", "095", "096", "097", "098", "099",
    "086", "088", "089", "081", "082", "083", "084", "085", "070", "076",
    "077", "078", "079", "056", "058", "059",
]

PAYMENT_METHODS = [
    "Tiền mặt khi nhận hàng (COD)",
    "Chuyển khoản ngân hàng",
    "Thẻ tín dụng/Ghi nợ",
    "Ví điện tử MoMo",
    "Ví điện tử ZaloPay",
    "Trả góp qua công ty tài chính",
]

SALES_CHANNELS = ["Website", "Ứng dụng di động", "Cửa hàng", "Hotline/Tổng đài"]

DELIVERY_UNITS = ["Giao hàng nội bộ FPT Shop", "Giao hàng nhanh (GHN)", "Viettel Post", "J&T Express"]

ORDER_STATUSES_FUTURE = ["Chờ xử lý", "Đang giao hàng"]
ORDER_STATUSES_PAST = ["Đã giao thành công", "Đã giao thành công", "Đã giao thành công", "Đã huỷ"]
# Lặp lại "Đã giao thành công" 3 lần để trọng số cao hơn "Đã huỷ" một cách
# có chủ đích (đơn hàng thực tế phần lớn giao thành công), không phải random
# đồng xác suất vô căn cứ.


@dataclass
class Customer:
    ma_khach_hang: str
    so_dien_thoai: str
    tinh_thanh: str
    so_lan_quay_lai: int = 0


@dataclass
class OrderRecord:
    """Một dòng dữ liệu hoàn chỉnh tương ứng với 1 sản phẩm trong 1 đơn hàng,
    đúng theo 24 cột yêu cầu của file products.csv."""
    Ma_Don: str
    Ngay_Dat: str
    Ma_Khach_Hang: str
    So_Dien_Thoai: str
    Tinh_Thanh: str
    Ma_San_Pham: str
    Ten_San_Pham: str
    Nhom_Hang: str
    So_Luong: int
    Don_Gia: int
    Ty_Le_Giam_Gia: str
    Tien_Giam: int
    Tong_Hang: int
    VAT_10: int
    Phi_Van_Chuyen: int
    Tong_Thanh_Toan: int
    Don_Vi_Giao: str
    Phuong_Thuc_Thanh_Toan: str
    Kenh_Ban: str
    Trang_Thai: str
    Ngay_Giao_Du_Kien: str
    So_Lan_Khach_Quay_Lai: int
    thuong_hieu: str
    danh_muc: str

    def as_dict(self) -> Dict:
        return self.__dict__


CSV_COLUMNS = [
    "Ma_Don", "Ngay_Dat", "Ma_Khach_Hang", "So_Dien_Thoai", "Tinh_Thanh",
    "Ma_San_Pham", "Ten_San_Pham", "Nhom_Hang", "So_Luong", "Don_Gia",
    "Ty_Le_Giam_Gia", "Tien_Giam", "Tong_Hang", "VAT_10", "Phi_Van_Chuyen",
    "Tong_Thanh_Toan", "Don_Vi_Giao", "Phuong_Thuc_Thanh_Toan", "Kenh_Ban",
    "Trang_Thai", "Ngay_Giao_Du_Kien", "So_Lan_Khach_Quay_Lai",
    "thuong_hieu", "danh_muc",
]


class OrderGenerator:
    """Sinh dữ liệu đơn hàng giả lập (synthetic) gắn với sản phẩm thật đã cào.

    Có thể tái lập kết quả (reproducible) nhờ tham số `seed`, tránh dữ liệu
    hỗn loạn giữa các lần chạy khi cần so sánh/kiểm thử.
    """

    def __init__(
        self,
        seed: int = 42,
        order_date_range_days: int = 90,
        repeat_customer_pool_size: int = 40,
        repeat_customer_probability: float = 0.45,
        log_callback: Optional[Callable[[str], None]] = None,
    ):
        self._rng = random.Random(seed)
        self.order_date_range_days = order_date_range_days
        self.repeat_customer_pool_size = repeat_customer_pool_size
        self.repeat_customer_probability = repeat_customer_probability
        self.log_callback = log_callback or (lambda msg: None)

        self._customers: List[Customer] = []
        self._order_sequence = 0
        self._today = date.today()

    def _log(self, message: str) -> None:
        self.log_callback(message)

    # -- Sinh khách hàng ------------------------------------------------

    def _new_customer(self) -> Customer:
        index = len(self._customers) + 1
        province = self._rng.choice(PROVINCES)
        prefix = self._rng.choice(MOBILE_PREFIXES)
        phone_suffix = "".join(str(self._rng.randint(0, 9)) for _ in range(7))
        customer = Customer(
            ma_khach_hang=f"KH{index:05d}",
            so_dien_thoai=f"{prefix}{phone_suffix}",
            tinh_thanh=province,
        )
        self._customers.append(customer)
        return customer

    def _pick_customer(self) -> Customer:
        """Chọn khách hàng cho 1 đơn hàng: có xác suất là khách quay lại
        (khách cũ trong "pool" khách trung thành), còn lại là khách mới.
        Việc này mô phỏng hành vi thực tế: một tỷ lệ nhất định khách hàng
        mua lặp lại nhiều lần."""
        have_enough_repeat_pool = len(self._customers) >= self.repeat_customer_pool_size
        if have_enough_repeat_pool and self._rng.random() < self.repeat_customer_probability:
            pool = self._customers[: self.repeat_customer_pool_size]
            customer = self._rng.choice(pool)
        else:
            customer = self._new_customer()
        customer.so_lan_quay_lai += 1
        return customer

    # -- Sinh từng đơn hàng ----------------------------------------------

    def _next_order_code(self, order_date: date) -> str:
        self._order_sequence += 1
        return f"DH{order_date.strftime('%Y%m%d')}-{self._order_sequence:05d}"

    def _random_order_date(self) -> date:
        days_ago = self._rng.randint(0, self.order_date_range_days)
        return self._today - timedelta(days=days_ago)

    def _discount_rate_for_category(self, category: str) -> float:
        """Tỷ lệ giảm giá hợp lý theo danh mục (quy tắc cố định theo nhóm
        hàng, có dao động nhẹ ngẫu nhiên trong biên độ hợp lý của nhóm đó
        thay vì random hoàn toàn tự do 0-100%)."""
        ranges = {
            "Điện thoại": (0.0, 0.10),
            "Laptop": (0.0, 0.08),
            "Máy tính bảng": (0.0, 0.10),
            "Phụ kiện": (0.05, 0.30),
        }
        low, high = ranges.get(category, (0.0, 0.10))
        return round(self._rng.uniform(low, high), 4)

    def _shipping_fee(self, province: str, tong_hang: int) -> int:
        """Phí vận chuyển: miễn phí cho đơn hàng lớn, còn lại theo khoảng
        cách địa lý ước lượng qua nhóm tỉnh/thành."""
        if tong_hang >= 5_000_000:
            return 0
        if province in FAST_SHIPPING_PROVINCES:
            return 20_000
        return 40_000

    # Phân phối số lượng mua hàng theo danh mục (quy tắc cố định, có trọng
    # số theo hành vi mua sắm thực tế — không phải xác suất đồng đều).
    # Điện thoại/laptop/tablet: phần lớn khách mua 1 cái cho cá nhân, nhưng
    # vẫn có tỷ lệ nhỏ khách mua sỉ/mua tặng nhiều cái. Phụ kiện giá rẻ nên
    # tỷ lệ mua nhiều cao hơn hẳn (mua theo lô, mua tặng kèm, mua dự phòng).
    _QUANTITY_WEIGHTS = {
        "Điện thoại": ([1, 2, 3, 5, 10], [72, 15, 7, 4, 2]),
        "Laptop": ([1, 2, 3, 5], [78, 13, 6, 3]),
        "Máy tính bảng": ([1, 2, 3, 5], [75, 15, 7, 3]),
        "Phụ kiện": ([1, 2, 3, 5, 10, 20], [28, 24, 18, 15, 10, 5]),
    }

    def _quantity_for_category(self, category: str) -> int:
        """Số lượng hợp lý theo danh mục, dùng phân phối trọng số cố định
        (xem _QUANTITY_WEIGHTS) để tránh tình trạng số lượng luôn là 1 —
        không thực tế — nhưng vẫn đảm bảo phần lớn đơn hàng cá nhân chỉ
        mua 1 sản phẩm, đúng với hành vi mua sắm thông thường."""
        values, weights = self._QUANTITY_WEIGHTS.get(category, ([1, 2], [85, 15]))
        return self._rng.choices(values, weights=weights, k=1)[0]

    def _delivery_days(self, province: str) -> int:
        if province in FAST_SHIPPING_PROVINCES:
            return self._rng.randint(1, 2)
        return self._rng.randint(3, 5)

    def _status_for_delivery(self, expected_delivery: date) -> str:
        if expected_delivery >= self._today:
            return self._rng.choice(ORDER_STATUSES_FUTURE)
        return self._rng.choice(ORDER_STATUSES_PAST)

    def generate_for_product(self, product: RawProduct) -> OrderRecord:
        """Sinh 1 đơn hàng (1 dòng CSV) cho một sản phẩm cào được."""
        order_date = self._random_order_date()
        customer = self._pick_customer()

        quantity = self._quantity_for_category(product.danh_muc)
        unit_price = product.don_gia
        discount_rate = self._discount_rate_for_category(product.danh_muc)

        goods_before_discount = unit_price * quantity
        discount_amount = int(round(goods_before_discount * discount_rate))
        tong_hang = goods_before_discount - discount_amount
        vat = int(round(tong_hang * 0.10))
        shipping_fee = self._shipping_fee(product.danh_muc, tong_hang)
        tong_thanh_toan = tong_hang + vat + shipping_fee

        delivery_days = self._delivery_days(customer.tinh_thanh)
        expected_delivery = order_date + timedelta(days=delivery_days)
        status = self._status_for_delivery(expected_delivery)

        record = OrderRecord(
            Ma_Don=self._next_order_code(order_date),
            Ngay_Dat=order_date.strftime("%d/%m/%Y"),
            Ma_Khach_Hang=customer.ma_khach_hang,
            So_Dien_Thoai=customer.so_dien_thoai,
            Tinh_Thanh=customer.tinh_thanh,
            Ma_San_Pham=product.ma_san_pham,
            Ten_San_Pham=product.ten_san_pham,
            Nhom_Hang=product.danh_muc,
            So_Luong=quantity,
            Don_Gia=unit_price,
            Ty_Le_Giam_Gia=f"{discount_rate * 100:.1f}%",
            Tien_Giam=discount_amount,
            Tong_Hang=tong_hang,
            VAT_10=vat,
            Phi_Van_Chuyen=shipping_fee,
            Tong_Thanh_Toan=tong_thanh_toan,
            Don_Vi_Giao=self._rng.choice(DELIVERY_UNITS),
            Phuong_Thuc_Thanh_Toan=self._rng.choice(PAYMENT_METHODS),
            Kenh_Ban=self._rng.choice(SALES_CHANNELS),
            Trang_Thai=status,
            Ngay_Giao_Du_Kien=expected_delivery.strftime("%d/%m/%Y"),
            So_Lan_Khach_Quay_Lai=customer.so_lan_quay_lai,
            thuong_hieu=product.thuong_hieu,
            danh_muc=product.danh_muc,
        )
        return record

    def generate_batch(self, products: List[RawProduct]) -> List[OrderRecord]:
        records = []
        for product in products:
            records.append(self.generate_for_product(product))
        self._log(f"Đã sinh {len(records)} dòng đơn hàng từ {len(products)} sản phẩm.")
        return records

    def generate_target(
        self,
        products: List[RawProduct],
        target_total: int,
        on_record: Optional[Callable[[OrderRecord], None]] = None,
        should_stop: Optional[Callable[[], bool]] = None,
    ) -> List[OrderRecord]:
        """Sinh đúng `target_total` dòng đơn hàng dựa trên danh sách sản
        phẩm thật đã cào được.

        Vì catalog thật của một website thương mại điện tử chỉ có giới hạn
        (vài trăm sản phẩm/danh mục), để đạt số dòng lớn (vd 10.000) ta cần
        SINH NHIỀU ĐƠN HÀNG LẶP LẠI cho mỗi sản phẩm — đúng với thực tế
        kinh doanh: một sản phẩm được nhiều khách khác nhau mua vào nhiều
        thời điểm khác nhau, chứ không phải "10.000 sản phẩm khác nhau".

        Quy tắc chia đều (không random tuỳ tiện):
            - Nếu target_total <= số sản phẩm: lấy lần lượt từng sản phẩm,
              mỗi sản phẩm 1 đơn hàng, cho tới khi đủ target_total.
            - Nếu target_total > số sản phẩm: mỗi sản phẩm được sinh
              `base = target_total // so_san_pham` đơn hàng, phần dư
              `target_total % so_san_pham` được rải thêm 1 đơn cho các sản
              phẩm đầu tiên, để tổng số dòng khớp CHÍNH XÁC target_total.
        """
        records: List[OrderRecord] = []
        num_products = len(products)
        if num_products == 0 or target_total <= 0:
            return records

        should_stop = should_stop or (lambda: False)

        if target_total <= num_products:
            selected = products[:target_total]
            for product in selected:
                if should_stop():
                    break
                record = self.generate_for_product(product)
                records.append(record)
                if on_record:
                    on_record(record)
            self._log(f"Đã sinh {len(records)} dòng đơn hàng (1 đơn/sản phẩm).")
            return records

        base_repeat = target_total // num_products
        remainder = target_total % num_products
        self._log(
            f"Tổng dòng mong muốn ({target_total}) lớn hơn số sản phẩm cào được "
            f"({num_products}) -> mỗi sản phẩm sẽ được sinh khoảng {base_repeat} "
            f"đơn hàng lặp lại (khác khách hàng/ngày đặt) để đạt đủ số dòng."
        )

        for index, product in enumerate(products):
            if should_stop():
                break
            repeat_count = base_repeat + (1 if index < remainder else 0)
            for _ in range(repeat_count):
                if should_stop():
                    break
                record = self.generate_for_product(product)
                records.append(record)
                if on_record:
                    on_record(record)

        self._log(f"Đã sinh {len(records)} dòng đơn hàng từ {num_products} sản phẩm thật.")
        return records


# ============================================================================
# PHẦN 3 - EXPORTER: Xuất dữ liệu ra file products.csv
# ============================================================================

import csv
import os
from typing import Dict, List, Optional


DEFAULT_OUTPUT_PATH = os.path.join(os.getcwd(), "products.csv")


class CSVExporter:
    """Ghi các OrderRecord ra file CSV theo chuẩn UTF-8 có BOM (utf-8-sig)
    để mở trực tiếp bằng Microsoft Excel không bị lỗi font tiếng Việt."""

    def __init__(self, output_path: str = DEFAULT_OUTPUT_PATH):
        self.output_path = output_path
        self._file = None
        self._writer = None
        self._is_open = False

    # -- Chế độ ghi theo luồng (streaming), phù hợp hiển thị real-time ------

    def open_for_streaming(self) -> None:
        """Mở file CSV và ghi sẵn dòng tiêu đề (header). Dùng khi muốn ghi
        từng dòng ngay khi 1 đơn hàng được sinh ra (real-time)."""
        self._file = open(self.output_path, mode="w", newline="", encoding="utf-8-sig")
        self._writer = csv.DictWriter(self._file, fieldnames=CSV_COLUMNS)
        self._writer.writeheader()
        self._is_open = True

    def write_record(self, record: OrderRecord) -> None:
        """Ghi 1 dòng dữ liệu. Phải gọi open_for_streaming() trước đó."""
        if not self._is_open:
            raise RuntimeError("Phải gọi open_for_streaming() trước khi write_record().")
        self._writer.writerow(record.as_dict())
        self._file.flush()  # đảm bảo dữ liệu được ghi ngay xuống đĩa

    def close(self) -> None:
        if self._is_open and self._file:
            self._file.close()
        self._is_open = False
        self._file = None
        self._writer = None

    # -- Chế độ ghi toàn bộ 1 lần --------------------------------------------

    def write_all(self, records: List[OrderRecord]) -> str:
        """Ghi toàn bộ danh sách bản ghi ra file CSV trong 1 lần gọi.
        Trả về đường dẫn file đã ghi."""
        with open(self.output_path, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for record in records:
                writer.writerow(record.as_dict())
        return self.output_path

    @staticmethod
    def read_all(path: str) -> List[Dict]:
        """Đọc lại file CSV đã xuất, trả về danh sách dict (hữu ích cho việc
        kiểm thử hoặc hiển thị lại dữ liệu trong GUI)."""
        rows: List[Dict] = []
        if not os.path.exists(path):
            return rows
        with open(path, mode="r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        return rows


# ============================================================================
# PHẦN 4 - MAIN (GUI): Giao diện Tkinter, quản lý Thread, Progress Bar, Log
# ============================================================================

import os
import queue
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk


APP_TITLE = "FPTShop Crawler - Cào & Xuất dữ liệu sản phẩm FPT Shop"
DEFAULT_CATEGORIES = list(CATEGORY_URLS.keys())

# Các cột hiển thị trong bảng real-time (rút gọn để vừa màn hình, file CSV
# vẫn xuất đầy đủ 24 cột theo generator.CSV_COLUMNS).
TABLE_DISPLAY_COLUMNS = [
    "Ma_Don", "Ten_San_Pham", "Nhom_Hang", "So_Luong", "Don_Gia",
    "Tong_Thanh_Toan", "Tinh_Thanh", "Trang_Thai", "thuong_hieu",
]


class QueueEvent:
    """Các loại sự kiện gửi từ worker thread lên GUI thread."""
    LOG = "LOG"
    PROGRESS = "PROGRESS"
    PROGRESS_RAW = "PROGRESS_RAW"
    NEW_RECORD = "NEW_RECORD"
    STAGE = "STAGE"
    FINISHED = "FINISHED"
    ERROR = "ERROR"


class FPTShopCrawlerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1180x760")
        self.root.minsize(980, 640)

        # Hàng đợi giao tiếp giữa worker thread và main thread
        self.event_queue: "queue.Queue" = queue.Queue()

        # Trạng thái điều khiển
        self.worker_thread: threading.Thread = None
        self._stop_requested = threading.Event()
        self._total_expected = 0
        self._total_done = 0

        self._build_widgets()
        self._poll_queue()

    # ------------------------------------------------------------------
    # Xây dựng giao diện
    # ------------------------------------------------------------------
    def _build_widgets(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        root_pad = ttk.Frame(self.root, padding=10)
        root_pad.pack(fill=tk.BOTH, expand=True)

        # ---- Khung cấu hình phía trên -----------------------------------
        config_frame = ttk.LabelFrame(root_pad, text="Cấu hình cào dữ liệu", padding=10)
        config_frame.pack(fill=tk.X, side=tk.TOP)

        # Danh mục
        cat_frame = ttk.Frame(config_frame)
        cat_frame.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))
        ttk.Label(cat_frame, text="Danh mục:").pack(side=tk.LEFT, padx=(0, 10))
        self.category_vars = {}
        for category in DEFAULT_CATEGORIES:
            var = tk.BooleanVar(value=True)
            self.category_vars[category] = var
            ttk.Checkbutton(cat_frame, text=category, variable=var).pack(side=tk.LEFT, padx=6)

        # Số sản phẩm tối đa / danh mục
        # Lưu ý: catalog thật của FPT Shop mỗi danh mục chỉ có khoảng vài trăm
        # sản phẩm (không phải hàng chục nghìn), nên để đạt số DÒNG ĐƠN HÀNG
        # lớn (vd 10.000) ta cần cào hết sản phẩm thật có thể lấy được rồi
        # SINH NHIỀU ĐƠN HÀNG LẶP LẠI cho mỗi sản phẩm (xem "Tổng số dòng
        # mong muốn" bên dưới) — giống thực tế 1 sản phẩm được nhiều khách
        # mua ở nhiều thời điểm khác nhau.
        ttk.Label(config_frame, text="Số SP tối đa / danh mục:").grid(row=1, column=0, sticky="w")
        self.max_products_var = tk.IntVar(value=50)
        ttk.Spinbox(config_frame, from_=5, to=3000, textvariable=self.max_products_var,
                    width=8).grid(row=1, column=1, sticky="w", padx=(4, 20))

        # Số lần bấm "Xem thêm"
        ttk.Label(config_frame, text="Số lần bấm 'Xem thêm':").grid(row=1, column=2, sticky="w")
        self.load_more_var = tk.IntVar(value=5)
        ttk.Spinbox(config_frame, from_=0, to=100, textvariable=self.load_more_var,
                    width=8).grid(row=1, column=3, sticky="w", padx=(4, 20))

        # Tổng số dòng đơn hàng mong muốn trong file CSV cuối cùng. Nếu số
        # này lớn hơn tổng số sản phẩm cào được, chương trình sẽ tự sinh
        # thêm nhiều đơn hàng lặp lại (khác khách hàng/ngày đặt) cho từng
        # sản phẩm để đạt đủ số dòng, thay vì chỉ sinh đúng 1 dòng/sản phẩm.
        ttk.Label(config_frame, text="Tổng số dòng mong muốn:").grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.target_rows_var = tk.IntVar(value=1000)
        ttk.Spinbox(config_frame, from_=1, to=1_000_000, increment=100,
                    textvariable=self.target_rows_var, width=10).grid(
            row=2, column=1, sticky="w", padx=(4, 20), pady=(8, 0))

        # Chế độ ẩn trình duyệt
        self.headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, text="Chạy ẩn trình duyệt (headless)",
                         variable=self.headless_var).grid(row=2, column=2, columnspan=2, sticky="w", pady=(8, 0))

        # Đường dẫn xuất file
        ttk.Label(config_frame, text="File xuất CSV:").grid(row=3, column=0, sticky="w", pady=(8, 0))
        self.output_path_var = tk.StringVar(
            value=os.path.join(os.getcwd(), "products.csv")
        )
        path_entry = ttk.Entry(config_frame, textvariable=self.output_path_var, width=60)
        path_entry.grid(row=3, column=1, columnspan=2, sticky="we", pady=(8, 0))
        ttk.Button(config_frame, text="Chọn...", command=self._choose_output_path).grid(
            row=3, column=3, sticky="w", padx=(6, 0), pady=(8, 0))

        note = ttk.Label(
            config_frame,
            foreground="#555555",
            text=("Ghi chú: mỗi danh mục FPT Shop thực tế chỉ có vài trăm sản phẩm. "
                  "Để đạt 'Tổng số dòng mong muốn' lớn, chương trình sẽ tự sinh "
                  "nhiều đơn hàng lặp lại hợp lý cho từng sản phẩm."),
            wraplength=900, justify="left",
        )
        note.grid(row=4, column=0, columnspan=4, sticky="w", pady=(6, 0))

        for col in range(4):
            config_frame.columnconfigure(col, weight=1)

        # ---- Khung nút điều khiển ---------------------------------------
        control_frame = ttk.Frame(root_pad, padding=(0, 10))
        control_frame.pack(fill=tk.X)

        self.start_button = ttk.Button(control_frame, text="▶ Bắt đầu cào dữ liệu",
                                        command=self._on_start_clicked)
        self.start_button.pack(side=tk.LEFT)

        self.stop_button = ttk.Button(control_frame, text="■ Dừng", command=self._on_stop_clicked,
                                       state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=8)

        self.status_label_var = tk.StringVar(value="Sẵn sàng.")
        ttk.Label(control_frame, textvariable=self.status_label_var).pack(side=tk.LEFT, padx=16)

        # ---- Progress bar --------------------------------------------------
        progress_frame = ttk.Frame(root_pad)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                             maximum=100, mode="determinate")
        self.progress_bar.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.progress_pct_var = tk.StringVar(value="0%")
        ttk.Label(progress_frame, textvariable=self.progress_pct_var, width=6).pack(side=tk.LEFT, padx=6)

        # ---- Khung chia đôi: Bảng dữ liệu real-time  |  Log -------------
        paned = ttk.Panedwindow(root_pad, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)

        table_frame = ttk.LabelFrame(paned, text="Dữ liệu đơn hàng (real-time)", padding=6)
        log_frame = ttk.LabelFrame(paned, text="Nhật ký xử lý (Log)", padding=6)
        paned.add(table_frame, weight=3)
        paned.add(log_frame, weight=2)

        self.tree = ttk.Treeview(table_frame, columns=TABLE_DISPLAY_COLUMNS, show="headings", height=14)
        for col in TABLE_DISPLAY_COLUMNS:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="w")
        self.tree.column("Ten_San_Pham", width=260)

        tree_scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscroll=tree_scroll_y.set, xscroll=tree_scroll_x.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        tree_scroll_x.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, height=10, wrap="word", state=tk.DISABLED,
                                 background="#111318", foreground="#d7f7d7", insertbackground="white")
        log_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscroll=log_scroll.set)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        log_scroll.grid(row=0, column=1, sticky="ns")
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

    # ------------------------------------------------------------------
    # Xử lý sự kiện nút bấm
    # ------------------------------------------------------------------
    def _choose_output_path(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Chọn nơi lưu file products.csv",
            defaultextension=".csv",
            initialfile="products.csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.output_path_var.set(path)

    def _on_start_clicked(self) -> None:
        selected_categories = [c for c, v in self.category_vars.items() if v.get()]
        if not selected_categories:
            messagebox.showwarning(APP_TITLE, "Vui lòng chọn ít nhất 1 danh mục.")
            return

        output_path = self.output_path_var.get().strip()
        if not output_path:
            messagebox.showwarning(APP_TITLE, "Vui lòng chọn đường dẫn file xuất CSV.")
            return

        # Reset giao diện cho lần chạy mới
        self._clear_table()
        self._clear_log()
        self.progress_var.set(0)
        self.progress_pct_var.set("0%")
        self._total_done = 0
        # Progress bar chia 2 giai đoạn: 0-50% là cào sản phẩm thật,
        # 50-100% là sinh dữ liệu đơn hàng cho đủ "Tổng số dòng mong muốn".
        self._total_expected = max(1, self.target_rows_var.get())
        self._stop_requested.clear()

        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        self.status_label_var.set("Đang chạy...")

        self.worker_thread = threading.Thread(
            target=self._worker_run,
            args=(selected_categories, output_path, self.max_products_var.get(),
                  self.load_more_var.get(), self.headless_var.get(),
                  self.target_rows_var.get()),
            daemon=True,
        )
        self.worker_thread.start()

    def _on_stop_clicked(self) -> None:
        self._stop_requested.set()
        self.status_label_var.set("Đang dừng, vui lòng đợi...")
        self.stop_button.configure(state=tk.DISABLED)

    # ------------------------------------------------------------------
    # Hàm chạy trên WORKER THREAD (không được đụng trực tiếp vào widget!)
    # ------------------------------------------------------------------
    def _worker_run(self, categories, output_path, max_products, load_more_clicks, headless,
                     target_rows) -> None:
        exporter = CSVExporter(output_path=output_path)
        try:
            self.event_queue.put((QueueEvent.STAGE, "Khởi động trình duyệt Playwright..."))
            self.event_queue.put((QueueEvent.LOG, f"[{self._now()}] Bắt đầu phiên làm việc mới."))
            self.event_queue.put((QueueEvent.LOG,
                                   f"[{self._now()}] Danh mục đã chọn: {', '.join(categories)}"))
            self.event_queue.put((QueueEvent.LOG,
                                   f"[{self._now()}] Tổng số dòng mong muốn: {target_rows}"))

            crawler = FPTShopCrawler(
                headless=headless,
                max_products_per_category=max_products,
                load_more_clicks=load_more_clicks,
                request_delay_seconds=0.8,
                log_callback=lambda msg: self.event_queue.put(
                    (QueueEvent.LOG, f"[{self._now()}] {msg}")),
                stop_flag=self._stop_requested.is_set,
            )

            generator = OrderGenerator(
                seed=42,
                log_callback=lambda msg: self.event_queue.put(
                    (QueueEvent.LOG, f"[{self._now()}] {msg}")),
            )

            # ---- GIAI ĐOẠN 1: cào toàn bộ sản phẩm thật (0% - 50%) ---------
            self.event_queue.put((QueueEvent.STAGE, "Đang cào sản phẩm thật từ FPT Shop..."))
            found_products: List[RawProduct] = []

            def on_product_found(product: RawProduct) -> None:
                found_products.append(product)

            def on_category_progress(category: str, current: int, total: int) -> None:
                # Giai đoạn cào chiếm nửa đầu thanh tiến độ
                pct = 0
                if target_rows > 0:
                    crawl_ratio = (current / total) if total > 0 else 0
                    pct = min(50, int(crawl_ratio * 50))
                self.event_queue.put((QueueEvent.PROGRESS_RAW, pct))
                self.event_queue.put((QueueEvent.STAGE,
                                       f"Đang cào '{category}': {current}/{total} sản phẩm"))

            crawler.crawl_categories(
                categories=categories,
                on_product_found=on_product_found,
                on_category_progress=on_category_progress,
            )

            self.event_queue.put((QueueEvent.LOG,
                                   f"[{self._now()}] Cào xong: {len(found_products)} sản phẩm thật."))

            # ---- GIAI ĐOẠN 2: sinh đủ target_rows dòng đơn hàng (50% - 100%) --
            processed_count = 0

            if found_products and not self._stop_requested.is_set():
                exporter.open_for_streaming()
                self.event_queue.put((QueueEvent.LOG, f"[{self._now()}] Đã mở file xuất: {output_path}"))
                self.event_queue.put((QueueEvent.STAGE, "Đang sinh dữ liệu đơn hàng..."))

                def on_record(record: OrderRecord) -> None:
                    nonlocal processed_count
                    exporter.write_record(record)
                    processed_count += 1
                    self.event_queue.put((QueueEvent.NEW_RECORD, record))
                    pct = 50 + min(50, int(processed_count / target_rows * 50))
                    self.event_queue.put((QueueEvent.PROGRESS_RAW, pct))

                generator.generate_target(
                    products=found_products,
                    target_total=target_rows,
                    on_record=on_record,
                    should_stop=self._stop_requested.is_set,
                )

                exporter.close()

            if self._stop_requested.is_set():
                self.event_queue.put((QueueEvent.LOG,
                                       f"[{self._now()}] Đã dừng theo yêu cầu người dùng. "
                                       f"Đã xuất {processed_count} dòng."))
            elif not found_products:
                self.event_queue.put((QueueEvent.LOG,
                                       f"[{self._now()}] Không cào được sản phẩm nào, "
                                       f"không có dữ liệu để xuất."))
            else:
                self.event_queue.put((QueueEvent.LOG,
                                       f"[{self._now()}] Hoàn tất! Đã xuất {processed_count} dòng "
                                       f"ra file: {output_path}"))

            self.event_queue.put((QueueEvent.FINISHED, (processed_count, output_path)))

        except Exception as exc:
            try:
                exporter.close()
            except Exception:
                pass
            self.event_queue.put((QueueEvent.ERROR, str(exc)))

    @staticmethod
    def _now() -> str:
        return datetime.now().strftime("%H:%M:%S")

    # ------------------------------------------------------------------
    # Vòng lặp đọc hàng đợi & cập nhật GUI (chạy trên MAIN THREAD)
    # ------------------------------------------------------------------
    def _poll_queue(self) -> None:
        try:
            while True:
                event_type, payload = self.event_queue.get_nowait()
                self._handle_event(event_type, payload)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._poll_queue)

    def _handle_event(self, event_type: str, payload) -> None:
        if event_type == QueueEvent.LOG:
            self._append_log(payload)

        elif event_type == QueueEvent.STAGE:
            self.status_label_var.set(payload)

        elif event_type == QueueEvent.PROGRESS_RAW:
            pct = max(0, min(100, int(payload)))
            self.progress_var.set(pct)
            self.progress_pct_var.set(f"{pct}%")

        elif event_type == QueueEvent.NEW_RECORD:
            self._append_row(payload)

        elif event_type == QueueEvent.FINISHED:
            processed_count, output_path = payload
            self.progress_var.set(100)
            self.progress_pct_var.set("100%")
            self.status_label_var.set(f"Hoàn tất. Đã xuất {processed_count} dòng.")
            self.start_button.configure(state=tk.NORMAL)
            self.stop_button.configure(state=tk.DISABLED)
            if processed_count > 0:
                messagebox.showinfo(
                    APP_TITLE,
                    f"Đã xuất thành công {processed_count} dòng dữ liệu ra:\n{output_path}",
                )

        elif event_type == QueueEvent.ERROR:
            self.status_label_var.set("Đã xảy ra lỗi.")
            self.start_button.configure(state=tk.NORMAL)
            self.stop_button.configure(state=tk.DISABLED)
            self._append_log(f"[LỖI] {payload}")
            messagebox.showerror(APP_TITLE, f"Đã xảy ra lỗi trong quá trình xử lý:\n{payload}")

    # ------------------------------------------------------------------
    # Các hàm hỗ trợ cập nhật widget (CHỈ được gọi từ main thread)
    # ------------------------------------------------------------------
    def _append_log(self, message: str) -> None:
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _append_row(self, record: OrderRecord) -> None:
        row_dict = record.as_dict()
        values = [row_dict.get(col, "") for col in TABLE_DISPLAY_COLUMNS]
        self.tree.insert("", tk.END, values=values)
        self.tree.see(self.tree.get_children()[-1])

    def _clear_table(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

    def _clear_log(self) -> None:
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)


def main() -> None:
    root = tk.Tk()
    app = FPTShopCrawlerApp(root)

    def on_close():
        if app.worker_thread and app.worker_thread.is_alive():
            if not messagebox.askyesno(APP_TITLE, "Đang cào dữ liệu. Bạn có chắc muốn thoát?"):
                return
            app._stop_requested.set()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
