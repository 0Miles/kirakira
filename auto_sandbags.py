import time

from auto_find_sandbags import check_room_list
import config
from game_control.room import join_room
from libs.steam_control import SteamControl
from libs.app_control import AppControl
from libs.scene_manager import SceneManager

from utils.constants import TEMPLATES_DIR

if __name__ == "__main__":
    print("[TEST] 初始化 Steam 和遊戲控制...")
    
    steam = SteamControl(config.STEAM_GAME_ID)
    game = AppControl(config.GAME_NAME, config.GAME_WINDOW_TITLE)
    scene_manager = SceneManager(game)
    
    while True:
        if not game.is_app_running():
            # 透過 Steam 啟動遊戲
            print(f"[TEST] 正在透過 Steam 啟動遊戲: {config.GAME_NAME}...")
            steam.start_game()

            # 檢測遊戲是否已開啟完畢
            while not game.is_app_running():
                print("[TEST] 遊戲尚未啟動，等待 5 秒後再次檢查...")
                time.sleep(5)
            print("[TEST] 遊戲啟動完成。")

        scene_manager.update_scene()
        if scene_manager.currentScene:
            if scene_manager.currentScene.scene_id == "title-screen":
                scene_manager.currentScene.buttons["start"].click()
                time.sleep(3)
            elif scene_manager.currentScene.scene_id == "lobby_information-dialog":
                scene_manager.currentScene.buttons["ok"].click()
                time.sleep(.5)
            elif scene_manager.currentScene.scene_id == "lobby":
                scene_manager.currentScene.buttons["duel"].click()
                time.sleep(1)
            elif scene_manager.currentScene.scene_id == "matching":
                scene_manager.currentScene.buttons["diethelm"].click()
                time.sleep(1)
            elif scene_manager.currentScene.scene_id == "matching_diethelm":
                room_list = check_room_list(scene_manager)
                if room_list:
                    target_room = next((room for room in room_list if room['owner'] == "燈心草"), None)
                    if target_room:
                        join_room(scene_manager, target_room['position'], target_room['owner'])
                        time.sleep(.2)
            elif scene_manager.currentScene.scene_id == "fighting":
                time.sleep(1)
                scene_manager.currentScene.buttons["surrender"].click()
                time.sleep(.5)
            elif scene_manager.currentScene.scene_id == "fighting_check-surrender-dialog":
                scene_manager.currentScene.buttons["ok"].click()
                time.sleep(.5)
            elif scene_manager.currentScene.scene_id == "fighting_surrender-dialog":
                game.close_app()
                time.sleep(.5)
            
        time.sleep(.1)
