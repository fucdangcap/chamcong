import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime

class FaceRecognizer:
    def __init__(self, db_path="ImagesAttendance"):
        self.db_path = db_path
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_database()
    
    def load_database(self):
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)
            print(f"Đã tạo thư mục '{self.db_path}' để lưu trữ ảnh. Vui lòng thêm ảnh vào thư mục này.")
            return
        
        myList = os.listdir(self.db_path)
        for cl in myList:
            if cl.lower().endswith(('.png', '.jpg', '.jpeg')):
                curImg = cv2.imread(f'{self.db_path}/{cl}')
                if curImg is None: continue
                
                self.known_face_names.append(os.path.splitext(cl)[0])
                imgRGB = cv2.cvtColor(curImg, cv2.COLOR_BGR2RGB)
                encodings = face_recognition.face_encodings(imgRGB)
                if len(encodings) > 0:
                    self.known_face_encodings.append(encodings[0])
        print(f"Đã tải thành công {len(self.known_face_names)} khuôn mặt vào bộ nhớ.")
        
    def mark_attendance(self, name):
        # ghi log thời gian ra file attendance.csv
        with open('attendance.csv', 'a') as f:
            now = datetime.now()
            dtString = now.strftime('%Y-%m-%d %H:%M:%S')
            f.write(f'{name},{dtString}\n')
    
    def scan_and_identify(self, frame):
        imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
        
        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
        
        results = []
        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            top, right, bottom, left = faceLoc
            top, right, bottom, left = top*4, right*4, bottom*4, left*4
            
            faceDis = face_recognition.face_distance(self.known_face_encodings, encodeFace)
            name = "Unknown"
            
            if len(faceDis) > 0:
                matchIndex = np.argmin(faceDis)
                if faceDis[matchIndex] < 0.45:
                    name = self.known_face_names[matchIndex].upper()
                    
            results.append((name, (top, right, bottom, left)))
        return results