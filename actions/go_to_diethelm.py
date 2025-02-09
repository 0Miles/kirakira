import asyncio
from libs.classes.action_base import ActionBase, once, loop

class GoToDiethelm(ActionBase):
    @loop("title-screen")
    async def handle_title_screen(self):
        self.scene_manager.currentScene.buttons["start"].click()
        await asyncio.sleep(1)

    @once("now-loading", None, 300)
    async def handle_now_loading(self):
        await asyncio.sleep(1)

    @loop("lobby_information-dialog")
    async def handle_lobby_information_dialog(self):
        self.scene_manager.currentScene.buttons["ok"].click()
        await asyncio.sleep(.5)

    @once("lobby")
    async def handle_lobby(self):
        await self.scene_manager.currentScene.buttons["duel"].wait_click()

    @loop("matching")
    async def handle_matching(self):
        button_x, button_y = self.scene_manager.get_scaled_position(400,160)
        self.scene_manager.game.click(button_x, button_y)
        await asyncio.sleep(1)

    @once("matching_diethelm")
    async def handle_matching_diethelm(self):
        print("[INFO] 已進入 Diethelm")
        self.stop()

    @once("error")
    async def handle_error(self):
        print("[INFO] 出現錯誤畫面，關閉遊戲")
        self.stop()
        self.game.close_app()