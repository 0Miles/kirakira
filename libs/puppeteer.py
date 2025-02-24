import os
import importlib
import inspect
from typing import Dict, Type, Optional, Any

from libs.classes.action_base import ActionBase
from libs.classes.service_base import ServiceBase
from libs.constants import ACTIONS_DIR, SERVICES_DIR
from libs.app_control import AppControl
from libs.scene_manager import SceneManager
from libs.logger import logger

class DependencyGraph:
    def __init__(self):
        self.graph = {}
        self.visiting = set()

    def add_edge(self, from_node: str, to_node: str):
        if from_node not in self.graph:
            self.graph[from_node] = set()
        self.graph[from_node].add(to_node)

    def detect_cycle(self, node: str, path: set = None) -> bool:
        if path is None:
            path = set()

        if node in path:
            return True

        if node in self.visiting:
            return False

        path.add(node)
        self.visiting.add(node)

        for neighbor in self.graph.get(node, []):
            if self.detect_cycle(neighbor, path):
                return True

        path.remove(node)
        return False

class Puppeteer:
    def __init__(self, game: AppControl, scene_manager: SceneManager = None):
        self.actions: Dict[str, ActionBase] = {}
        self.services: Dict[str, Type[ServiceBase]] = {}
        self.service_instances: Dict[str, Any] = {}
        
        self.game = game
        self.scene_manager = scene_manager if scene_manager else SceneManager(game)

    async def initialize(self) -> None:
        await self.load_services()
        await self.load_actions()
        logger.info("Puppeteer 初始化完成")

    async def load_services(self) -> None:
        if not os.path.exists(SERVICES_DIR):
            os.makedirs(SERVICES_DIR)
        
        dependency_graph = DependencyGraph()

        for filename in os.listdir(SERVICES_DIR):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f"services.{module_name}")
                    
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, ServiceBase) and 
                            obj != ServiceBase):
                            
                            self.services[obj.__name__] = obj
                            
                            for _, dep_type in obj.__annotations__.items():
                                if hasattr(dep_type, '__name__'):
                                    dependency_graph.add_edge(obj.__name__, dep_type.__name__)
                            
                except Exception as e:
                    logger.error(f"載入服務類 {module_name} 時發生錯誤: {e}")

        for service_name in self.services:
            if dependency_graph.detect_cycle(service_name):
                raise ValueError(f" {service_name} 檢測到循環相依")

        for service_name, service_class in self.services.items():
            await self._create_service_instance(service_name, service_class)

    async def _create_service_instance(self, service_name: str, service_class: Type[ServiceBase]) -> Any:
        if service_name in self.service_instances:
            return self.service_instances[service_name]

        instance = service_class(scene_manager=self.scene_manager)
        self.service_instances[service_name] = instance
        
        await self._inject_dependencies(instance)
        
        logger.info(f"已載入服務: {service_name}")
        return instance

    async def _inject_dependencies(self, instance: Any) -> None:
        annotations = instance.__class__.__annotations__

        for attr_name, attr_type in annotations.items():
            # 檢查是否是需要注入的服務
            service_class = self.services.get(attr_type.__name__)
            if service_class:
                # 遞迴創建依賴的服務實例
                service = await self._create_service_instance(
                    attr_type.__name__, 
                    service_class
                )
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
                                game=self.game,
                                scene_manager=self.scene_manager
                            )
                            
                            # 注入服務依賴
                            await self._inject_dependencies(action_instance)
                            
                            self.actions[name] = action_instance
                            logger.info(f"已載入動作: {name}")
                            
                except Exception as e:
                    logger.error(f"載入動作 {module_name} 時發生錯誤: {e}")

    def get_action(self, action_name: str) -> Optional[ActionBase]:
        return self.actions.get(action_name)

    async def start_action(self, action_name: str) -> bool:
        self.scene_manager.check_window_size_info()
        script = self.get_action(action_name)
        if script:
            logger.info(f"開始執行動作: {action_name}")
            await script.run()
            return True
        logger.warning(f"找不到動作: {action_name}")
        return False

    def stop_action(self, action_name: str) -> bool:
        script = self.get_action(action_name)
        if script:
            try:
                script.stop()
                return True
            except Exception as e:
                logger.error(f"停止動作 {action_name} 時發生錯誤: {e}")
                return False
        return False

    def stop_all_actions(self) -> None:
        logger.info(f"正在停止所有動作")
        for action_name, script in self.actions.items():
            try:
                script.stop()
            except Exception as e:
                logger.error(f"停止動作 {action_name} 時發生錯誤: {e}")

    def list_available_actions(self) -> list[str]:
        return list(self.actions.keys())