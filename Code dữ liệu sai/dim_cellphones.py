import pandas as pd
from config import SOURCES, MAX_PRODUCTS_PER_SOURCE
from web_utils import scrape_products


class DimCellphoneS:

    def build(self):

        products = scrape_products(
            source_url=SOURCES["cellphones"],
            id_prefix="CPS",
            allowed_fragments=["mobile", "dien-thoai", "laptop", "phu-kien", "linh-kien", "man-hinh"],
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
                "cps_product_id",
                "product_name",
                "brand",
                "category",
                "unit_price",
                "product_url",
                "source_url"
            ]
        )
