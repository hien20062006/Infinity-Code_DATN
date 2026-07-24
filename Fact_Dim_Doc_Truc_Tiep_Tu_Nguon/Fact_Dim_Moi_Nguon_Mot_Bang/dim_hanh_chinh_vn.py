import pandas as pd
import requests
from config import SOURCES
from web_utils import DEFAULT_HEADERS


class DimHanhChinhVN:

    def build(self):

        url = SOURCES["hanh_chinh_vn"]

        response = requests.get(
            url,
            headers=DEFAULT_HEADERS,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list) or not data:
            raise RuntimeError(
                "API hành chính không trả về danh sách tỉnh/thành hợp lệ."
            )

        rows = []

        for location_id, province in enumerate(data, start=1):

            rows.append([
                location_id,
                province.get("code"),
                province.get("name") or province.get("full_name"),
                province.get("division_type"),
                province.get("codename"),
                province.get("phone_code"),
                url
            ])

        return pd.DataFrame(
            rows,
            columns=[
                "location_id",
                "province_code",
                "province_name",
                "division_type",
                "codename",
                "phone_code",
                "source_url"
            ]
        )
