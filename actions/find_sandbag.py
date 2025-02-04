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
                if not self.scene_manager.extra_info.get("ap-not-enough", False):
                    click_success = self.scene_manager.currentScene.buttons["create"].click()
                    if not click_success:
                        self.scene_manager.extra_info["failed_count"] = self.scene_manager.extra_info.get("failed_count", 0) + 1
                        if self.scene_manager.extra_info["failed_count"] > 20:
                            self.game.close_app()
                            self.stop()
                    else:
                        self.scene_manager.extra_info["failed_count"] = 0
                    await asyncio.sleep(.5)
                else:
                    self.scene_manager.currentScene.buttons["item"].click()
                    await asyncio.sleep(2)
            # 匹配畫面(迪特赫姆) - 使用道具
            elif self.scene_manager.currentScene.scene_id == "matching_diethelm_use-item-dialog":
                has_green_tea = self.scene_manager.currentScene.buttons["green-tea"].click()
                await asyncio.sleep(1)
                if has_green_tea:
                    use_success = self.scene_manager.currentScene.buttons["use"].click()
                    if use_success:
                        self.scene_manager.extra_info["ap-not-enough"] = False
                    else:
                        self.scene_manager.extra_info["green-tea-not-enough"] = True
                        self.scene_manager.currentScene.buttons["close"].click()
                        self.stop()
                        return
                    await asyncio.sleep(.5)
                self.scene_manager.currentScene.buttons["close"].click()
                await asyncio.sleep(2)
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
            # 匹配畫面(迪特赫姆) - AP不足
            elif self.scene_manager.currentScene.scene_id == "matching_diethelm_ap-not-enough-dialog":
                self.scene_manager.currentScene.buttons["ok"].click()
                self.scene_manager.extra_info["ap-not-enough"] = True
                await asyncio.sleep(1)
            # 戰鬥 - 畫面
            elif self.scene_manager.currentScene.scene_id == "fighting":
                self.scene_manager.currentScene.buttons["ok"].click()
                await asyncio.sleep(1)
            # 戰鬥 - 投降成功彈窗
            elif self.scene_manager.currentScene.scene_id == "fighting_surrender-dialog":
                self.scene_manager.currentScene.buttons["ok"].click()
                await asyncio.sleep(1)
                self.stop()
            # 異常畫面
            elif self.scene_manager.currentScene.scene_id == "error":
                self.game.close_app()
                self.stop()
            else:
                await asyncio.sleep(1)
                self.stop()
        else:
            await asyncio.sleep(1)