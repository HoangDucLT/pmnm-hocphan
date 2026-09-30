from flask import Flask, request, url_for

app = Flask(__name__)
# Request
@app.route("/home")
@app.route("/index")
@app.route("/")
def index():
    return f"<a href='{url_for('index')}'>Trang chủ</a><a href='{url_for('gioi_thieu')}'>Giới thiệu</a><a href='{url_for('user_profile', username='Nguyen Van A')}'>User profile</a><a href='{url_for('square', x=5)}'>Square</a><a href='{url_for('tong', strs='1,2,3,4,5')}'>Sum</a><a href='{url_for('tinh_toan')}?a=10&b=5&op=add'>Tính toán</a>"

@app.route("/gioithieu")
def gioi_thieu():
    return "xin chào, đây là trang giới thiệu"
@app.route("/user/<username>")
def user_profile(username):
    return f"xin chào, {username}!"
@app.route("/square/<x>")
def square(x):
    return f"{float(x)}^2 = {float(x)**2}"
@app.route("/sum/<strs>")
def tong(strs):
    numbers = strs.split(",")
    total = sum(float(num) for num in numbers)
    return f"Tổng của {strs} là : {total}"
@app.route("/tinh-toan")
def tinh_toan():
    a = request.args.get("a")
    b = request.args.get("b")
    op = request.args.get("op")
    if op == "add":
        return f"Tổng của a và b : {float(a) + float(b)}"
    elif op == "sub":
        return f"Hiệu của a và b : {float(a) - float(b)}"
    else:
        return f"Phép toán không hợp lệ"

if __name__ == '__main__':
    app.run(debug=True)