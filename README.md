# Klaviyo Business Crawler

Script để crawl danh sách các doanh nghiệp từ Klaviyo Connect directory.

## Tính năng

- Crawl danh sách doanh nghiệp từ Klaviyo Connect
- Hỗ trợ filter theo quốc gia và ngân sách
- Export kết quả ra file JSON
- Lưu page source để debug

## Cài đặt

### Yêu cầu
- Python 3.7+
- Kết nối internet

### Cài đặt dependencies

```bash
pip install -r requirements.txt
```

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

Script sử dụng 2 phương pháp:

1. **Requests + BeautifulSoup** (mặc định):
   - Nhanh, nhẹ
   - Phù hợp với trang web static
   - Ít tốn tài nguyên

2. **Playwright** (backup):
   - Xử lý JavaScript rendering
   - Phù hợp với trang web dynamic
   - Cần cài thêm browser:
   ```bash
   pip install playwright
   playwright install chromium
   ```

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
