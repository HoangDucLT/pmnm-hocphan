from datetime import datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.datastructures import FileStorage

from app import db
from app.forms import BookForm, CategoryForm, OrderStatusForm
from app.models import (
    ALLOWED_TRANSITIONS,
    LOW_STOCK_THRESHOLD,
    ORDER_STATUSES,
    STATUS_CANCELLED,
    STATUS_DONE,
    STATUS_PENDING,
    Book,
    Category,
    Order,
    OrderHistory,
    OrderItem,
)
from app.utils import (
    delete_cover_image,
    like_pattern,
    redirect_back,
    save_cover_image,
)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

BOOKS_PER_PAGE = 5
ORDERS_PER_PAGE = 10


# ------------------------------------------------------------ Màn hình 6
@admin_bp.route("/")
def dashboard():
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_books = db.session.query(func.count(Book.id)).scalar()
    pending_orders = (
        db.session.query(func.count(Order.id)).filter(Order.status == STATUS_PENDING).scalar()
    )
    revenue_month = (
        db.session.query(func.coalesce(func.sum(Order.total_amount), 0))
        .filter(Order.status == STATUS_DONE, Order.created_at >= month_start)
        .scalar()
    )
    low_stock_count = (
        db.session.query(func.count(Book.id))
        .filter(Book.stock <= LOW_STOCK_THRESHOLD)
        .scalar()
    )

    latest_orders = Order.query.order_by(Order.created_at.desc(), Order.id.desc()).limit(5).all()
    low_stock_books = (
        Book.query.filter(Book.stock <= LOW_STOCK_THRESHOLD)
        .order_by(Book.stock, Book.title)
        .all()
    )

    # Doanh thu 7 ngày gần nhất (đơn Hoàn tất)
    start_day = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
    rows = (
        db.session.query(func.date(Order.created_at), func.sum(Order.total_amount))
        .filter(Order.status == STATUS_DONE, Order.created_at >= start_day)
        .group_by(func.date(Order.created_at))
        .all()
    )
    by_day = {str(day): int(total or 0) for day, total in rows}
    chart_labels, chart_values = [], []
    for i in range(7):
        day = start_day + timedelta(days=i)
        chart_labels.append(day.strftime("%d/%m"))
        chart_values.append(by_day.get(day.strftime("%Y-%m-%d"), 0))

    return render_template(
        "admin/dashboard.html",
        total_books=total_books,
        pending_orders=pending_orders,
        revenue_month=revenue_month,
        low_stock_count=low_stock_count,
        latest_orders=latest_orders,
        low_stock_books=low_stock_books,
        chart_labels=chart_labels,
        chart_values=chart_values,
        threshold=LOW_STOCK_THRESHOLD,
    )


# ------------------------------------------------------------ Màn hình 7
@admin_bp.route("/books")
def books():
    q = request.args.get("q", "").strip()
    category_id = request.args.get("category_id", type=int)
    stock_filter = request.args.get("stock", "")
    page = request.args.get("page", 1, type=int)

    query = Book.query
    if q:
        pattern = like_pattern(q)
        query = query.filter(
            or_(
                Book.title.ilike(pattern, escape="\\"),
                Book.author.ilike(pattern, escape="\\"),
            )
        )
    if category_id:
        query = query.filter(Book.category_id == category_id)
    if stock_filter == "in":
        query = query.filter(Book.stock > 0)
    elif stock_filter == "low":
        query = query.filter(Book.stock <= LOW_STOCK_THRESHOLD)
    elif stock_filter == "out":
        query = query.filter(Book.stock == 0)
    else:
        stock_filter = ""

    pagination = query.order_by(Book.created_at.desc(), Book.id.desc()).paginate(
        page=page, per_page=BOOKS_PER_PAGE, error_out=False
    )

    # Các sách trên trang hiện tại đã nằm trong đơn hàng (không được xoá)
    page_ids = [b.id for b in pagination.items]
    ordered_ids = set()
    if page_ids:
        ordered_ids = {
            row[0]
            for row in db.session.query(OrderItem.book_id)
            .filter(OrderItem.book_id.in_(page_ids))
            .distinct()
            .all()
        }

    filters = {
        k: v
        for k, v in {"q": q, "category_id": category_id, "stock": stock_filter}.items()
        if v
    }
    return render_template(
        "admin/books.html",
        pagination=pagination,
        ordered_ids=ordered_ids,
        categories=Category.query.order_by(Category.name).all(),
        filters=filters,
        q=q,
        category_id=category_id,
        stock_filter=stock_filter,
        threshold=LOW_STOCK_THRESHOLD,
    )


@admin_bp.route("/books/<int:book_id>/delete", methods=["POST"])
def book_delete(book_id):
    book = db.get_or_404(Book, book_id)

    in_orders = (
        db.session.query(func.count(OrderItem.id)).filter(OrderItem.book_id == book.id).scalar()
    )
    if in_orders:
        flash(f"Không thể xoá «{book.title}» vì sách đã có trong đơn hàng.", "danger")
        return redirect_back("admin.books")

    cover = book.cover_image
    title = book.title
    try:
        db.session.delete(book)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        flash("Không thể xoá sách lúc này. Vui lòng thử lại.", "danger")
        return redirect_back("admin.books")

    delete_cover_image(cover)
    flash(f"Đã xoá sách «{title}».", "success")
    return redirect_back("admin.books")


# ------------------------------------------------------------ Màn hình 8
@admin_bp.route("/books/new", methods=["GET", "POST"])
@admin_bp.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def book_form(book_id=None):
    book = db.get_or_404(Book, book_id) if book_id else None
    form = BookForm(obj=book, book_id=book_id)

    if form.validate_on_submit():
        is_new = book is None
        target = Book() if is_new else book

        target.title = form.title.data
        target.author = form.author.data
        target.publisher = form.publisher.data or None
        target.publish_year = form.publish_year.data
        target.price = form.price.data
        target.stock = form.stock.data
        target.category_id = form.category_id.data
        target.description = form.description.data or None

        old_cover, new_cover = None, None
        upload = form.cover_image.data
        if isinstance(upload, FileStorage) and upload.filename:
            old_cover = target.cover_image
            new_cover = save_cover_image(upload)
            target.cover_image = new_cover

        try:
            if is_new:
                db.session.add(target)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            delete_cover_image(new_cover)
            flash("Không thể lưu sách lúc này. Vui lòng thử lại.", "danger")
        else:
            if old_cover:
                delete_cover_image(old_cover)  # xoá ảnh cũ trên ổ đĩa
            flash(
                f"Đã thêm sách «{target.title}»." if is_new else f"Đã cập nhật sách «{target.title}».",
                "success",
            )
            return redirect(url_for("admin.books"))

    return render_template("admin/book_form.html", form=form, book=book)


# ------------------------------------------------------------ Màn hình 9
def _category_rows():
    # Một truy vấn duy nhất: outerjoin + group_by + count (gồm cả danh mục 0 sách)
    return (
        db.session.query(Category, func.count(Book.id).label("book_count"))
        .outerjoin(Book, Book.category_id == Category.id)
        .group_by(Category.id)
        .order_by(Category.name)
        .all()
    )


def _render_categories(form, editing=None):
    return render_template(
        "admin/categories.html", rows=_category_rows(), form=form, editing=editing
    )


@admin_bp.route("/categories", methods=["GET", "POST"])
def categories():
    form = CategoryForm()
    if form.validate_on_submit():
        try:
            db.session.add(
                Category(name=form.name.data, description=form.description.data or None)
            )
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash("Không thể thêm danh mục lúc này. Vui lòng thử lại.", "danger")
        else:
            flash(f"Đã thêm danh mục «{form.name.data}».", "success")
            return redirect(url_for("admin.categories"))
    return _render_categories(form)


@admin_bp.route("/categories/<int:category_id>/edit", methods=["GET", "POST"])
def category_edit(category_id):
    category = db.get_or_404(Category, category_id)
    form = CategoryForm(obj=category, category_id=category.id)
    if form.validate_on_submit():
        try:
            category.name = form.name.data
            category.description = form.description.data or None
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash("Không thể cập nhật danh mục lúc này. Vui lòng thử lại.", "danger")
        else:
            flash(f"Đã cập nhật danh mục «{category.name}».", "success")
            return redirect(url_for("admin.categories"))
    return _render_categories(form, editing=category)


@admin_bp.route("/categories/<int:category_id>/delete", methods=["POST"])
def category_delete(category_id):
    category = db.get_or_404(Category, category_id)
    book_count = (
        db.session.query(func.count(Book.id)).filter(Book.category_id == category.id).scalar()
    )
    if book_count > 0:
        flash(
            f"Không thể xoá danh mục «{category.name}» vì còn {book_count} sách thuộc danh mục này.",
            "danger",
        )
    else:
        name = category.name
        db.session.delete(category)
        db.session.commit()
        flash(f"Đã xoá danh mục «{name}».", "success")
    return redirect(url_for("admin.categories"))


# ------------------------------------------------------------ Màn hình 10
@admin_bp.route("/orders")
def orders():
    status = request.args.get("status", "").strip()
    if status not in ORDER_STATUSES:
        status = ""
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)

    # Số đơn mỗi trạng thái: một truy vấn group_by
    count_rows = (
        db.session.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
    )
    counts = dict(count_rows)
    all_count = sum(counts.values())

    base = Order.query
    if status:
        base = base.filter(Order.status == status)
    if q:
        pattern = like_pattern(q)
        conditions = [
            Order.customer_name.ilike(pattern, escape="\\"),
            Order.customer_phone.ilike(pattern, escape="\\"),
        ]
        order_no = q.lstrip("#")
        if order_no.isdigit() and len(order_no) <= 9:
            conditions.append(Order.id == int(order_no))
        base = base.filter(or_(*conditions))

    total_orders, total_value = base.with_entities(
        func.count(Order.id), func.coalesce(func.sum(Order.total_amount), 0)
    ).one()

    pagination = base.order_by(Order.created_at.desc(), Order.id.desc()).paginate(
        page=page, per_page=ORDERS_PER_PAGE, error_out=False
    )

    filters = {k: v for k, v in {"status": status, "q": q}.items() if v}
    return render_template(
        "admin/orders.html",
        pagination=pagination,
        filters=filters,
        status=status,
        q=q,
        statuses=ORDER_STATUSES,
        counts=counts,
        all_count=all_count,
        total_orders=total_orders,
        total_value=total_value,
    )


# ------------------------------------------------------------ Màn hình 11
@admin_bp.route("/orders/<int:order_id>")
def order_detail(order_id):
    order = db.get_or_404(Order, order_id)
    allowed = ALLOWED_TRANSITIONS.get(order.status, [])
    forward_statuses = [s for s in allowed if s != STATUS_CANCELLED]
    can_cancel = STATUS_CANCELLED in allowed
    return render_template(
        "admin/order_detail.html",
        order=order,
        form=OrderStatusForm(),
        forward_statuses=forward_statuses,
        can_cancel=can_cancel,
        cancelled_status=STATUS_CANCELLED,
    )


@admin_bp.route("/orders/<int:order_id>/status", methods=["POST"])
def order_status(order_id):
    order = db.get_or_404(Order, order_id)
    form = OrderStatusForm()
    if not form.validate_on_submit():
        flash("Yêu cầu cập nhật trạng thái không hợp lệ.", "danger")
        return redirect(url_for("admin.order_detail", order_id=order.id))

    new_status = form.status.data
    if new_status not in ALLOWED_TRANSITIONS.get(order.status, []):
        flash(f"Không thể chuyển đơn từ «{order.status}» sang «{new_status}».", "danger")
        return redirect(url_for("admin.order_detail", order_id=order.id))

    try:
        order.status = new_status
        order.history.append(OrderHistory(status=new_status))
        if new_status == STATUS_CANCELLED:
            # Huỷ đơn: hoàn lại tồn kho
            for item in order.items:
                item.book.stock += item.quantity
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        flash("Không thể cập nhật trạng thái lúc này. Vui lòng thử lại.", "danger")
        return redirect(url_for("admin.order_detail", order_id=order.id))

    if new_status == STATUS_CANCELLED:
        flash(f"Đã huỷ đơn #{order.id} và hoàn lại tồn kho.", "success")
    else:
        flash(f"Đã chuyển đơn #{order.id} sang «{new_status}».", "success")
    return redirect(url_for("admin.order_detail", order_id=order.id))
