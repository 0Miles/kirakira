import os
import importlib
import inspect
from typing import Dict, Type, Optional
import logging
import asyncio

from libs.classes.action_base import ActionBase
from libs.steam_control import SteamControl
from libs.app_control import AppControl
from libs.scene_manager import SceneManager

class Puppeteer:
    """
    主控制類，負責管理和協調所有遊戲動作的執行
    自動載入動作並注入必要的依賴
    """
    def __init__(self, steam_control: SteamControl, app_control: AppControl):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.actions: Dict[str, ActionBase] = {}
        
        # 初始化共享的控制器實例
        self.steam_control = steam_control
        self.app_control = app_control
        self.scene_manager = SceneManager(app_control)

    async def initialize(self) -> None:
        """
        初始化 Puppeteer，載入所有動作
        """
        await self.load_actions()
        self.logger.info("Puppeteer 初始化完成")

    async def load_actions(self) -> None:
        """
        自動載入 actions 目錄下的所有動作
        """
        actions_dir = 'actions'
        
        for filename in os.listdir(actions_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]  # 移除 .py 副檔名
                try:
                    # 動態導入模組
                    module = importlib.import_module(f'actions.{module_name}')
                    
                    # 在模組中尋找 ActionBase 的子類
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, ActionBase) and 
                            obj != ActionBase):
                            
                            # 創建動作實例並注入依賴
                            script_instance = obj(
                                steam=self.steam_control,
                                game=self.app_control,
                                scene_manager=self.scene_manager
                            )
                            
                            self.actions[name] = script_instance
                            self.logger.info(f"已載入動作: {name}")
                            
                except Exception as e:
                    self.logger.error(f"載入動作 {module_name} 時發生錯誤: {e}")

    def get_action(self, script_name: str) -> Optional[ActionBase]:
        """
        獲取指定名稱的動作實例
        """
        return self.actions.get(script_name)

    async def start_action(self, script_name: str) -> bool:
        """
        啟動指定的動作
        """
        script = self.get_action(script_name)
        if script:
            try:
                await script.run()
                return True
            except Exception as e:
                self.logger.error(f"啟動動作 {script_name} 時發生錯誤: {e}")
                return False
        self.logger.warning(f"找不到動作: {script_name}")
        return False

    def stop_action(self, script_name: str) -> bool:
        """
        停止指定的動作
        """
        script = self.get_action(script_name)
        if script:
            try:
                script.stop()
                return True
            except Exception as e:
                self.logger.error(f"停止動作 {script_name} 時發生錯誤: {e}")
                return False
        return False

    def stop_all_actions(self) -> None:
        """
        停止所有正在運行的動作
        """
        for script_name, script in self.actions.items():
            try:
                script.stop()
            except Exception as e:
                self.logger.error(f"停止動作 {script_name} 時發生錯誤: {e}")

    def list_available_actions(self) -> list[str]:
        """
        列出所有可用的動作名稱
        """
        return list(self.actions.keys())
