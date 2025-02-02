from libs.classes.scene_base import scene

@scene
class FightingSurrenderDialog():
    scene_id = "fighting_surrender-dialog"
    identification_images = [
        "scenes/fighting/surrender-dialog/dialog.png",
        ["scenes/button-ok.png", "scenes/button-ok-hover.png"],
    ]
    button_configs = [
        {
            "id": "ok", 
            "template": ["scenes/button-ok.png", "scenes/button-ok-hover.png"]
        },
    ]