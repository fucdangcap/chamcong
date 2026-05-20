import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import time
import serial 

COM_PORT = 'COM3'
TOLERANCE_THRESHOLD = 0.45
ATTENDANCE_FILE = 'attendance.csv'

try:
    ser = serial.Serial(COM_PORT, 9600, timeout=1)
    print("Đã kết nối thành công với mạch Arduino!")
    time.sleep(2) # Chờ 2 giây để Arduino ổn định kết nối
except Exception as e:
    print(f"LỖI: Không thể kết nối với Arduino. Vui lòng kiểm tra lại cổng COM. Chi tiết: {e}")
    ser = None
    

# 1. Đọc dữ liệu ảnh nhân viên từ thư mục
path = 'ImagesAttendance'
images = []
classNames = []
myList = os.listdir(path)

for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    # Lấy tên file bỏ đuôi (.jpg, .png) làm tên nhân viên
    classNames.append(os.path.splitext(cl)[0])

# 2. Hàm mã hóa khuôn mặt (Trích xuất đặc trưng - 128 chiều)
def findEncodings(images, names):
    encodeList = []
    validNames = []
    for img, name in zip(images, names):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img)
        if len(encodings) > 0:
            encodeList.append(encodings[0])
            validNames.append(name)
        else:
            print(f"CẢNH BÁO: Không tìm thấy khuôn mặt trong ảnh của {name}. Sẽ bỏ qua dữ liệu này.")
    return encodeList, validNames

print("Đang tiến hành mã hóa dữ liệu khuôn mặt...")
encodeListKnown, classNames = findEncodings(images, classNames)
print(f"Mã hóa thành công {len(encodeListKnown)} nhân viên!")

# 3. Hàm ghi nhận chấm công vào file CSV
def markAttendance(name):
    # Tạo cấu trúc file nếu chưa tồn tại
    if not os.path.isfile(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, 'w', encoding='utf-8') as f:
            f.write('Name,Time\n')

    with open(ATTENDANCE_FILE, 'r+', encoding='utf-8') as f:
        myDataList = f.readlines()
        nameList = [line.split(',')[0].strip() for line in myDataList]
        
        # Nếu tên chưa có trong danh sách thì tiến hành ghi
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%Y-%m-%d %H:%M:%S')
            
            # Đảm bảo file có newline ở cuối trước khi thêm dòng mới
            if len(myDataList) > 0 and not myDataList[-1].endswith('\n'):
                f.write('\n')
                
            f.write(f'{name},{dtString}\n')

# 4. Mở Webcam và nhận diện thời gian thực
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # Số 0 là webcam mặc định của máy

time_to_close = 0

while True:
    success, img = cap.read()
    if not success or img is None:
        continue
    
    # NẾU ĐÃ NHẬN DIỆN THÀNH CÔNG -> BỎ QUA QUÉT KHUÔN MẶT, CHỈ HIỂN THỊ VIDEO TRONG 5 GIÂY RỒI TỰ ĐỘNG TẮT CAMERA
    if time_to_close > 0:
        # Nếu đã trôi qua đủ 2 giây kể từ lúc nhận diện
        if time.time() >= time_to_close:
            print("Đã hoàn tất quá trình chấm công. Đang tắt camera...")
            break
    
    # Trong lúc chờ 2 giây, video vẫn chạy mượt, ta in thêm thông báo lên góc trên camera
        cv2.putText(img, "XAC NHAN THANH CONG! DANG MO CUA...", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow('He thong cham cong', img)
        cv2.waitKey(1)
        continue # Lệnh này giúp bỏ qua đoạn quét AI bên dưới, hết lag/khựng 100%
        
    # Thu nhỏ frame hình lại (1/2) để hệ thống xử lý nhanh hơn (tăng FPS)
    imgS = cv2.resize(img, (0, 0), None, 0.5, 0.5)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Tìm vị trí khuôn mặt và mã hóa khuôn mặt trong frame hiện tại
    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    # Duyệt qua từng khuôn mặt bắt được trên camera
    # Duyệt qua từng khuôn mặt bắt được trên camera
    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        
        # Lấy ra vị trí của khuôn mặt
        y1, x2, y2, x1 = faceLoc
        y1, x2, y2, x1 = y1*2, x2*2, y2*2, x1*2

        matchIndex = np.argmin(faceDis)

        # KIỂM TRA NGƯỠNG AN TOÀN (0.5 là mức khuyên dùng cho khóa cửa)
        # Số này càng nhỏ thì độ chính xác đòi hỏi càng cao
        if faceDis[matchIndex] < TOLERANCE_THRESHOLD:
            name = classNames[matchIndex].upper()
            
            # 1. NHẬN DIỆN THÀNH CÔNG -> VẼ KHUNG XANH LÁ
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2-35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1+6, y2-6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            markAttendance(name)
            print(f"Đã xác nhận: {name}. Đang tiến hành mở cửa...")
            
            if ser is not None:
                ser.write(b'1')
            
            time_to_close = time.time() + 2
            # Cập nhật hình ảnh lên màn hình để thấy khung xanh
            cv2.imshow('He thong cham cong', img)
            
        else:
            # 2. CẢNH BÁO NGƯỜI LẠ -> VẼ KHUNG ĐỎ
            name = "UNKNOWN"
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.rectangle(img, (x1, y2-35), (x2, y2), (0, 0, 255), cv2.FILLED)
            cv2.putText(img, name, (x1+6, y2-6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            print("CẢNH BÁO: Phát hiện người lạ!")
            ser.write(b'0')
    # Hiển thị cửa sổ Camera
    cv2.imshow('He thong cham cong', img)
    
    # Bấm phím 'q' để thoát chương trình
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()