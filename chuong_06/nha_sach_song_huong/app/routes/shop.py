from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.forms import CheckoutForm
from app.models import (
    STATUS_PENDING,
    Book,
    Category,
    Order,
    OrderHistory,
    OrderItem,
)
from app.utils import (
    FREE_SHIPPING_FROM,
    calc_shipping_fee,
    like_pattern,
    redirect_back,
)

shop_bp = Blueprint("shop", __name__)


# ------------------------------------------------------------ Giỏ hàng (session)
def get_cart():
    """Giỏ hàng trong session chỉ lưu {str(book_id): quantity}, không lưu giá."""
    cart = session.get("cart")
    return dict(cart) if isinstance(cart, dict) else {}


def save_cart(cart):
    session["cart"] = cart
    session.modified = True


def build_cart():
    """Dựng giỏ hàng từ session + giá/tồn kho MỚI NHẤT trong CSDL."""
    raw = get_cart()
    ids = [int(k) for k in raw if str(k).isdigit()]
    books_by_id = (
        {b.id: b for b in Book.query.filter(Book.id.in_(ids)).all()} if ids else {}
    )

    items, missing, subtotal = [], [], 0
    for key, qty in raw.items():
        try:
            book_id, qty = int(key), int(qty)
        except (TypeError, ValueError):
            missing.append(key)
            continue
        book = books_by_id.get(book_id)
        if book is None or qty < 1:
            missing.append(key)
            continue
        line_total = book.price * qty
        items.append({"book": book, "quantity": qty, "line_total": line_total})
        subtotal += line_total

    shipping_fee = calc_shipping_fee(subtotal) if items else 0
    return {
        "items": items,
        "subtotal": subtotal,
        "shipping_fee": shipping_fee,
        "total": subtotal + shipping_fee,
        "missing": missing,
    }


def prune_cart(missing):
    if not missing:
        return
    cart = get_cart()
    for key in missing:
        cart.pop(key, None)
    save_cart(cart)
    flash("Một số sách trong giỏ không còn được bán nên đã được loại khỏi giỏ hàng.", "warning")


# ------------------------------------------------------------ Màn hình 1
@shop_bp.route("/")
@shop_bp.route("/books")
def books():
    q = request.args.get("q", "").strip()
    category_id = request.args.get("category_id", type=int)

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

    book_list = query.order_by(Book.created_at.desc(), Book.id.desc()).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template(
        "shop/books.html",
        books=book_list,
        categories=categories,
        q=q,
        category_id=category_id,
    )


@shop_bp.route("/cart/add/<int:book_id>", methods=["POST"])
def cart_add(book_id):
    """Thêm nhanh 1 cuốn từ danh sách; quay lại đúng trang đang xem."""
    book = db.get_or_404(Book, book_id)
    cart = get_cart()
    in_cart = int(cart.get(str(book.id), 0))

    if book.stock <= 0:
        flash(f"«{book.title}» đã hết hàng.", "danger")
    elif in_cart + 1 > book.stock:
        flash(
            f"Trong giỏ đã có {in_cart} cuốn «{book.title}», bằng số lượng còn trong kho.",
            "warning",
        )
    else:
        cart[str(book.id)] = in_cart + 1
        save_cart(cart)
        flash(f"Đã thêm «{book.title}» vào giỏ hàng.", "success")
    return redirect_back("shop.books")


# ------------------------------------------------------------ Màn hình 2
@shop_bp.route("/books/<int:book_id>")
def book_detail(book_id):
    book = db.get_or_404(Book, book_id)
    in_cart = int(get_cart().get(str(book.id), 0))
    max_addable = max(book.stock - in_cart, 0)
    return render_template(
        "shop/book_detail.html", book=book, in_cart=in_cart, max_addable=max_addable
    )


@shop_bp.route("/books/<int:book_id>/add", methods=["POST"])
def book_add(book_id):
    book = db.get_or_404(Book, book_id)
    cart = get_cart()
    in_cart = int(cart.get(str(book.id), 0))
    max_addable = max(book.stock - in_cart, 0)

    try:
        quantity = int(request.form.get("quantity", "").strip())
    except ValueError:
        quantity = None

    if quantity is None or quantity < 1 or quantity > max_addable:
        if max_addable == 0:
            flash("Sách đã hết hàng hoặc bạn đã thêm tối đa số lượng còn trong kho.", "danger")
        else:
            flash(f"Số lượng không hợp lệ. Bạn có thể thêm từ 1 đến {max_addable} cuốn.", "danger")
    else:
        cart[str(book.id)] = in_cart + quantity
        save_cart(cart)
        flash(f"Đã thêm {quantity} cuốn «{book.title}» vào giỏ hàng.", "success")
    return redirect(url_for("shop.book_detail", book_id=book.id))


# ------------------------------------------------------------ Màn hình 3
@shop_bp.route("/cart")
def cart():
    summary = build_cart()
    if summary["missing"]:
        prune_cart(summary["missing"])
    return render_template("shop/cart.html", **summary)


@shop_bp.route("/cart/update/<int:book_id>", methods=["POST"])
def cart_update(book_id):
    action = request.form.get("action")
    if action not in ("inc", "dec"):
        abort(400)

    cart = get_cart()
    key = str(book_id)
    if key not in cart:
        flash("Sách này không có trong giỏ hàng.", "warning")
        return redirect(url_for("shop.cart"))

    book = db.session.get(Book, book_id)
    quantity = int(cart[key])

    if action == "inc":
        if book is None or quantity + 1 > book.stock:
            flash("Đã đạt số lượng tối đa còn trong kho.", "warning")
        else:
            cart[key] = quantity + 1
    else:
        if quantity - 1 <= 0:
            del cart[key]
            flash("Đã xoá sách khỏi giỏ hàng.", "info")
        else:
            cart[key] = quantity - 1

    save_cart(cart)
    return redirect(url_for("shop.cart"))


@shop_bp.route("/cart/remove/<int:book_id>", methods=["POST"])
def cart_remove(book_id):
    cart = get_cart()
    if cart.pop(str(book_id), None) is not None:
        save_cart(cart)
        flash("Đã xoá sách khỏi giỏ hàng.", "info")
    return redirect(url_for("shop.cart"))


@shop_bp.route("/cart/clear", methods=["POST"])
def cart_clear():
    session.pop("cart", None)
    flash("Đã xoá toàn bộ giỏ hàng.", "info")
    return redirect(url_for("shop.cart"))


# ------------------------------------------------------------ Màn hình 4
@shop_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    summary = build_cart()
    if summary["missing"]:
        prune_cart(summary["missing"])

    if not summary["items"]:
        flash("Giỏ hàng đang trống. Hãy chọn sách trước khi đặt hàng.", "warning")
        return redirect(url_for("shop.cart"))

    form = CheckoutForm()
    if form.validate_on_submit():
        # 1) Kiểm tra lại tồn kho thực tế trong CSDL
        shortages = []
        for item in summary["items"]:
            book = item["book"]
            db.session.refresh(book)
            if book.stock < item["quantity"]:
                shortages.append(
                    f"«{book.title}» (còn {book.stock}, bạn chọn {item['quantity']})"
                )
        if shortages:
            flash("Không đủ hàng cho: " + "; ".join(shortages) + ". Vui lòng điều chỉnh giỏ hàng.", "danger")
            return redirect(url_for("shop.cart"))

        # 2) Tạo đơn hàng, chi tiết, lịch sử và trừ tồn kho
        try:
            order = Order(
                customer_name=form.customer_name.data,
                customer_phone=form.customer_phone.data,
                customer_email=form.customer_email.data or None,
                shipping_address=form.shipping_address.data,
                note=form.note.data or None,
                payment_method=form.payment_method.data,
                subtotal=summary["subtotal"],
                shipping_fee=summary["shipping_fee"],
                total_amount=summary["total"],
                status=STATUS_PENDING,
            )
            for item in summary["items"]:
                book = item["book"]
                order.items.append(
                    OrderItem(
                        book_id=book.id,
                        quantity=item["quantity"],
                        unit_price=book.price,  # snapshot giá lúc đặt
                    )
                )
                book.stock -= item["quantity"]
            order.history.append(OrderHistory(status=STATUS_PENDING))
            db.session.add(order)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash("Không thể tạo đơn hàng lúc này. Vui lòng thử lại.", "danger")
            return redirect(url_for("shop.checkout"))

        session.pop("cart", None)
        flash("Đặt hàng thành công! Cảm ơn bạn đã mua sách tại Nhà sách Sông Hương.", "success")
        return redirect(url_for("shop.order_success", order_id=order.id))

    return render_template(
        "shop/checkout.html", form=form, free_ship_from=FREE_SHIPPING_FROM, **summary
    )


# ------------------------------------------------------------ Màn hình 5
@shop_bp.route("/orders/<int:order_id>")
def order_success(order_id):
    order = db.get_or_404(Order, order_id)
    return render_template("shop/order_success.html", order=order)
