from game_control.room import check_room_list, join_room
from libs.classes.action_base import ActionBase, once, loop
import asyncio
import config

class BeingASandbag(ActionBase):

    @loop("matching_diethelm")
    async def handle_matching_diethelm(self):
        room_list = check_room_list(self.scene_manager)
        if room_list:
            target_room = next(
                (room for room in room_list if config.AUTO_SANDBAG_TARGET_USERNAME in room['owner']), 
                None
            )
            if target_room:
                join_room(
                    self.scene_manager, 
                    target_room['position'], 
                    target_room['owner']
                )
                await asyncio.sleep(.5)

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
        self.game.close_app()
        await asyncio.sleep(1)
        self.stop()

    @once("error")
    async def handle_error(self):
        print("[INFO] 出現錯誤畫面，關閉遊戲")
        self.game.close_app()
        await asyncio.sleep(1)
        self.stop()