from flask import (
    Flask, request, jsonify, redirect, url_for, 
    abort, make_response, render_template
)

app = Flask(__name__)

# Cấu hình JSON tiếng Việt có dấu
app.config['JSON_AS_ASCII'] = False
app.json.ensure_ascii = False

# Dữ liệu mẫu
STUDENTS = {
    "23T1020001": {
        "name": "Nguyễn Văn An",
        "lop": "K47A",
        "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0}
    },
    "23T1020002": {
        "name": "Trần Thị Bình",
        "lop": "K47A",
        "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}
    },
    "23T1020003": {
        "name": "Lê Hoàng Cường",
        "lop": "K47B",
        "scores": {"PMMNM": 9.5, "CSDL": 9.0}
    },
    "23T1020004": {
        "name": "Phạm Minh Dũng",
        "lop": "K47B",
        "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}
    },
    "23T1020005": {
        "name": "Hoàng Thu Hà",
        "lop": "K47A",
        "scores": {}
    },
    "23T1020006": {
        "name": "Võ Quốc Khánh",
        "lop": "K47C",
        "scores": {"PMMNM": 7.5, "MMT": 8.0}
    }
}

def average(scores):
    if not scores:
        return None
    return round(sum(scores.values()) / len(scores), 2)

def rank(avg):
    if avg is None:
        return "Chưa có điểm"
    if avg >= 8.5:
        return "Giỏi"
    if avg >= 7.0:
        return "Khá"
    if avg >= 5.0:
        return "Trung bình"
    return "Yếu"

def student_summary(mssv):
    if mssv not in STUDENTS:
        return None
    data = STUDENTS[mssv]
    avg = average(data["scores"])
    return {
        "mssv": mssv,
        "name": data["name"],
        "lop": data["lop"],
        "scores": data["scores"],
        "average": avg,
        "rank": rank(avg)
    }

@app.route("/")
def index():
    total_students = len(STUDENTS)
    classes = set(s["lop"] for s in STUDENTS.values())
    total_classes = len(classes)
    return render_template("index.html", title="Trang chủ", total_students=total_students, total_classes=total_classes)

@app.route("/students")
def student_list():
    lop_filter = request.args.get("lop", "").strip()
    all_classes = sorted(list(set(s["lop"] for s in STUDENTS.values())))
    filtered_students = [student_summary(m) for m, data in STUDENTS.items() if not lop_filter or data["lop"].upper() == lop_filter.upper()]
    return render_template("student_list.html", title="Danh sách sinh viên", students=filtered_students, all_classes=all_classes, current_lop=lop_filter)

@app.route("/students/<mssv>")
def student_detail(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    info = student_summary(mssv)
    return render_template("student_detail.html", title=f"Chi tiết sinh viên - {info['name']}", info=info, host_url=request.host_url)

@app.route("/sv/<mssv>")
def short_student_detail(mssv):
    return redirect(url_for('student_detail', mssv=mssv), code=301)

@app.route("/students/<mssv>/export")
def export_student_csv(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    scores = STUDENTS[mssv]["scores"]
    lines = ["hoc_phan,diem"] + [f"{c},{s}" for c, s in scores.items()]
    response = make_response("\n".join(lines))
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=diem_{mssv}.csv"
    return response

@app.route("/search")
def search():
    q = request.args.get("q", "")
    results = []
    if q.strip():
        q_lower = q.strip().lower()
        results = [student_summary(m) for m, d in STUDENTS.items() if q_lower in m.lower() or q_lower in d["name"].lower()]
    return render_template("search.html", title="Tìm kiếm sinh viên", q=q, results=results)

@app.route("/api/students", methods=["GET"])
def api_students():
    lop_filter = request.args.get("lop", "").strip()
    min_avg_raw = request.args.get("min_avg")
    min_avg = None
    if min_avg_raw is not None:
        try:
            min_avg = float(min_avg_raw)
        except ValueError:
            abort(400, description="Tham số min_avg phải là một số thực hợp lệ.")
            
    res = []
    for mssv in STUDENTS:
        info = student_summary(mssv)
        if lop_filter and info["lop"].upper() != lop_filter.upper():
            continue
        if min_avg is not None and (info["average"] is None or info["average"] < min_avg):
            continue
        res.append(info)
    return jsonify(res)

@app.route("/api/students/<mssv>", methods=["GET"])
def api_student_detail(mssv):
    info = student_summary(mssv)
    if info is None:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    return jsonify(info)

@app.route("/api/students/<mssv>/scores/<course>", methods=["GET", "PUT", "DELETE"])
def api_course_score(mssv, course):
    course_upper = course.upper()
    if mssv not in STUDENTS:
        abort(404, description=f"Không tìm thấy sinh viên với MSSV = {mssv}.")
        
    student_scores = STUDENTS[mssv]["scores"]
    
    if request.method == "GET":
        if course_upper not in student_scores:
            abort(404, description=f"Sinh viên không có điểm môn {course_upper}.")
        return jsonify({"mssv": mssv, "course": course_upper, "score": student_scores[course_upper]})
        
    elif request.method == "PUT":
        score_raw = request.args.get("score")
        if score_raw is None:
            abort(400, description="Thiếu tham số 'score'.")
        try:
            score = float(score_raw)
        except ValueError:
            abort(400, description="Tham số 'score' phải là số.")
            
        if score < 0 or score > 10:
            abort(400, description="Điểm 'score' phải nằm trong khoảng từ 0 đến 10.")
            
        is_new = course_upper not in student_scores
        student_scores[course_upper] = score
        response_data = {"mssv": mssv, "course": course_upper, "score": score, "average": average(student_scores)}
        
        if is_new:
            resp = make_response(jsonify(response_data), 201)
            resp.headers["Location"] = url_for('api_course_score', mssv=mssv, course=course_upper)
            return resp
        return jsonify(response_data), 200
            
    elif request.method == "DELETE":
        if course_upper not in student_scores:
            abort(404, description=f"Không tìm thấy điểm môn {course_upper} để xóa.")
        del student_scores[course_upper]
        return "", 204
@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
def handle_error(error):
    status_code = getattr(error, 'code', 500)
    title_map = {400: "Dữ liệu không hợp lệ", 404: "Không tìm thấy", 405: "Phương thức không được hỗ trợ"}
    title = title_map.get(status_code, "Lỗi hệ thống")
    description = getattr(error, 'description', str(error))
    
    if request.path.startswith("/api/"):
        return jsonify({"error": title, "detail": description}), status_code
    return render_template("error.html", title=f"Lỗi {status_code} - {title}", status_code=status_code, description=description), status_code

if __name__ == "__main__":
    app.run(port=8000, debug=True)