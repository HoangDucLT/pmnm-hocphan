from flask import Flask, render_template, jsonify, abort, request

app = Flask(__name__)

BOOKS = [
    {
        "id": 1,
        "title": "Lập trình Python",
        "author": "Nguyễn Văn A",
        "year": 2024,
        "category": "Lập trình",
        "available": True
    },
    {
        "id": 2,
        "title": "Lập trình Flask",
        "author": "Trần Văn B",
        "year": 2023,
        "category": "Lập trình",
        "available": True
    },
    {
        "id": 3,
        "title": "Cơ sở dữ liệu",
        "author": "Lê Văn C",
        "year": 2022,
        "category": "Cơ sở dữ liệu",
        "available": False
    },
    {
        "id": 4,
        "title": "HTML và CSS",
        "author": "Phạm Văn D",
        "year": 2024,
        "category": "Web",
        "available": True
    },
    {
        "id": 5,
        "title": "Java cơ bản",
        "author": "Hoàng Văn E",
        "year": 2021,
        "category": "Lập trình",
        "available": False
    }
]


def find_book(book_id):
    for book in BOOKS:
        if book["id"] == book_id:
            return book
    return None


@app.route("/")
def index():
    total = len(BOOKS)

    available = 0

    for book in BOOKS:
        if book["available"]:
            available += 1

    return render_template(
        "index.html",
        total=total,
        available=available
    )


@app.route("/books")
def books():
    category = request.args.get("category")

    if category:
        ds_sach = []

        for book in BOOKS:
            if book["category"] == category:
                ds_sach.append(book)
    else:
        ds_sach = BOOKS

    categories = []

    for book in BOOKS:
        if book["category"] not in categories:
            categories.append(book["category"])

    return render_template(
        "books.html",
        books=ds_sach,
        categories=categories,
        selected_category=category
    )


@app.route("/books/<int:book_id>")
def book_detail(book_id):
    book = find_book(book_id)

    if book is None:
        abort(404)

    return render_template("book_detail.html", book=book)


@app.route("/api/books/<int:book_id>")
def api_book(book_id):
    book = find_book(book_id)

    if book is None:
        return jsonify({"error": "Không có sách với ID = " + str(book_id)}), 404

    return jsonify(book)


@app.route("/about")
def about():
    return """
    <h1>LibraryMS v0.1</h1>
    <p>Hệ thống quản lý thư viện đơn giản bằng Flask.</p>
    """


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)