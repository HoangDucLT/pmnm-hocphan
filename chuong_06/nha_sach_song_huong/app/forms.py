import os
from datetime import datetime

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from werkzeug.datastructures import FileStorage
from wtforms import IntegerField, SelectField, StringField, TextAreaField
from wtforms.validators import (
    DataRequired,
    Email,
    InputRequired,
    Length,
    NumberRange,
    Optional,
    Regexp,
    ValidationError,
)

from app.models import Book, Category, ORDER_STATUSES, PAYMENT_METHODS
from app.utils import exists_ci

MAX_COVER_SIZE = 2 * 1024 * 1024  # 2 MB


def strip_filter(value):
    return value.strip() if isinstance(value, str) else value


class VNIntegerField(IntegerField):
    """IntegerField với thông báo lỗi tiếng Việt."""

    def process_formdata(self, valuelist):
        if not valuelist:
            return
        try:
            self.data = int(valuelist[0])
        except ValueError:
            self.data = None
            raise ValueError("Vui lòng nhập số nguyên hợp lệ.")


# ---------------------------------------------------------------- Phần A
class CheckoutForm(FlaskForm):
    customer_name = StringField(
        "Họ và tên",
        filters=[strip_filter],
        validators=[DataRequired("Vui lòng nhập họ tên."), Length(max=120)],
    )
    customer_phone = StringField(
        "Số điện thoại",
        filters=[strip_filter],
        validators=[
            DataRequired("Vui lòng nhập số điện thoại."),
            Regexp(
                r"^0\d{9}$",
                message="Số điện thoại phải gồm đúng 10 chữ số và bắt đầu bằng số 0.",
            ),
        ],
    )
    shipping_address = TextAreaField(
        "Địa chỉ giao hàng",
        filters=[strip_filter],
        validators=[DataRequired("Vui lòng nhập địa chỉ giao hàng.")],
    )
    customer_email = StringField(
        "Email",
        filters=[strip_filter],
        validators=[
            Optional(),
            Email("Email không đúng định dạng."),
            Length(max=120),
        ],
    )
    note = TextAreaField("Ghi chú", filters=[strip_filter], validators=[Optional()])
    payment_method = SelectField(
        "Phương thức thanh toán",
        choices=[("", "— Chọn phương thức —")] + list(PAYMENT_METHODS.items()),
        validators=[DataRequired("Vui lòng chọn phương thức thanh toán.")],
    )


# ---------------------------------------------------------------- Phần B
class BookForm(FlaskForm):
    title = StringField(
        "Tên sách",
        filters=[strip_filter],
        validators=[DataRequired("Vui lòng nhập tên sách."), Length(max=200)],
    )
    author = StringField(
        "Tác giả",
        filters=[strip_filter],
        validators=[DataRequired("Vui lòng nhập tác giả."), Length(max=150)],
    )
    publisher = StringField(
        "Nhà xuất bản", filters=[strip_filter], validators=[Optional(), Length(max=150)]
    )
    publish_year = VNIntegerField("Năm xuất bản", validators=[Optional()])
    price = VNIntegerField(
        "Giá bán (₫)",
        validators=[
            InputRequired("Vui lòng nhập giá bán."),
            NumberRange(min=1000, message="Giá bán phải từ 1.000 ₫ trở lên."),
        ],
    )
    stock = VNIntegerField(
        "Tồn kho",
        validators=[
            InputRequired("Vui lòng nhập số lượng tồn kho."),
            NumberRange(min=0, message="Tồn kho không được âm."),
        ],
    )
    category_id = SelectField(
        "Danh mục",
        coerce=int,
        validators=[DataRequired("Vui lòng chọn danh mục.")],
    )
    description = TextAreaField("Mô tả", filters=[strip_filter], validators=[Optional()])
    cover_image = FileField(
        "Ảnh bìa",
        validators=[
            FileAllowed(["jpg", "jpeg", "png", "webp"], "Chỉ chấp nhận ảnh JPG, PNG hoặc WEBP.")
        ],
    )

    def __init__(self, *args, book_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.book_id = book_id
        self.category_id.choices = [(0, "— Chọn danh mục —")] + [
            (c.id, c.name) for c in Category.query.order_by(Category.name).all()
        ]

    def validate_title(self, field):
        if exists_ci(Book, Book.title, field.data, exclude_id=self.book_id):
            raise ValidationError("Tên sách này đã tồn tại.")

    def validate_publish_year(self, field):
        current_year = datetime.now().year
        if field.data is not None and not (1900 <= field.data <= current_year):
            raise ValidationError(f"Năm xuất bản phải từ 1900 đến {current_year}.")

    def validate_cover_image(self, field):
        file = field.data
        if isinstance(file, FileStorage) and file.filename:
            file.stream.seek(0, os.SEEK_END)
            size = file.stream.tell()
            file.stream.seek(0)
            if size > MAX_COVER_SIZE:
                raise ValidationError("Ảnh bìa tối đa 2 MB.")


class CategoryForm(FlaskForm):
    name = StringField(
        "Tên danh mục",
        filters=[strip_filter],
        validators=[DataRequired("Vui lòng nhập tên danh mục."), Length(max=100)],
    )
    description = TextAreaField("Mô tả", filters=[strip_filter], validators=[Optional()])

    def __init__(self, *args, category_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.category_id = category_id

    def validate_name(self, field):
        if exists_ci(Category, Category.name, field.data, exclude_id=self.category_id):
            raise ValidationError("Tên danh mục này đã tồn tại.")


class OrderStatusForm(FlaskForm):
    status = SelectField(
        "Trạng thái",
        choices=[(s, s) for s in ORDER_STATUSES],
        validators=[DataRequired("Vui lòng chọn trạng thái.")],
    )
