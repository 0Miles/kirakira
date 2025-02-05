import asyncio
import os
import json
import importlib
from typing import Dict, Optional, List

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
        self.extra_info = {}
        self._next_scene_futures: List[asyncio.Future] = []

    def match_template(self, screenshot, template_path, threshold=0.8):
        return self.image_processor.match_template(screenshot, os.path.join(TEMPLATES_DIR, template_path), threshold)

    def find_first_matching_template_key(self, screenshot, template_dict, threshold=0.8):
        result = None
        for key in template_dict.keys():
            matches = self.match_template(screenshot, template_dict[key], threshold)
            if matches:
                result = key
                break
        return result

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
                any(self.match_template(screenshot, img, threshold=0.9)
                    for img in (img_list if isinstance(img_list, list) else [img_list]))
                for img_list in required_images
            )
            if match_all:
                sub_scene = self.find_matching_scene(screenshot, scene_id)
                return sub_scene if sub_scene else scene
        return None

    def scene_has_changed(self):
        return self.currentScene and self.prevAvailableScene and self.currentScene.scene_id != self.prevAvailableScene.scene_id

    async def onNextScene(self) -> None:
        """等待下一次場景切換"""
        future = asyncio.Future()
        self._next_scene_futures.append(future)
        await future

    async def refresh(self):
        window_geometry = self.game.get_window_geometry()
        if not window_geometry:
            print("[ERROR] 無法獲取視窗大小與位置。")
            await asyncio.sleep(3)
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
                
                # 完成所有等待場景切換的 Future
                for future in self._next_scene_futures:
                    if not future.done():
                        future.set_result(None)
                self._next_scene_futures.clear()