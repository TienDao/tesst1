# Klaviyo Business Crawler

Script để crawl danh sách các doanh nghiệp từ Klaviyo Connect directory.

## Tính năng

- Crawl danh sách doanh nghiệp từ Klaviyo Connect
- **Tự động load more để lấy hết tất cả kết quả** (sử dụng Playwright)
- Hỗ trợ filter theo quốc gia và ngân sách
- Export kết quả ra file JSON
- Lưu page source để debug

## Cài đặt

### Yêu cầu
- Python 3.7+
- Kết nối internet

### Cài đặt dependencies

```bash
# Cài đặt Python packages
pip install -r requirements.txt

# Cài đặt Playwright browsers (bắt buộc để sử dụng tính năng load-more)
playwright install
```

**Lưu ý:** Tính năng load-more tự động yêu cầu Playwright browsers. Nếu không cài được browsers, script sẽ tự động chuyển sang chế độ requests (chỉ lấy trang đầu tiên).

## Sử dụng

### Chạy script cơ bản

```bash
python crawl_klaviyo.py
```

### Tùy chỉnh URL

Mở file `crawl_klaviyo.py` và thay đổi URL trong hàm `main()`:

```python
def main():
    # Thay đổi country và budget theo nhu cầu
    url = "https://connect.klaviyo.com/?country=US&f_monthly-budget=2500-or-unsure"
    # Hoặc thử các filter khác:
    # url = "https://connect.klaviyo.com/?country=VN"
    # url = "https://connect.klaviyo.com/?f_monthly-budget=5000-10000"
```

### Các tham số filter có thể dùng:

- `country`: Mã quốc gia (VD: US, VN, UK, AU)
- `f_monthly-budget`: Ngân sách hàng tháng
  - `2500-or-unsure`
  - `5000-10000`
  - `10000-25000`
  - `25000-plus`

## Kết quả

Script sẽ tạo ra các file sau:

### 1. `klaviyo_businesses.json`
File JSON chứa danh sách các doanh nghiệp:

```json
{
  "total": 15,
  "businesses": [
    "Business Name 1",
    "Business Name 2",
    "..."
  ],
  "source_url": "https://connect.klaviyo.com/..."
}
```

### 2. `page_source.html`
File HTML của trang web (để debug nếu cần)

## Cách hoạt động

Script sử dụng 2 phương pháp với auto-fallback:

1. **Playwright** (mặc định - có load-more):
   - **Tự động click "Load More" cho đến khi hết kết quả**
   - Xử lý JavaScript rendering và dynamic content
   - Lấy được toàn bộ danh sách businesses
   - Giới hạn tối đa 100 lần click để tránh vòng lặp vô hạn
   - Yêu cầu cài đặt browsers: `playwright install`

2. **Requests + BeautifulSoup** (fallback tự động):
   - Tự động kích hoạt nếu Playwright không khả dụng
   - Chỉ lấy được trang đầu tiên (không có load-more)
   - Nhanh, nhẹ, ít tốn tài nguyên

## Troubleshooting

### Lỗi 403 Forbidden
- Website có thể block request tự động
- Thử thêm delay giữa các request
- Sử dụng Playwright thay vì requests

### Không tìm thấy businesses
- Kiểm tra file `page_source.html` để xem cấu trúc trang
- Website có thể đã thay đổi cấu trúc HTML
- Cần update CSS selectors trong script

### Network/Proxy errors
- Kiểm tra kết nối internet
- Nếu đang dùng proxy/VPN, thử tắt đi
- Một số môi trường có firewall chặn requests

## Lưu ý

- Script tuân thủ robots.txt và rate limiting
- Không nên chạy quá thường xuyên để tránh bị block IP
- Dữ liệu crawl thuộc quyền sở hữu của Klaviyo
- Chỉ sử dụng cho mục đích hợp pháp

## Ví dụ sử dụng

```bash
# Cài đặt
pip install -r requirements.txt

# Chạy script
python crawl_klaviyo.py

# Xem kết quả
cat klaviyo_businesses.json
```

## Giấy phép

MIT License - Sử dụng tự do với mục đích hợp pháp.
