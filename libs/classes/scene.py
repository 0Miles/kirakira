from typing import TYPE_CHECKING, List, Dict
from libs.classes.button import Button
from libs.classes.input import TextInput, Select, Checkbox

if TYPE_CHECKING:
    from libs.scene_manager import SceneManager

class Scene:
    scene_id: str
    template: List[str]
    scene_manager: 'SceneManager'
    button_configs: List[Dict] = []  # 定義按鈕結構 [{id: str, template: str | list, region: list, color: bool}]
    input_configs: List[Dict] = []  # 定義輸入框結構 [{id: str, type: str, label_template: str, offset: (x, y), input_template: str, position: str, checked_template: str | list}]
    order: int = 0

    def __init__(self, scene_manager: 'SceneManager' = None, scene_id: str = None, template: List[str] = None, button_configs: List[Dict] = None, input_configs: List[Dict] = None, order: int = 0):
        self.scene_manager = scene_manager
        self.order = order
        if scene_id is not None:
            self.scene_id = scene_id
        if template is not None:
            self.template = template
        if button_configs is not None:
            self.button_configs = button_configs
        if input_configs is not None:
            self.input_configs = input_configs
        
        self.buttons: Dict[str, Button] = {}
        self.inputs: Dict[str, TextInput | Select | Checkbox] = {}
        
        # 依據 button_configs 配置實例化 Button
        for button_config in self.button_configs:
            self.buttons[button_config["id"]] = Button(
                button_config["id"], 
                scene_manager,
                button_config.get("template", None),
                button_config.get("position", None),
                button_config.get("region", None),
                button_config.get("color", False),
                button_config.get("threshold", 0.8)
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
                    scene_manager
                )
            elif input_type == "select":
                self.inputs[input_config["id"]] = Select(
                    input_config["id"],
                    input_config["label_template"], 
                    input_offset, 
                    input_config["input_template"], 
                    input_position,
                    scene_manager
                )
            elif input_type == "checkbox":
                self.inputs[input_config["id"]] = Checkbox(
                    input_config["id"],
                    input_config["label_template"], 
                    input_offset, 
                    input_config["input_template"], 
                    input_position,
                    input_config.get("checked_template", []),
                    scene_manager
                )
