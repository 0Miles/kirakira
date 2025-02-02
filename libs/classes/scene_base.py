from libs.classes.button import Button
from libs.classes.input import TextInput, Select, Checkbox
from libs.scene_manager import SceneManager

class SceneBase():
    scene_id: str
    identification_images: list
    scene_manager: SceneManager
    button_configs: list = []  # 定義按鈕結構 [{id: str, template: str | list}]
    input_configs: list = []  # 定義輸入框結構 [{id: str, type: str, label_template: str, offset: (x, y), input_template: str, position: str, checked_template: str | list}]

    def __init__(self, scene_manager=None):
        self.scene_manager = scene_manager
        self.buttons = {}
        self.inputs = {}
        
        # 依據 button_configs 配置實例化 Button
        for button_config in self.button_configs:
            self.buttons[button_config["id"]] = Button(
                button_config["id"], 
                button_config["template"], 
                self.scene_manager
            )
        
        # 依據 input_configs 配置實例化不同類型的 Input
        for input_config in self.input_configs:
            input_type = input_config.get("type", "text")
            input_position = input_config.get("position", "right")
            input_offset = input_config.get("offset", (0, 0))
            if input_type == "text":
                self.inputs[input_config["id"]] = TextInput(
                    input_config["id"],
                    input_config["label_template"], 
                    input_offset, 
                    input_config["input_template"], 
                    input_position,
                    self.scene_manager
                )
            elif input_type == "select":
                self.inputs[input_config["id"]] = Select(
                    input_config["id"],
                    input_config["label_template"], 
                    input_offset, 
                    input_config["input_template"], 
                    input_position,
                    self.scene_manager
                )
            elif input_type == "checkbox":
                self.inputs[input_config["id"]] = Checkbox(
                    input_config["id"],
                    input_config["label_template"], 
                    input_offset, 
                    input_config["input_template"], 
                    input_position,
                    input_config.get("checked_template", []),
                    self.scene_manager
                )
