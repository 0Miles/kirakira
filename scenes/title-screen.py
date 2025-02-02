from libs.classes.scene_base import SceneBase

class TitleScreen(SceneBase):
    scene_id = "title-screen"
    identification_images = ["scenes/title-screen/click-to-start.png"]
    button_configs = [
        {
            "id": "start", 
            "template": "scenes/title-screen/click-to-start.png"
        }
    ]