import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import os
import json
import importlib
from typing import Dict, Optional

from libs.app_control import AppControl
from libs.image_processing import ImageProcessor
from libs.ocr import OCRProcessor
from libs.classes.scene import Scene
from libs.constants import SCENES_DIR, TEMPLATES_DIR

class SceneManager:
    def __init__(self, game: AppControl):
        self.currentScene: Optional['Scene'] = None
        self.prevAvailableScene: Optional['Scene'] = None
        self.image_processor = ImageProcessor()
        self.ocr_processor = OCRProcessor()
        self.scenes: Dict[str, 'Scene'] = self.load_scenes()
        self.game = game

    def load_scenes(self) -> Dict[str, 'Scene']:
        scenes = {}
        if os.path.exists(SCENES_DIR):
            # load scenes from Python files
            for filename in os.listdir(SCENES_DIR):
                if filename.endswith(".py") and not filename.startswith("__"):
                    module_name = f"scenes.{filename[:-3]}"
                    module = importlib.import_module(module_name)
                    class_name = filename[:-3].title().replace("-", "").replace("_", "")
                    if hasattr(module, class_name):
                        scene_class = getattr(module, class_name)
                        scene_instance = scene_class(scene_manager=self)
                        scenes[scene_instance.scene_id] = scene_instance
            # load scenes from JSON files
            for filename in os.listdir(SCENES_DIR):
                if filename.endswith(".json"):
                    config_path = os.path.join(SCENES_DIR, filename)
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    scene_id = config.get('scene_id', filename[:-5])
                    if not scenes.get(scene_id):
                        scene_instance = Scene(scene_manager=self, scene_id=scene_id, identification_images=config.get('identification_images', []), button_configs=config.get('button_configs', []), input_configs=config.get('input_configs', []))
                        scenes[scene_id] = scene_instance
        return scenes
    
    def find_matching_scene(self, screenshot, parent_scene: Optional[str] = None) -> Optional['Scene']:
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
    
    async def refresh_async(self, scene: 'Scene'):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, self.refresh, scene)

    def refresh(self):
        window_geometry = self.game.get_window_geometry()
        if not window_geometry:
            print("[ERROR] 無法獲取視窗大小與位置。")
            time.sleep(3)
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