class CompleteDataset:

    def build(
        self,
        fact_order,
        dim_hanh_chinh,
        dim_thegioididong,
        dim_fptshop,
        dim_cellphones,
        dim_ghn,
        dim_ghtk,
        dim_viettelpost,
        dim_jtexpress,
        dim_dangkykinhdoanh,
        synthetic_customer
    ):

        dataset = fact_order.copy()

        dataset = dataset.merge(
            dim_hanh_chinh,
            on="location_id",
            how="left"
        )

        dataset = dataset.merge(
            dim_thegioididong,
            on="tgdd_product_id",
            how="left",
            suffixes=("", "_tgdd")
        )

        dataset = dataset.merge(
            dim_fptshop,
            on="fpt_product_id",
            how="left",
            suffixes=("", "_fpt")
        )

        dataset = dataset.merge(
            dim_cellphones,
            on="cps_product_id",
            how="left",
            suffixes=("", "_cps")
        )

        dataset = dataset.merge(
            dim_ghn,
            on="ghn_id",
            how="left",
            suffixes=("", "_ghn")
        )

        dataset = dataset.merge(
            dim_ghtk,
            on="ghtk_id",
            how="left",
            suffixes=("", "_ghtk")
        )

        dataset = dataset.merge(
            dim_viettelpost,
            on="viettelpost_id",
            how="left",
            suffixes=("", "_viettelpost")
        )

        dataset = dataset.merge(
            dim_jtexpress,
            on="jtexpress_id",
            how="left",
            suffixes=("", "_jtexpress")
        )

        dataset = dataset.merge(
            dim_dangkykinhdoanh,
            on="business_source_id",
            how="left"
        )

        dataset = dataset.merge(
            synthetic_customer,
            on="customer_id",
            how="left"
        )

        return dataset
