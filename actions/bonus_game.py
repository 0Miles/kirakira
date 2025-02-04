from game_control.room import check_room_list
from libs.classes.action_base import ActionBase
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

                print("獎勵遊戲 - 選擇")
                await asyncio.sleep(.5)
            # 獎勵遊戲 - highlow
            elif self.scene_manager.currentScene.scene_id == "result_bonus-highlow":

                print("獎勵遊戲 - highlow")
                await asyncio.sleep(.5)
            # 獎勵遊戲 - 失敗
            elif self.scene_manager.currentScene.scene_id == "result_bonus-failed":
                print("獎勵遊戲 - 失敗")
                await asyncio.sleep(.5)
            elif self.scene_manager.currentScene.scene_id == "result_bonus-failed_use-item-dialog":
                print("獎勵遊戲 - 失敗 - 使用道具")
                await asyncio.sleep(.5)
            else:
                self.stop()