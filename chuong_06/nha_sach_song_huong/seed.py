"""Nạp dữ liệu mẫu cho Nhà sách Sông Hương.

Cách dùng:
    python seed.py            # tạo bảng (nếu chưa có) và nạp dữ liệu mẫu nếu CSDL còn trống
    python seed.py --reset    # xoá toàn bộ dữ liệu cũ rồi nạp lại
"""
import os
import sys
import textwrap
import uuid
from datetime import datetime, timedelta
from xml.sax.saxutils import escape

from app import create_app, db
from app.models import (
    STATUS_CANCELLED,
    STATUS_DONE,
    STATUS_PENDING,
    STATUS_SHIPPING,
    Book,
    Category,
    Order,
    OrderHistory,
    OrderItem,
)
from app.utils import calc_shipping_fee

NOW = datetime.now()

CATEGORIES = [
    ("Lập trình", "Ngôn ngữ lập trình và phát triển ứng dụng."),
    ("Cơ sở dữ liệu", "Thiết kế, truy vấn và quản trị cơ sở dữ liệu."),
    ("Công cụ", "Công cụ hỗ trợ phát triển và vận hành phần mềm."),
    ("Mạng", "Mạng máy tính và hạ tầng."),
    ("Kỹ năng lập trình", "Tư duy, thuật toán và thực hành viết mã tốt."),
    ("Thiết kế", "Thiết kế giao diện và trải nghiệm người dùng."),
]

# (tên, tác giả, NXB, năm, giá, tồn kho gốc, danh mục, mô tả)
BOOKS = [
    ("Lập trình Python cơ bản", "Nguyễn Văn An", "NXB Thanh Niên", 2022, 95000, 30, "Lập trình",
     "Nhập môn Python qua các ví dụ ngắn gọn: biến, hàm, lớp, xử lý tệp và thư viện chuẩn."),
    ("Phát triển web với Flask", "Trần Minh Quân", "NXB Lao Động", 2021, 189000, 12, "Lập trình",
     "Xây dựng ứng dụng web hoàn chỉnh với Flask: Blueprint, Jinja2, biểu mẫu và triển khai."),
    ("Cơ sở dữ liệu quan hệ và SQL", "Lê Thị Hoa", "NXB Đại học Quốc gia", 2020, 120000, 25, "Cơ sở dữ liệu",
     "Mô hình quan hệ, chuẩn hoá, truy vấn SELECT nâng cao, JOIN và chỉ mục."),
    ("SQLAlchemy thực hành", "Phạm Quốc Bảo", "NXB Thông tin và Truyền thông", 2023, 135000, 5, "Cơ sở dữ liệu",
     "Làm việc với ORM: model, quan hệ, truy vấn tổng hợp và migration."),
    ("Git và GitHub cho người mới", "Đỗ Thanh Tùng", "NXB Thanh Niên", 2021, 78000, 3, "Công cụ",
     "Quản lý phiên bản, nhánh, gộp mã và cộng tác nhóm với GitHub."),
    ("Docker từ cơ bản đến nâng cao", "Võ Hoàng Long", "NXB Lao Động", 2022, 210000, 18, "Công cụ",
     "Đóng gói và triển khai ứng dụng bằng container, Docker Compose và mạng ảo."),
    ("Mạng máy tính căn bản", "Hoàng Văn Nam", "NXB Giáo dục Việt Nam", 2019, 99000, 40, "Mạng",
     "Mô hình OSI, TCP/IP, định tuyến, DNS, HTTP và bảo mật cơ bản."),
    ("Viết mã sạch trong thực tế", "Nguyễn Hải Đăng", "NXB Thông tin và Truyền thông", 2022, 150000, 0, "Kỹ năng lập trình",
     "Đặt tên, tách hàm, kiểm thử và tái cấu trúc để mã dễ đọc, dễ bảo trì."),
    ("Tư duy thuật toán", "Bùi Anh Khoa", "NXB Đại học Quốc gia", 2021, 110000, 8, "Kỹ năng lập trình",
     "Phân tích độ phức tạp, đệ quy, quy hoạch động và các bài toán kinh điển."),
    ("Thiết kế giao diện với Bootstrap 5", "Phan Thu Hà", "NXB Thanh Niên", 2023, 125000, 22, "Thiết kế",
     "Hệ thống lưới, thành phần dựng sẵn, tuỳ biến biến CSS và thiết kế responsive."),
    ("Nguyên lý thiết kế UI/UX", "Lý Mỹ Linh", "NXB Mỹ Thuật", 2022, 165000, 2, "Thiết kế",
     "Phân cấp thị giác, màu sắc, chữ, khả năng tiếp cận và kiểm thử người dùng."),
]

COVER_COLORS = ["#1f5f5b", "#8a4b2d", "#2f4a7a", "#6b3f6e", "#3d6b3a", "#9a6a1f", "#4a4f57", "#a23b4a"]


def make_cover_svg(index, title, author):
    """Sinh ảnh bìa SVG đơn giản để giao diện có hình ngay khi chạy thử."""
    color = COVER_COLORS[index % len(COVER_COLORS)]
    lines = textwrap.wrap(title, width=14)[:5]
    text = "".join(
        f'<text x="150" y="{150 + i * 34}" text-anchor="middle" font-family="Georgia, serif" '
        f'font-size="27" font-weight="bold" fill="#ffffff">{escape(line)}</text>'
        for i, line in enumerate(lines)
    )
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 400">'
        f'<rect width="300" height="400" fill="{color}"/>'
        '<rect x="0" y="0" width="22" height="400" fill="rgba(0,0,0,0.22)"/>'
        '<rect x="48" y="96" width="204" height="3" fill="rgba(255,255,255,0.55)"/>'
        f"{text}"
        '<rect x="48" y="338" width="204" height="2" fill="rgba(255,255,255,0.55)"/>'
        f'<text x="150" y="368" text-anchor="middle" font-family="sans-serif" font-size="16" '
        f'fill="rgba(255,255,255,0.85)">{escape(author)}</text>'
        "</svg>"
    )
    filename = f"{uuid.uuid4().hex}.svg"
    from flask import current_app

    with open(os.path.join(current_app.config["UPLOAD_FOLDER"], filename), "w", encoding="utf-8") as f:
        f.write(svg)
    return filename


def make_order(customer, lines, flow, days_ago=0, hours_ago=0):
    """Tạo đơn mẫu: trừ tồn kho; nếu kết thúc ở 'Đã huỷ' thì hoàn lại tồn kho."""
    name, phone, email, address, payment, note = customer
    created = NOW - timedelta(days=days_ago, hours=hours_ago)
    subtotal = sum(book.price * qty for book, qty in lines)
    fee = calc_shipping_fee(subtotal)

    order = Order(
        customer_name=name,
        customer_phone=phone,
        customer_email=email,
        shipping_address=address,
        note=note,
        payment_method=payment,
        subtotal=subtotal,
        shipping_fee=fee,
        total_amount=subtotal + fee,
        status=flow[-1],
        created_at=created,
    )
    for book, qty in lines:
        order.items.append(OrderItem(book=book, quantity=qty, unit_price=book.price))
        book.stock -= qty
    for i, status in enumerate(flow):
        order.history.append(OrderHistory(status=status, changed_at=created + timedelta(hours=5 * i)))
    if flow[-1] == STATUS_CANCELLED:
        for book, qty in lines:
            book.stock += qty
    db.session.add(order)
    return order


def seed():
    if "--reset" in sys.argv:
        db.drop_all()
    db.create_all()

    if Category.query.first() is not None:
        print("CSDL đã có dữ liệu. Dùng 'python seed.py --reset' để nạp lại từ đầu.")
        return

    categories = {}
    for name, description in CATEGORIES:
        category = Category(name=name, description=description)
        db.session.add(category)
        categories[name] = category
    db.session.flush()

    books = {}
    for index, (title, author, publisher, year, price, stock, cat, desc) in enumerate(BOOKS):
        book = Book(
            title=title,
            author=author,
            publisher=publisher,
            publish_year=year,
            price=price,
            stock=stock,
            description=desc,
            cover_image=make_cover_svg(index, title, author),
            category_id=categories[cat].id,
            created_at=NOW - timedelta(days=len(BOOKS) - index),
        )
        db.session.add(book)
        books[title] = book
    db.session.flush()

    b = books  # viết tắt
    make_order(
        ("Nguyễn Thị Lan", "0912345678", "lan.nguyen@example.com", "12 Lê Lợi, Phường Vĩnh Ninh, TP. Huế", "COD", None),
        [(b["Lập trình Python cơ bản"], 2), (b["Mạng máy tính căn bản"], 1)],
        [STATUS_PENDING, STATUS_SHIPPING, STATUS_DONE],
        days_ago=1,
    )
    make_order(
        ("Trần Văn Hùng", "0987654321", None, "45 Hùng Vương, Phường Phú Nhuận, TP. Huế", "BANK", "Gọi trước khi giao"),
        [(b["Cơ sở dữ liệu quan hệ và SQL"], 1)],
        [STATUS_PENDING, STATUS_SHIPPING, STATUS_DONE],
        days_ago=3,
    )
    make_order(
        ("Lê Minh Châu", "0905123456", "chau.le@example.com", "78 Nguyễn Huệ, Phường Phú Hội, TP. Huế", "COD", None),
        [(b["Docker từ cơ bản đến nâng cao"], 1)],
        [STATUS_PENDING, STATUS_SHIPPING],
        days_ago=1,
        hours_ago=3,
    )
    make_order(
        ("Phạm Quốc Việt", "0934567890", "viet.pham@example.com", "9 Trần Phú, Phường Vĩnh Ninh, TP. Huế", "BANK", "Giao giờ hành chính"),
        [(b["Phát triển web với Flask"], 1)],
        [STATUS_PENDING],
        hours_ago=2,
    )
    make_order(
        ("Hoàng Thu Trang", "0977123456", None, "21 Phan Bội Châu, Phường Trường An, TP. Huế", "COD", None),
        [(b["Git và GitHub cho người mới"], 2)],
        [STATUS_PENDING, STATUS_CANCELLED],
        days_ago=2,
    )

    db.session.commit()
    print(
        f"Đã nạp {len(CATEGORIES)} danh mục, {len(BOOKS)} đầu sách và 5 đơn hàng mẫu "
        "(đủ 4 trạng thái)."
    )


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed()
