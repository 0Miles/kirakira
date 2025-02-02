import os
from libs.classes.scene_base import SceneBase
from utils.constants import TEMPLATES_DIR

class MatchingDiethelm(SceneBase):
    scene_id = "matching_diethelm"
    identification_images = [
        "scenes/matching/title.png",
        "scenes/matching/left-bottom.png",
        "scenes/matching/right-top.png",
        "scenes/matching/diethelm/title.png",
    ]
    button_configs = [
        {
            "id": "create", 
            "template": ["scenes/matching/diethelm/button-create.png", "scenes/matching/diethelm/button-create-hover.png"]
        },
        {
            "id": "enter", 
            "template": ["scenes/matching/diethelm/button-enter.png", "scenes/matching/diethelm/button-enter-hover.png"]
        },
    ]