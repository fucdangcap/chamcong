"""
Enrollment module - Handles capturing and saving new faces
"""
import cv2
import face_recognition
import numpy as np
from modules.duplicate_checker import DuplicateChecker


class EnrollmentManager:
    """Manages face enrollment process"""
    
    @staticmethod
    def capture_frames(cap, num_frames=20):
        """
        Capture frames from camera
        
        Args:
            cap: OpenCV video capture object
            num_frames: Number of frames to capture
        
        Returns:
            List of captured encodings, or None if failed/cancelled
        """
        print(f"\n📸 Đang nạp khuôn mặt")
        print(f"Hãy quay camera lên và di chuyển đầu nhẹ nhàng trong {num_frames} frame...")
        print(f"Nhấn ESC để hủy\n")
        
        captured_encodings = []
        frame_count = 0
        
        while frame_count < num_frames:
            ret, frame = cap.read()
            if not ret:
                print("❌ Lỗi đọc camera")
                cv2.destroyAllWindows()
                return None
            
            # Detect and encode faces
            imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            
            faces = face_recognition.face_locations(imgS)
            encodings = face_recognition.face_encodings(imgS, faces)
            
            # Only proceed if exactly 1 face detected
            if len(faces) == 1 and len(encodings) > 0:
                captured_encodings.append(encodings[0])
                frame_count += 1
                print(f"  ✓ Captured {frame_count}/{num_frames}", end='\r')
                
                # Draw rectangle on face
                top, right, bottom, left = faces[0]
                top, right, bottom, left = top*4, right*4, bottom*4, left*4
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, f"Frame {frame_count}/{num_frames}", (left, top-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            else:
                if len(faces) == 0:
                    cv2.putText(frame, "Khong phat hien khuon mat", (50, 50),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                elif len(faces) > 1:
                    cv2.putText(frame, f"Phat hien {len(faces)} khuon mat. Chi 1 khuon!", (50, 50),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame, f"Frame {frame_count}/{num_frames}", (50, 100),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
            
            cv2.imshow("Enrollment - Nạp khuôn mặt", frame)
            
            # Press ESC to cancel
            if cv2.waitKey(1) & 0xFF == 27:
                print("\n❌ Đã hủy enrollment")
                cv2.destroyWindow("Enrollment - Nạp khuôn mặt")
                return None
        
        cv2.destroyAllWindows()
        print(f"\n✅ Đã capture {len(captured_encodings)} frame thành công")
        return captured_encodings
    
    @staticmethod
    def enroll_new_person(cap, person_name, db_manager, known_encodings, known_names, num_frames=20):
        """
        Complete enrollment process with duplicate check
        
        Args:
            cap: OpenCV video capture object
            person_name: Name of person to enroll
            db_manager: DatabaseManager instance
            known_encodings: Current known encodings
            known_names: Current known names
            num_frames: Number of frames to capture
        
        Returns:
            True if successful, False otherwise
        """
        # Capture frames
        captured_encodings = EnrollmentManager.capture_frames(cap, num_frames)
        if captured_encodings is None:
            return False
        
        # Check for duplicate
        matched_name, distance = DuplicateChecker.check_duplicate(
            captured_encodings, known_encodings, known_names
        )
        
        if matched_name is not None:
            print(f"\n⚠️  CẢNH BÁO: Mặt này đã có trong database!")
            print(f"   Người: {matched_name}")
            print(f"   Distance: {distance:.3f}")
            print(f"\nBạn có chắc muốn nạp vào tên '{person_name}'?")
            response = input("Nhập 'y' để tiếp tục, bất cứ phím nào để hủy: ").lower()
            if response != 'y':
                print("❌ Đã hủy")
                return False
        
        # Check if person exists - offer options
        if db_manager.person_exists(person_name):
            print(f"\n⚠️  Tên '{person_name}' đã tồn tại!")
            print("Bạn muốn:")
            print("  1. Thêm ảnh mới (append)")
            print("  2. Xóa cái cũ & nạp lại (replace)")
            print("  3. Hủy bỏ")
            choice = input("Chọn (1/2/3): ").strip()
            
            if choice == '1':
                db_manager.append_encodings(person_name, captured_encodings)
                print(f"✅ Đã thêm {len(captured_encodings)} encoding cho {person_name}")
            elif choice == '2':
                db_manager.add_person(person_name, captured_encodings)
                print(f"✅ Đã thay thế {len(captured_encodings)} encoding cho {person_name}")
            elif choice == '3':
                print("❌ Đã hủy")
                return False
            else:
                print("❌ Lựa chọn không hợp lệ")
                return False
        else:
            # New person
            db_manager.add_person(person_name, captured_encodings)
            print(f"✅ Đã nạp thành công {len(captured_encodings)} encoding cho {person_name}")
        
        return True