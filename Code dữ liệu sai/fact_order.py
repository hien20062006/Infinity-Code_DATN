import random
import pandas as pd


class FactOrder:

    def __init__(
        self,
        dim_hanh_chinh,
        dim_thegioididong,
        dim_fptshop,
        dim_cellphones,
        dim_ghn,
        dim_ghtk,
        dim_viettelpost,
        dim_jtexpress,
        dim_dangkykinhdoanh,
        synthetic_customer,
        synthetic_order
    ):

        self.dim_hanh_chinh = dim_hanh_chinh
        self.dim_thegioididong = dim_thegioididong
        self.dim_fptshop = dim_fptshop
        self.dim_cellphones = dim_cellphones
        self.dim_ghn = dim_ghn
        self.dim_ghtk = dim_ghtk
        self.dim_viettelpost = dim_viettelpost
        self.dim_jtexpress = dim_jtexpress
        self.dim_dangkykinhdoanh = dim_dangkykinhdoanh
        self.synthetic_customer = synthetic_customer
        self.synthetic_order = synthetic_order

    def build(self):

        rows = []

        for _, order in self.synthetic_order.iterrows():

            location = self.dim_hanh_chinh.iloc[random.randrange(len(self.dim_hanh_chinh))]
            customer = self.synthetic_customer.iloc[random.randrange(len(self.synthetic_customer))]
            business = self.dim_dangkykinhdoanh.iloc[random.randrange(len(self.dim_dangkykinhdoanh))]

            product_source = random.choice([
                "THEGIOIDIDONG",
                "FPTSHOP",
                "CELLPHONES"
            ])

            tgdd_product_id = None
            fpt_product_id = None
            cps_product_id = None

            if product_source == "THEGIOIDIDONG":

                product = self.dim_thegioididong.iloc[random.randrange(len(self.dim_thegioididong))]
                tgdd_product_id = product["tgdd_product_id"]

            elif product_source == "FPTSHOP":

                product = self.dim_fptshop.iloc[random.randrange(len(self.dim_fptshop))]
                fpt_product_id = product["fpt_product_id"]

            else:

                product = self.dim_cellphones.iloc[random.randrange(len(self.dim_cellphones))]
                cps_product_id = product["cps_product_id"]

            carrier_source = random.choice([
                "GHN",
                "GHTK",
                "VIETTELPOST",
                "JTEXPRESS"
            ])

            ghn_id = None
            ghtk_id = None
            viettelpost_id = None
            jtexpress_id = None

            if carrier_source == "GHN":

                carrier = self.dim_ghn.iloc[0]
                ghn_id = carrier["ghn_id"]

            elif carrier_source == "GHTK":

                carrier = self.dim_ghtk.iloc[0]
                ghtk_id = carrier["ghtk_id"]

            elif carrier_source == "VIETTELPOST":

                carrier = self.dim_viettelpost.iloc[0]
                viettelpost_id = carrier["viettelpost_id"]

            else:

                carrier = self.dim_jtexpress.iloc[0]
                jtexpress_id = carrier["jtexpress_id"]

            quantity = random.randint(1, 5)
            unit_price = int(product["unit_price"])
            gross_value = quantity * unit_price

            discount_rate = float(order["discount_rate"])
            discount_amount = int(
                round(
                    gross_value
                    *
                    discount_rate
                    /
                    1000
                )
                *
                1000
            )

            net_goods_value = (
                gross_value
                -
                discount_amount
            )

            vat_10 = int(
                round(
                    net_goods_value
                    *
                    0.10
                    /
                    1000
                )
                *
                1000
            )

            delivery_days = random.randint(
                int(carrier["min_delivery_days"] or 1),
                int(carrier["max_delivery_days"] or 5)
            )

            shipping_fee = (
                15000
                +
                delivery_days
                *
                5000
            )

            total_payment = (
                net_goods_value
                +
                vat_10
                +
                shipping_fee
            )

            rows.append([
                order["order_id"],
                order["order_date"],
                location["location_id"],
                tgdd_product_id,
                fpt_product_id,
                cps_product_id,
                ghn_id,
                ghtk_id,
                viettelpost_id,
                jtexpress_id,
                business["business_source_id"],
                customer["customer_id"],
                product_source,
                carrier_source,
                order["sales_channel"],
                order["payment_method"],
                order["order_status"],
                quantity,
                unit_price,
                discount_rate,
                discount_amount,
                gross_value,
                net_goods_value,
                vat_10,
                shipping_fee,
                total_payment
            ])

        return pd.DataFrame(
            rows,
            columns=[
                "order_id",
                "order_date",
                "location_id",
                "tgdd_product_id",
                "fpt_product_id",
                "cps_product_id",
                "ghn_id",
                "ghtk_id",
                "viettelpost_id",
                "jtexpress_id",
                "business_source_id",
                "customer_id",
                "product_source",
                "carrier_source",
                "sales_channel",
                "payment_method",
                "order_status",
                "quantity",
                "unit_price",
                "discount_rate",
                "discount_amount",
                "gross_value",
                "net_goods_value",
                "vat_10",
                "shipping_fee",
                "total_payment"
            ]
        )