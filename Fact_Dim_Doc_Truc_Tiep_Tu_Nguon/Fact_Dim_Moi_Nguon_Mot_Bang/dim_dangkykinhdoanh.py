import pandas as pd
from config import SOURCES
from web_utils import scrape_site_profile


class DimDangKyKinhDoanh:

    def build(self):

        profile = scrape_site_profile(
            source_url=SOURCES["dangkykinhdoanh"],
            source_id="DKKD001",
            source_name="Cổng thông tin quốc gia về đăng ký doanh nghiệp"
        )

        rows = [[
            profile["source_id"],
            profile["source_name"],
            profile["page_title"],
            profile["description"],
            profile["source_url"]
        ]]

        return pd.DataFrame(
            rows,
            columns=[
                "business_source_id",
                "source_name",
                "page_title",
                "description",
                "source_url"
            ]
        )
