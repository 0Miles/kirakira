import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import os
import importlib
from libs.app_control import AppControl
from utils.image_processing import ImageProcessor
from utils.constants import SCENES_DIR, TEMPLATES_DIR
from utils.ocr import OCRProcessor

class SceneManager:
    def __init__(self, game: AppControl):
        self.currentScene = None
        self.prevAvailableScene = None
        self.image_processor = ImageProcessor()
        self.ocr_processor = OCRProcessor()
        self.scenes = self.load_scene_classes()
        self.game = game  # 存儲 AppControl 實例
    
    def load_scene_classes(self):
        scenes = {}
        if os.path.exists(SCENES_DIR):
            for filename in os.listdir(SCENES_DIR):
                if filename.endswith(".py") and filename != "__init__.py":
                    module_name = f"scenes.{filename[:-3]}"
                    module = importlib.import_module(module_name)
                    class_name = filename[:-3].title().replace("-", "").replace("_", "")
                    if hasattr(module, class_name):
                        scene_instance = getattr(module, class_name)(scene_manager=self)
                        scenes[scene_instance.scene_id] = scene_instance
        return scenes
    
    def find_matching_scene(self, screenshot, parent_scene=None):
        for scene_id, scene in self.scenes.items():
            if parent_scene and not scene_id.startswith(parent_scene + "_"):
                continue
            required_images = scene.identification_images
            match_all = all(
                any(self.image_processor.match_template(screenshot, os.path.join(TEMPLATES_DIR, img), threshold=0.9)
                    for img in (img_list if isinstance(img_list, list) else [img_list]))
                for img_list in required_images
            )
            if match_all:
                sub_scene = self.find_matching_scene(screenshot, scene_id)
                return sub_scene if sub_scene else scene
        return None
    
    async def update_scene_async(self, scene):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, self.update_scene, scene)

    def update_scene(self):
        # try:
        #     if not self.game.is_app_focused():
        #         self.game.focus_window()
        # except Exception as e:
        #     print(f"[WARNING] 無法聚焦視窗，將在 1 秒後重試: {e}")
        #     time.sleep(1)
        #     return

        window_geometry = self.game.get_window_geometry()
        if not window_geometry:
            print("[ERROR] 無法獲取視窗大小與位置。")
            return

        screenshot = self.game.capture_screen()
        detected_scene = self.find_matching_scene(screenshot)
        if detected_scene != self.currentScene:
            if not self.currentScene is None:
                self.prevAvailableScene = self.currentScene
            self.currentScene = detected_scene
            if self.currentScene:
                print(f"[SCENE] 場景切換: {self.currentScene.scene_id}")
                if hasattr(self.currentScene, "execute_actions"):
                    self.currentScene.execute_actions()