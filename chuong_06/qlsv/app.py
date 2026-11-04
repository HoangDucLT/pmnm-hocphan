from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)

# Cấu hình CSDL SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qlsv.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Khai báo Header trả về văn bản thuần (plain text) để không bị hiểu lầm là thẻ HTML
TEXT = {"Content-Type": "text/plain; charset=utf-8"}

# ----------------------------------------------------
# 1. Khai báo Model Student
# ----------------------------------------------------
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mssv = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    gpa = db.Column(db.Float, nullable=False)

    # Thêm __repr__ để hiển thị chuỗi dạng <Student MSSV Tên> như slide
    def __repr__(self):
        return f"<Student {self.mssv} {self.name}>"

with app.app_context():
    db.create_all()

# ----------------------------------------------------
# 2. Bước 5: Route thêm dữ liệu mẫu
# ----------------------------------------------------
@app.get("/them-mau")
def add_sample():
    total = db.session.scalar(db.select(func.count(Student.id)))
    if total > 0:
        return f"Đã có {total} sinh viên, không thêm nữa. <a href='/'>Quay lại trang chủ</a>"
    
    an = Student(mssv="23T1020001", name="Nguyễn Văn An", gpa=8.5)
    before = an.id
    
    db.session.add(an)
    db.session.add_all([
        Student(mssv="23T1020002", name="Trần Thị Bình", gpa=6.8),
        Student(mssv="23T1020003", name="Lê Hoàng Cường", gpa=9.1),
        Student(mssv="23T1020004", name="Phạm Minh Dũng", gpa=4.5),
        Student(mssv="23T1020005", name="Hoàng Thu Hà", gpa=7.4),
    ])
    
    db.session.commit()
    
    return (f"Đã thêm 5 sinh viên. id của An: "
            f"trước commit = {before}, "
            f"sau commit = {an.id}. <br><br>"
            f"<a href='/'>Đi đến trang xem danh sách</a>")

# ----------------------------------------------------
# 3. Bước 6 (Trên Slide): Đọc dữ liệu bằng view function
# ----------------------------------------------------
@app.get("/thu-truy-van")
def try_queries():
    # Kiểm tra xem đã có dữ liệu chưa
    if db.session.scalar(db.select(func.count(Student.id))) == 0:
        return "Chưa có dữ liệu, hãy mở /them-mau trước."
    
    lines = []
    # 1. Lấy theo ID chính xác
    lines.append(f"1. get(3): {db.session.get(Student, 3)}")
    lines.append(f"2. get(99): {db.session.get(Student, 99)}")
    
    # 2. Lấy tất cả danh sách sinh viên
    everyone = db.session.execute(db.select(Student)).scalars().all()
    lines.append(f"3. Tất cả: {len(everyone)} sinh viên")
    
    # 3. Lọc theo điều kiện GPA >= 8 và sắp xếp giảm dần
    stmt = (db.select(Student)
            .where(Student.gpa >= 8)
            .order_by(Student.gpa.desc()))
    good = db.session.execute(stmt).scalars().all()
    lines.append(f"4. Điểm >= 8: {good}")
    
    # 4. Tìm kiếm theo MSSV
    binh = db.session.scalar(db.select(Student).filter_by(mssv="23T1020002"))
    lines.append(f"5. MSSV 23T1020002: {binh}")
    
    # 5. Đếm số lượng và tính GPA trung bình
    count = db.session.scalar(db.select(func.count(Student.id)))
    avg = db.session.scalar(db.select(func.avg(Student.gpa)))
    lines.append(f"6. Số SV: {count}, điểm TB: {avg:.2f}")
    
    # Trả về kết quả nối các dòng bằng ký tự xuống dòng '\n' và kèm header plain text
    return "\n".join(lines), TEXT

# ----------------------------------------------------
# Trang chủ xem giao diện HTML
# ----------------------------------------------------
@app.get("/")
def index():
    students = db.session.scalars(db.select(Student).order_by(Student.gpa.desc())).all()
    return render_template("danh_sach.html", students=students, title="Tất Cả Sinh Viên", loai="all")
# ----------------------------------------------------
# Route mới: Lọc và hiển thị Bảng Sinh viên Giỏi (GPA >= 8.0)
# ----------------------------------------------------
# ----------------------------------------------------
# Route phân loại sinh viên: Giỏi / Khá / Trung Bình / Yếu
# ----------------------------------------------------
@app.get("/danh-sach/<loai>")
def student_by_rank(loai):
    if loai == "gioi":
        title = "Danh Sách Sinh Viên Giỏi (GPA ≥ 8.0)"
        stmt = db.select(Student).where(Student.gpa >= 8.0)
    elif loai == "kha":
        title = "Danh Sách Sinh Viên Khá (6.5 ≤ GPA < 8.0)"
        stmt = db.select(Student).where(Student.gpa >= 6.5, Student.gpa < 8.0)
    elif loai == "trung-binh":
        title = "Danh Sách Sinh Viên Trung Bình (5.0 ≤ GPA < 6.5)"
        stmt = db.select(Student).where(Student.gpa >= 5.0, Student.gpa < 6.5)
    elif loai == "yeu":
        title = "Danh Sách Sinh Viên Yếu (GPA < 5.0)"
        stmt = db.select(Student).where(Student.gpa < 5.0)
    else:
        return "Loại xếp loại không hợp lệ!", 404

    # Sắp xếp điểm giảm dần
    students = db.session.scalars(stmt.order_by(Student.gpa.desc())).all()
    
    return render_template("danh_sach.html", students=students, title=title, loai=loai)

if __name__ == "__main__":
    app.run(debug=True)