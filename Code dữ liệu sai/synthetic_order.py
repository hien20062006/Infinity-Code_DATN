import random
import pandas as pd
from datetime import datetime
from datetime import timedelta


class SyntheticOrder:

    def build(self, n_orders=10000):

        start_date = datetime(2020, 1, 1)
        end_date = datetime(2025, 12, 31)

        total_days = (
            end_date - start_date
        ).days

        rows = []

        for i in range(1, n_orders + 1):

            order_date = (
                start_date
                +
                timedelta(
                    days=random.randint(
                        0,
                        total_days
                    )
                )
            ).date()

            rows.append([
                f"DH{order_date.year}{i:06d}",
                order_date,
                random.choice([
                    "Shopee",
                    "Lazada",
                    "TikTok Shop",
                    "Facebook",
                    "Website",
                    "Zalo"
                ]),
                random.choice([
                    "COD",
                    "Chuyển khoản",
                    "Ví điện tử",
                    "Thẻ ngân hàng"
                ]),
                random.choices(
                    [
                        "Đã giao",
                        "Đang giao",
                        "Đã hủy",
                        "Hoàn hàng"
                    ],
                    weights=[
                        0.78,
                        0.12,
                        0.05,
                        0.05
                    ]
                )[0],
                random.choice([
                    0,
                    0.05,
                    0.10,
                    0.15,
                    0.20
                ]),
                "Dữ liệu tự tạo"
            ])

        return pd.DataFrame(
            rows,
            columns=[
                "order_id",
                "order_date",
                "sales_channel",
                "payment_method",
                "order_status",
                "discount_rate",
                "data_origin"
            ]
        )
