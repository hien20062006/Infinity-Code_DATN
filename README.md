# Đồ Án Tốt Nghiệp: Phân Tích Hàng Hóa Điện Tử Việt Nam

Chào mừng bạn đến với kho lưu trữ mã nguồn của dự án Phân Tích Hàng Hóa Điện Tử Việt Nam.

Đây là đồ án tốt nghiệp xây dựng hệ thống xử lý và phân tích dữ liệu hàng hóa điện tử Việt Nam, ứng dụng Python để thu thập và xử lý dữ liệu, SQL Server để lưu trữ và xây dựng Data Warehouse theo mô hình Star Schema, cuối cùng sử dụng Tableau để trực quan hóa dữ liệu.

Hệ thống tập trung vào việc phân tích hàng hóa điện tử, thương hiệu, đối tác, thị phần và phân bố cửa hàng theo địa phương.

# Tổng Quan Dự Án

Thu thập dữ liệu hàng hóa điện tử từ nhiều nguồn.

Xử lý và làm sạch dữ liệu.

Chuẩn hóa dữ liệu sản phẩm, thương hiệu và địa phương.

Xây dựng Data Warehouse trên SQL Server.

Xây dựng mô hình dữ liệu Star Schema.

Phân tích dữ liệu hàng hóa điện tử Việt Nam.

Trực quan hóa dữ liệu bằng Tableau.

# 🌐 Nguồn dữ liệu

Hệ thống sử dụng Python Web Scraping, dữ liệu thương mại hàng hóa và REST API để thu thập dữ liệu từ các nguồn sau.

Thiết bị điện tử

https://www.thegioididong.com/

https://fptshop.com.vn/

https://cellphones.com.vn/

https://phongvu.vn/

Dữ liệu thương mại hàng hóa

Dữ liệu xuất nhập khẩu hàng hóa điện tử được sử dụng để phân tích:

- Năm báo cáo
- Tháng báo cáo
- Kỳ báo cáo
- Tên nước đối tác
- Mã hàng hóa
- Mô tả hàng hóa
- Số lượng
- Trọng lượng
- Giá trị CIF
- Giá trị FOB
- Giá trị giao dịch

Dữ liệu hành chính

https://provinces.open-api.vn/

Dữ liệu được sử dụng để chuẩn hóa thông tin tỉnh/thành phố và phường/xã.

# 🏗️ Kiến trúc hệ thống

```mermaid
flowchart TD

A1["🌐 Thế Giới Di Động"]
A2["🌐 FPT Shop"]
A3["🌐 CellphoneS"]
A4["🌐 Phong Vũ"]
A5["🌐 Dữ liệu thương mại hàng hóa"]
A6["🗺 Dữ liệu hành chính"]

A1 --> B["🐍 Python Web Scraping"]
A2 --> B
A3 --> B
A4 --> B
A5 --> B
A6 --> B

B --> C["📂 Raw Dataset"]
C --> D["🧹 Data Processing"]
D --> E["🗄️ SQL Server"]
E --> F["⭐ Star Schema"]
F --> G["📊 Tableau Dashboard"]