import psutil
import pygetwindow as gw
import subprocess
import time
import os
import pyautogui
import cv2
import numpy as np

class AppControl:
    def __init__(self, app_names, window_title=None):
        self.app_names = app_names if isinstance(app_names, list) else [app_names]
        self.window_title = window_title
    
    def is_app_running(self):
        for process in psutil.process_iter(attrs=['pid', 'name']):
            for name in self.app_names:
                if name.lower() in process.info['name'].lower():
                    return True
        return False

    def is_app_focused(self):
        if self.window_title:
            focused_window = gw.getActiveWindow()
            if focused_window and self.window_title.lower() in focused_window.title.lower():
                return True
        return False
    
    def start_app(self, app_path):
        if not self.is_app_running():
            subprocess.Popen(app_path, shell=True)
            time.sleep(5)  # 等待應用啟動
        else:
            print(f"{self.app_names} 之一已在運行中。")
    
    def close_app(self):
        found = False
        for process in psutil.process_iter(attrs=['pid', 'name']):
            for name in self.app_names:
                if name.lower() in process.info['name'].lower():
                    os.kill(process.info['pid'], 9)
                    print(f"{name} 已關閉。")
                    found = True
                    break
        if not found:
            print(f"{self.app_names} 未在運行。")
    
    def focus_window(self):
        try:
            if self.window_title:
                windows = gw.getWindowsWithTitle(self.window_title)
                if windows:
                    windows[0].activate()
                    print(f"已將 {self.window_title} 視窗置於前台。")
                else:
                    print(f"找不到視窗: {self.window_title}")
            else:
                print("未指定視窗標題。")
        except Exception as e:
            print("發生錯誤:", e)

    def get_window_geometry(self):
        if self.window_title:
            window = gw.getWindowsWithTitle(self.window_title)
            if window:
                win = window[0]
                return {
                    'x': win.left,
                    'y': win.top,
                    'width': win.width,
                    'height': win.height
                }
        return None
    
    def capture_screen(self):
        if self.window_title:
            window = gw.getWindowsWithTitle(self.window_title)
            if window:
                win = window[0]
                # 取得視窗的大小與位置
                x, y, width, height = win.left, win.top, win.width, win.height
                # 擷取螢幕畫面
                screenshot = pyautogui.screenshot(region=(x, y, width, height))
                # 將截圖轉換為 OpenCV 格式
                screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                return screenshot
        return None
    
    def capture_full_screen(self):
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        return screenshot