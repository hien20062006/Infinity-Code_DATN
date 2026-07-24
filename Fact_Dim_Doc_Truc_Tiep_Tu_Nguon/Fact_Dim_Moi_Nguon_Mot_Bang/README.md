# FACT–DIM ĐỌC TRỰC TIẾP TỪ NGUỒN

Project không còn khai báo thủ công danh sách sản phẩm hoặc thông tin đơn vị vận chuyển trong các bảng DIM.

## DIM đọc trực tiếp từ nguồn

- `Dim_HanhChinhVN`: gọi API tỉnh/thành Việt Nam.
- `Dim_TheGioiDiDong`: đọc sản phẩm và giá từ JSON-LD/HTML của website.
- `Dim_FPTShop`: đọc sản phẩm và giá từ JSON-LD/HTML của website.
- `Dim_CellphoneS`: đọc sản phẩm và giá từ JSON-LD/HTML của website.
- `Dim_GHN`, `Dim_GHTK`, `Dim_ViettelPost`, `Dim_JTExpress`: đọc tiêu đề, mô tả dịch vụ và khoảng ngày nếu trang công khai có cung cấp.
- `Dim_DangKyKD`: đọc thông tin mô tả của Cổng thông tin đăng ký doanh nghiệp.

## Dữ liệu tự tạo

- `synthetic_customer.py`
- `synthetic_order.py`

## Bảng FACT

`Fact_Order` chọn khóa từ các DIM sản phẩm, vận chuyển, địa lý và nguồn đăng ký kinh doanh; sau đó tạo số lượng, giảm giá, VAT, phí vận chuyển và tổng thanh toán.

## Cách chạy

```bash
pip install -r requirements.txt
python main.py
```

## Lưu ý

Website bán lẻ có thể đổi HTML hoặc chặn yêu cầu tự động. Khi không đọc được sản phẩm có giá, chương trình sẽ báo lỗi rõ ràng và không thay thế bằng dữ liệu viết tay. Hãy tôn trọng robots.txt, điều khoản sử dụng và giới hạn tần suất truy cập của từng website.
