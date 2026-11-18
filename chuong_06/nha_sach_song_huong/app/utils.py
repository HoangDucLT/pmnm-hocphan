import os
import uuid
from urllib.parse import urlparse

from flask import current_app, redirect, request, url_for

SHIPPING_FEE = 20000
FREE_SHIPPING_FROM = 200000
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def calc_shipping_fee(subtotal):
    """20.000 ₫, miễn phí khi tạm tính >= 200.000 ₫."""
    return 0 if subtotal >= FREE_SHIPPING_FROM else SHIPPING_FEE


def format_vnd(value):
    return f"{int(value or 0):,}".replace(",", ".") + " ₫"


def format_datetime(value):
    return value.strftime("%d/%m/%Y %H:%M") if value else ""


def like_pattern(term):
    """Escape ký tự đặc biệt của LIKE; dùng cùng escape='\\\\'."""
    escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def is_safe_redirect(target):
    """Chỉ cho phép redirect nội bộ (chống open redirect)."""
    if not target or "\\" in target:
        return False
    parsed = urlparse(target)
    return (
        not parsed.scheme
        and not parsed.netloc
        and target.startswith("/")
        and not target.startswith("//")
    )


def redirect_back(default_endpoint, **values):
    """Quay lại URL trong trường ẩn `next` (giữ query string), nếu không hợp lệ thì về mặc định."""
    target = request.form.get("next", "")
    if is_safe_redirect(target):
        return redirect(target)
    return redirect(url_for(default_endpoint, **values))


def exists_ci(model, column, value, exclude_id=None):
    """Kiểm tra trùng không phân biệt hoa/thường (xử lý ở Python để đúng với tiếng Việt)."""
    from app import db

    needle = (value or "").strip().casefold()
    for row_id, current in db.session.query(model.id, column).all():
        if current and current.strip().casefold() == needle and row_id != exclude_id:
            return True
    return False


def cover_url(book):
    from flask import url_for as _url_for

    if book is not None and book.cover_image:
        return _url_for("static", filename="uploads/" + book.cover_image)
    return _url_for("static", filename="img/placeholder.svg")


def save_cover_image(file_storage):
    """Lưu ảnh bìa với tên ngẫu nhiên (UUID), trả về tên file."""
    ext = os.path.splitext(file_storage.filename)[1].lower().lstrip(".")
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError("Định dạng ảnh không được hỗ trợ.")
    filename = f"{uuid.uuid4().hex}.{ext}"
    file_storage.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
    return filename


def delete_cover_image(filename):
    if not filename:
        return
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], os.path.basename(filename))
    try:
        if os.path.isfile(path):
            os.remove(path)
    except OSError:
        pass
