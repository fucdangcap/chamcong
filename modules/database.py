"""
Database module - Handles loading, saving, and querying face encodings
"""
import pickle
import os


class DatabaseManager:
    """Manages face encoding database"""
    
    def __init__(self, db_file="face_encodings_db.pkl"):
        self.db_file = db_file
        self.data = {}  # {name: [encoding1, encoding2, ...]}
        self.load()
    
    def load(self):
        """Load encodings from pickle file"""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'rb') as f:
                self.data = pickle.load(f)
                print(f"✓ Đã tải database từ {self.db_file}")
        else:
            print(f"⚠ Không tìm thấy {self.db_file}, sẽ tạo mới")
            self.data = {}
    
    def save(self):
        """Save encodings to pickle file"""
        with open(self.db_file, 'wb') as f:
            pickle.dump(self.data, f)
        print(f"✓ Đã lưu database vào {self.db_file}")
    
    def add_person(self, name, encodings):
        """Add or replace person's encodings"""
        self.data[name] = encodings
        self.save()
    
    def append_encodings(self, name, encodings):
        """Append encodings to existing person"""
        if name not in self.data:
            self.data[name] = []
        self.data[name].extend(encodings)
        self.save()
    
    def remove_person(self, name):
        """Remove person from database"""
        if name in self.data:
            del self.data[name]
            self.save()
            return True
        return False
    
    def person_exists(self, name):
        """Check if person exists"""
        return name in self.data
    
    def get_all_people(self):
        """Get list of all people"""
        return list(self.data.keys())
    
    def get_person_encodings(self, name):
        """Get encodings of a person"""
        return self.data.get(name, [])
    
    def get_flat_encodings_and_names(self):
        """Get flattened lists for face_recognition library"""
        encodings = []
        names = []
        for name, encs in self.data.items():
            for enc in encs:
                encodings.append(enc)
                names.append(name)
        return encodings, names
    
    def get_stats(self):
        """Get database statistics"""
        total_people = len(self.data)
        total_encodings = sum(len(encs) for encs in self.data.values())
        file_size = os.path.getsize(self.db_file) / 1024 if os.path.exists(self.db_file) else 0
        
        return {
            'total_people': total_people,
            'total_encodings': total_encodings,
            'file_size_kb': file_size,
            'people': self.data
        }