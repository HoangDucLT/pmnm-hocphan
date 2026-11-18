# Nhà sách Sông Hương

Ứng dụng web bán sách bằng **Flask** (Blueprint, Flask-SQLAlchemy, Flask-Migrate, Flask-WTF, Bootstrap 5).
Gồm 11 màn hình: trang bán hàng (Phần A, 5 màn hình) và trang quản trị `/admin` (Phần B, 6 màn hình).

## Chạy trong VS Code

1. Mở thư mục `nha_sach_song_huong` bằng VS Code (`File > Open Folder`), mở Terminal (`Ctrl+``).
2. Tạo và kích hoạt môi trường ảo:

   Windows (PowerShell):
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
   macOS / Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   Nếu PowerShell báo lỗi quyền chạy script: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.
3. Chọn interpreter: `Ctrl+Shift+P` → **Python: Select Interpreter** → chọn `.venv`.
4. Cài thư viện:
   ```bash
   pip install -r requirements.txt
   ```
5. Nạp dữ liệu mẫu (tự tạo bảng):
   ```bash
   python seed.py
   ```
   Muốn nạp lại từ đầu: `python seed.py --reset`.
6. Chạy ứng dụng:
   ```bash
   python run.py
   ```
   hoặc nhấn `F5` (cấu hình sẵn trong `.vscode/launch.json`).
7. Mở trình duyệt:
   - Trang bán hàng: http://127.0.0.1:5000/
   - Trang quản trị: http://127.0.0.1:5000/admin

## Dùng Flask-Migrate (thay cho create_all)

Xoá file `nhasach.db` (nếu có), rồi:
```bash
flask --app run db init
flask --app run db migrate -m "Tao bang ban dau"
flask --app run db upgrade
python seed.py
```

## Cấu trúc

```
app/
  __init__.py   app factory, context_processor (badge giỏ hàng / đơn chờ), error handlers
  models.py     Category, Book, Order, OrderItem, OrderHistory + máy trạng thái đơn
  forms.py      CheckoutForm, BookForm, CategoryForm, OrderStatusForm
  utils.py      phí ship, định dạng tiền, lưu/xoá ảnh bìa, redirect an toàn
  routes/shop.py   Màn hình 1–5
  routes/admin.py  Màn hình 6–11
  templates/ static/
seed.py  config.py  run.py
```

## Ghi chú

- Giỏ hàng chỉ lưu `{book_id: số lượng}` trong session; giá luôn lấy mới từ CSDL.
- `OrderItem.unit_price` lưu giá tại thời điểm đặt hàng.
- Đề bài không yêu cầu đăng nhập nên `/admin` chưa có xác thực. Nếu triển khai thật cần bổ sung.
- Tìm kiếm dùng `LIKE` của SQLite nên không phân biệt hoa/thường với chữ không dấu, nhưng chữ có dấu thì phân biệt (ví dụ "á" khác "Á"). Kiểm tra trùng tên sách/danh mục đã xử lý đúng với tiếng Việt.
