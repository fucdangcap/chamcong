"""
Main entry point for Access Control System
"""
import cv2
import time
from serial_controller import ArduinoController
from modules.database import DatabaseManager
from modules.attendance import AttendanceLogger
from modules.enroll import EnrollmentManager
from modules.recognition import RecognitionManager
from modules.cli_menu import MenuManager


def run_recognition_loop(cap, db_manager, attendance_logger, hardware_module, menu_manager):
    """Main loop for face recognition and access control"""
    time_to_close = 0
    saved_name = ""
    saved_box = None
    
    menu_manager.show_main_menu()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        current_time = time.time()
        
        # If door is open - just display and skip AI processing
        if time_to_close > current_time:
            if saved_box is not None:
                top, right, bottom, left = saved_box
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, f"{saved_name} - UNLOCKED", (left + 6, bottom - 6),
                           cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 2)
        
        # Door is closed - run face recognition
        else:
            if time_to_close != 0:
                print("Hệ thống: Khóa cửa lại.")
                time_to_close = 0
            
            # Get current known encodings and names
            known_encodings, known_names = db_manager.get_flat_encodings_and_names()
            
            # Scan and identify faces
            results = RecognitionManager.scan_and_identify(frame, known_encodings, known_names)
            
            # Process recognition results
            for name, display_name, box, confidence in results:
                if name != "Unknown":
                    saved_name = name
                    saved_box = box
                    
                    attendance_logger.mark_attendance(name)
                    hardware_module.open_door(display_name)
                    print(f"✅ Mở cửa cho: {display_name} (độ tin cậy: {confidence:.2%})")
                    
                    time_to_close = time.time() + 2
                    break
                else:
                    hardware_module.reject()
        
        # Draw results on frame
        known_encodings, known_names = db_manager.get_flat_encodings_and_names()
        results = RecognitionManager.scan_and_identify(frame, known_encodings, known_names)
        frame = RecognitionManager.draw_results_on_frame(frame, results)
        
        cv2.imshow("He Thong Cham Cong - Access Control", frame)
        
        # Check for key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('e'):
            cv2.destroyAllWindows()
            EnrollmentManager.enroll_new_person(cap, input("Nhập tên người cần nạp: ").strip().upper(),
                                                db_manager, *db_manager.get_flat_encodings_and_names())
            print("Quay lại chế độ nhận diện...")
        elif key == ord('m'):
            cv2.destroyAllWindows()
            menu_manager.show_management_menu(db_manager, *db_manager.get_flat_encodings_and_names(), cap)
            print("Quay lại chế độ nhận diện...")


def main():
    """Main function"""
    # Initialize modules
    db_manager = DatabaseManager()
    attendance_logger = AttendanceLogger()
    hardware_module = ArduinoController('COM3')
    menu_manager = MenuManager()
    
    cap = cv2.VideoCapture(1)
    
    try:
        run_recognition_loop(cap, db_manager, attendance_logger, hardware_module, menu_manager)
    except KeyboardInterrupt:
        print("\n❌ Bị gián đoạn")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        hardware_module.close()
        print("✅ Đã tắt hệ thống")


if __name__ == "__main__":
    main()