from libs.classes.action_base import ActionBase, once, loop
from services.room_service import RoomService
import asyncio
import config

class BeingASandbag(ActionBase):
    room_service: RoomService

    @loop("matching_diethelm")
    async def handle_matching_diethelm(self):
        # 使用注入的服務
        room_list = self.room_service.check_room_list()
        if room_list:
            target_room = next(
                (room for room in room_list if config.AUTO_SANDBAG_TARGET_USERNAME in room['owner']), 
                None
            )
            if target_room:
                await self.room_service.join_room(
                    target_room['position'], 
                    target_room['owner']
                )
                await asyncio.sleep(.5)
    
    @once("matching_diethelm_room-is-full-dialog")
    async def handle_matching_diethelm_room_is_full_dialog(self):
        self.scene_manager.currentScene.buttons["ok"].click()
        await asyncio.sleep(1)

    @once("now-loading", None, 300)
    async def handle_now_loading(self):
        pass

    @loop("fighting")
    async def handle_fighting(self):
        await asyncio.sleep(1)
        self.scene_manager.currentScene.buttons["surrender"].click()
        await asyncio.sleep(1)

    @loop("fighting_check-surrender-dialog")
    async def handle_fighting_check_surrender_dialog(self):
        self.scene_manager.currentScene.buttons["ok"].click()
        await asyncio.sleep(1)

    @once("fighting_surrender-dialog")
    async def handle_fighting_surrender_dialog(self):
        self.scene_manager.currentScene.buttons["ok"].click()
        self.stop()
        self.game.close_app()
        await asyncio.sleep(1)

    @once("error")
    async def handle_error(self):
        print("[INFO] 出現錯誤畫面，關閉遊戲")
        self.game.close_app()
        await asyncio.sleep(1)
        self.stop()