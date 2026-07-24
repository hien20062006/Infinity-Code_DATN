import pandas as pd


class ExportExcel:

    def export(
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
        synthetic_order,
        fact_order,
        complete_dataset,
        output_path
    ):

        with pd.ExcelWriter(
            output_path,
            engine="openpyxl"
        ) as writer:

            dim_hanh_chinh.to_excel(writer, sheet_name="Dim_HanhChinhVN", index=False)
            dim_thegioididong.to_excel(writer, sheet_name="Dim_TheGioiDiDong", index=False)
            dim_fptshop.to_excel(writer, sheet_name="Dim_FPTShop", index=False)
            dim_cellphones.to_excel(writer, sheet_name="Dim_CellphoneS", index=False)
            dim_ghn.to_excel(writer, sheet_name="Dim_GHN", index=False)
            dim_ghtk.to_excel(writer, sheet_name="Dim_GHTK", index=False)
            dim_viettelpost.to_excel(writer, sheet_name="Dim_ViettelPost", index=False)
            dim_jtexpress.to_excel(writer, sheet_name="Dim_JTExpress", index=False)
            dim_dangkykinhdoanh.to_excel(writer, sheet_name="Dim_DangKyKD", index=False)

            synthetic_customer.to_excel(writer, sheet_name="DuLieu_TuTao_KH", index=False)
            synthetic_order.to_excel(writer, sheet_name="DuLieu_TuTao_DH", index=False)

            fact_order.to_excel(writer, sheet_name="Fact_Order", index=False)
            complete_dataset.to_excel(writer, sheet_name="DuLieu_HoanChinh", index=False)
