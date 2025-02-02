from libs.classes.scene_base import scene

@scene
class LobbyInformationDialog():
    scene_id = "lobby_information-dialog"
    identification_images = [
        "scenes/lobby/information-dialog/dialog-title.png",
        ["scenes/lobby/information-dialog/button-ok.png", "scenes/lobby/information-dialog/button-ok-hover.png"]
    ]

    button_configs = [
        {
            "id": "ok", 
            "template": ["scenes/lobby/information-dialog/button-ok.png", "scenes/lobby/information-dialog/button-ok-hover.png"]
        }
    ]