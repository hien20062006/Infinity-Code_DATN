# 📊 PHÂN TÍCH HÀNG HÓA ĐIỆN TỬ VIỆT NAM

> **Đồ án tốt nghiệp – Xử lý và phân tích dữ liệu**

## 1. 📌 Tổng quan dự án

Dự án **Phân tích hàng hóa điện tử Việt Nam** được xây dựng nhằm thu thập, xử lý, tích hợp và phân tích dữ liệu liên quan đến thị trường hàng điện tử tại Việt Nam.

Hệ thống kết hợp nhiều nguồn dữ liệu khác nhau để xây dựng một mô hình dữ liệu tập trung, từ đó hỗ trợ:

* Phân tích tình hình xuất nhập khẩu hàng điện tử.
* Phân tích doanh thu và hành vi mua hàng.
* Phân tích sản phẩm, thương hiệu và danh mục.
* Phân tích xu hướng thị trường điện thoại.
* Đánh giá mức tăng trưởng theo năm.
* Phân tích **YoY – Year-over-Year**.
* Xác định các nhóm hàng, thương hiệu và thị trường có biến động nổi bật.
* Xây dựng Dashboard trực quan trên **Tableau**.

---

# 2. 🎯 Mục tiêu dự án

### Mục tiêu tổng quát

Xây dựng một hệ thống phân tích dữ liệu giúp chuyển đổi dữ liệu thô thành thông tin có giá trị phục vụ việc đánh giá và theo dõi thị trường hàng điện tử Việt Nam.

### Mục tiêu cụ thể

1. Thu thập và tổng hợp dữ liệu từ nhiều nguồn.
2. Làm sạch và chuẩn hóa dữ liệu.
3. Xử lý dữ liệu thiếu, sai kiểu dữ liệu và không đồng nhất.
4. Thiết kế mô hình dữ liệu theo **Star Schema**.
5. Xây dựng Fact Table và Dimension Table.
6. Tính toán các chỉ số kinh doanh.
7. Phân tích tăng trưởng **YoY**.
8. Xác định các phát hiện chính từ dữ liệu.
9. Xây dựng Dashboard trực quan bằng Tableau.
10. Hỗ trợ người dùng theo dõi xu hướng và đưa ra quyết định dựa trên dữ liệu.

---

# 3. 📂 Dataset

Dự án hiện sử dụng 3 nguồn dữ liệu chính.

## 3.1. Dataset xuất nhập khẩu

**File:** `Data_XNK_goc_hoan_chinh_csv.csv`

| Thuộc tính   |          Giá trị |
| ------------ | ---------------: |
| Số dòng      |            3,125 |
| Số cột       |               14 |
| Giai đoạn    |        2015–2025 |
| Loại dữ liệu |   Xuất nhập khẩu |
| Đối tượng    | Hàng hóa điện tử |

### Một số trường dữ liệu

* `Nam_bao_cao`
* `Tuan_bao_cao`
* `Loai_luong_(XNK)`
* `Ten_nuoc_doi_tac`
* `Mo_hang_hoa`
* `Don_vi_so_luong`
* `So_luong`
* `Trong_luong_tinh_kg`
* `Gia_tri_CIF_(USD)`
* `Gia_tri_FOB_(USD)`
* `Gia_tri_chinh_(USD)`

Dataset này được sử dụng để phân tích:

* Kim ngạch xuất khẩu.
* Kim ngạch nhập khẩu.
* Đối tác thương mại.
* Nhóm hàng hóa.
* Xu hướng xuất nhập khẩu theo năm.
* Tăng trưởng YoY.

---

# 4. 🛒 Dataset bán hàng điện tử

**File:** `Dien_tu_goc_da_thay_doi_csv.csv`

| Thuộc tính     | Giá trị |
| -------------- | ------: |
| Số dòng        |  10,000 |
| Số cột         |      16 |
| Nhóm hàng      | Điện tử |
| Số danh mục    |      12 |
| Số thương hiệu |      12 |

### Một số trường dữ liệu

* `Tinh_Thanh`
* `Phuong_Xa`
* `Dia_Chi_Cu_The`
* `Ma_San_Pham`
* `Ten_San_Pham`
* `Nhom_Hang`
* `So_Luong`
* `Don_Gia`
* `Ty_Le_Giam_Gia`
* `Tien_Giam`
* `Tong_Hang`
* `Tong_Thanh_Toan`
* `Tan_suat_mua_hang`
* `Thuong_Hieu`
* `Danh_Muc`

Dataset được sử dụng để phân tích:

* Doanh thu.
* Số lượng bán.
* Giá bán.
* Mức giảm giá.
* Thương hiệu.
* Danh mục sản phẩm.
* Khu vực bán hàng.
* Hành vi mua hàng.

---

# 5. 📱 Dataset thương hiệu điện thoại

**File:** `Hang_dien_thoai_sach.xlsx`

Sheet:

`hang_viet_nam`

Dataset gồm dữ liệu theo tháng và năm, phục vụ phân tích xu hướng của các thương hiệu điện thoại tại Việt Nam.

Các thương hiệu tiêu biểu:

* Apple
* Samsung
* Oppo
* Xiaomi
* Vivo
* Nokia
* Realme
* Huawei
* Sony
* Vsmart
* LG
* Asus
* Google
* Tecno
* Motorola
* Honor
* OnePlus
* ZTE
* Infinix
* Và các thương hiệu khác.

Giai đoạn dữ liệu:

**2010–2026**

Dataset này được sử dụng để phân tích:

* Xu hướng thương hiệu.
* Thị phần tương đối.
* Tăng trưởng theo thời gian.
* Biến động thương hiệu.
* So sánh các thương hiệu điện thoại.

---

# 6. 🔄 Quy trình xử lý dữ liệu

Hệ thống được xây dựng theo quy trình:

```text
DATA SOURCES
     │
     ▼
┌─────────────────────────┐
│      RAW DATA           │
│ CSV / Excel / Sources   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      DATA CLEANING      │
│                         │
│ - Remove duplicates     │
│ - Handle missing data   │
│ - Standardize columns   │
│ - Convert data types    │
│ - Normalize values      │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│        ETL              │
│ Extract - Transform     │
│ - Load                  │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      DATA WAREHOUSE     │
│                         │
│      STAR SCHEMA        │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│     DATA ANALYSIS       │
│                         │
│ KPI / YoY / Trend       │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      TABLEAU            │
│       DASHBOARD         │
└─────────────────────────┘
```

---

# 7. 🏗️ Kiến trúc hệ thống

## Tổng quan kiến trúc

```text
                    ┌──────────────────────┐
                    │      DATA SOURCES    │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
         CSV XNK          CSV BÁN HÀNG      EXCEL
         3,125 rows       10,000 rows       PHONE
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                    ┌──────────────────────┐
                    │      PYTHON ETL      │
                    │                      │
                    │ Cleaning             │
                    │ Transformation       │
                    │ Validation           │
                    │ Standardization      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    DATA WAREHOUSE    │
                    │                      │
                    │    STAR SCHEMA       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       TABLEAU        │
                    │                      │
                    │ Dashboard / KPI       │
                    │ YoY / Trend           │
                    │ Visualization         │
                    └──────────────────────┘
```

---

# 8. ⭐ Star Schema

Mô hình dữ liệu được thiết kế theo kiến trúc **Star Schema**, trong đó Fact Table nằm ở trung tâm và liên kết với các Dimension Table.

## Mô hình tổng quan

```text
                         ┌──────────────────┐
                         │     DIM_DATE     │
                         │──────────────────│
                         │ Date_Key         │
                         │ Date             │
                         │ Day              │
                         │ Month            │
                         │ Quarter          │
                         │ Year             │
                         └────────┬─────────┘
                                  │
                                  │
┌──────────────────┐              │              ┌──────────────────┐
│   DIM_PRODUCT    │              │              │   DIM_CUSTOMER   │
│──────────────────│              │              │──────────────────│
│ Product_Key      │              │              │ Customer_Key     │
│ Product_ID       │              │              │ Province         │
│ Product_Name     │              │              │ District         │
│ Category         │              │              │ Address          │
│ Brand            │              │              └────────┬─────────┘
└────────┬─────────┘              │                       │
         │                        │                       │
         │              ┌─────────▼─────────┐             │
         └─────────────►│    FACT_SALES     │◄────────────┘
                        │───────────────────│
                        │ Sales_Key         │
                        │ Date_Key          │
                        │ Product_Key       │
                        │ Customer_Key      │
                        │ Quantity          │
                        │ Unit_Price        │
                        │ Discount          │
                        │ Revenue           │
                        │ Purchase_Frequency│
                        └─────────┬─────────┘
                                  │
                                  │
                         ┌────────▼─────────┐
                         │   DIM_CATEGORY   │
                         │──────────────────│
                         │ Category_Key     │
                         │ Category_Name    │
                         │ Product_Group    │
                         └──────────────────┘
```

---

# 9. 📊 Fact Table

## FACT_SALES

Fact Sales lưu trữ các chỉ số định lượng phục vụ phân tích bán hàng.

| Cột                  | Ý nghĩa                 |
| -------------------- | ----------------------- |
| `Sales_Key`          | Khóa giao dịch          |
| `Date_Key`           | Khóa thời gian          |
| `Product_Key`        | Khóa sản phẩm           |
| `Customer_Key`       | Khóa khách hàng/khu vực |
| `Category_Key`       | Khóa danh mục           |
| `Quantity`           | Số lượng                |
| `Unit_Price`         | Đơn giá                 |
| `Discount`           | Giá trị giảm giá        |
| `Revenue`            | Doanh thu               |
| `Purchase_Frequency` | Tần suất mua            |

### Công thức doanh thu

```text
Revenue = Quantity × Unit Price - Discount
```

Hoặc sử dụng trường:

```text
Revenue = Tong_Thanh_Toan
```

sau khi kiểm tra và chuẩn hóa dữ liệu nguồn.

---

# 10. 📅 DIM_DATE

Dimension thời gian được sử dụng để phân tích xu hướng và tăng trưởng.

| Cột        | Ý nghĩa          |
| ---------- | ---------------- |
| `Date_Key` | Khóa ngày        |
| `Date`     | Ngày             |
| `Day`      | Ngày trong tháng |
| `Month`    | Tháng            |
| `Quarter`  | Quý              |
| `Year`     | Năm              |
| `Week`     | Tuần             |

DIM_DATE đặc biệt quan trọng đối với phân tích:

* YoY
* MoM
* QoQ
* Trend
* Seasonal Analysis

---

# 11. 📦 DIM_PRODUCT

Dimension sản phẩm lưu thông tin mô tả sản phẩm.

| Cột             | Ý nghĩa          |
| --------------- | ---------------- |
| `Product_Key`   | Khóa sản phẩm    |
| `Product_ID`    | Mã sản phẩm      |
| `Product_Name`  | Tên sản phẩm     |
| `Brand_Key`     | Khóa thương hiệu |
| `Category_Key`  | Khóa danh mục    |
| `Product_Group` | Nhóm hàng        |

---

# 12. 🏷️ DIM_CATEGORY

Dimension danh mục giúp phân tích sản phẩm theo nhóm.

Ví dụ:

```text
Điện tử
│
├── Máy in
├── Điện thoại
├── Phụ kiện
├── Laptop
├── Máy tính
├── Thiết bị mạng
└── Các thiết bị khác
```

---

# 13. 🌎 DIM_LOCATION

Dimension khu vực được sử dụng để phân tích sự khác biệt giữa các địa phương.

| Cột            | Ý nghĩa        |
| -------------- | -------------- |
| `Location_Key` | Khóa khu vực   |
| `Tinh_Thanh`   | Tỉnh/Thành phố |
| `Phuong_Xa`    | Phường/Xã      |
| `Dia_Chi`      | Địa chỉ        |

Có thể sử dụng Dimension này để xây dựng bản đồ trên Tableau.

---

# 14. 🌍 DIM_PARTNER

Dimension đối tác phục vụ phân tích xuất nhập khẩu.

| Cột            | Ý nghĩa              |
| -------------- | -------------------- |
| `Partner_Key`  | Khóa đối tác         |
| `Partner_Name` | Tên quốc gia/đối tác |
| `Partner_Type` | Loại đối tác         |

Ví dụ:

```text
Thế giới
Trung Quốc
Hàn Quốc
Nhật Bản
Hoa Kỳ
...
```

---

# 15. 🚢 FACT_IMPORT_EXPORT

Đối với dữ liệu xuất nhập khẩu, xây dựng Fact riêng để tránh trộn lẫn bản chất nghiệp vụ bán hàng và thương mại quốc tế.

```text
                 DIM_DATE
                     │
                     │
                     ▼
DIM_PARTNER ──► FACT_IMPORT_EXPORT ◄── DIM_PRODUCT
                     │
                     │
                     ▼
               DIM_TRADE_TYPE
```

### Các chỉ số chính

* `Quantity`
* `Weight_KG`
* `CIF_USD`
* `FOB_USD`
* `Trade_Value_USD`

Trong đó:

```text
CIF = Giá trị nhập khẩu
FOB = Giá trị xuất khẩu
```

---

# 16. 📈 Phân tích tăng trưởng YoY

**YoY – Year-over-Year** dùng để so sánh giá trị của một chỉ tiêu với cùng kỳ năm trước.

### Công thức

```text
YoY Growth (%) =
(
    Giá trị năm hiện tại
    -
    Giá trị năm trước
)
/
Giá trị năm trước
× 100
```

Hoặc:

```text
YoY Growth (%) =
(Current Year / Previous Year - 1) × 100
```

### Ví dụ

Nếu doanh thu:

```text
2024 = 100 tỷ
2025 = 120 tỷ
```

thì:

```text
YoY = (120 / 100 - 1) × 100
     = 20%
```

=> Doanh thu tăng **20% so với năm trước**.

---

# 17. 🔎 Các KPI chính

Dashboard dự kiến tập trung vào các KPI:

### Bán hàng

```text
Total Revenue
Total Quantity
Average Order Value
Total Products
Total Brands
Total Categories
```

### Xuất nhập khẩu

```text
Total Import Value
Total Export Value
Total Quantity
Total Weight
Trade Value
```

### Tăng trưởng

```text
Revenue YoY %
Import YoY %
Export YoY %
Quantity YoY %
```

### Sản phẩm

```text
Top Products
Top Brands
Top Categories
Top Provinces
```

---

# 18. 💡 Phát hiện chính dự kiến

Sau khi hoàn thành ETL và phân tích, dự án tập trung trả lời các câu hỏi:

### 1. Thị trường đang tăng hay giảm?

Theo dõi:

```text
Revenue
Quantity
Import Value
Export Value
```

qua từng năm.

---

### 2. Năm nào có mức tăng trưởng cao nhất?

So sánh:

```text
YoY 2016
YoY 2017
YoY 2018
...
YoY 2025
```

Từ đó xác định những năm có biến động bất thường.

---

### 3. Thương hiệu nào đang chiếm ưu thế?

Phân tích:

```text
Brand
Sales
Quantity
Market Trend
YoY
```

để xác định các thương hiệu nổi bật.

---

### 4. Danh mục sản phẩm nào tạo ra doanh thu cao nhất?

Phân tích:

```text
Category
Revenue
Quantity
Average Price
YoY
```

---

### 5. Khu vực nào có hoạt động mua hàng cao?

Phân tích theo:

```text
Tỉnh/Thành phố
Số lượng
Doanh thu
Tần suất mua
```

---

### 6. Quốc gia nào là đối tác thương mại chính?

Đối với dữ liệu XNK:

```text
Partner
Import Value
Export Value
Trade Value
YoY
```

---

# 19. 🧹 ETL Pipeline

## Extract

Đọc dữ liệu từ:

```text
CSV
Excel
Database
```

## Transform

Thực hiện:

```text
Remove duplicates
Handle missing values
Standardize column names
Convert data types
Normalize currency
Normalize product/category names
Standardize province names
Create Date Dimension
Create surrogate keys
Calculate Revenue
Calculate YoY
Validate data
```

## Load

Đưa dữ liệu đã xử lý vào:

```text
Data Warehouse
       │
       ▼
Star Schema
       │
       ▼
Tableau
```

---

# 20. 🗂️ Cấu trúc thư mục dự án

```text
Vietnam-Electronics-Analysis/
│
├── README.md
│
├── data/
│   ├── raw/
│   │   ├── Data_XNK_goc_hoan_chinh_csv.csv
│   │   ├── Dien_tu_goc_da_thay_doi_csv.csv
│   │   └── Hang_dien_thoai_sach.xlsx
│   │
│   ├── cleaned/
│   │   ├── sales_clean.csv
│   │   ├── import_export_clean.csv
│   │   └── phone_brand_clean.csv
│   │
│   └── warehouse/
│       ├── fact_sales.csv
│       ├── fact_import_export.csv
│       ├── dim_date.csv
│       ├── dim_product.csv
│       ├── dim_category.csv
│       ├── dim_location.csv
│       └── dim_partner.csv
│
├── src/
│   ├── extraction/
│   ├── cleaning/
│   ├── transformation/
│   ├── validation/
│   └── etl/
│
├── sql/
│   ├── create_database.sql
│   ├── create_dimension.sql
│   ├── create_fact.sql
│   └── analysis.sql
│
├── tableau/
│   └── electronics_dashboard.twbx
│
├── docs/
│   ├── data_dictionary.xlsx
│   ├── data_quality_report.xlsx
│   └── architecture.png
│
└── requirements.txt
```

---

# 21. 🖥️ Dashboard Tableau

Dashboard được chia thành các nhóm:

## Dashboard 1 – Executive Overview

```text
┌────────────────────────────────────────────┐
│ TOTAL REVENUE │ TOTAL SALES │ YOY │ PRODUCT│
├────────────────────────────────────────────┤
│                                            │
│        Revenue Trend by Year               │
│                                            │
├───────────────────────┬────────────────────┤
│ Revenue by Category   │ Revenue by Brand    │
├───────────────────────┴────────────────────┤
│              Geographic Map                │
└────────────────────────────────────────────┘
```

---

## Dashboard 2 – Sales Analysis

Phân tích:

* Doanh thu.
* Sản lượng.
* Sản phẩm.
* Danh mục.
* Thương hiệu.
* Khu vực.

---

## Dashboard 3 – YoY Growth

```text
Revenue
   │
   ├── Current Year
   ├── Previous Year
   └── YoY Growth %
```

Biểu đồ:

* YoY theo năm.
* YoY theo danh mục.
* YoY theo thương hiệu.
* YoY theo khu vực.

---

## Dashboard 4 – Import & Export

Phân tích:

* Import.
* Export.
* Trade Value.
* Quốc gia đối tác.
* Nhóm hàng.
* Xu hướng XNK.

---

# 22. 🔗 Mối quan hệ giữa các thành phần

```text
                RAW DATA
                   │
                   ▼
             DATA CLEANING
                   │
                   ▼
                  ETL
                   │
                   ▼
             STAR SCHEMA
                   │
          ┌────────┴────────┐
          ▼                 ▼
     FACT TABLE       DIMENSION TABLE
          │                 │
          └────────┬────────┘
                   ▼
               KPI / YoY
                   │
                   ▼
              DATA ANALYSIS
                   │
                   ▼
                TABLEAU
                   │
                   ▼
              INSIGHTS
                   │
                   ▼
             DECISION MAKING
```

---

# 23. 🎯 Kết quả đầu ra

Dự án hướng tới các sản phẩm cuối cùng:

* ✅ Dataset đã làm sạch.
* ✅ Data Dictionary.
* ✅ Data Quality Report.
* ✅ ETL Pipeline.
* ✅ Data Warehouse.
* ✅ Star Schema.
* ✅ Fact Tables.
* ✅ Dimension Tables.
* ✅ Bộ KPI.
* ✅ Phân tích YoY.
* ✅ Tableau Dashboard.
* ✅ Báo cáo phân tích.
* ✅ Các phát hiện chính từ dữ liệu.

---

# 24. 🚀 Công nghệ sử dụng

| Công nghệ    | Mục đích                          |
| ------------ | --------------------------------- |
| Python       | ETL và xử lý dữ liệu              |
| Pandas       | Data Cleaning / Transformation    |
| SQL Server   | Data Warehouse                    |
| SQL          | Truy vấn và phân tích             |
| Tableau      | Dashboard                         |
| Excel        | Kiểm tra và xử lý dữ liệu ban đầu |
| Git / GitHub | Quản lý mã nguồn                  |

---

# 25. 👥 Quy trình làm việc nhóm

```text
                 PROJECT MANAGER
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   DATA SOURCE      DATA ETL      DATABASE
        │              │              │
        └──────────────┼──────────────┘
                       │
                       ▼
                  DATA ANALYSIS
                       │
                       ▼
                    TABLEAU
                       │
                       ▼
                  PRESENTATION
```

---

# 26. 📌 Kết luận

Dự án xây dựng một quy trình phân tích dữ liệu hoàn chỉnh từ **dữ liệu thô → làm sạch → ETL → Data Warehouse → Star Schema → KPI → YoY → Tableau Dashboard**.

Việc áp dụng Star Schema giúp tách biệt dữ liệu nghiệp vụ và dữ liệu mô tả, tăng khả năng mở rộng và thuận tiện cho việc phân tích.

Thông qua các chỉ số doanh thu, sản lượng, xuất nhập khẩu, thương hiệu, danh mục và **YoY Growth**, hệ thống có thể giúp xác định xu hướng phát triển của thị trường hàng điện tử Việt Nam và hỗ trợ đưa ra các quyết định dựa trên dữ liệu.

---

## ⭐ Project Flow

```text
┌──────────────┐
│ DATA SOURCES │
└──────┬───────┘
       ▼
┌──────────────┐
│ DATA CLEANING│
└──────┬───────┘
       ▼
┌──────────────┐
│     ETL      │
└──────┬───────┘
       ▼
┌──────────────┐
│ DATA WAREHOUSE│
└──────┬───────┘
       ▼
┌──────────────┐
│ STAR SCHEMA  │
└──────┬───────┘
       ▼
┌──────────────┐
│ KPI + YOY    │
└──────┬───────┘
       ▼
┌──────────────┐
│   TABLEAU    │
└──────┬───────┘
       ▼
┌──────────────┐
│   INSIGHTS   │
└──────────────┘
```

**Vietnam Electronics Analysis – Data → Insight → Decision**
