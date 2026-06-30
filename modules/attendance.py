"""
Attendance module - Logs attendance records with timestamp
"""
from datetime import datetime


class AttendanceLogger:
    """Logs attendance records to CSV file"""
    
    def __init__(self, attendance_file='attendance.csv'):
        self.attendance_file = attendance_file
    
    def mark_attendance(self, name):
        """Log attendance with timestamp"""
        with open(self.attendance_file, 'a') as f:
            now = datetime.now()
            dtString = now.strftime('%Y-%m-%d %H:%M:%S')
            f.write(f'{name},{dtString}\n')