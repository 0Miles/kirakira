import os
import importlib
import inspect
from typing import Dict, Type, Optional, Any

from libs.classes.action_base import ActionBase
from libs.classes.service_base import ServiceBase
from libs.constants import ACTIONS_DIR, SERVICES_DIR
from libs.steam_control import SteamControl
from libs.app_control import AppControl
from libs.scene_manager import SceneManager

class Puppeteer:
    def __init__(self, steam_control: SteamControl, app_control: AppControl, scene_manager: SceneManager = None):
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

    async def load_services(self) -> None:
        if not os.path.exists(SERVICES_DIR):
            os.makedirs(SERVICES_DIR)
            
        for filename in os.listdir(SERVICES_DIR):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f"services.{module_name}")
                    
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, ServiceBase) and 
                            obj != ServiceBase):
                            
                            # 創建服務實例
                            service_instance = obj(scene_manager=self.scene_manager)
                            self.services[obj.__name__] = service_instance
                            print(f"[INFO] 已載入服務: {obj.__name__}")
                            
                except Exception as e:
                    print(f"[ERROR] 載入服務 {module_name} 時發生錯誤: {e}")

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
        if not os.path.exists(ACTIONS_DIR):
            os.makedirs(ACTIONS_DIR)
            
        for filename in os.listdir(ACTIONS_DIR):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f"actions.{module_name}")
                    
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
                            print(f"[INFO] 已載入動作: {name}")
                            
                except Exception as e:
                    print(f"[ERROR] 載入動作 {module_name} 時發生錯誤: {e}")

    def get_action(self, action_name: str) -> Optional[ActionBase]:
        return self.actions.get(action_name)

    async def start_action(self, action_name: str) -> bool:
        self.scene_manager.check_window_size_info()
        script = self.get_action(action_name)
        if script:
            print(f"[INFO] 開始執行動作: {action_name}")
            await script.run()
            return True
        print(f"[WARNING] 找不到動作: {action_name}")
        return False

    def stop_action(self, action_name: str) -> bool:
        script = self.get_action(action_name)
        if script:
            try:
                script.stop()
                return True
            except Exception as e:
                print(f"[ERROR] 停止動作 {action_name} 時發生錯誤: {e}")
                return False
        return False

    def stop_all_actions(self) -> None:
        print(f"[INFO] 正在停止所有動作")
        for action_name, script in self.actions.items():
            try:
                script.stop()
            except Exception as e:
                print(f"[ERROR] 停止動作 {action_name} 時發生錯誤: {e}")

    def list_available_actions(self) -> list[str]:
        return list(self.actions.keys())