# CHƯƠNG 3 · BÀI TẬP TỔNG HỢP

## 1. Kết quả flask --app sodiem routes
```
Endpoint                    Methods                 Rule
--------------------------  ----------------------  ---------------------------------------------
api_manage_scores_endpoint  DELETE, GET, PUT        /api/students/<mssv>/scores/<course>
api_student_detail          GET                     /api/students/<mssv>
api_students                GET                     /api/students
index                       GET                     /
search                      GET                     /search
static                      GET                     /static/<path:filename>
student_detail              GET                     /students/<mssv>
student_export              GET                     /students/<mssv>/export
student_list                GET                     /students
student_short_link          GET                     /sv/<mssv>
```

## 2. Các lệnh curl và kết quả
Thực thi các lệnh curl sẽ trả về kết quả theo đúng đặc tả yêu cầu, như chuyển hướng 301, nội dung tải xuống file CSV, dữ liệu JSON các trạng thái HTTP tương ứng: 200, 201, 204, 400, 404, 405.

## 3. Trả lời câu hỏi

**Vì sao Câu 4 dùng 301 còn Câu 8 trả 201 kèm Location?**
- Câu 4 sử dụng mã HTTP 301 (Moved Permanently) để thông báo cho trình duyệt hoặc client rằng đường dẫn rút gọn (`/sv/<mssv>`) được chuyển hướng vĩnh viễn tới đường dẫn đầy đủ (`/students/<mssv>`), giúp trình duyệt chuyển đến URL chính xác.
- Câu 8 sử dụng mã HTTP 201 (Created) trong REST API để thông báo cho client rằng một tài nguyên mới (điểm học phần) đã được tạo mới thành công, và header `Location` được cung cấp để chỉ ra đường dẫn (URI) tới tài nguyên đó.

**Thêm điểm cho 23T1020005 rồi khởi động lại server, điểm đó còn không? Vì sao?**
- Điểm đó **không còn**.
- Lý do: Ứng dụng này đang sử dụng cấu trúc dữ liệu lưu trên bộ nhớ (dictionary `STUDENTS` trong biến toàn cục của mã nguồn) để lưu trữ. Do đó, các thay đổi (chẳng hạn như qua phương thức PUT) chỉ tồn tại tạm thời trong lúc server đang chạy (trong RAM). Khi khởi động lại server, bộ nhớ này bị xóa và dữ liệu sẽ khôi phục lại trạng thái ban đầu được định nghĩa trong file `sodiem.py`.
