import time
from game_control.room import check_room_list
from libs.classes.action_base import ActionBase, once, loop
import asyncio
import config

class FindSandbag(ActionBase):
    fight_start_time = None  # 新增時間戳記屬性

    async def on_start(self):
        self.fight_start_time = None

    @once("matching_diethelm")
    async def handle_matching_diethelm(self):
        if not self.scene_manager.extra_info.get("ap-not-enough", False):
            await self.scene_manager.currentScene.buttons["create"].wait_click()
            await asyncio.sleep(1)
        else:
            self.scene_manager.currentScene.buttons["item"].click()
            await asyncio.sleep(1)

    @once("matching_diethelm_use-item-dialog")
    async def handle_matching_diethelm_use_item_dialog(self):
        has_green_tea = self.scene_manager.currentScene.buttons["green-tea"].click()
        await asyncio.sleep(.5)
        if has_green_tea:
            self.scene_manager.currentScene.buttons["use"].click()
            self.scene_manager.extra_info["ap-not-enough"] = False
            await asyncio.sleep(.5)
        else:
            self.scene_manager.extra_info["green-tea-not-enough"] = True
            self.scene_manager.currentScene.buttons["close"].click()
            self.stop()
        self.scene_manager.currentScene.buttons["close"].click()
        await asyncio.sleep(1)

    @once("matching_diethelm_create-dialog")
    async def handle_matching_diethelm_create_dialog(self):
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

    @loop("matching_diethelm_wating-dialog")
    async def handle_matching_diethelm_wating_dialog(self):
        await asyncio.sleep(3)
        room_list = check_room_list(self.scene_manager)
        if len(room_list) > 0 and not any(room["owner"] == config.FIND_SANDBAG_USERNAME for room in room_list):
            self.scene_manager.currentScene.buttons["cancel"].click()
        await asyncio.sleep(1)

    @once("now-loading", None, 300)
    async def handle_now_loading(self):
        await asyncio.sleep(1)

    @once("matching_diethelm_ap-not-enough-dialog")
    async def handle_matching_diethelm_ap_not_enough_dialog(self):
        self.scene_manager.currentScene.buttons["ok"].click()
        self.scene_manager.extra_info["ap-not-enough"] = True
        await asyncio.sleep(1)

    @loop("fighting")
    async def handle_fighting(self):
        # 第一次進入戰鬥時記錄時間
        if self.fight_start_time is None:
            self.fight_start_time = time.time()
            print(f"[INFO] 開始戰鬥時間: {time.strftime('%H:%M:%S', time.localtime(self.fight_start_time))}")
        
        # 檢查戰鬥時間
        current_time = time.time()
        elapsed_time = current_time - self.fight_start_time
        if elapsed_time > 180:  # 超過3分鐘 (180秒)
            print(f"[INFO] 戰鬥時間超過3分鐘，掛機中")
            await asyncio.sleep(10)
        else:
            # 按OK
            self.scene_manager.currentScene.buttons["ok"].click()
            await asyncio.sleep(1)

    @once("fighting_surrender-dialog")
    async def handle_fighting_surrender_dialog(self):
        self.scene_manager.currentScene.buttons["ok"].click()
        await asyncio.sleep(1)
        self.stop()

    @once("error")
    async def handle_error(self):
        print("[INFO] 出現錯誤畫面，關閉遊戲")
        self.stop()
        self.game.close_app()