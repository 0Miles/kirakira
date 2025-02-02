from libs.classes.scene_base import SceneBase

class FightingResult(SceneBase):
    scene_id = "fighting_result"
    identification_images = [
        "scenes/fighting/result/result.png",
        [
            "scenes/fighting/result/win.png",
            "scenes/fighting/result/lose.png",
        ]
    ]
    button_configs = [
        {
            "id": "surrender", 
            "template": ["scenes/fighting/result/button-ok.png", "scenes/fighting/result/button-ok-hover.png"]
        },
    ]