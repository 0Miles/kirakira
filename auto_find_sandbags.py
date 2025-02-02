import time
import config
from game_control.room import check_room_list
from libs.steam_control import SteamControl
from libs.app_control import AppControl
from libs.scene_manager import SceneManager

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
            # 打開創建房間對話框時，自動填入房間名稱、選擇規則
            if scene_manager.currentScene.scene_id == "matching_diethelm_create-dialog":
                scene_manager.currentScene.inputs["select-rule"].select_option("scenes/matching/diethelm/create-dialog/option-3v3.png")
                time.sleep(.1)
                scene_manager.currentScene.inputs["text-room-name"].change_text("徵投降包 感謝")
                time.sleep(.1)
                scene_manager.currentScene.buttons["corner"].click()
                scene_manager.currentScene.buttons["ok"].click()

            elif scene_manager.currentScene.scene_id == "matching_diethelm_wating-dialog":
                room_list = check_room_list()
                print(room_list)
                if not any(room['owner'] == '燈心草' for room in room_list):
                    scene_manager.currentScene.buttons["cancel"].click()
            
            elif scene_manager.currentScene.scene_id == "matching_diethelm":
                scene_manager.currentScene.buttons["create"].click()
            
        time.sleep(.3)

