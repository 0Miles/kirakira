import config
from libs.classes.action_base import ActionBase, once, loop
from game_control.bonus import check_bonus_info
import asyncio

class BonusGameGemCollectMode(ActionBase):

    bonus_get_failed_count = 0
    
    @loop("result")
    async def handle_result(self):
        self.scene_manager.currentScene.buttons["ok"].click()
        await asyncio.sleep(1)

    @loop("result_bonus-select")
    async def handle_result_bonus_select(self):
        bonus_info = check_bonus_info(self.scene_manager)
        current_bonus = bonus_info.get("current_bonus")
        if current_bonus in config.BONUS_GAME_TARGET_ITEMS:
            if not await self.scene_manager.currentScene.buttons["get"].wait_click(3):
                self.scene_manager.currentScene.buttons["get"].click_prev_success_position()
                await asyncio.sleep(1)
        else:
            self.scene_manager.currentScene.buttons["next"].click()

    @loop("result_bonus-highlow")
    async def handle_result_bonus_highlow(self):
        bonus_info = check_bonus_info(self.scene_manager)
        target_num = bonus_info.get("target_num")
        print(f"[INFO] 目標數字: {target_num}")
        if target_num > 7:
            print(f"[INFO] 選擇 low")
            self.scene_manager.currentScene.buttons["low"].click()
        else:
            print(f"[INFO] 選擇 high")
            self.scene_manager.currentScene.buttons["high"].click()
        await asyncio.sleep(1)

    @once("result_bonus-failed")
    async def handle_result_bonus_failed(self):
        self.stop()
        self.game.close_app()

    @once("result_bonus-failed_use-item-dialog")
    async def handle_result_bonus_failed_use_item_dialog(self):
        await asyncio.sleep(.5)

    @once("error")
    async def handle_error(self):
        print("[INFO] 出現錯誤畫面，關閉遊戲")
        self.stop()
        self.game.close_app()