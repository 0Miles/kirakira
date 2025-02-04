from libs.classes.action_base import ActionBase
from game_control.bonus import check_bonus_info
import asyncio
import config

class BonusGame(ActionBase):
    async def process(self):
        await self.scene_manager.refresh()
        
        if self.scene_manager.currentScene:
            # 結算畫面
            if self.scene_manager.currentScene.scene_id == "result":
                self.scene_manager.currentScene.buttons["ok"].click()
                await asyncio.sleep(3)
            # 獎勵遊戲 - 選擇
            elif self.scene_manager.currentScene.scene_id == "result_bonus-select":
                bonus_info = check_bonus_info(self.scene_manager)
                current_bonus = bonus_info.get("current_bonus")
                if (current_bonus == "green-tea" or current_bonus == "gem"):
                    self.scene_manager.currentScene.buttons["get"].click()
                else:
                    self.scene_manager.currentScene.buttons["next"].click()
                await asyncio.sleep(.5)
            # 獎勵遊戲 - highlow
            elif self.scene_manager.currentScene.scene_id == "result_bonus-highlow":
                bonus_info = check_bonus_info(self.scene_manager)
                target_num = bonus_info.get("target_num")
                if (target_num >= 7):
                    self.scene_manager.currentScene.buttons["low"].click()
                else:
                    self.scene_manager.currentScene.buttons["high"].click()
                await asyncio.sleep(.5)
            # 獎勵遊戲 - 失敗
            elif self.scene_manager.currentScene.scene_id == "result_bonus-failed":
                self.game.close_app()
                self.stop()
            elif self.scene_manager.currentScene.scene_id == "result_bonus-failed_use-item-dialog":
                await asyncio.sleep(.5)
            else:
                self.stop()