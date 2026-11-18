import os

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFError, CSRFProtect
from sqlalchemy import func

from config import Config

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)  # Bật CSRF cho mọi form POST

    from app import models
    from app.utils import cover_url, format_datetime, format_vnd

    # ---- Blueprints ----
    from app.routes.admin import admin_bp
    from app.routes.shop import shop_bp

    app.register_blueprint(shop_bp)
    app.register_blueprint(admin_bp)

    # ---- Jinja filters / globals ----
    app.jinja_env.filters["vnd"] = format_vnd
    app.jinja_env.filters["dt"] = format_datetime
    app.jinja_env.filters["status_class"] = lambda s: models.STATUS_CLASS.get(s, "text-bg-secondary")
    app.jinja_env.filters["payment_label"] = lambda p: models.PAYMENT_METHODS.get(p, p)
    app.jinja_env.globals["cover_url"] = cover_url

    @app.context_processor
    def inject_globals():
        # Badge giỏ hàng (tổng số cuốn) cho navbar Phần A
        cart = session.get("cart")
        cart_count = 0
        if isinstance(cart, dict):
            for qty in cart.values():
                try:
                    cart_count += int(qty)
                except (TypeError, ValueError):
                    pass
        context = {"cart_count": cart_count}

        # Badge số đơn "Chờ xác nhận" cho sidebar Phần B
        if request.blueprint == "admin":
            context["pending_count"] = (
                db.session.query(func.count(models.Order.id))
                .filter(models.Order.status == models.STATUS_PENDING)
                .scalar()
            )
        return context

    # ---- Xử lý lỗi ----
    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(413)
    def too_large(error):
        flash("Tệp tải lên quá lớn. Ảnh bìa tối đa 2 MB.", "danger")
        return redirect(request.referrer or url_for("admin.books"))

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        flash("Phiên làm việc đã hết hạn hoặc yêu cầu không hợp lệ. Vui lòng thử lại.", "danger")
        return redirect(request.referrer or url_for("shop.books"))

    return app
