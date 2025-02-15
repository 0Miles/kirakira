import config
from libs.classes.action_base import ActionBase, once, loop
from services.bonus_service import BonusService
import asyncio

class BonusGameBasicMode(ActionBase):
    bonus_service: BonusService

    @loop("result")
    async def handle_result(self):
        self.scene_manager.currentScene.buttons["ok"].click()
        await asyncio.sleep(1)

    @loop("result_bonus-select")
    async def handle_result_bonus_select(self):
        bonus_info = self.bonus_service.check_bonus_info()
        star_rank = bonus_info.get("star_rank", self.bonus_service.prev_star_rank)

        if star_rank < 70:
            print(f"[INFO] star_rank < 70: {star_rank}")
            # 戰敗的場合，直接關閉遊戲
            self.stop()
            self.game.close_app()
            return
    
        await self.bonus_service.handle_bonus_select(bonus_info)
        await asyncio.sleep(1)

    @loop("result_bonus-highlow")
    async def handle_result_bonus_highlow(self):
        await self.bonus_service.handle_highlow_choice()
        await asyncio.sleep(3)

    @once("result_bonus-failed")
    async def handle_result_bonus_failed(self):
        self.stop()
        self.game.close_app()

    @once("result_bonus-failed_use-item-dialog")
    async def handle_result_bonus_failed_use_item_dialog(self):
        await asyncio.sleep(.5)

    @once("error")
    async def handle_error(self):
        """處理錯誤並關閉遊戲"""
        print("[INFO] 出現錯誤畫面，關閉遊戲")
        self.stop()
        self.game.close_app()