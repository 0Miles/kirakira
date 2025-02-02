from libs.classes.scene_base import scene

@scene
class Matching():
    scene_id = "matching"
    identification_images = [
        "scenes/matching/title.png",
        "scenes/matching/left-bottom.png",
        "scenes/matching/right-top.png",
    ]
    button_configs = [
        {
            "id": "diethelm", 
            "template": ["scenes/matching/button-diethelm.png", "scenes/matching/button-diethelm-hover.png"]
        }
    ]