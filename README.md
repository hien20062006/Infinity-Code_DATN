# Đồ Án Tốt Nghiệp: Phân Tích Ngành Điện Tử Việt Nam
Chào mừng bạn đến với kho lưu trữ mã nguồn của dự án Phân tích Ngành Điện tử Việt Nam. Đây là đồ án tốt nghiệp thiết kế và xây dựng một quy trình ELT (Extract – Load – Transform) nhằm thu thập, tích hợp, làm sạch và chuẩn hóa dữ liệu về ngành điện tử Việt Nam, đồng thời xây dựng Kho dữ liệu (Data Warehouse) phục vụ phân tích dữ liệu và trực quan hóa bằng Tableau.
# Tổng Quan Dự Án
Dự án giải quyết bài toán xử lý dữ liệu ngành điện tử Việt Nam từ nhiều nguồn dữ liệu (CSV, Excel hoặc dữ liệu thống kê công khai), thực hiện kiểm soát chất lượng dữ liệu (Data Quality) thông qua các bộ quy tắc nghiệp vụ được cấu hình sẵn, tự động phát hiện và xử lý dữ liệu lỗi (Data Healing), sau đó nạp dữ liệu vào SQL Server Data Warehouse theo mô hình Star Schema.

Kho dữ liệu sau khi hoàn thiện được kết nối với Tableau Desktop để xây dựng Dashboard và Story trực quan, hỗ trợ phân tích xu hướng phát triển ngành điện tử Việt Nam, giúp doanh nghiệp và nhà quản lý dễ dàng khai thác dữ liệu phục vụ ra quyết định.
# Các Giai Đoạn & Tính Năng Cốt Lõi
Hệ thống được tổ chức theo quy trình ELT (Extract – Load – Transform).
```mermaid
flowchart TB

subgraph S1["📥 Data Sources"]
A1["CSV Files"]
A2["Excel Files"]
A3["Open Data / Statistics"]
end

subgraph S2["⚙️ ELT Pipeline"]
B1["Extract"]
B2["Data Validation"]
B3["Data Cleaning"]
B4["Data Transformation"]
end

subgraph S3["🗄️ Data Storage"]
C1["Staging Database"]
C2["Data Warehouse"]
C3["Star Schema"]
end

subgraph S4["📊 Analytics"]
D1["Tableau Dashboard"]
D2["Interactive Reports"]
D3["Business Insights"]
end

A1 --> B1
A2 --> B1
A3 --> B1

B1 --> B2
B2 --> B3
B3 --> B4

B4 --> C1
C1 --> C2
C2 --> C3

C3 --> D1
C3 --> D2
D1 --> D3
D2 --> D3
```
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
