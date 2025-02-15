import psutil
import pygetwindow as gw
import subprocess
import time
import os
import cv2
import numpy as np
import win32gui
import win32con
import win32api
import win32ui
import pyperclip
from ctypes import windll, c_int, pointer, Structure, byref, WINFUNCTYPE, c_int
from ctypes.wintypes import RECT, DWORD

# 新增系統指標常數
SM_CYCAPTION = 4       # 標題列高度
SM_CXFRAME = 32       # 視窗框架寬度
SM_CYFRAME = 33       # 視窗框架高度
SM_CXPADDEDBORDER = 92  # Windows Vista/7 之後額外的邊框寬度

class NONCLIENTMETRICS(Structure):
    _fields_ = [
        ("cbSize", DWORD),
        ("iBorderWidth", c_int),
        ("iScrollWidth", c_int),
        ("iScrollHeight", c_int),
        ("iCaptionWidth", c_int),
        ("iCaptionHeight", c_int),
    ]

PROCESS_PER_MONITOR_DPI_AWARE = 2
MDT_EFFECTIVE_DPI = 0

class AppControl:
    def __init__(self, app_names, window_title=None):
        self.app_names = app_names if isinstance(app_names, list) else [app_names]
        self.window_title = window_title
        
        # 設置 DPI 感知
        try:
            # Windows 8.1 及以上版本
            windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)
        except AttributeError:
            # Windows 8 及以下版本
            windll.user32.SetProcessDPIAware()
    
    def is_app_running(self):
        for process in psutil.process_iter(attrs=["pid", "name"]):
            for name in self.app_names:
                if name.lower() in process.info["name"].lower():
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
        if not self.is_app_running():
            print(f"{self.app_names} 未在運行。")
        found = False
        for process in psutil.process_iter(attrs=["pid", "name"]):
            for name in self.app_names:
                if name.lower() in process.info["name"].lower():
                    os.kill(process.info["pid"], 9)
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
                    "x": win.left,
                    "y": win.top,
                    "width": win.width,
                    "height": win.height
                }
        return None
    
    def get_window_dpi_scaling(self, hwnd):
        """ 獲取視窗的 DPI 縮放比例 """
        try:
            # 獲取視窗的 DPI 縮放
            dpi_x = c_int()
            dpi_y = c_int()
            windll.shcore.GetDpiForMonitor(
                win32api.MonitorFromWindow(hwnd, 0),
                MDT_EFFECTIVE_DPI,
                pointer(dpi_x),
                pointer(dpi_y)
            )
            if (dpi_x.value <= 0):
                return 1.0
            
            return dpi_x.value / 96.0
        except Exception:
            return 1.0  # 如果無法獲取 DPI，返回 1.0（無縮放）
        
    def get_window_frame_sizes(self):
        """ 使用 GetSystemMetrics 獲取視窗框架尺寸 """
        try:
            # 獲取系統的視窗度量值
            caption_height = windll.user32.GetSystemMetrics(SM_CYCAPTION)
            frame_x = windll.user32.GetSystemMetrics(SM_CXFRAME)
            frame_y = windll.user32.GetSystemMetrics(SM_CYFRAME)
            padded_border = windll.user32.GetSystemMetrics(SM_CXPADDEDBORDER)

            # 計算實際的邊框尺寸（包含填充）
            total_frame_x = frame_x + padded_border
            total_frame_y = frame_y + padded_border

            return {
                "caption_height": caption_height,
                "frame_width": total_frame_x,
                "frame_height": total_frame_y
            }
        except Exception as e:
            print(f"[ERROR] 無法獲取系統視窗框架尺寸: {e}")
            return None

    def get_window_size_info(self, hwnd = None):
        if self.window_title:
            try:
                # 獲取視窗句柄
                hwnd = hwnd if hwnd else win32gui.FindWindow(None, self.window_title)
                if not hwnd:
                    print(f"[ERROR] 找不到視窗: {self.window_title}")
                    return None
                
                # 獲取視窗和客戶區域矩形
                window_left, window_top, window_right, window_bottom = win32gui.GetWindowRect(hwnd)
                client_left, client_top, client_right, client_bottom = win32gui.GetClientRect(hwnd)
                
                # 獲取系統視窗框架尺寸
                frame_sizes = self.get_window_frame_sizes()
                if not frame_sizes:
                    return None

                dpi_scale = self.get_window_dpi_scaling(hwnd)

                return {
                    "window_rect": (window_left, window_top, window_right - window_left, window_bottom - window_top),
                    "client_rect": (client_left, client_top, client_right, client_bottom),
                    "dpi_scale": dpi_scale,
                    "title_bar_height": frame_sizes["caption_height"],
                    "frame_left": frame_sizes["frame_width"],
                    "frame_right": frame_sizes["frame_width"],
                    "frame_bottom": frame_sizes["frame_height"]
                }

            except Exception as e:
                print(f"[ERROR] 無法獲取視窗資訊: {e}")
                return None

    def capture_screen(self):
        """ 使用 PrintWindow 截取視窗畫面（支援 DPI 縮放） """
        if self.window_title:
            try:
                # 獲取視窗句柄
                hwnd = win32gui.FindWindow(None, self.window_title)
                if not hwnd:
                    print(f"[ERROR] 找不到視窗: {self.window_title}")
                    return None

                # 獲取視窗大小
                window_info = self.get_window_size_info(hwnd)
                if not window_info:
                    return None
                
                width = window_info["window_rect"][2]
                height = window_info["window_rect"][3]
                dpi_scale = window_info["dpi_scale"]
                
                # 創建設備上下文（DC）
                hwnd_dc = win32gui.GetWindowDC(hwnd)
                mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
                save_dc = mfc_dc.CreateCompatibleDC()

                # 創建點陣圖
                save_bitmap = win32ui.CreateBitmap()
                save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
                save_dc.SelectObject(save_bitmap)

                # 使用 PrintWindow 獲取視窗內容
                result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 2)  # 使用 PW_CLIENTONLY
                if result == 1:
                    # 只在成功時處理圖片
                    bmpstr = save_bitmap.GetBitmapBits(True)
                    img = np.frombuffer(bmpstr, dtype='uint8')
                    img.shape = (height, width, 4)
                else:
                    print(f"[ERROR] PrintWindow 失敗，錯誤碼: {win32api.GetLastError()}")
                    return None

                # 清理資源
                win32gui.DeleteObject(save_bitmap.GetHandle())
                save_dc.DeleteDC()
                mfc_dc.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwnd_dc)

                # 轉換為 BGR 格式並處理 DPI 縮放
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                if dpi_scale != 1.0:
                    new_width = int(width / dpi_scale)
                    new_height = int(height / dpi_scale)
                    img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
                return img

            except Exception as e:
                print(f"[ERROR] 截圖時發生錯誤: {e}")
                return None
        return None
    
    def click(self, x, y):
        """ 使用 Windows 訊息在非活動視窗內點擊 """
        try:
            # 獲取目標視窗的句柄
            hwnd = win32gui.FindWindow(None, self.window_title)
            if not hwnd:
                print(f"[ERROR] 找不到視窗: {self.window_title}")
                return False

            # 獲取視窗的客戶區域位置
            left, top, right, bottom = win32gui.GetClientRect(hwnd)
            
            # 確保點擊位置在視窗範圍內
            if not (0 <= x <= (right - left) and 0 <= y <= (bottom - top)):
                print(f"[ERROR] 點擊位置 ({x}, {y}) 超出視窗範圍")
                return False

            # 發送滑鼠事件
            l_param = win32api.MAKELONG(x, y)
            
            # 直接發送滑鼠訊息，不需要激活視窗
            windll.user32.SendNotifyMessageW(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, l_param)
            time.sleep(0.1)  # 短暫延遲確保訊息被處理
            windll.user32.SendNotifyMessageW(hwnd, win32con.WM_LBUTTONUP, 0, l_param)
            return True
            
        except Exception as e:
            print(f"[ERROR] 無法點擊 {self.window_title}: {e}")
            return False

    def input_text(self, text, x, y, max_retries=3):
        """ 在非活動視窗的指定位置輸入文字 """
        for attempt in range(max_retries):
            try:
                hwnd = win32gui.FindWindow(None, self.window_title)
                if not hwnd:
                    print(f"[ERROR] 找不到視窗: {self.window_title}")
                    return False

                # 先準備新文字到剪貼簿
                original_clipboard = pyperclip.paste()
                pyperclip.copy(text)
                time.sleep(0.1)  # 等待剪貼簿更新
                
                # 計算滑鼠座標參數
                l_param = win32api.MAKELONG(x, y)
                
                # 點擊以設置焦點
                windll.user32.SendMessageW(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, l_param)
                time.sleep(0.2)
                windll.user32.SendMessageW(hwnd, win32con.WM_LBUTTONUP, 0, l_param)
                time.sleep(0.1)
                
                # 全選現有文字 (Ctrl+A)
                windll.user32.SendMessageW(hwnd, win32con.WM_KEYDOWN, win32con.VK_CONTROL, 0)
                windll.user32.SendMessageW(hwnd, win32con.WM_KEYDOWN, ord('A'), 0)
                time.sleep(0.1)
                windll.user32.SendMessageW(hwnd, win32con.WM_KEYUP, ord('A'), 0)
                windll.user32.SendMessageW(hwnd, win32con.WM_KEYUP, win32con.VK_CONTROL, 0)
                time.sleep(0.1)
                
                # 清除選中的文字 (Delete)
                windll.user32.SendMessageW(hwnd, win32con.WM_KEYDOWN, win32con.VK_DELETE, 0)
                time.sleep(0.1)
                windll.user32.SendMessageW(hwnd, win32con.WM_KEYUP, win32con.VK_DELETE, 0)
                time.sleep(0.1)
                
                # 直接插入新文字
                for char in text:
                    windll.user32.SendMessageW(hwnd, win32con.WM_CHAR, ord(char), 0)
                    time.sleep(0.05)

                # 恢復原有的剪貼簿內容
                time.sleep(0.1)
                pyperclip.copy(original_clipboard)
                
                print(f"[INFO] 已在 {self.window_title} ({x}, {y}) 輸入文字: {text}")
                return True
                
            except Exception as e:
                print(f"[WARNING] 第 {attempt + 1} 次嘗試輸入文字失敗: {e}")
                time.sleep(1)
                continue
                
        print(f"[ERROR] 在 {max_retries} 次嘗試後仍無法在 {self.window_title} 輸入文字")
        return False