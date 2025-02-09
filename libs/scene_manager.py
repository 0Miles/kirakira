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
    def __init__(self, game: AppControl, template_origin_client_size=None, title_bar_height=0, frame_left=0):
        self.currentScene: Optional['Scene'] = None
        self.prevAvailableScene: Optional['Scene'] = None
        self.image_processor = ImageProcessor()
        self.ocr_processor = OCRProcessor()
        self.scenes: Dict[str, 'Scene'] = self.load_scenes()
        self.game = game
        self.extra_info = {}

        self._template_origin_client_size = template_origin_client_size  # 設定模板原始尺寸
        self._scale_ratio = 1
        self._frame_left = frame_left
        self._title_bar_height = title_bar_height
        self.check_window_size_info()

    def get_scaled_position(self, x: int, y: int) -> tuple[int, int]:
        """
        根據當前視窗縮放比例計算實際座標
        Args:
            x: 原始 x 座標
            y: 原始 y 座標
        Returns:
            tuple[int, int]: 縮放後的 (x, y) 座標
        """
        if not self._scale_ratio:
            self.check_window_size_info()
        
        scaled_x = int(x * self._scale_ratio)
        scaled_y = int(y * self._scale_ratio)
        
        return (scaled_x, scaled_y)

    def get_safe_client_region(self, x: int, y: int, width: int, height: int) -> tuple[int, int, int, int]:
        if not self._scale_ratio:
            self.check_window_size_info()

        # 計算縮放後的座標和尺寸
        scaled_x = int((x ) * self._scale_ratio)
        scaled_y = int((y ) * self._scale_ratio)
        scaled_width = int(width * self._scale_ratio)
        scaled_height = int(height * self._scale_ratio)

        scaled_title_height = int(self._title_bar_height * self._scale_ratio)
        scaled_frame_left = int(self._frame_left * self._scale_ratio)
        
        return (scaled_x + scaled_frame_left, scaled_y + scaled_title_height, scaled_width, scaled_height)

    def check_window_size_info(self):
        """獲取當前視窗與模板比例"""
        
        window_size_info = self.game.get_window_size_info()
        if not window_size_info:
            print("[WARNING] 無法獲取視窗資訊，使用預設比例 1")
            return 1

        client_width = window_size_info["client_rect"][2]
        client_height = window_size_info["client_rect"][3]
        dpi_scale = window_size_info["dpi_scale"]

        # 計算實際的客戶區域尺寸（考慮 DPI 縮放）
        actual_width = int(client_width / dpi_scale)
        actual_height = int(client_height / dpi_scale)

        if self._template_origin_client_size:
            # 計算寬度和高度的縮放比例
            width_ratio = actual_width / self._template_origin_client_size[0]
            height_ratio = actual_height / self._template_origin_client_size[1]

            self._scale_ratio = min(width_ratio, height_ratio)

    def match_template(self, screenshot, template_path, threshold=0.8, region=None, color=False):
        offset_x, offset_y = 0, 0
        
        if region:
            x, y, w, h = region
            
            screenshot = screenshot[y:y+h, x:x+w]  # 裁剪區域
            offset_x, offset_y = x, y

        if color:
            match_region = self.image_processor.match_template_color(
                screenshot, 
                os.path.join(TEMPLATES_DIR, template_path), 
                threshold=threshold,
                scale_ratio=self._scale_ratio
            )
        else:
            match_region = self.image_processor.match_template(
                screenshot, 
                os.path.join(TEMPLATES_DIR, template_path), 
                threshold=threshold,
                scale_ratio=self._scale_ratio
            )

        if match_region:
            return [(x + offset_x, y + offset_y, w, h) for x, y, w, h in match_region]
        return None

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
                        scene_instance = Scene(
                            scene_manager=self,
                            scene_id=scene_id,
                            template=config.get('template', []),
                            button_configs=config.get('button_configs', []),
                            input_configs=config.get('input_configs', [])
                        )
                        scenes[scene_id] = scene_instance
        return scenes
    
    def find_matching_scene(self, screenshot, parent_scene: Optional[str] = None) -> Optional['Scene']:
        for scene_id, scene in self.scenes.items():
            if parent_scene and not scene_id.startswith(parent_scene + "_"):
                continue
            required_images = scene.template
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

    async def check_current_screen(self):
        screenshot = self.game.capture_screen()
        detected_scene = self.find_matching_scene(screenshot)
        if detected_scene:
            return detected_scene
        else:
            return None

    async def refresh(self):
        window_geometry = self.game.get_window_geometry()
        if not window_geometry:
            print("[ERROR] 無法獲取視窗大小與位置。")
            await asyncio.sleep(3)
            return False

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
        return True