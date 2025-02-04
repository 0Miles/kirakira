import config
from libs.classes.action_base import ActionBase
import asyncio

class BootSteam(ActionBase):
    is_steam_booting: bool = False

    async def on_start(self):
        self.is_steam_booting = False

    async def process(self):
        if not self.steam.is_steam_running() and not self.is_steam_booting:
            # 啟動 Steam
            print(f"[TEST] 正在啟動 Steam: {config.STEAM_NAME}...")
            self.steam.start_steam()
            self.is_steam_booting = True

        elif not self.steam.is_steam_running() and self.is_steam_booting:
            # 檢測 Steam 是否已開啟完畢
            print("[TEST] Steam 尚未啟動，等待 5 秒後再次檢查...")
            await asyncio.sleep(5)
        
        else:
            print("[TEST] Steam啟動完成。")
            self.is_steam_booting = False
            self.stop()