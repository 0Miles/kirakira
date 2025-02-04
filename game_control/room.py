import os
import re
import time

import pyautogui

from libs.scene_manager import SceneManager
from libs.constants import TEMPLATES_DIR


def check_room_list(scene_manager: SceneManager):
    screenshot = scene_manager.game.capture_screen()
    # 取得 title 的位置
    matches = scene_manager.match_template(screenshot, "scenes/matching/title.png")
    if not matches:
        return None
    title_x, title_y, title_w, title_h = matches[0]

    region = (0, title_y + 65, 450, 420)

    ocr_result = scene_manager.ocr_processor.process_screenshot(screenshot, region)

    room = []
    for index, item in enumerate(ocr_result):
        if item['text'].startswith('Lv.') and item['position'][0] < 50:
            match = re.match(r'^Lv\.\d+', item['text'])
            owner_lv = match.group(0) if match else None
            owner = item['text'][len(owner_lv):]
            room_name = ""
            if (index > 0 and abs(item.get("position")[1] - ocr_result[index - 1].get("position")[1]) < 30):
                room_name = ocr_result[index - 1]['text']

            guest_lv = None
            guest = None
            if (index + 2 < len(ocr_result) and ocr_result[index + 2]['text'].startswith('Lv.') and abs(item.get("position")[1] - ocr_result[index + 2].get("position")[1]) < 10):
                match = re.match(r'^Lv\.\d+', ocr_result[index + 2]['text'])
                guest_lv = match.group(0) if match else None
                guest = ocr_result[index + 2]['text'][len(guest_lv):] if match else None
            room.append({
                'owner': owner,
                'owner_lv': owner_lv,
                'room_name': room_name,
                'guest': guest,
                'guest_lv': guest_lv,
                'is_full': guest is not None,
                'position': item.get("position")
            })
        else:
            continue
    return room


def check_room_info(scene_manager: SceneManager):
    screenshot = scene_manager.game.capture_screen()
    # 取得 title 的位置
    matches = scene_manager.match_template(screenshot, "scenes/matching/title.png")
    if not matches:
        return None
    title_x, title_y, title_w, title_h = matches[0]

    region = (480, title_y + 35, 440, 350)
    ocr_result = scene_manager.ocr_processor.process_screenshot(screenshot, region)

    # 初始化欄位
    player_1 = {
        "level": None, "player_name": None, "battle_point": None, 
        "win_draw_record": None, "win_rate": None, "enter_button": None
    }
    
    player_2 = {
        "level": None, "player_name": None, "battle_point": None, 
        "win_draw_record": None, "win_rate": None
    }

    # 記錄 BattlePoint 位置來區分第一名與第二名玩家
    battle_points = []

    for item in ocr_result:
        text = item["text"]
        x1, y1, x2, y2 = item["position"]

        # 記錄 BattlePoint 出現的位置
        if "BattlePoint" in text:
            battle_points.append(y1)
            continue  # 跳過不儲存標籤

    # 沒有任何 BattlePoint，代表沒有玩家資訊
    if (len(battle_points) == 0):
        return None

    # 判斷是否有第二名玩家
    has_second_player = len(battle_points) > 1

    for item in ocr_result:
        text = item["text"]
        x1, y1, x2, y2 = item["position"]

        # 第一名玩家 (y < 200)
        if y1 < 200:
            if "Level" in text:
                player_1["level"] = text
            elif 590 < x1 < 690 and title_y + 80 < y1 < title_y + 100:
                player_1["player_name"] = text
            elif 590 < x1 < 690 and title_y + 106 < y1 < title_y + 126:
                player_1["battle_point"] = text
            elif 590 < x1 < 690 and title_y + 135 < y1 < title_y + 160:
                player_1["win_draw_record"] = text
            elif 590 < x1 < 690 and title_y + 165 < y1 < title_y + 190:
                player_1["win_rate"] = text

        # 第二名玩家 (y > 200)
        elif has_second_player and y1 > 200:
            if "Level" in text:
                player_2["level"] = text
            elif 715 < x1 < 810 and title_y + 225 < y1 < title_y + 250:
                player_2["player_name"] = text
            elif 715 < x1 < 810 and title_y + 260 < y1 < title_y + 280:
                player_2["battle_point"] = text
            elif 715 < x1 < 810 and title_y + 285 < y1 < title_y + 310:
                player_2["win_draw_record"] = text
            elif 715 < x1 < 810 and title_y + 315 < y1 < title_y + 345:
                player_2["win_rate"] = text

    return {
        "player_1": player_1,
        "player_2": player_2 if has_second_player else None,
        "has_second_player": has_second_player
    }


def join_room(scene_manager: SceneManager, room_position, player_name):
    window_geometry = scene_manager.game.get_window_geometry()
    x, y, w, h = room_position  # 取第一個匹配結果
    target_x = window_geometry['x'] + x + w // 2
    target_y = window_geometry['y'] + y
    
    # 將游標移到目標坐標並點擊
    pyautogui.moveTo(target_x, target_y)
    pyautogui.click()

    room_info = None
    time_count = 0
    while room_info == None:
        room_info = check_room_info(scene_manager)
        time.sleep(.5)
        time_count += 1
        if time_count > 10:
            return False


    print(room_info)
    print(player_name)
    if room_info["player_1"]["player_name"] == player_name:
        scene_manager.currentScene.buttons["enter"].click()
        return True
    else:
        return False
                    
