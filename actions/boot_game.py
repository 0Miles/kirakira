import config
from libs.classes.action_base import ActionBase
import asyncio

class BootGame(ActionBase):
    is_game_booting: bool = False

    async def on_start(self) -> None:
        self.is_game_booting = False

    async def process(self) -> None:
        if not self.game.is_app_running() and not self.is_game_booting:
            # 透過 Steam 啟動遊戲
            print(f"[TEST] 正在透過 Steam 啟動遊戲: {config.GAME_NAME}...")
            self.steam.start_game()
            self.is_game_booting = True

        elif not self.game.is_app_running() and self.is_game_booting:
            # 檢測遊戲是否已開啟完畢
            print("[TEST] 遊戲尚未啟動，等待 5 秒後再次檢查...")
            await asyncio.sleep(5)
        
        else:
            print("[TEST] 遊戲啟動完成。")
            self.is_game_booting = False
            self.stop()