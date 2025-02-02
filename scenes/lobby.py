from libs.classes.scene_base import scene

@scene
class Lobby():
    scene_id = "lobby"
    identification_images = [
        "scenes/lobby/left-top.png",
        "scenes/lobby/left-bottom.png",
        "scenes/lobby/left.png"
    ]
    button_configs = [
        {
            "id": "duel", 
            "template": ["scenes/lobby/button-duel.png", "scenes/lobby/button-duel-hover.png"]
        }
    ]