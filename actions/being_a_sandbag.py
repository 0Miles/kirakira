from game_control.room import check_room_list, join_room
from libs.classes.action_base import ActionBase
import asyncio
import config

class BeingASandbag(ActionBase):
    async def process(self):
        await self.scene_manager.refresh()
        
        if self.scene_manager.currentScene:
            # 標題畫面
            if self.scene_manager.currentScene.scene_id == "title-screen":
                self.scene_manager.currentScene.buttons["start"].click()
                await asyncio.sleep(3)
            # 遊戲大廳 - 資訊彈窗
            elif self.scene_manager.currentScene.scene_id == "lobby_information-dialog":
                self.scene_manager.currentScene.buttons["ok"].click()
                await asyncio.sleep(.5)
            # 遊戲大廳
            elif self.scene_manager.currentScene.scene_id == "lobby":
                self.scene_manager.currentScene.buttons["duel"].click()
                await asyncio.sleep(1)
            # 匹配畫面
            elif self.scene_manager.currentScene.scene_id == "matching":
                self.scene_manager.currentScene.buttons["diethelm"].click()
                await asyncio.sleep(1)
            # 匹配畫面(迪特赫姆)
            elif self.scene_manager.currentScene.scene_id == "matching_diethelm":
                room_list = check_room_list(self.scene_manager)
                if room_list:
                    target_room = next((room for room in room_list if room['owner'] == config.AUTO_SANDBAG_TARGET_USERNAME), None)
                    if target_room:
                        join_room(self.scene_manager, target_room['position'], target_room['owner'])
                        await asyncio.sleep(.2)
            # 戰鬥畫面
            elif self.scene_manager.currentScene.scene_id == "fighting":
                await asyncio.sleep(1)
                self.scene_manager.currentScene.buttons["surrender"].click()
                await asyncio.sleep(.5)
            # 戰鬥 - 投降確認彈窗
            elif self.scene_manager.currentScene.scene_id == "fighting_check-surrender-dialog":
                self.scene_manager.currentScene.buttons["ok"].click()
                await asyncio.sleep(.5)
            # 戰鬥 - 投降成功彈窗
            elif self.scene_manager.currentScene.scene_id == "fighting_surrender-dialog":
                self.scene_manager.currentScene.buttons["ok"].click()
                self.stop()
            # 異常畫面
            elif self.scene_manager.currentScene.scene_id == "error":
                self.game.close_app()
                self.stop()