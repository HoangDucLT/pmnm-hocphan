import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, g

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "library.db")

app = Flask(__name__)
app.secret_key = "kiemtra-opensource-secret"


# ---------------------- Kết nối CSDL SQLite ----------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")  # bật ràng buộc khóa ngoại
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        );
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            price REAL DEFAULT 0,
            quantity INTEGER DEFAULT 0,
            year INTEGER,
            category_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
        );
        """
    )
    db.commit()
    db.close()


# ---------------------- Dashboard ----------------------
@app.route("/")
def dashboard():
    db = get_db()
    total_categories = db.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    total_books = db.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    total_quantity = db.execute("SELECT COALESCE(SUM(quantity),0) FROM books").fetchone()[0]
    total_value = db.execute("SELECT COALESCE(SUM(price*quantity),0) FROM books").fetchone()[0]
    stats = db.execute(
        """SELECT c.id, c.name, COUNT(b.id) AS book_count,
                  COALESCE(SUM(b.quantity),0) AS qty
           FROM categories c LEFT JOIN books b ON b.category_id = c.id
           GROUP BY c.id ORDER BY book_count DESC"""
    ).fetchall()
    latest_books = db.execute(
        """SELECT b.*, c.name AS category_name FROM books b
           JOIN categories c ON c.id = b.category_id
           ORDER BY b.id DESC LIMIT 5"""
    ).fetchall()
    return render_template(
        "dashboard.html",
        total_categories=total_categories,
        total_books=total_books,
        total_quantity=total_quantity,
        total_value=total_value,
        stats=stats,
        latest_books=latest_books,
    )


# ---------------------- CRUD Danh mục ----------------------
@app.route("/categories")
def categories():
    q = request.args.get("q", "").strip()
    db = get_db()
    rows = db.execute(
        """SELECT c.*, COUNT(b.id) AS book_count FROM categories c
           LEFT JOIN books b ON b.category_id = c.id
           WHERE c.name LIKE ? GROUP BY c.id ORDER BY c.id DESC""",
        (f"%{q}%",),
    ).fetchall()
    return render_template("categories.html", categories=rows, q=q)


@app.route("/categories/add", methods=["GET", "POST"])
def category_add():
    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form.get("description", "").strip()
        if not name:
            flash("Tên danh mục không được để trống!", "danger")
            return render_template("category_form.html", category=None)
        try:
            db = get_db()
            db.execute("INSERT INTO categories (name, description) VALUES (?, ?)", (name, description))
            db.commit()
            flash("Thêm danh mục thành công!", "success")
            return redirect(url_for("categories"))
        except sqlite3.IntegrityError:
            flash("Tên danh mục đã tồn tại!", "danger")
    return render_template("category_form.html", category=None)


@app.route("/categories/<int:cid>/edit", methods=["GET", "POST"])
def category_edit(cid):
    db = get_db()
    category = db.execute("SELECT * FROM categories WHERE id = ?", (cid,)).fetchone()
    if category is None:
        flash("Không tìm thấy danh mục!", "danger")
        return redirect(url_for("categories"))
    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form.get("description", "").strip()
        if not name:
            flash("Tên danh mục không được để trống!", "danger")
            return render_template("category_form.html", category=category)
        try:
            db.execute("UPDATE categories SET name=?, description=? WHERE id=?", (name, description, cid))
            db.commit()
            flash("Cập nhật danh mục thành công!", "success")
            return redirect(url_for("categories"))
        except sqlite3.IntegrityError:
            flash("Tên danh mục đã tồn tại!", "danger")
    return render_template("category_form.html", category=category)


@app.route("/categories/<int:cid>/delete", methods=["POST"])
def category_delete(cid):
    db = get_db()
    db.execute("DELETE FROM categories WHERE id = ?", (cid,))  # sách thuộc danh mục bị xóa theo (CASCADE)
    db.commit()
    flash("Đã xóa danh mục và các sách thuộc danh mục!", "success")
    return redirect(url_for("categories"))


# ---------------------- CRUD Sách theo danh mục ----------------------
@app.route("/categories/<int:cid>/books")
def books(cid):
    db = get_db()
    category = db.execute("SELECT * FROM categories WHERE id = ?", (cid,)).fetchone()
    if category is None:
        flash("Không tìm thấy danh mục!", "danger")
        return redirect(url_for("categories"))
    q = request.args.get("q", "").strip()
    rows = db.execute(
        """SELECT * FROM books WHERE category_id = ? AND (title LIKE ? OR author LIKE ?)
           ORDER BY id DESC""",
        (cid, f"%{q}%", f"%{q}%"),
    ).fetchall()
    return render_template("books.html", category=category, books=rows, q=q)


@app.route("/categories/<int:cid>/books/add", methods=["GET", "POST"])
def book_add(cid):
    db = get_db()
    category = db.execute("SELECT * FROM categories WHERE id = ?", (cid,)).fetchone()
    if category is None:
        return redirect(url_for("categories"))
    if request.method == "POST":
        data = _read_book_form()
        if not data["title"] or not data["author"]:
            flash("Tên sách và tác giả không được để trống!", "danger")
            return render_template("book_form.html", category=category, book=None)
        db.execute(
            """INSERT INTO books (title, author, price, quantity, year, category_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (data["title"], data["author"], data["price"], data["quantity"], data["year"], cid),
        )
        db.commit()
        flash("Thêm sách thành công!", "success")
        return redirect(url_for("books", cid=cid))
    return render_template("book_form.html", category=category, book=None)


@app.route("/books/<int:bid>/edit", methods=["GET", "POST"])
def book_edit(bid):
    db = get_db()
    book = db.execute("SELECT * FROM books WHERE id = ?", (bid,)).fetchone()
    if book is None:
        flash("Không tìm thấy sách!", "danger")
        return redirect(url_for("categories"))
    category = db.execute("SELECT * FROM categories WHERE id = ?", (book["category_id"],)).fetchone()
    if request.method == "POST":
        data = _read_book_form()
        if not data["title"] or not data["author"]:
            flash("Tên sách và tác giả không được để trống!", "danger")
            return render_template("book_form.html", category=category, book=book)
        db.execute(
            """UPDATE books SET title=?, author=?, price=?, quantity=?, year=? WHERE id=?""",
            (data["title"], data["author"], data["price"], data["quantity"], data["year"], bid),
        )
        db.commit()
        flash("Cập nhật sách thành công!", "success")
        return redirect(url_for("books", cid=book["category_id"]))
    return render_template("book_form.html", category=category, book=book)


@app.route("/books/<int:bid>/delete", methods=["POST"])
def book_delete(bid):
    db = get_db()
    book = db.execute("SELECT category_id FROM books WHERE id = ?", (bid,)).fetchone()
    if book is None:
        return redirect(url_for("categories"))
    db.execute("DELETE FROM books WHERE id = ?", (bid,))
    db.commit()
    flash("Đã xóa sách!", "success")
    return redirect(url_for("books", cid=book["category_id"]))


def _read_book_form():
    def to_int(v, default=0):
        try:
            return int(v)
        except (TypeError, ValueError):
            return default

    def to_float(v, default=0.0):
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    return {
        "title": request.form.get("title", "").strip(),
        "author": request.form.get("author", "").strip(),
        "price": to_float(request.form.get("price")),
        "quantity": to_int(request.form.get("quantity")),
        "year": to_int(request.form.get("year"), None),
    }


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
