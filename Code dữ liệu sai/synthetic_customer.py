import random
import string
import pandas as pd


class SyntheticCustomer:

    def build(self, n_customers=1200):

        last_names = [
            "Nguyễn", "Trần", "Lê", "Phạm",
            "Hoàng", "Huỳnh", "Võ", "Đặng"
        ]

        middle_names = [
            "Văn", "Thị", "Minh", "Gia",
            "Bảo", "Đức", "Thanh", "Ngọc"
        ]

        first_names = [
            "An", "Bình", "Châu", "Dũng",
            "Giang", "Hạnh", "Khang", "Linh",
            "Minh", "Nam", "Phúc", "Trang"
        ]

        rows = []

        for i in range(1, n_customers + 1):

            customer_name = (
                f"{random.choice(last_names)} "
                f"{random.choice(middle_names)} "
                f"{random.choice(first_names)}"
            )

            phone_number = (
                random.choice([
                    "090", "091", "093",
                    "096", "097", "098"
                ])
                +
                "".join(
                    random.choices(
                        string.digits,
                        k=7
                    )
                )
            )

            rows.append([
                f"KH{i:05d}",
                customer_name,
                random.choice(["Anh", "Chị"]),
                phone_number,
                random.randint(0, 15),
                "Dữ liệu tự tạo"
            ])

        return pd.DataFrame(
            rows,
            columns=[
                "customer_id",
                "customer_name",
                "title",
                "phone_number",
                "return_count",
                "data_origin"
            ]
        )
