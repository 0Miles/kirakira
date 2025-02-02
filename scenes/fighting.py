from libs.classes.scene_base import scene

@scene
class Fighting():
    scene_id = "fighting"
    identification_images = [
        "scenes/fighting/turn.png",
        [
            "scenes/fighting/button-ok-hover.png",
            "scenes/fighting/button-ok-disabled.png",
            "scenes/fighting/button-ok.png"
        ]
    ]
    button_configs = [
        {
            "id": "surrender", 
            "template": ["scenes/fighting/button-surrender.png", "scenes/fighting/button-surrender-hover.png"]
        },
    ]