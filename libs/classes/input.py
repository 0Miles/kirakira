import os
import time
import pyautogui
import pyperclip
from typing import List, Union, Tuple, TYPE_CHECKING
from libs.constants import TEMPLATES_DIR

if TYPE_CHECKING:
    from libs.scene_manager import SceneManager

class Input:
    def __init__(self, input_id: str, label_template: Union[str, List[str]], 
                 offset: Tuple[int, int], input_template: Union[str, List[str]], 
                 position: str, scene_manager: 'SceneManager'):
        self.input_id = input_id
        self.label_template = label_template if isinstance(label_template, list) else [label_template]
        self.offset = offset
        self.input_template = input_template if isinstance(input_template, list) else [input_template]
        self.position = position  # 指定Input相對於標籤的位置 ('top', 'bottom', 'left', 'right')
        self.scene_manager = scene_manager

    def find_input(self) -> Tuple[int, int, int, int]:
        """ 找到Input的位置 """
        screenshot = self.scene_manager.game.capture_screen()
        
        match_label = None
        # 遍歷所有標籤模板
        for template in self.label_template:
            template_ocr_result = self.scene_manager.ocr_processor.process_image(os.path.join(TEMPLATES_DIR, template))
            if not template_ocr_result[0]:
                continue

            template_ocr_text = template_ocr_result[0].get("text", "")

            label_matches = self.scene_manager.match_template(screenshot, template)
            if label_matches:
                # 遍歷匹配的標籤
                for x, y, w, h in label_matches:
                    label_region = screenshot[y:y+h, x:x+w]
                    ocr_result = self.scene_manager.ocr_processor.process_screenshot(label_region)
                    print(ocr_result)
                    for item in ocr_result:
                        if (item.get("text") == template_ocr_text):
                            result_x, result_y, result_w, result_h = item.get("position")
                            match_label = (x + result_x, y + result_y, result_w, result_h)
                            break
                else:
                    continue
                break
        
        if not match_label:
            print(f"[WARNING] 未找到標籤 {self.label_template}")
            return None
        label_x, label_y, label_w, label_h = match_label
        
        # 遍歷所有Input模板，尋找標籤旁最近的Input
        closest_input = None
        min_distance = float("inf")
        for template in self.input_template:
            input_matches = self.scene_manager.match_template(screenshot, template)
            for input_x, input_y, input_w, input_h in input_matches:
                if self.position == "left":
                    distance = abs((input_x + input_w) - label_x) + abs(input_y - label_y)
                elif self.position == "right":
                    distance = abs(input_x - (label_x + label_w)) + abs(input_y - label_y)
                elif self.position == "top":
                    distance = abs(input_x - label_x) + abs((input_y + input_h) - label_y)
                elif self.position == "bottom":
                    distance = abs(input_x - label_x) + abs(input_y - (label_y + label_h))
                
                if distance < min_distance:
                    min_distance = distance
                    closest_input = (input_x, input_y, input_w, input_h)
        
        if closest_input:
            print(f"[INFO] 找到Input {self.input_template} 位置: {closest_input}")
            return closest_input
        
        print(f"[WARNING] 未找到Input {self.input_template} 附近標籤 {self.label_template}")
        return None

    def click(self) -> bool:
        position = self.find_input()
        if position:
            x, y, w, h = position
            window_geometry = self.scene_manager.game.get_window_geometry()
            target_x = window_geometry['x'] + x + w // 2
            target_y = window_geometry['y'] + y + h // 2
            pyautogui.click(target_x, target_y)
            print(f"[INFO] 點擊Input {self.input_id}")
            return True
        print(f"[ERROR] 無法點擊Input {self.input_id}")
        return False


class TextInput(Input):
    def get_text(self) -> str:
        """ 讀取Input中的文字 """
        position = self.find_input()
        if position:
            x, y, w, h = position
            screenshot = self.scene_manager.game.capture_screen()
            input_region = screenshot[y:y+h, x:x+w]
            return self.scene_manager.ocr_processor.process_screenshot(input_region)
        print(f"[WARNING] 無法讀取Input {self.input_id} 內的文字")
        return ""
    
    def change_text(self, text: str) -> bool:
        """ 更改Input內的文字 """
        if self.click():
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('ctrl', 'v')
            print(f"[INFO] 修改Input {self.input_id} 內容為: {text}")
            return True
        print(f"[ERROR] 無法更改Input {self.input_id} 內容")
        return False


class Select(Input):
    def select_option(self, option_template: str) -> bool:
        """ 選擇下拉選單中的選項 """
        if self.click():
            time.sleep(.5)
            screenshot = self.scene_manager.game.capture_screen()
            option_matches = self.scene_manager.match_template(screenshot, option_template)
            if option_matches:
                x, y, w, h = option_matches[0]
                window_geometry = self.scene_manager.game.get_window_geometry()
                target_x = window_geometry['x'] + x + w // 2
                target_y = window_geometry['y'] + y + h // 2
                pyautogui.click(target_x, target_y)
                print(f"[INFO] 選擇選項 {option_template}")
                return True
        print(f"[ERROR] 無法選擇選項 {option_template}")
        return False


class Checkbox(Input):
    def __init__(self, input_id: str, label_template: Union[str, List[str]], 
                 offset: Tuple[int, int], input_template: Union[str, List[str]], 
                 position: str, checked_template: Union[str, List[str]], 
                 scene_manager: 'SceneManager'):
        super().__init__(input_id, label_template, offset, input_template, position, scene_manager)
        self.checked_template = checked_template if isinstance(checked_template, list) else [checked_template]
    
    def is_checked(self) -> bool:
        """ 判斷Checkbox是否已勾選 """
        screenshot = self.scene_manager.game.capture_screen()
        matches = []
        for template in self.checked_template:
            matches.extend(self.scene_manager.match_template(screenshot, template))
        return bool(matches)
    
    def toggle(self) -> None:
        """ 切換Checkbox的狀態 """
        self.click()
        print(f"[INFO] 切換Checkbox {self.input_id}")
    
    def set_checked(self, state: bool) -> None:
        """ 設定Checkbox狀態 (勾選/取消勾選) """
        if self.is_checked() != state:
            self.toggle()
        print(f"[INFO] 設定Checkbox {self.input_id} 為 {'勾選' if state else '未勾選'}")
