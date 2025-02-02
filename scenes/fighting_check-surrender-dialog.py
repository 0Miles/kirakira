from libs.classes.scene_base import scene

@scene
class FightingCheckSurrenderDialog():
    scene_id = "fighting_check-surrender-dialog"
    identification_images = [
        "scenes/fighting/check-surrender-dialog/dialog.png",
        ["scenes/button-ok.png", "scenes/button-ok-hover.png"],
        ["scenes/button-cancel.png", "scenes/button-cancel-hover.png"]
    ]
    button_configs = [
        {
            "id": "ok", 
            "template": ["scenes/button-ok.png", "scenes/button-ok-hover.png"]
        },
        {
            "id": "cancel", 
            "template": ["scenes/button-cancel.png", "scenes/button-cancel-hover.png"]
        },
    ]