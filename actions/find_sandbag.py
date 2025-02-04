from game_control.room import check_room_list
from libs.classes.action_base import ActionBase
import asyncio
import config

class FindSandbag(ActionBase):
    async def process(self):
        await self.scene_manager.refresh()
        
        if self.scene_manager.currentScene:
            # 標題畫面
            if self.scene_manager.currentScene.scene_id == "title-screen":
                self.scene_manager.currentScene.buttons["start"].click()
                await asyncio.sleep(3)
            # 載入中
            elif self.scene_manager.currentScene.scene_id == "now-loading":
                await asyncio.sleep(1)
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
                self.scene_manager.currentScene.buttons["create"].click()
                await asyncio.sleep(.5)
            # 匹配畫面(迪特赫姆) - 創建房間
            elif self.scene_manager.currentScene.scene_id == "matching_diethelm_create-dialog":
                self.scene_manager.currentScene.inputs["select-rule"].select_option("scenes/matching/diethelm/create-dialog/option-3v3.png")
                await asyncio.sleep(.1)
                self.scene_manager.currentScene.inputs["text-room-name"].change_text(config.FIND_SANDBAG_ROOM_NAME)
                await asyncio.sleep(.1)
                if config.FIND_SANDBAG_FRIEND_ONLY:
                    self.scene_manager.currentScene.inputs["checkbox-friend"].click()
                    await asyncio.sleep(.1)
                self.scene_manager.currentScene.buttons["corner"].click()
                self.scene_manager.currentScene.buttons["ok"].click()
                await asyncio.sleep(.5)
            # 匹配畫面(迪特赫姆) - 等待中
            elif self.scene_manager.currentScene.scene_id == "matching_diethelm_wating-dialog":
                room_list = check_room_list(self.scene_manager)
                print(room_list)
                if not any(room["owner"] == config.FIND_SANDBAG_USERNAME for room in room_list):
                    self.scene_manager.currentScene.buttons["cancel"].click()
            # 戰鬥 - 畫面
            elif self.scene_manager.currentScene.scene_id == "fighting":
                self.scene_manager.currentScene.buttons["ok"].click()
            # 戰鬥 - 投降成功彈窗
            elif self.scene_manager.currentScene.scene_id == "fighting_surrender-dialog":
                self.scene_manager.currentScene.buttons["ok"].click()
                await asyncio.sleep(1)
                self.stop()
            else:
                await asyncio.sleep(1)
                self.stop()
        else:
            await asyncio.sleep(1)