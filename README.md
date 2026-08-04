# Đồ Án Tốt Nghiệp: Phân Tích Ngành Điện Tử Việt Nam
Chào mừng bạn đến với kho lưu trữ mã nguồn của dự án Phân tích ngành điện tử Việt Nam. Đây là đồ án tốt nghiệp thiết kế và xây dựng một quy trình ELT (Extract - Load - Transform) nhằm thu thập, tích hợp, làm sạch và chuẩn hóa dữ liệu về hoạt động xuất khẩu, nhập khẩu và sản xuất ngành điện tử Việt Nam, đồng thời xây dựng Kho dữ liệu (Data Warehouse) phục vụ phân tích dữ liệu và báo cáo quản trị thông minh (Business Intelligence).

# Cấu trúc dự án

```text
Du_An_Tot_Nghiep/
│
├── data/
│   ├── raw/          <- Dữ liệu gốc, không chỉnh sửa
│   ├── interim/      <- Dữ liệu trung gian đã qua xử lý
│   ├── processed/    <- Dữ liệu cuối cùng dùng để modeling
│   └── external/     <- Dữ liệu từ nguồn bên ngoài
│
├── notebooks/        <- Jupyter notebooks
├── models/           <- Model đã train
│
├── reports/
│   └── figures/      <- Biểu đồ, hình ảnh báo cáo
│
├── docs/             <- Tài liệu dự án
├── references/       <- Tài liệu tham khảo
│
├── du_an_tot_nghiep/
│   ├── config.py
│   ├── dataset.py
│   ├── features.py
│   ├── plots.py
│   │
│   └── modeling/
│       ├── train.py
│       └── predict.py
│
├── requirements.txt
└── pyproject.toml
```
