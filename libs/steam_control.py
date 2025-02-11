import subprocess
import psutil
import winreg
import os

class SteamControl:
    def __init__(self, default_game_id):
        self.default_game_id = default_game_id
    
    def is_steam_running(self):
        for process in psutil.process_iter(attrs=["pid", "name"]):
            if "steam.exe" in process.info["name"].lower():
                return True
        return False

    def get_steam_path(self):
        """從 Windows 登錄檔獲取 Steam 安裝路徑"""
        try:
            # 嘗試從登錄檔讀取 Steam 路徑
            hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Valve\\Steam")
            steam_path = winreg.QueryValueEx(hkey, "InstallPath")[0]
            winreg.CloseKey(hkey)
            
            # 確認 steam.exe 存在
            steam_exe = os.path.join(steam_path, "Steam.exe")
            if os.path.exists(steam_exe):
                return steam_exe
        except Exception as e:
            print(f"無法從登錄檔讀取 Steam 路徑: {e}")
            
        # 如果登錄檔讀取失敗，嘗試預設路徑
        default_paths = [
            "C:\\Program Files (x86)\\Steam\\Steam.exe",
            "C:\\Program Files\\Steam\\Steam.exe"
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                return path
                
        return None
    
    def start_steam(self):
        if not self.is_steam_running():
            steam_path = self.get_steam_path()
            if steam_path:
                try:
                    subprocess.Popen([steam_path])
                    print("正在啟動 Steam...")
                except Exception as e:
                    print(f"啟動 Steam 時發生錯誤: {e}")
            else:
                print("找不到 Steam 安裝路徑")
        else:
            print("Steam 已在運行中。")
    
    def start_game(self, game_id=None):
        start_game_id = game_id if game_id else self.default_game_id
        if not self.is_steam_running():
            self.start_steam()
        subprocess.Popen(f"start steam://rungameid/{start_game_id}", shell=True)
        print(f"正在啟動遊戲 (ID: {start_game_id})...")