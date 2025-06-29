import config
from libs.classes.action_base import ActionBase, once, loop
from services.bonus_service import BonusService
import asyncio
from libs.logger import logger

class BonusGameStarRankMode(ActionBase):
    bonus_service: BonusService

    async def on_start(self):
        self.bonus_service.reset_prev_star_rank()

    @loop("result")
    async def handle_result(self):
        self.scene_manager.currentScene.buttons["ok"].click()
        await asyncio.sleep(1)

    @loop("result_bonus-select")
    async def handle_result_bonus_select(self):
        bonus_info = self.bonus_service.check_bonus_info()
        star_rank = bonus_info.get("star_rank", self.bonus_service.prev_star_rank)

        if star_rank < 70:
            logger.info(f"star_rank < 70: {star_rank}")
            # 戰敗的場合，直接關閉遊戲
            self.stop()
            self.game.close_app()
            return
    
        await self.bonus_service.handle_bonus_select(bonus_info)
        await asyncio.sleep(1)

    @loop("result_bonus-highlow")
    async def handle_result_bonus_highlow(self):
        await self.bonus_service.handle_highlow_choice()
        await asyncio.sleep(3)

    @loop("result_bonus-failed")
    async def handle_result_bonus_failed(self):
        bonus_info = self.bonus_service.check_bonus_info()
        if config.BONUS_GAME_USE_ITEM_WHEN_FAILED and len(config.BONUS_GAME_USE_ITEM_WHEN_FAILED) > 0 and (not config.BONUS_GAME_MAX_GET_STAR_RANK or bonus_info.get("star_rank", 0) < config.BONUS_GAME_MAX_GET_STAR_RANK):
            self.scene_manager.currentScene.buttons["use-item"].click()
        else:
            if config.BONUS_GAME_WHEN_FAILED_END == "close":
                logger.info("關閉遊戲")
                self.stop()
                self.game.close_app()
            elif config.BONUS_GAME_WHEN_FAILED_END == "exit":
                self.scene_manager.currentScene.buttons["end"].click()
            else:
                pass

    @once("result_bonus-failed_use-item-dialog")
    async def handle_result_bonus_failed_use_item_dialog(self):
        for use_item in config.BONUS_GAME_USE_ITEM_WHEN_FAILED:
            logger.info(f"尋找: {use_item}")
            click_item_result = await self.bonus_service.click_bonus_item(use_item)
            await asyncio.sleep(.5)
            if click_item_result:
                logger.info(f"嘗試使用: {use_item}")
                click_use_result = await self.scene_manager.currentScene.buttons["use"].try_wait_click(3, .5)
                if click_use_result:
                    break
            else:
                logger.info(f"未找到: {use_item}")
                logger.info("退回基本模式")
                # 缺少其中一種道具時，退回基本模式，避免發生用把花5當花1用的浪費情況
                config.BONUS_GAME_TARGET = "basic" # 基本模式
                config.BONUS_GAME_TARGET_ITEMS = ["green-tea", "gem"]

                if config.BONUS_GAME_WHEN_FAILED_END == "close":
                    logger.info("關閉遊戲")
                    self.game.close_app()
                    self.stop()
                elif config.BONUS_GAME_WHEN_FAILED_END == "exit":
                    self.scene_manager.currentScene.buttons["end"].click()
                else:
                    pass
        await asyncio.sleep(1)

    @once("error")
    async def handle_error(self):
        """處理錯誤並關閉遊戲"""
        logger.info("出現錯誤畫面，關閉遊戲")
        self.stop()
        self.game.close_app()
    
    @loop("has-ok-button")
    async def handle_has_ok_button(self):
        if self.scene_manager.currentScene.buttons.get("ok"):
            self.scene_manager.currentScene.buttons["ok"].click()
        await asyncio.sleep(1)