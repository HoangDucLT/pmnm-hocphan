from flask import Flask, render_template, request

app = Flask(__name__)

OPS = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "*": lambda x, y: x * y,
    "/": lambda x, y: x / y,
}


def parse_number(text):
    """Chuyển chuỗi thành số, chấp nhận dấu phẩy thập phân (2,5). Lỗi -> None."""
    text = (text or "").strip().replace(",", ".")
    try:
        value = float(text)
    except ValueError:
        return None
    # float("nan") / float("inf") hợp lệ với Python nhưng không phải số nhập thông thường
    if value != value or value in (float("inf"), float("-inf")):
        return None
    return value


def fmt(n):
    """In số gọn: 8.0 -> 8, 3.5 -> 3.5"""
    return str(int(n)) if n == int(n) else str(round(n, 10))


@app.route("/", methods=["GET", "POST"])
def index():
    # Giá trị mặc định khi mở trang lần đầu
    form = {"a": "", "op": "+", "b": ""}
    errors = {}
    result = None

    if request.method == "POST":
        form["a"] = request.form.get("a", "")
        form["op"] = request.form.get("op", "+")
        form["b"] = request.form.get("b", "")

        a = parse_number(form["a"])
        b = parse_number(form["b"])

        if a is None:
            errors["a"] = "Vui lòng nhập một số."
        if b is None:
            errors["b"] = "Vui lòng nhập một số."
        if form["op"] not in OPS:
            errors["op"] = "Phép toán không hợp lệ."

        # Chia cho 0 (chỉ kiểm tra khi b đã hợp lệ)
        if not errors and form["op"] == "/" and b == 0:
            errors["b"] = "Không thể chia cho 0."

        if not errors:
            value = OPS[form["op"]](a, b)
            result = f"{fmt(a)} {form['op']} {fmt(b)} = {fmt(value)}"

    return render_template("index.html", form=form, errors=errors, result=result)


if __name__ == "__main__":
    app.run(debug=True)