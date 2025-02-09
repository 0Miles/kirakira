import config
from libs.classes.action_base import ActionBase, once, loop
from game_control.bonus import check_bonus_info, click_bonus_item
import asyncio

class BonusGameStarRankMode(ActionBase):

    bonus_get_failed_count = 0
    
    @loop("result")
    async def handle_result(self):
        self.scene_manager.currentScene.buttons["ok"].click()
        await asyncio.sleep(1)

    @loop("result_bonus-select")
    async def handle_result_bonus_select(self):
        bonus_info = check_bonus_info(self.scene_manager)
        current_bonus = bonus_info.get("current_bonus")

        if current_bonus in config.BONUS_GAME_TARGET_ITEMS and (not config.MIN_GET_STAR_RANK or bonus_info.get("star_rank", 0) > config.MIN_GET_STAR_RANK):
            if not await self.scene_manager.currentScene.buttons["get"].wait_click(3):
                self.scene_manager.currentScene.buttons["get"].click_prev_success_position()
        else:
            self.scene_manager.currentScene.buttons["next"].click()
        await asyncio.sleep(1)

    @loop("result_bonus-highlow")
    async def handle_result_bonus_highlow(self):
        bonus_info = check_bonus_info(self.scene_manager)
        target_num = bonus_info.get("target_num")
        print(f"[INFO] 目標數字: {target_num}")
        if target_num > 7:
            print(f"[INFO] 選擇 low")
            self.scene_manager.currentScene.buttons["low"].click()
        else:
            print(f"[INFO] 選擇 high")
            self.scene_manager.currentScene.buttons["high"].click()
        await asyncio.sleep(1)

    @loop("result_bonus-failed")
    async def handle_result_bonus_failed(self):
        bonus_info = check_bonus_info(self.scene_manager)
        if config.USE_ITEM_WHEN_FAILED and len(config.USE_ITEM_WHEN_FAILED) > 0 and (not config.MAX_GET_STAR_RANK or bonus_info.get("star_rank", 0) < config.MAX_GET_STAR_RANK):
            self.scene_manager.currentScene.buttons["use-item"].click()
        else:
            if config.FAILED_AND_NO_ITEM_OR_OVER_MAX_STAR_RANK == "close":
                print("[INFO] 關閉遊戲")
                self.stop()
                self.game.close_app()
            elif config.FAILED_AND_NO_ITEM_OR_OVER_MAX_STAR_RANK == "exit":
                exit_bonus_game_x, exit_bonus_game_y = self.scene_manager.get_scaled_position(562,240)
                self.game.click(exit_bonus_game_x, exit_bonus_game_y)
            else:
                pass

    @once("result_bonus-failed_use-item-dialog")
    async def handle_result_bonus_failed_use_item_dialog(self):
        use_item = False
        for use_item in config.USE_ITEM_WHEN_FAILED:
            print(f"[INFO] 尋找: {use_item}")
            click_item_result = await click_bonus_item(self.scene_manager, use_item)
            await asyncio.sleep(.5)
            if click_item_result:
                print(f"[INFO] 嘗試使用: {use_item}")
                click_use_result = await self.scene_manager.currentScene.buttons["use"].try_wait_click(3, .5)
                if click_use_result:
                    use_item = True
                    break
            else:
                print(f"[INFO] 未找到: {use_item}")

        if not use_item:
            print("[INFO] 沒有可使用道具")

            # 沒有可使用道具時，退回洗GEM模式
            config.BONUS_GAME_TARGET = "gem" # 洗GEM模式
            config.BONUS_GAME_TARGET_ITEMS = ["green-tea", "gem"]

            if config.FAILED_AND_NO_ITEM_OR_OVER_MAX_STAR_RANK == "close":
                print("[INFO] 關閉遊戲")
                self.stop()
                self.game.close_app()
            elif config.FAILED_AND_NO_ITEM_OR_OVER_MAX_STAR_RANK == "exit":
                exit_bonus_game_x, exit_bonus_game_y = self.scene_manager.get_scaled_position(562,240)
                self.game.click(exit_bonus_game_x, exit_bonus_game_y)
            else:
                pass
        await asyncio.sleep(1)

    @once("error")
    async def handle_error(self):
        print("[INFO] 出現錯誤畫面，關閉遊戲")
        self.stop()
        self.game.close_app()