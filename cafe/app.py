import math
from datetime import datetime
from flask import Flask, render_template, request, abort

app = Flask(__name__)

SHOP = {
    "name": "Cà phê Sông Hương",
    "address": "12 Lê Lợi, TP. Huế",
    "open_hour": 8,
    "closed_hour": 22
}

MENU = [
    {"name": "cà phê đen", "price": "20,000", "available": True},
    {"name": "bạc xỉu", "price": "25,000", "available": False},
    {"name": "cà phê sữa", "price": "25,000", "available": True},
    {"name": "trà đào", "price": "30,000", "available": True},
    {"name": "nước cam", "price": "20,000", "available": False},
    {"name": "trà sữa", "price": "35,000", "available": True},
    {"name": "sinh tố bơ", "price": "40,000", "available": True}
]

PER_PAGE = 3  # Mỗi trang 3 món

@app.route("/")
def index():
    hour = request.args.get("giờ", type=int)
    if hour is None or not (0 <= hour <= 23):
        hour = datetime.now().hour
    is_open = SHOP["open_hour"] <= hour < SHOP["closed_hour"]
    return render_template("index.html", shop=SHOP, is_open=is_open, hour=hour)

@app.route("/menu")
def menu():
    page = request.args.get("page", 1, type=int)
    total_items = len(MENU)
    if total_items == 0:
        pages = 1
        items_on_page = []
    else:
        pages = math.ceil(total_items / PER_PAGE) 
        if page < 1 or page > pages:
            abort(404)
        start = (page - 1) * PER_PAGE
        end = start + PER_PAGE
        items_on_page = MENU[start:end]
    avg_price = int(round(sum(int(item["price"].replace(",", "")) for item in MENU) / total_items, -3)) if total_items > 0 else 0
    return render_template(
        "menu.html", 
        menu=items_on_page, 
        page=page, 
        pages=pages, 
        avg_price=avg_price
    )
@app.route("/content")
def content():
    return render_template("content.html", shop=SHOP)
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
if __name__ == "__main__":
    app.run(debug=True)