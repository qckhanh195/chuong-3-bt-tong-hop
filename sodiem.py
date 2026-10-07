from flask import Flask, url_for, request, abort, redirect, make_response, jsonify
from markupsafe import escape
import csv
import io

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

STUDENTS = {
    "23T1020001": {"name": "Nguyễn Văn An", "lop": "K47A", "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0}},
    "23T1020002": {"name": "Trần Thị Bình", "lop": "K47A", "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}},
    "23T1020003": {"name": "Lê Hoàng Cường", "lop": "K47B", "scores": {"PMMNM": 9.5, "CSDL": 9.0}},
    "23T1020004": {"name": "Phạm Minh Dũng", "lop": "K47B", "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}},
    "23T1020005": {"name": "Hoàng Thu Hà", "lop": "K47A", "scores": {}},
    "23T1020006": {"name": "Võ Quốc Khánh", "lop": "K47C", "scores": {"PMMNM": 7.5, "MMT": 8.0}},
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
    s = STUDENTS[mssv]
    avg = average(s.get("scores", {}))
    return {
        "mssv": mssv,
        "name": s["name"],
        "lop": s["lop"],
        "scores": s.get("scores", {}),
        "average": avg,
        "rank": rank(avg)
    }

def layout(title, body):
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{escape(title)} - Sổ điểm</title>
</head>
<body>
    <nav>
        <a href="{url_for('index')}">Trang chủ</a> &middot;
        <a href="{url_for('student_list')}">Sinh viên</a> &middot;
        <a href="{url_for('search')}">Tìm kiếm</a>
    </nav>
    <hr>
    {body}
</body>
</html>"""

@app.route("/")
def index():
    total_students = len(STUDENTS)
    classes = set(s['lop'] for s in STUDENTS.values())
    total_classes = len(classes)
    
    body = f"""
    <h1>Tổng quan</h1>
    <p>Tổng số sinh viên: {total_students}</p>
    <p>Tổng số lớp: {total_classes}</p>
    <ul>
        <li><a href="{url_for('student_list')}">Danh sách sinh viên</a></li>
        <li><a href="/api/students">API danh sách sinh viên</a></li>
    </ul>
    """
    return layout("Trang chủ", body)

@app.route("/students")
def student_list():
    filter_lop = request.args.get("lop", "").upper()
    
    classes = sorted(list(set(s['lop'] for s in STUDENTS.values())))
    
    filter_links = [f'<a href="{url_for("student_list")}">Tất cả</a>']
    for c in classes:
        filter_links.append(f'<a href="{url_for("student_list", lop=c)}">{c}</a>')
    
    filter_html = " | ".join(filter_links)
    
    filtered_students = []
    for mssv, data in STUDENTS.items():
        if filter_lop and data['lop'].upper() != filter_lop:
            continue
        summary = student_summary(mssv)
        filtered_students.append(summary)
        
    if not filtered_students:
        body = f"""
        <h1>Danh sách sinh viên</h1>
        <p>Thanh lọc {filter_html}</p>
        <p>Không có sinh viên phù hợp.</p>
        """
        return layout("Danh sách sinh viên", body)
        
    table_rows = ""
    for s in filtered_students:
        avg_str = s['average'] if s['average'] is not None else "—"
        table_rows += f"""
        <tr>
            <td><a href="{url_for('student_detail', mssv=s['mssv'])}">{s['mssv']}</a></td>
            <td>{escape(s['name'])}</td>
            <td>{escape(s['lop'])}</td>
            <td>{avg_str}</td>
            <td>{s['rank']}</td>
        </tr>
        """
        
    body = f"""
    <h1>Danh sách sinh viên</h1>
    <p>Thanh lọc {filter_html}</p>
    <table border="1">
        <tr>
            <th>MSSV</th>
            <th>Họ tên</th>
            <th>Lớp</th>
            <th>Điểm TB</th>
            <th>Xếp loại</th>
        </tr>
        {table_rows}
    </table>
    """
    return layout("Danh sách sinh viên", body)

@app.route("/students/<mssv>")
def student_detail(mssv):
    summary = student_summary(mssv)
    if not summary:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
        
    scores_rows = ""
    for hp, diem in summary['scores'].items():
        scores_rows += f"""
        <tr>
            <td>{escape(hp)}</td>
            <td>{diem}</td>
        </tr>
        """
        
    if not summary['scores']:
        scores_rows = "<tr><td colspan='2'>Chưa có điểm</td></tr>"
        
    avg_str = summary['average'] if summary['average'] is not None else "Chưa có điểm"
    
    body = f"""
    <h1>{escape(summary['name'])}</h1>
    <ul>
        <li>MSSV: {summary['mssv']}</li>
        <li>Điểm TB: {avg_str}</li>
        <li>Xếp loại: {summary['rank']}</li>
        <li>Lớp: <a href="{url_for('student_list', lop=summary['lop'])}">{escape(summary['lop'])}</a></li>
    </ul>
    <h2>Bảng điểm</h2>
    <table border="1">
        <tr>
            <th>Học phần</th>
            <th>Điểm</th>
        </tr>
        {scores_rows}
    </table>
    <br>
    <a href="{url_for('student_export', mssv=mssv)}">Tải bảng điểm (CSV)</a>
    <p>Link rút gọn: <a href="{url_for('student_short_link', mssv=mssv)}">/sv/{mssv}</a></p>
    """
    return layout(f"Chi tiết {summary['name']}", body)

@app.route("/sv/<mssv>")
def student_short_link(mssv):
    return redirect(url_for('student_detail', mssv=mssv), code=301)

@app.route("/students/<mssv>/export")
def student_export(mssv):
    summary = student_summary(mssv)
    if not summary:
        abort(404)
        
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(["hoc_phan", "diem"])
    for hp, diem in summary['scores'].items():
        cw.writerow([hp, diem])
        
    output = make_response(si.getvalue())
    output.headers["Content-Type"] = "text/csv; charset=utf-8"
    output.headers["Content-Disposition"] = f"attachment; filename=diem_{mssv}.csv"
    return output

@app.route("/search")
def search():
    q = request.args.get("q", "")
    
    results = []
    if q:
        q_lower = q.lower()
        for mssv, data in STUDENTS.items():
            if q_lower in mssv.lower() or q_lower in data['name'].lower():
                results.append(student_summary(mssv))
                
    results_html = ""
    if q:
        results_html += f"<p>Tìm thấy {len(results)} kết quả cho &ldquo;{escape(q)}&rdquo;</p>"
        if results:
            results_html += "<ul>"
            for s in results:
                results_html += f"""<li><a href="{url_for('student_detail', mssv=s['mssv'])}">{s['mssv']} - {escape(s['name'])}</a></li>"""
            results_html += "</ul>"
            
    body = f"""
    <h1>Tìm kiếm sinh viên</h1>
    <form method="GET" action="{url_for('search')}">
        <input type="text" name="q" value="{escape(q)}" placeholder="Nhập từ khóa...">
        <button type="submit">Tìm kiếm</button>
    </form>
    {results_html}
    """
    return layout("Tìm kiếm", body)

@app.route("/api/students")
def api_students():
    lop = request.args.get("lop")
    if "min_avg" in request.args:
        try:
            min_avg = float(request.args.get("min_avg"))
        except (ValueError, TypeError):
            abort(400, description="min_avg không hợp lệ.")
    else:
        min_avg = None

    results = []
    for mssv in STUDENTS:
        summary = student_summary(mssv)
        
        if lop and summary['lop'].upper() != lop.upper():
            continue
            
        if min_avg is not None:
            if summary['average'] is None or summary['average'] < min_avg:
                continue
                
        results.append(summary)
        
    return jsonify(results)

@app.route("/api/students/<mssv>")
def api_student_detail(mssv):
    summary = student_summary(mssv)
    if not summary:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    return jsonify(summary)

@app.route("/api/students/<mssv>/scores/<course>", methods=["GET", "PUT", "DELETE", "POST"])
def api_manage_scores_endpoint(mssv, course):
    if request.method == "POST":
        abort(405, description="Phương thức không được hỗ trợ")
        
    if mssv not in STUDENTS:
        abort(404, description="Sinh viên không tồn tại.")
        
    course = course.upper()
    student = STUDENTS[mssv]
    scores = student.setdefault("scores", {})
    
    if request.method == "GET":
        if course not in scores:
            abort(404, description="Học phần chưa có điểm.")
        return jsonify({"mssv": mssv, "course": course, "score": scores[course]})
        
    elif request.method == "DELETE":
        if course not in scores:
            abort(404, description="Học phần chưa có điểm.")
        del scores[course]
        return "", 204
        
    elif request.method == "PUT":
        if "score" not in request.args:
            abort(400, description="Thiếu tham số score.")
        try:
            score = float(request.args.get("score"))
        except (ValueError, TypeError):
            abort(400, description="Tham số score sai kiểu.")
            
        if score < 0 or score > 10:
            abort(400, description="Tham số score ngoài khoảng [0, 10].")
            
        is_new = course not in scores
        scores[course] = score
        
        body = {
            "mssv": mssv,
            "course": course,
            "score": score,
            "average": average(scores)
        }
        
        response = jsonify(body)
        if is_new:
            response.status_code = 201
            response.headers["Location"] = request.url
        else:
            response.status_code = 200
            
        return response

@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
def handle_error(error):
    titles = {
        400: "Dữ liệu không hợp lệ",
        404: "Không tìm thấy",
        405: "Phương thức không được hỗ trợ"
    }
    code = getattr(error, "code", 500)
    title = titles.get(code, getattr(error, "name", "Lỗi máy chủ"))
    description = getattr(error, "description", "")
    
    if request.path.startswith("/api/"):
        return jsonify({
            "error": title,
            "detail": description
        }), code
    else:
        body = f"""
        <h1>{code} - {title}</h1>
        <p>{description}</p>
        """
        return layout(f"Lỗi {code}", body), code

if __name__ == "__main__":
    app.run(debug=True, port=8000)