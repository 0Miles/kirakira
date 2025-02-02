import os

import pyautogui

from libs.scene_manager import SceneManager
from utils.constants import TEMPLATES_DIR


class Button:
    scene_manager: SceneManager
    def __init__(self, button_id, template, scene_manager):
        self.button_id = button_id
        self.template = template if isinstance(template, list) else [template]
        self.scene_manager = scene_manager

    def click(self):
        try:
            window_geometry = self.scene_manager.game.get_window_geometry()
            screenshot = self.scene_manager.game.capture_screen()
            
            for template in self.template:
                matches = self.scene_manager.image_processor.match_template(
                    screenshot, os.path.join(TEMPLATES_DIR, template)
                )
                if matches:
                    # 計算目標按鈕在畫面中的坐標
                    x, y, w, h = matches[0]  # 取第一個匹配結果
                    target_x = window_geometry['x'] + x + w // 2
                    target_y = window_geometry['y'] + y + h // 2
                    
                    # 將游標移到目標坐標並點擊
                    pyautogui.moveTo(target_x, target_y)
                    pyautogui.click()
                    print(f"[INFO] 點擊按鈕: {self.button_id} at ({target_x}, {target_y})")
                    return True
            
            print(f"[WARNING] 未找到按鈕 {self.button_id} 的匹配項")
            return False
        except Exception as e:
            print(f"[ERROR] 點擊按鈕 {self.button_id} 時發生錯誤: {e}")
            return False
