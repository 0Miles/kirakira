import asyncio
import re
import time
from libs.classes.service_base import ServiceBase
from libs.logger import logger

class RoomService(ServiceBase):
    def check_room_list(self):
        screenshot = self.scene_manager.game.capture_screen()

        # 房間列表區域
        x, y, w, h = self.scene_manager.get_safe_client_region(0, 65, 450, 420)
        region = (x, y, w, h)

        ocr_result = self.scene_manager.ocr_processor.process_screenshot(screenshot, region)

        room_list = []
        for index, item in enumerate(ocr_result):
            # 確保必要的欄位存在
            if not item or not isinstance(item, dict):
                continue
            
            text = item.get("text", "")
            position = item.get("position")
            
            # 跳過無效的資料
            if not text or not position or len(position) < 2:
                continue

            # 檢查是否為玩家資訊行
            if text.startswith("Lv.") and position[0] < 50:
                try:
                    match = re.match(r"^Lv\.\d+", text)
                    owner_lv = match.group(0) if match else None
                    owner = text[len(owner_lv):] if owner_lv else text

                    # 檢查上一行是否為房間名稱
                    room_name = ""
                    if (index > 0 and 
                        isinstance(ocr_result[index - 1], dict) and 
                        "position" in ocr_result[index - 1] and 
                        "text" in ocr_result[index - 1] and
                        abs(position[1] - ocr_result[index - 1]["position"][1]) < 30):
                        room_name = ocr_result[index - 1]["text"]

                    # 檢查是否有訪客資訊
                    guest_lv = None
                    guest = None
                    if (index + 2 < len(ocr_result) and 
                        isinstance(ocr_result[index + 2], dict) and
                        "text" in ocr_result[index + 2] and 
                        ocr_result[index + 2]["text"].startswith("Lv.") and
                        "position" in ocr_result[index + 2] and
                        abs(position[1] - ocr_result[index + 2]["position"][1]) < 10):
                        guest_text = ocr_result[index + 2]["text"]
                        guest_match = re.match(r"^Lv\.\d+", guest_text)
                        guest_lv = guest_match.group(0) if guest_match else None
                        guest = guest_text[len(guest_lv):] if guest_lv else guest_text

                    room_list.append({
                        "owner": owner.strip() if owner else "",
                        "owner_lv": owner_lv,
                        "room_name": room_name.strip() if room_name else "",
                        "guest": guest.strip() if guest else None,
                        "guest_lv": guest_lv,
                        "is_full": guest is not None,
                        "position": position
                    })
                except Exception as e:
                    logger.warning(f"處理房間資訊時發生錯誤: {e}")
                    continue
        print("房間列表:")
        for room in room_list:
            print(f"  - {room['owner']}: {room['room_name']}, guest: {room['guest']} isFull: {room['is_full']}")

        return room_list


    def check_room_info(self):
        try:
            screenshot = self.scene_manager.game.capture_screen()

            # 玩家資訊區域
            x, y, w, h = self.scene_manager.get_safe_client_region(480, 35, 440, 350)
            region = (x, y, w, h)
            ocr_result = self.scene_manager.ocr_processor.process_screenshot(screenshot, region)

            # 初始化欄位
            player_1 = {
                "level": None, "player_name": None, "battle_point": None, 
                "win_draw_record": None, "win_rate": None, "enter_button": None
            }
            
            player_2 = {
                "level": None, "player_name": None, "battle_point": None, 
                "win_draw_record": None, "win_rate": None
            }

            # 獲取座標範圍
            scaled_ranges = {
                "p1_name": self.scene_manager.get_safe_client_region(590, 80, 100, 20),
                "p1_bp": self.scene_manager.get_safe_client_region(590, 106, 100, 20),
                "p1_record": self.scene_manager.get_safe_client_region(590, 135, 100, 25),
                "p1_rate": self.scene_manager.get_safe_client_region(590, 165, 100, 25),
                "p2_name": self.scene_manager.get_safe_client_region(715, 225, 95, 25),
                "p2_bp": self.scene_manager.get_safe_client_region(715, 260, 95, 20),
                "p2_record": self.scene_manager.get_safe_client_region(715, 285, 95, 25),
                "p2_rate": self.scene_manager.get_safe_client_region(715, 315, 95, 30),
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

                # 第一名玩家資訊
                if y1 < scaled_ranges["p1_rate"][1]:  # 使用p1區域的Y座標作為分界
                    if "Level" in text:
                        player_1["level"] = text
                    elif x1 > scaled_ranges["p1_name"][0] and x1 < scaled_ranges["p1_name"][0] + scaled_ranges["p1_name"][2]:
                        if y1 > scaled_ranges["p1_name"][1] and y1 < scaled_ranges["p1_name"][1] + scaled_ranges["p1_name"][3]:
                            player_1["player_name"] = text
                    elif x1 > scaled_ranges["p1_bp"][0] and x1 < scaled_ranges["p1_bp"][0] + scaled_ranges["p1_bp"][2]:
                        if y1 > scaled_ranges["p1_bp"][1] and y1 < scaled_ranges["p1_bp"][1] + scaled_ranges["p1_bp"][3]:
                            player_1["battle_point"] = text
                    elif x1 > scaled_ranges["p1_record"][0] and x1 < scaled_ranges["p1_record"][0] + scaled_ranges["p1_record"][2]:
                        if y1 > scaled_ranges["p1_record"][1] and y1 < scaled_ranges["p1_record"][1] + scaled_ranges["p1_record"][3]:
                            player_1["win_draw_record"] = text
                    elif x1 > scaled_ranges["p1_rate"][0] and x1 < scaled_ranges["p1_rate"][0] + scaled_ranges["p1_rate"][2]:
                        if y1 > scaled_ranges["p1_rate"][1] and y1 < scaled_ranges["p1_rate"][1] + scaled_ranges["p1_rate"][3]:
                            player_1["win_rate"] = text

                # 第二名玩家資訊
                elif has_second_player and y1 > scaled_ranges["p2_name"][1]:
                    if "Level" in text:
                        player_2["level"] = text
                    elif x1 > scaled_ranges["p2_name"][0] and x1 < scaled_ranges["p2_name"][0] + scaled_ranges["p2_name"][2]:
                        if y1 > scaled_ranges["p2_name"][1] and y1 < scaled_ranges["p2_name"][1] + scaled_ranges["p2_name"][3]:
                            player_2["player_name"] = text
                    elif x1 > scaled_ranges["p2_bp"][0] and x1 < scaled_ranges["p2_bp"][0] + scaled_ranges["p2_bp"][2]:
                        if y1 > scaled_ranges["p2_bp"][1] and y1 < scaled_ranges["p2_bp"][1] + scaled_ranges["p2_bp"][3]:
                            player_2["battle_point"] = text
                    elif x1 > scaled_ranges["p2_record"][0] and x1 < scaled_ranges["p2_record"][0] + scaled_ranges["p2_record"][2]:
                        if y1 > scaled_ranges["p2_record"][1] and y1 < scaled_ranges["p2_record"][1] + scaled_ranges["p2_record"][3]:
                            player_2["win_draw_record"] = text
                    elif x1 > scaled_ranges["p2_rate"][0] and x1 < scaled_ranges["p2_rate"][0] + scaled_ranges["p2_rate"][2]:
                        if y1 > scaled_ranges["p2_rate"][1] and y1 < scaled_ranges["p2_rate"][1] + scaled_ranges["p2_rate"][3]:
                            player_2["win_rate"] = text

            return {
                "player_1": player_1,
                "player_2": player_2 if has_second_player else None,
                "has_second_player": has_second_player
            }
        except Exception as e:
            logger.error(f"check_room_info 發生錯誤: {e}")
            return None


    async def join_room(self, room_position, player_name):
        x, y, w, h = room_position
        click_x = x + w // 2
        click_y = y
        
        if not self.scene_manager.game.click(click_x, click_y):
            return False

        room_info = None
        time_count = 0
        while room_info == None:
            room_info = self.check_room_info()
            if room_info:
                break
            await asyncio.sleep(.3)
            time_count += 1
            if time_count > 20:
                return False

        print(room_info)
        print(player_name)
        if room_info["player_1"]["player_name"] in player_name:
            self.scene_manager.currentScene.buttons["enter"].click()
            return True
        else:
            return False

