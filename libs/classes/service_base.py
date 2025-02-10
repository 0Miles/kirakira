from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from libs.scene_manager import SceneManager

class ServiceBase:
    def __init__(self, scene_manager: 'SceneManager'):
        self.scene_manager = scene_manager
