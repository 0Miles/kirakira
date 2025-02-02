import subprocess
import time
import psutil
import os

class SteamControl:
    def __init__(self, game_id):
        self.game_id = game_id
    
    def is_steam_running(self):
        for process in psutil.process_iter(attrs=['pid', 'name']):
            if "steam.exe" in process.info['name'].lower():
                return True
        return False
    
    def start_steam(self):
        if not self.is_steam_running():
            subprocess.Popen("start steam://open", shell=True)
            time.sleep(5)  # 等待 Steam 啟動
        else:
            print("Steam 已在運行中。")
    
    def start_game(self):
        if not self.is_steam_running():
            self.start_steam()
        subprocess.Popen(f"start steam://rungameid/{self.game_id}", shell=True)
        print(f"正在啟動遊戲 (ID: {self.game_id})...")