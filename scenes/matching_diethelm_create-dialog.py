from libs.classes.scene_base import SceneBase

class MatchingDiethelmCreateDialog(SceneBase):
    scene_id = "matching_diethelm_create-dialog"
    identification_images = [
        "scenes/matching/diethelm/create-dialog/title.png",
        "scenes/matching/diethelm/create-dialog/dialog-title.png"
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
        {
            "id": "corner",
            "template": "scenes/matching/diethelm/create-dialog/corner.png"
        }
    ]

    input_configs = [
        {
            "id": "text-room-name",
            "label_template": "scenes/matching/diethelm/create-dialog/label-room-name.png",
            "offset": (0, 0),
            "input_template": "scenes/matching/diethelm/create-dialog/input.png",
            "position": "right"
        },
        {
            "id": "select-rule",
            "type": "select",
            "label_template": "scenes/matching/diethelm/create-dialog/label-rule.png",
            "offset": (0, 0),
            "input_template": "scenes/matching/diethelm/create-dialog/select-rule.png",
            "position": "right"
        },
        {
            "id": "checkbox-friend",
            "type": "checkbox",
            "label_template": "scenes/matching/diethelm/create-dialog/label-friend.png",
            "offset": (0, 0),
            "input_template": "scenes/matching/diethelm/create-dialog/checkbox.png",
            "position": "right",
            "checked_template": "scenes/matching/diethelm/create-dialog/checkbox-checked.png"
        }
    ]