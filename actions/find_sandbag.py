import time
from libs.classes.action_base import ActionBase, once, loop
import asyncio
import config
from services.room_service import RoomService
from libs.logger import logger

class FindSandbag(ActionBase):
    room_service: RoomService

    fight_start_time = None
    ap_not_enough = False
    green_tea_not_enough = False

    async def on_start(self):
        self.fight_start_time = None

    @once("matching_diethelm")
    async def handle_matching_diethelm(self):
        if not self.ap_not_enough:
            await self.scene_manager.currentScene.buttons["create"].wait_click()
            await asyncio.sleep(1)
        else:
            self.scene_manager.currentScene.buttons["item"].click()
            await asyncio.sleep(1)

    @once("matching_diethelm_use-item-dialog")
    async def handle_matching_diethelm_use_item_dialog(self):
        if self.ap_not_enough:
            has_green_tea = self.scene_manager.currentScene.buttons["purple-tea"].click()
            await asyncio.sleep(.5)
            if has_green_tea:
                self.scene_manager.currentScene.buttons["use"].click()
                self.ap_not_enough = False
                await asyncio.sleep(.5)
            else:
                self.green_tea_not_enough = True
                self.stop()
        self.scene_manager.currentScene.buttons["close"].click()
        await asyncio.sleep(1)

    @once("matching_diethelm_create-dialog")
    async def handle_matching_diethelm_create_dialog(self):
        if not self.scene_manager.currentScene.inputs["select-rule"].select_option("scenes/matching/diethelm/create-dialog/option-3v3.png"):
            # 若沒有找到，改選另一個 3v3 option 的 template
            self.scene_manager.currentScene.inputs["select-rule"].select_option("scenes/matching/diethelm/create-dialog/option-3v3-2.png")
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
        room_list = self.room_service.check_room_list()
        if len(room_list) > 0 and not any(room["owner"] == config.FIND_SANDBAG_USERNAME for room in room_list):
            self.scene_manager.currentScene.buttons["cancel"].click()
        await asyncio.sleep(1)

    @once("now-loading", None, 300)
    async def handle_now_loading(self):
        await asyncio.sleep(1)

    @once("matching_diethelm_ap-not-enough-dialog")
    async def handle_matching_diethelm_ap_not_enough_dialog(self):
        self.scene_manager.currentScene.buttons["ok"].click()
        self.ap_not_enough = True
        await asyncio.sleep(1)

    @loop("fighting")
    async def handle_fighting(self):
        # 第一次進入戰鬥時記錄時間
        if self.fight_start_time is None:
            self.fight_start_time = time.time()
            logger.info(f"開始戰鬥時間: {time.strftime('%H:%M:%S', time.localtime(self.fight_start_time))}")
        
        # 檢查戰鬥時間
        current_time = time.time()
        elapsed_time = current_time - self.fight_start_time
        if elapsed_time > 180:  # 超過3分鐘 (180秒)
            logger.info("戰鬥時間超過3分鐘，掛機中")
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
        logger.info("出現錯誤畫面，關閉遊戲")
        self.stop()
        self.game.close_app()