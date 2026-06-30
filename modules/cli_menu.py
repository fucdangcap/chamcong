"""
CLI Menu module - Handles user interface and menus
"""
from modules.database import DatabaseManager
from modules.enroll import EnrollmentManager


class MenuManager:
    """Manages user interface and menus"""
    
    @staticmethod
    def show_main_menu():
        """Display main menu"""
        print("\n" + "="*50)
        print("🚪 HỆ THỐNG CHẤM CÔNG - KIỂM SOÁT CỬA")
        print("="*50)
        print("Phím tắt trong chế độ quét:")
        print("  'E' - Nạp khuôn mặt người mới")
        print("  'M' - Menu quản lý database")
        print("  'Q' - Thoát chương trình")
        print("="*50 + "\n")
    
    @staticmethod
    def show_management_menu(db_manager, known_encodings, known_names, cap):
        """Display database management menu"""
        while True:
            print("\n" + "="*50)
            print("📊 MENU QUẢN LÝ DATABASE")
            print("="*50)
            print("1. Xem danh sách người")
            print("2. Xem thống kê")
            print("3. Xóa người")
            print("4. Quay lại")
            print("="*50)
            
            choice = input("Chọn (1/2/3/4): ").strip()
            
            if choice == '1':
                MenuManager._show_people_list(db_manager)
            elif choice == '2':
                MenuManager._show_statistics(db_manager)
            elif choice == '3':
                MenuManager._delete_person(db_manager)
            elif choice == '4':
                break
            else:
                print("❌ Lựa chọn không hợp lệ")
    
    @staticmethod
    def _show_people_list(db_manager):
        """Show list of all people in database"""
        people = db_manager.get_all_people()
        
        if not people:
            print("\n❌ Database trống!")
            return
        
        print("\n" + "="*50)
        print("📋 DANH SÁCH NGƯỜI")
        print("="*50)
        for i, person in enumerate(people, 1):
            encodings_count = len(db_manager.get_person_encodings(person))
            print(f"{i}. {person:<20} - {encodings_count} encoding")
        print("="*50)
    
    @staticmethod
    def _show_statistics(db_manager):
        """Show database statistics"""
        stats = db_manager.get_stats()
        
        print("\n" + "="*50)
        print("📊 THỐNG KÊ DATABASE")
        print("="*50)
        print(f"Tổng người: {stats['total_people']}")
        print(f"Tổng encodings: {stats['total_encodings']}")
        avg_encodings = stats['total_encodings'] / max(stats['total_people'], 1)
        print(f"Trung bình/người: {avg_encodings:.1f}")
        print(f"Dung lượng file: {stats['file_size_kb']:.2f} KB")
        print("="*50)
        
        if stats['people']:
            print("\n📝 Chi tiết:")
            for person, encodings in sorted(stats['people'].items()):
                print(f"  • {person:<20} - {len(encodings)} encoding")
    
    @staticmethod
    def _delete_person(db_manager):
        """Delete a person from database"""
        people = db_manager.get_all_people()
        
        if not people:
            print("\n❌ Database trống!")
            return
        
        print("\nNhập tên người cần xóa (hoặc Enter để hủy):")
        person_name = input("Tên: ").strip().upper()
        
        if not person_name:
            print("❌ Đã hủy")
            return
        
        if db_manager.person_exists(person_name):
            confirm = input(f"⚠️  Xác nhận xóa '{person_name}'? (y/n): ").lower()
            if confirm == 'y':
                db_manager.remove_person(person_name)
                print(f"✅ Đã xóa '{person_name}'")
            else:
                print("❌ Đã hủy")
        else:
            print(f"❌ Không tìm thấy '{person_name}'")