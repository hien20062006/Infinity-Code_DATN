import pandas as pd
from config import SOURCES, MAX_PRODUCTS_PER_SOURCE
from web_utils import scrape_products


class DimTheGioiDiDong:

    def build(self):

        products = scrape_products(
            source_url=SOURCES["thegioididong"],
            id_prefix="TGDD",
            allowed_fragments=["dtdd", "dien-thoai", "laptop", "tai-nghe", "man-hinh"],
            max_products=MAX_PRODUCTS_PER_SOURCE
        )

        rows = []

        for product in products:

            rows.append([
                product["product_id"],
                product["product_name"],
                product["brand"],
                product["category"],
                product["unit_price"],
                product["product_url"],
                product["source_url"]
            ])

        return pd.DataFrame(
            rows,
            columns=[
                "tgdd_product_id",
                "product_name",
                "brand",
                "category",
                "unit_price",
                "product_url",
                "source_url"
            ]
        )
