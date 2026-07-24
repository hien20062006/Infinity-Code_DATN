import json
import re
import warnings
from urllib.parse import urljoin, urlparse

import certifi
import requests
import urllib3
from bs4 import BeautifulSoup


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/150.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
}


def fetch_soup(url, timeout=30):
    try:
        # Dùng bundle chứng chỉ mới nhất từ certifi thay vì mặc định của hệ điều hành.
        response = requests.get(
            url,
            headers=DEFAULT_HEADERS,
            timeout=timeout,
            verify=certifi.where(),
        )
    except requests.exceptions.SSLError:
        # Fallback: một số máy (do antivirus/firewall chặn/inject SSL) vẫn không xác
        # thực được dù đã dùng certifi. Bỏ qua xác thực SSL để không chặn việc scrape,
        # kèm cảnh báo rõ ràng cho người dùng biết đang chạy ở chế độ không an toàn.
        warnings.warn(
            f"Không xác thực được chứng chỉ SSL cho {url}. "
            "Đang thử lại với verify=False (không an toàn, chỉ nên dùng khi phát triển/test).",
            RuntimeWarning,
        )
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(
            url,
            headers=DEFAULT_HEADERS,
            timeout=timeout,
            verify=False,
        )
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser"), response.url


def clean_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def parse_price(value):
    if value is None:
        return None
    text = clean_text(value)
    digits = re.sub(r"[^0-9]", "", text)
    if not digits:
        return None
    number = int(digits)
    # Tránh nhận nhầm mã sản phẩm hoặc số quá nhỏ thành giá.
    return number if number >= 10000 else None


def iter_json_objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_json_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_json_objects(child)


def extract_jsonld_products(soup, base_url):
    products = []
    for script in soup.select('script[type="application/ld+json"]'):
        raw = script.string or script.get_text(" ", strip=True)
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            continue

        for obj in iter_json_objects(data):
            obj_type = obj.get("@type")
            types = obj_type if isinstance(obj_type, list) else [obj_type]
            if "Product" not in types:
                continue

            offers = obj.get("offers") or {}
            if isinstance(offers, list):
                offers = offers[0] if offers else {}

            brand = obj.get("brand") or ""
            if isinstance(brand, dict):
                brand = brand.get("name") or ""

            product = {
                "product_name": clean_text(obj.get("name")),
                "brand": clean_text(brand),
                "category": clean_text(obj.get("category")),
                "unit_price": parse_price(
                    offers.get("price")
                    or offers.get("lowPrice")
                    or obj.get("price")
                ),
                "product_url": urljoin(
                    base_url,
                    obj.get("url") or offers.get("url") or ""
                ),
            }
            if product["product_name"]:
                products.append(product)
    return products


def extract_product_links(soup, base_url, allowed_fragments=None, limit=30):
    links = []
    seen = set()
    host = urlparse(base_url).netloc

    for anchor in soup.select("a[href]"):
        href = urljoin(base_url, anchor.get("href"))
        parsed = urlparse(href)
        if parsed.netloc != host:
            continue
        if allowed_fragments and not any(fragment in parsed.path.lower() for fragment in allowed_fragments):
            continue

        name = clean_text(
            anchor.get("title")
            or anchor.get("aria-label")
            or anchor.get_text(" ", strip=True)
        )
        if len(name) < 5 or href in seen:
            continue
        seen.add(href)
        links.append((name, href))
        if len(links) >= limit:
            break
    return links


def scrape_products(source_url, id_prefix, allowed_fragments=None, max_products=20):
    soup, final_url = fetch_soup(source_url)
    products = extract_jsonld_products(soup, final_url)

    # Nếu trang danh mục không có Product JSON-LD, đọc liên kết sản phẩm và mở trang chi tiết.
    if not products:
        for anchor_name, product_url in extract_product_links(
            soup,
            final_url,
            allowed_fragments=allowed_fragments,
            limit=max_products * 2,
        ):
            try:
                detail_soup, detail_url = fetch_soup(product_url, timeout=20)
                detail_products = extract_jsonld_products(detail_soup, detail_url)
                if detail_products:
                    products.extend(detail_products)
                else:
                    # Chỉ nhận giá thật xuất hiện trong meta/itemprop; không tự đặt giá.
                    price_node = (
                        detail_soup.select_one('[itemprop="price"]')
                        or detail_soup.select_one('meta[property="product:price:amount"]')
                    )
                    price = None
                    if price_node:
                        price = parse_price(price_node.get("content") or price_node.get_text(" "))
                    if price:
                        title = clean_text(
                            (detail_soup.select_one("h1") or detail_soup.title).get_text(" ", strip=True)
                        )
                        products.append({
                            "product_name": title or anchor_name,
                            "brand": "",
                            "category": "",
                            "unit_price": price,
                            "product_url": detail_url,
                        })
            except requests.RequestException:
                continue
            if len(products) >= max_products:
                break

    cleaned = []
    seen = set()
    for product in products:
        key = (product["product_name"].lower(), product.get("unit_price"))
        if key in seen or not product.get("unit_price"):
            continue
        seen.add(key)
        cleaned.append({
            "product_id": f"{id_prefix}{len(cleaned) + 1:04d}",
            **product,
            "source_url": source_url,
        })
        if len(cleaned) >= max_products:
            break

    if not cleaned:
        raise RuntimeError(
            f"Không đọc được sản phẩm có giá từ {source_url}. "
            "Website có thể đã đổi cấu trúc hoặc chặn yêu cầu tự động."
        )
    return cleaned


def scrape_site_profile(source_url, source_id, source_name):
    soup, final_url = fetch_soup(source_url)
    title = clean_text(soup.title.get_text(" ", strip=True) if soup.title else source_name)
    description_node = soup.select_one('meta[name="description"]') or soup.select_one('meta[property="og:description"]')
    description = clean_text(description_node.get("content") if description_node else "")
    page_text = clean_text(soup.get_text(" ", strip=True))

    day_ranges = re.findall(r"(\d+)\s*[-–]\s*(\d+)\s*ngày", page_text, flags=re.IGNORECASE)
    min_days = int(day_ranges[0][0]) if day_ranges else None
    max_days = int(day_ranges[0][1]) if day_ranges else None

    return {
        "source_id": source_id,
        "source_name": source_name,
        "page_title": title,
        "description": description,
        "min_delivery_days": min_days,
        "max_delivery_days": max_days,
        "source_url": final_url,
    }