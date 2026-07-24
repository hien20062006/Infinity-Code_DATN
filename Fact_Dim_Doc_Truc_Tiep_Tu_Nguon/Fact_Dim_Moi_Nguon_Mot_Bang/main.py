import random
import numpy as np

from config import RANDOM_SEED, N_ORDERS, N_CUSTOMERS, OUTPUT_FILE
from dim_hanh_chinh_vn import DimHanhChinhVN
from dim_thegioididong import DimTheGioiDiDong
from dim_fptshop import DimFPTShop
from dim_cellphones import DimCellphoneS
from dim_ghn import DimGHN
from dim_ghtk import DimGHTK
from dim_viettelpost import DimViettelPost
from dim_jtexpress import DimJTExpress
from dim_dangkykinhdoanh import DimDangKyKinhDoanh
from synthetic_customer import SyntheticCustomer
from synthetic_order import SyntheticOrder
from fact_order import FactOrder
from complete_dataset import CompleteDataset
from export_excel import ExportExcel


def build_source(name, builder):
    print(f"Đang đọc nguồn: {name}")
    try:
        dataframe = builder.build()
    except Exception as exc:
        raise RuntimeError(
            f"Không thể tạo {name} từ nguồn trực tuyến. Chi tiết: {exc}"
        ) from exc

    if dataframe.empty:
        raise RuntimeError(f"Nguồn {name} trả về bảng rỗng.")

    print(f"  -> Đã lấy {len(dataframe):,} dòng")
    return dataframe


def main():
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    dim_hanh_chinh = build_source("Dim_HanhChinhVN", DimHanhChinhVN())
    dim_thegioididong = build_source("Dim_TheGioiDiDong", DimTheGioiDiDong())
    dim_fptshop = build_source("Dim_FPTShop", DimFPTShop())
    dim_cellphones = build_source("Dim_CellphoneS", DimCellphoneS())
    dim_ghn = build_source("Dim_GHN", DimGHN())
    dim_ghtk = build_source("Dim_GHTK", DimGHTK())
    dim_viettelpost = build_source("Dim_ViettelPost", DimViettelPost())
    dim_jtexpress = build_source("Dim_JTExpress", DimJTExpress())
    dim_dangkykinhdoanh = build_source("Dim_DangKyKD", DimDangKyKinhDoanh())

    synthetic_customer = SyntheticCustomer().build(n_customers=N_CUSTOMERS)
    synthetic_order = SyntheticOrder().build(n_orders=N_ORDERS)

    fact_order = FactOrder(
        dim_hanh_chinh=dim_hanh_chinh,
        dim_thegioididong=dim_thegioididong,
        dim_fptshop=dim_fptshop,
        dim_cellphones=dim_cellphones,
        dim_ghn=dim_ghn,
        dim_ghtk=dim_ghtk,
        dim_viettelpost=dim_viettelpost,
        dim_jtexpress=dim_jtexpress,
        dim_dangkykinhdoanh=dim_dangkykinhdoanh,
        synthetic_customer=synthetic_customer,
        synthetic_order=synthetic_order
    ).build()

    complete_dataset = CompleteDataset().build(
        fact_order=fact_order,
        dim_hanh_chinh=dim_hanh_chinh,
        dim_thegioididong=dim_thegioididong,
        dim_fptshop=dim_fptshop,
        dim_cellphones=dim_cellphones,
        dim_ghn=dim_ghn,
        dim_ghtk=dim_ghtk,
        dim_viettelpost=dim_viettelpost,
        dim_jtexpress=dim_jtexpress,
        dim_dangkykinhdoanh=dim_dangkykinhdoanh,
        synthetic_customer=synthetic_customer
    )

    ExportExcel().export(
        dim_hanh_chinh=dim_hanh_chinh,
        dim_thegioididong=dim_thegioididong,
        dim_fptshop=dim_fptshop,
        dim_cellphones=dim_cellphones,
        dim_ghn=dim_ghn,
        dim_ghtk=dim_ghtk,
        dim_viettelpost=dim_viettelpost,
        dim_jtexpress=dim_jtexpress,
        dim_dangkykinhdoanh=dim_dangkykinhdoanh,
        synthetic_customer=synthetic_customer,
        synthetic_order=synthetic_order,
        fact_order=fact_order,
        complete_dataset=complete_dataset,
        output_path=OUTPUT_FILE
    )

    print(f"Đã tạo thành công file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
