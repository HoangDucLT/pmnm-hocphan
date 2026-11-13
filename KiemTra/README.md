# Bài kiểm tra Phần mềm mã nguồn mở – Quản lý Sách (Flask + SQLite)

## Cấu trúc
KiemTra/
├── app.py              # Ứng dụng Flask (route + SQLite)
├── requirements.txt
├── library.db          # Tự tạo khi chạy lần đầu
└── templates/          # Giao diện HTML (Bootstrap)

## Cách chạy
### Windows
    cd KiemTra
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python app.py

### macOS / Linux
    cd KiemTra
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python app.py

Mở trình duyệt: http://127.0.0.1:5000
