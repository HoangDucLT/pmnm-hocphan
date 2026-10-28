from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from flask import Flask, render_template, request

app = Flask(__name__)

# (tên trường, nhãn hiển thị, tên dùng trong lỗi, giá trị nhỏ nhất, lớn nhất)
CAC_O = [
    ("cao", "Chiều cao (cm)", "chiều cao", 50, 250),
    ("nang", "Cân nặng (kg)", "cân nặng", 10, 300),
]


def kiem_tra(text, ten_o, nho_nhat, lon_nhat):
    """Hàm kiểm tra dùng chung cho cả 2 ô.
    Trả về (số, None) nếu hợp lệ, hoặc (None, thông báo lỗi) nếu sai."""
    text = (text or "").strip().replace(",", ".")
    try:
        so = Decimal(text)
    except InvalidOperation:
        return None, f"Lỗi ô {ten_o}: Vui lòng nhập một số."
    if not so.is_finite():            # loại "nan", "inf"
        return None, f"Lỗi ô {ten_o}: Vui lòng nhập một số."
    if so < nho_nhat or so > lon_nhat:
        return None, f"Lỗi ô {ten_o}: Giá trị phải từ {nho_nhat} đến {lon_nhat}."
    return so, None


def lam_tron(x):
    """Làm tròn 1 chữ số thập phân (giống hàm round của Python)."""
    return x.quantize(Decimal("0.1"), rounding=ROUND_HALF_EVEN)


def phan_loai(bmi):
    """Chuẩn người châu Á. Trả về (tên nhóm, màu)."""
    if bmi < Decimal("18.5"):
        return "Thiếu cân", "vang"
    if bmi < 23:
        return "Bình thường", "xanh"
    if bmi < 25:
        return "Thừa cân", "vang"
    return "Béo phì", "do"


@app.route("/", methods=["GET", "POST"])
def index():
    form = {ma: "" for ma, *_ in CAC_O}
    errors = {}
    result = None

    if request.method == "POST":
        so = {}
        for ma, _, ten_o, nho, lon in CAC_O:
            form[ma] = request.form.get(ma, "")
            gia_tri, loi = kiem_tra(form[ma], ten_o, nho, lon)
            if loi:
                errors[ma] = loi
            else:
                so[ma] = gia_tri

        if not errors:
            cao_m = so["cao"] / 100                 # đổi cm -> m
            bmi = lam_tron(so["nang"] / (cao_m * cao_m))
            nhom, mau = phan_loai(bmi)
            result = {
                "bmi": str(bmi),
                "nhom": nhom,
                "mau": mau,
                # cân nặng ứng với BMI 18,5 - 22,9
                "nen_co_tu": str(lam_tron(Decimal("18.5") * cao_m * cao_m)),
                "nen_co_den": str(lam_tron(Decimal("22.9") * cao_m * cao_m)),
            }

    return render_template("index.html", cac_o=CAC_O, form=form, errors=errors, result=result)


if __name__ == "__main__":
    app.run(debug=True)