import pandas as pd
from config import SOURCES
from web_utils import scrape_site_profile


class DimGHN:

    def build(self):

        profile = scrape_site_profile(
            source_url=SOURCES["ghn"],
            source_id="GHN001",
            source_name="Giao Hàng Nhanh"
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
                "ghn_id",
                "carrier_name",
                "page_title",
                "service_description",
                "min_delivery_days",
                "max_delivery_days",
                "source_url"
            ]
        )
