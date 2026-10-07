from flask import Flask, request as req, url_for
from markupsafe import escape

app = Flask(__name__)

STUDENTS = {
    "23T1020001": {
        "name": "Nguyễn Văn An",
        "lop": "K47A",
        "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0},
    },
    "23T1020002": {
        "name": "Trần Thị Bình",
        "lop": "K47A",
        "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0},
    },
    "23T1020003": {
        "name": "Lê Hoàng Cường",
        "lop": "K47B",
        "scores": {"PMMNM": 9.5, "CSDL": 9.0},
    },
    "23T1020004": {
        "name": "Phạm Minh Dũng",
        "lop": "K47B",
        "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0},
    },
    "23T1020005": {"name": "Hoàng Thu Hà", "lop": "K47A", "scores": {}},
    "23T1020006": {
        "name": "Võ Quốc Khánh",
        "lop": "K47C",
        "scores": {"PMMNM": 7.5, "MMT": 8.0},
    },
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
    student = STUDENTS.get(mssv)
    if not student:
        return None

    avg = average(student["scores"])
    return {
        "mssv": mssv,
        "name": student["name"],
        "lop": student["lop"],
        "scores": student["scores"],
        "average": avg,
        "rank": rank(avg),
    }


def layout(title, body):
    escaped_title = escape(title)
    home_url = url_for("home")
    students_url = url_for("student_list")
    search_url = url_for("search")

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>{escaped_title} - Sổ điểm</title>
</head>
<body>
    <nav>
        <a href="{home_url}">Trang chủ</a> · 
        <a href="{students_url}">Sinh viên</a> · 
        <a href="{search_url}">Tìm kiếm</a>
    </nav>
    <hr>
    <main>
        {body}
    </main>
</body>
</html>"""

@app.route("/")
def home():
    return layout("Trang chủ", "<h1>Chào mừng đến với Sổ điểm</h1>")


@app.route("/students")
def student_list():
    return layout("Danh sách sinh viên", "<p>Nội dung danh sách sinh viên...</p>")


@app.route("/search")
def search():
    return layout("Tìm kiếm", "<p>Form tìm kiếm...</p>")


if __name__ == "__main__":
    print(student_summary("23T1020001"))
    print(student_summary("23T1020005"))
    app.run(debug=True)