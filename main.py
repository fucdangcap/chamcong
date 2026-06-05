import cv2
import time
from face_recognizer import FaceRecognizer
from serial_controller import ArduinoController

def main():
    # Khởi tạo các Modules
    ai_module = FaceRecognizer("ImagesAttendance")
    hardware_module = ArduinoController('COM3') 
    
    cap = cv2.VideoCapture(0)
    
    time_to_close = 0
    saved_name = ""
    saved_box = None

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        current_time = time.time()
        
        # Nhánh 1: Nếu cửa ĐANG MỞ -> Bỏ qua AI, chỉ duy trì vẽ khung xanh để Camera mượt
        if time_to_close > current_time:
            if saved_box is not None:
                top, right, bottom, left = saved_box
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, f"{saved_name} - UNLOCKED", (left + 6, bottom - 6), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 2)
        
        # Nhánh 2: Nếu cửa ĐANG ĐÓNG -> Liên tục quét AI
        else:
            if time_to_close != 0:
                print("Hệ thống: Khóa cửa lại.")
                time_to_close = 0 # Reset sau khi đóng
                
            results = ai_module.scan_and_identify(frame)
            
            for name, display_name, box in results:
                top, right, bottom, left = box
                
                if name != "Unknown":
                    # --- DUYỆT ĐÚNG NGƯỜI ---
                    saved_name = name
                    saved_box = box
                    
                    ai_module.mark_attendance(name)
                    hardware_module.open_door(display_name)
                    print(f"Mở cửa cho: {display_name}")
                    
                    # Đặt đồng hồ đếm ngược 2 giây để giữ khung hình
                    time_to_close = time.time() + 2
                    break 
                else:
                    # --- NGƯỜI LẠ ---
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    cv2.putText(frame, "UNKNOWN", (left + 6, bottom - 6), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 2)
                    hardware_module.reject()

        cv2.imshow("He Thong Cham Cong - Access Control", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    # Tắt hệ thống an toàn
    cap.release()
    cv2.destroyAllWindows()
    hardware_module.close()

if __name__ == "__main__":
    main()