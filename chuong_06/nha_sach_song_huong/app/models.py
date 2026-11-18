from datetime import datetime

from app import db

# ---- Hằng số nghiệp vụ ----
STATUS_PENDING = "Chờ xác nhận"
STATUS_SHIPPING = "Đang giao"
STATUS_DONE = "Hoàn tất"
STATUS_CANCELLED = "Đã huỷ"

ORDER_STATUSES = [STATUS_PENDING, STATUS_SHIPPING, STATUS_DONE, STATUS_CANCELLED]

# Máy trạng thái: trạng thái hiện tại -> các trạng thái được phép chuyển tới
ALLOWED_TRANSITIONS = {
    STATUS_PENDING: [STATUS_SHIPPING, STATUS_CANCELLED],
    STATUS_SHIPPING: [STATUS_DONE, STATUS_CANCELLED],
    STATUS_DONE: [],
    STATUS_CANCELLED: [],
}

STATUS_CLASS = {
    STATUS_PENDING: "text-bg-warning",
    STATUS_SHIPPING: "text-bg-info",
    STATUS_DONE: "text-bg-success",
    STATUS_CANCELLED: "text-bg-secondary",
}

PAYMENT_METHODS = {
    "COD": "Tiền mặt khi nhận hàng",
    "BANK": "Chuyển khoản",
}

LOW_STOCK_THRESHOLD = 5


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    books = db.relationship("Book", backref="category", lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), unique=True, nullable=False)
    author = db.Column(db.String(150), nullable=False)
    publisher = db.Column(db.String(150), nullable=True)
    publish_year = db.Column(db.Integer, nullable=True)
    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text, nullable=True)
    cover_image = db.Column(db.String(255), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)

    order_items = db.relationship("OrderItem", backref="book", lazy=True)

    def __repr__(self):
        return f"<Book {self.title}>"


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(10), nullable=False)
    customer_email = db.Column(db.String(120), nullable=True)
    shipping_address = db.Column(db.Text, nullable=False)
    note = db.Column(db.Text, nullable=True)
    payment_method = db.Column(db.String(10), nullable=False)
    subtotal = db.Column(db.Integer, nullable=False)
    shipping_fee = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(30), nullable=False, default=STATUS_PENDING, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)

    items = db.relationship(
        "OrderItem", backref="order", lazy=True, cascade="all, delete-orphan"
    )
    history = db.relationship(
        "OrderHistory",
        backref="order",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="OrderHistory.changed_at, OrderHistory.id",
    )

    def __repr__(self):
        return f"<Order #{self.id}>"


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    # Snapshot đơn giá tại thời điểm đặt hàng
    unit_price = db.Column(db.Integer, nullable=False)

    @property
    def line_total(self):
        return self.unit_price * self.quantity


class OrderHistory(db.Model):
    __tablename__ = "order_history"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    status = db.Column(db.String(30), nullable=False)
    changed_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
