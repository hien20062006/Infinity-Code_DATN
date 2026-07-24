import pandas as pd
from config import SOURCES
from web_utils import scrape_site_profile


class DimGHTK:

    def build(self):

        profile = scrape_site_profile(
            source_url=SOURCES["ghtk"],
            source_id="GHTK001",
            source_name="Giao Hàng Tiết Kiệm"
        )

        rows = [[
            profile["source_id"],
            profile["source_name"],
            profile["page_title"],
            profile["description"],
            profile["min_delivery_days"],
            profile["max_delivery_days"],
            profile["source_url"]
        ]]

        return pd.DataFrame(
            rows,
            columns=[
                "ghtk_id",
                "carrier_name",
                "page_title",
                "service_description",
                "min_delivery_days",
                "max_delivery_days",
                "source_url"
            ]
        )
