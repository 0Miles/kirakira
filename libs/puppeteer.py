import os
import importlib
import inspect
from typing import Dict, Type, Optional, Any
import logging

from libs.classes.action_base import ActionBase
from libs.classes.service_base import ServiceBase
from libs.steam_control import SteamControl
from libs.app_control import AppControl
from libs.scene_manager import SceneManager

class Puppeteer:
    def __init__(self, steam_control: SteamControl, app_control: AppControl, scene_manager: SceneManager = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.actions: Dict[str, ActionBase] = {}
        self.services: Dict[str, Any] = {}
        
        # 初始化共享的控制器實例
        self.steam_control = steam_control
        self.app_control = app_control
        self.scene_manager = scene_manager if scene_manager else SceneManager(app_control)

    async def initialize(self) -> None:
        # 首先載入所有服務
        await self.load_services()
        # 然後載入所有動作
        await self.load_actions()
        print("[INFO] Puppeteer 初始化完成")
        self.logger.info("Puppeteer 初始化完成")

    async def load_services(self) -> None:
        services_dir = 'services'
        if not os.path.exists(services_dir):
            os.makedirs(services_dir)
            
        for filename in os.listdir(services_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f'services.{module_name}')
                    
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, ServiceBase) and 
                            obj != ServiceBase):
                            
                            # 創建服務實例
                            service_instance = obj(scene_manager=self.scene_manager)
                            self.services[obj.__name__] = service_instance
                            self.logger.info(f"已載入服務: {obj.__name__}")
                            
                except Exception as e:
                    self.logger.error(f"載入服務 {module_name} 時發生錯誤: {e}")

    def _inject_dependencies(self, instance: Any) -> None:
        # 獲取類的 __annotations__ (類型註解)
        annotations = instance.__class__.__annotations__

        # 遍歷所有被標注的屬性
        for attr_name, attr_type in annotations.items():
            # 檢查是否是需要注入的服務
            service = self.services.get(attr_type.__name__)
            if service:
                setattr(instance, attr_name, service)
    
    async def load_actions(self) -> None:
        actions_dir = 'actions'
        if not os.path.exists(actions_dir):
            os.makedirs(actions_dir)
            
        for filename in os.listdir(actions_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f'actions.{module_name}')
                    
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, ActionBase) and 
                            obj != ActionBase):
                            
                            # 創建動作實例並注入基本依賴
                            action_instance = obj(
                                steam=self.steam_control,
                                game=self.app_control,
                                scene_manager=self.scene_manager
                            )
                            
                            # 注入服務依賴
                            self._inject_dependencies(action_instance)
                            
                            self.actions[name] = action_instance
                            self.logger.info(f"已載入動作: {name}")
                            
                except Exception as e:
                    self.logger.error(f"載入動作 {module_name} 時發生錯誤: {e}")

    def get_action(self, script_name: str) -> Optional[ActionBase]:
        return self.actions.get(script_name)

    async def start_action(self, script_name: str) -> bool:
        self.scene_manager.check_window_size_info()
        script = self.get_action(script_name)
        if script:
            print(f"[INFO] 開始執行動作: {script_name}")
            await script.run()
            return True
        print(f"[WARNING] 找不到動作: {script_name}")
        self.logger.warning(f"找不到動作: {script_name}")
        return False

    def stop_action(self, script_name: str) -> bool:
        script = self.get_action(script_name)
        if script:
            try:
                script.stop()
                print(f"[INFO] 停止動作: {script_name}")
                return True
            except Exception as e:
                print(f"[ERROR] 停止動作 {script_name} 時發生錯誤: {e}")
                self.logger.error(f"停止動作 {script_name} 時發生錯誤: {e}")
                return False
        return False

    def stop_all_actions(self) -> None:
        for script_name, script in self.actions.items():
            try:
                script.stop()
                print(f"[INFO] 停止所有動作")
            except Exception as e:
                self.logger.error(f"停止動作 {script_name} 時發生錯誤: {e}")

    def list_available_actions(self) -> list[str]:
        return list(self.actions.keys())