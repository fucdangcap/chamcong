# Hệ thống chấm công và kiểm soát cửa bằng nhận diện khuôn mặt

Đây là một ứng dụng Python dùng webcam để nhận diện khuôn mặt, ghi nhận chấm công vào CSV và điều khiển Arduino mở hoặc từ chối cửa qua cổng serial.

## Tính năng chính

- Nhận diện khuôn mặt theo thời gian thực từ camera.
- Chấm công tự động và lưu vào file `attendance.csv`.
- Nạp khuôn mặt mới trực tiếp từ giao diện chương trình.
- Quản lý database khuôn mặt: xem danh sách, xem thống kê, xóa người dùng.
- Gửi lệnh mở cửa hoặc từ chối qua Arduino.
- Phát hiện trùng khuôn mặt khi nạp mới để hạn chế nhập sai dữ liệu.

## Cấu trúc dự án

- `main.py`: điểm vào của chương trình.
- `serial_controller.py`: giao tiếp với Arduino qua serial.
- `modules/recognition.py`: phát hiện và nhận diện khuôn mặt.
- `modules/enroll.py`: nạp khuôn mặt mới.
- `modules/database.py`: lưu và tải encodings khuôn mặt.
- `modules/attendance.py`: ghi log chấm công ra CSV.
- `modules/cli_menu.py`: menu console để quản lý database.
- `modules/duplicate_checker.py`: kiểm tra khuôn mặt trùng khi nạp.
- `attendance.csv`: file lịch sử chấm công.

## Yêu cầu

- Python 3.10+.
- Webcam hoạt động được với OpenCV.
- Arduino kết nối qua serial nếu muốn điều khiển cửa.
- Các thư viện Python chính:
  - `opencv-python`
  - `face_recognition`
  - `numpy`
  - `pyserial`

Lưu ý: `face_recognition` thường cần thêm các phụ thuộc hệ thống của `dlib` tùy máy Windows.

## Cài đặt

Tạo môi trường ảo và cài thư viện:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install opencv-python face_recognition numpy pyserial
```

Nếu máy bạn cài `face_recognition` gặp lỗi build, cần cài thêm các gói phụ thuộc của `dlib` theo môi trường Windows đang dùng.

## Chạy chương trình

```bash
python main.py
```

Mặc định chương trình đang dùng:

- Camera index: `1` trong `main.py`
- Cổng Arduino: `COM3` trong `serial_controller.py`
- Ngưỡng nhận diện: `0.4` trong `modules/__init__.py`

Nếu máy bạn dùng camera hoặc cổng COM khác, hãy sửa lại hai giá trị này cho phù hợp.

## Phím tắt khi chạy

- `E`: nạp khuôn mặt mới.
- `M`: mở menu quản lý database.
- `Q`: thoát chương trình.

## Dữ liệu lưu trữ

- Database khuôn mặt được lưu trong file `face_encodings_db.pkl`.
- Lịch sử chấm công được ghi thêm vào file `attendance.csv`.

## Quy trình sử dụng

1. Kết nối webcam và Arduino.
2. Chạy `python main.py`.
3. Nạp khuôn mặt người dùng bằng phím `E`.
4. Khi nhận diện thành công, hệ thống sẽ ghi chấm công và gửi lệnh mở cửa.
5. Dùng phím `M` để quản lý danh sách người trong database.

## Ghi chú

- Khi nạp khuôn mặt, chương trình yêu cầu chỉ có 1 khuôn mặt trong khung hình để tránh dữ liệu sai.
- Nếu cùng một tên đã tồn tại, hệ thống cho phép thêm ảnh mới hoặc thay thế toàn bộ encodings cũ.
- Nếu không có Arduino, chương trình vẫn có thể chạy phần nhận diện và chấm công, nhưng lệnh mở cửa sẽ không được thực thi.
