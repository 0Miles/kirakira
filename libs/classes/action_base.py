import asyncio
from abc import ABC, abstractmethod
from typing import Optional
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from libs.scene_manager import SceneManager
    from libs.app_control import AppControl
    from libs.steam_control import SteamControl

class ActionBase(ABC):
    def __init__(self, steam: 'SteamControl', game: 'AppControl', scene_manager: 'SceneManager'):
        self.steam = steam
        self.game = game
        self.scene_manager = scene_manager
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def process(self):
        """
        實現具體的腳本流程邏輯
        此方法必須由子類實現
        """
        pass

    async def on_start(self):
        """
        生命週期方法：腳本開始執行時調用
        子類可以覆寫此方法以添加自定義的啟動邏輯
        """
        pass

    async def on_end(self):
        """
        生命週期方法：腳本結束執行時調用
        子類可以覆寫此方法以添加自定義的清理邏輯
        """
        pass

    async def run(self):
        """
        在非同步循環中執行腳本流程
        """
        if self._running:
            self.logger.warning("Script is already running")
            return

        self._running = True
        try:
            await self.on_start()
            while self._running:
                await self.process()
                await asyncio.sleep(0.1)
        except Exception as e:
            self.logger.error(f"Error in script execution: {e}")
            self._running = False
            raise
        finally:
            await self.on_end()
            self._running = False

    def start(self):
        """
        啟動腳本的非同步執行
        """
        if self._task and not self._task.done():
            self.logger.warning("Script task already exists and is running")
            return

        self._task = asyncio.create_task(self.run())

    def stop(self):
        """
        停止腳本執行
        """
        self._running = False
        if self._task:
            self._task.cancel()
