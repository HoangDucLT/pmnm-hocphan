from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from flask import Flask, render_template, request

app = Flask(__name__)

# (tên trường trong form, nhãn hiển thị, tên ngắn dùng trong thông báo lỗi, hệ số)
CAC_O = [
    ("cc", "Chuyên cần (10%)", "CC", Decimal("0.1")),
    ("gk", "Giữa kỳ (30%)", "GK", Decimal("0.3")),
    ("ck", "Cuối kỳ (60%)", "CK", Decimal("0.6")),
]


def kiem_tra_diem(text, ten_o):
    """Hàm kiểm tra DÙNG CHUNG cho cả 3 ô.
    Trả về (điểm, None) nếu hợp lệ, hoặc (None, thông báo lỗi) nếu sai."""
    text = (text or "").strip().replace(",", ".")
    loi_so = f"Lỗi ô {ten_o}: Vui lòng nhập một số."
    try:
        diem = Decimal(text)
    except InvalidOperation:
        return None, loi_so
    if not diem.is_finite():          # loại "nan", "inf"
        return None, loi_so
    if diem < 0 or diem > 10:
        return None, f"Lỗi ô {ten_o}: Điểm phải từ 0 đến 10."
    return diem, None


def xep_loai(diem, diem_ck):
    if diem_ck < 1:                   # điểm liệt
        return "F"
    if diem >= Decimal("8.5"):
        return "A"
    if diem >= Decimal("7.0"):
        return "B"
    if diem >= Decimal("5.5"):
        return "C"
    if diem >= Decimal("4.0"):
        return "D"
    return "F"


@app.route("/", methods=["GET", "POST"])
def index():
    form = {ma: "" for ma, _, _, _ in CAC_O}
    errors = {}
    result = None

    if request.method == "POST":
        diem_so = {}
        for ma, _, ten_o, _ in CAC_O:
            form[ma] = request.form.get(ma, "")
            diem, loi = kiem_tra_diem(form[ma], ten_o)
            if loi:
                errors[ma] = loi
            else:
                diem_so[ma] = diem

        if not errors:
            tong = sum(diem_so[ma] * he_so for ma, _, _, he_so in CAC_O)
            tong = tong.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)  # làm tròn 1 chữ số
            chu = xep_loai(tong, diem_so["ck"])
            result = {
                "diem": str(tong),
                "chu": chu,
                "liet": diem_so["ck"] < 1,
            }

    return render_template("index.html", cac_o=CAC_O, form=form, errors=errors, result=result)


if __name__ == "__main__":
    app.run(debug=True)