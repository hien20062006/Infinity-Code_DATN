# Infinity Code-DATN

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
