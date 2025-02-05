from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from libs.scene_manager import SceneManager

class Button:
    def __init__(self, button_id, template, scene_manager: 'SceneManager'):
        self.button_id = button_id
        self.template = template if isinstance(template, list) else [template]
        self.scene_manager = scene_manager

    def click(self):
        try:
            window_geometry = self.scene_manager.game.get_window_geometry()
            screenshot = self.scene_manager.game.capture_screen()
            
            for template in self.template:
                matches = self.scene_manager.match_template(screenshot, template)
                if matches:
                    # 計算相對於視窗的點擊位置
                    x, y, w, h = matches[0]  # 取第一個匹配結果
                    click_x = x + w // 2
                    click_y = y + h // 2
                    
                    # 使用 AppControl 的 click 方法
                    if self.scene_manager.game.click(click_x, click_y):
                        print(f"[INFO] 點擊按鈕: {self.button_id} at ({click_x}, {click_y})")
                        return True
                    return False
            
            print(f"[WARNING] 未找到按鈕 {self.button_id} 的匹配項")
            return False
        except Exception as e:
            print(f"[ERROR] 點擊按鈕 {self.button_id} 時發生錯誤: {e}")
            return False
