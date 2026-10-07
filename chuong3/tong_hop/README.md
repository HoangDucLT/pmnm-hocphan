# BÀI TẬP TỔNG HỢP CHƯƠNG 3 - SỔ ĐIỂM LỚP HỌC

## 1. Kết quả lệnh `flask --app sodiem routes`

```text
Endpoint             Methods  Rule
-------------------  -------  -----------------------------------------
api_course_score     DELETE   /api/students/<mssv>/scores/<course>
api_course_score     GET      /api/students/<mssv>/scores/<course>
api_course_score     PUT      /api/students/<mssv>/scores/<course>
api_student_detail   GET      /api/students/<mssv>
api_students         GET      /api/students
export_student_csv   GET      /students/<mssv>/export
index                GET      /
search               GET      /search
short_student_detail GET      /sv/<mssv>
static               GET      /static/<path:filename>
student_detail       GET      /students/<mssv>
student_list         GET      /students