import serial
import time

class ArduinoController:
    def __init__(self, port= 'COM3', baudrate=9600):
        self.ser = None
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2) # Chờ 2 giây để mạch Arduino khởi động
            print(f"Kết nối thành công với Arduino")
        except Exception as e:
            print(f"Lỗi khi kết nối với Arduino: {e}")
    
    def open_door(self, employee_name):
        if self.ser is not None and self.ser.is_open:
            try:
                data_to_send = f"1:{employee_name}\n"
                
                self.ser.write(data_to_send.encode('utf-8'))
                print(f"--> Đã gửi lệnh mở cửa + Tên: {data_to_send.strip()}")
            except Exception as e:
                print("Lỗi khi gửi lệnh mở cửa: ", e)
    
    def reject(self):
        if self.ser is not None and self.ser.is_open:
            try:
                self.ser.write(b'0')
            except Exception as e:
                print("Lỗi khi gửi lệnh cảnh báo: ", e)
    
    def close(self):
        if self.ser is not None and self.ser.is_open:
            self.ser.close()
            print("Đã đóng kết nối với Arduino")        