from libs.classes.scene_base import scene

@scene
class MatchingDiethelmWatingDialog():
    scene_id = "matching_diethelm_wating-dialog"
    identification_images = [
        "scenes/matching/title.png",
        "scenes/matching/diethelm/wating/wating-left-bottom.png",
        "scenes/matching/diethelm/wating/wating-right-bottom.png",
        "scenes/matching/diethelm/wating/wating-top.png",
    ]

    button_configs = [
        {
            "id": "cancel", 
            "template": ["scenes/matching/diethelm/wating/button-cancel.png", "scenes/matching/diethelm/wating/button-cancel-hover.png"]
        },
    ]