import asyncio
import config
from libs.classes.service_base import ServiceBase

class BonusService(ServiceBase):
    async def click_bonus_item(self, item_name: str):
        item_fields = [
            (230, 166),
            (230, 227),
            (230, 288),
            (230, 349),
            (230, 410),
            (230, 471),
        ]
        for item_field in item_fields:
            click_x, click_y = self.scene_manager.get_safe_client_region(item_field[0], item_field[1], 60, 60)[:2]
            self.scene_manager.game.click(click_x, click_y)
            await asyncio.sleep(.5)
            item_name_region = self.scene_manager.get_safe_client_region(15, 65, 215, 50)
            screenshot = self.scene_manager.game.capture_screen()
            item_name_result = self.scene_manager.ocr_processor.process_screenshot(screenshot, item_name_region)
            if item_name_result and item_name_result[0]['text'] == item_name:
                return True
        return False

    prev_star_rank = 0

    def reset_prev_star_rank(self):
        self.prev_star_rank = 0

    def check_bonus_info(self):
        screenshot = self.scene_manager.game.capture_screen()

        # 使用 get_safe_client_region 處理所有區域
        # 安全地轉換字串為數字
        def safe_int(value, default=0):
            try:
                # 移除非數字字符
                num_str = ''.join(c for c in str(value) if c.isdigit())
                return int(num_str) if num_str else default
            except (ValueError, TypeError):
                return default

        # 取得當前獎勵等級
        rank_x, rank_y, rank_w, rank_h = self.scene_manager.get_safe_client_region(625, 0, 100, 70)
        star_rank_region = (rank_x, rank_y, rank_w, rank_h)
        star_rank_ocr_result = self.scene_manager.ocr_processor.process_screenshot(screenshot, star_rank_region)
        star_rank = star_rank_ocr_result[0]['text'] if star_rank_ocr_result else f"{self.prev_star_rank + 1}"

        # 確保獎勵等級不會因為OCR辨識錯誤倒退
        if safe_int(star_rank) < self.prev_star_rank:
            star_rank = f"{self.prev_star_rank}"
        self.prev_star_rank = safe_int(star_rank)

        # 取得當前目標數字
        target_num_template = {
            "12": "scenes/result/bonus-highlow/12.png",
            "11": "scenes/result/bonus-highlow/11.png",
            "10": "scenes/result/bonus-highlow/10.png",
            "9": "scenes/result/bonus-highlow/9.png",
            "8": "scenes/result/bonus-highlow/8.png",
            "7": "scenes/result/bonus-highlow/7.png",
            "6": "scenes/result/bonus-highlow/6.png",
            "5": "scenes/result/bonus-highlow/5.png",
            "4": "scenes/result/bonus-highlow/4.png",
            "3": "scenes/result/bonus-highlow/3.png",
            "2": "scenes/result/bonus-highlow/2.png",
        }

        # 調整目標數字區域
        num_x, num_y, num_w, num_h = self.scene_manager.get_safe_client_region(650, 90, 180, 190)
        target_num_region = (num_x, num_y, num_w, num_h)
        target_num_screenshot = screenshot[target_num_region[1]:target_num_region[1]+target_num_region[3], 
                                        target_num_region[0]:target_num_region[0]+target_num_region[2]]
        target_num = self.scene_manager.find_first_matching_template_key(target_num_screenshot, target_num_template) or "12"

        # 獎勵卡設置
        bonus_card_list = [
            {
                "name": "gem",
                "current_template": "scenes/result/bonus-highlow/current-gem.png",
                "next_template": "scenes/result/bonus-highlow/gem.png"
            },
            {
                "name": "green-tea",
                "current_template": "scenes/result/bonus-highlow/current-green-tea.png",
                "next_template": "scenes/result/bonus-highlow/green-tea.png"
            },
            {
                "name": "exp",
                "current_template": "scenes/result/bonus-highlow/current-exp.png",
                "next_template": "scenes/result/bonus-highlow/exp.png"
            }
        ]

        def find_bonus_card(screenshot, template_key="current_template"):
            for item in bonus_card_list:
                template_path = item[template_key]
                matches = self.scene_manager.match_template(screenshot, template_path, color=item.get("color", False))
                if matches:
                    return item["name"]
            return "unknown"
        
        # 調整當前獎勵區域
        curr_x, curr_y, curr_w, curr_h = self.scene_manager.get_safe_client_region(350, 380, 250, 350)
        current_bonus_region = (curr_x, curr_y, curr_w, curr_h)
        current_bonus_screenshot = screenshot[current_bonus_region[1]:current_bonus_region[1]+current_bonus_region[3],
                                        current_bonus_region[0]:current_bonus_region[0]+current_bonus_region[2]]

        current_bonus = find_bonus_card(current_bonus_screenshot)
        if current_bonus == "unknown":
            card_name_ocr_range = self.scene_manager.get_safe_client_region(405, 418, 155, 30)
            card_name_ocr_result = self.scene_manager.ocr_processor.process_screenshot(screenshot, card_name_ocr_range)
            if card_name_ocr_result:
                current_bonus = card_name_ocr_result[0]['text']


        # 調整三個下一個獎勵區域
        next_regions = []
        for x_start in [603, 715, 828]:
            x, y, w, h = self.scene_manager.get_safe_client_region(x_start, 555, 114, 159)
            next_regions.append((x, y, w, h))

        next_bonuses = []
        for region in next_regions:
            bonus_screenshot = screenshot[region[1]:region[1]+region[3], 
                                    region[0]:region[0]+region[2]]
            bonus = find_bonus_card(bonus_screenshot, "next_template")
            if bonus == "unknown":
                card_name_ocr_range = self.scene_manager.get_safe_client_region(region[0] + 30, region[1], 70, 26)
                card_name_ocr_result = self.scene_manager.ocr_processor.process_screenshot(screenshot, card_name_ocr_range)
                if card_name_ocr_result:
                    bonus = card_name_ocr_result[0]['text']
            next_bonuses.append(bonus)

        return {
            "star_rank": safe_int(star_rank, self.prev_star_rank),
            "target_num": safe_int(target_num, 12),
            "current_bonus": current_bonus,
            "next_bonuses": next_bonuses
        }

    async def handle_highlow_choice(self):
        """處理 high-low 的選擇"""
        bonus_info = self.check_bonus_info()
        target_num = bonus_info.get("target_num")
        print(f"[INFO] 目標數字: {target_num}")
        
        if target_num > 7:
            print(f"[INFO] 選擇 low")
            self.scene_manager.currentScene.buttons["low"].click()
        else:
            print(f"[INFO] 選擇 high")
            self.scene_manager.currentScene.buttons["high"].click()

    async def handle_bonus_select(self, info = None):
        """處理獎勵選擇"""
        bonus_info = info if info else self.check_bonus_info()
        star_rank = bonus_info.get("star_rank", self.prev_star_rank)
        current_bonus = bonus_info.get("current_bonus", "")

        target_items = []
        
        if isinstance(config.BONUS_GAME_TARGET_ITEMS, dict):
            for rank_threshold in sorted(config.BONUS_GAME_TARGET_ITEMS.keys()):
                if star_rank >= rank_threshold:
                    target_items = config.BONUS_GAME_TARGET_ITEMS.get(rank_threshold, [])
        else:
            target_items = config.BONUS_GAME_TARGET_ITEMS if config.BONUS_GAME_TARGET_ITEMS else []

        print(f"[INFO] 目前星等: {star_rank}")
        print(f"[INFO] 目前獎勵: {current_bonus}, 接下來的獎勵: {bonus_info.get('next_bonuses', [])}")
        print(f"[INFO] 目標獎勵: {target_items}")

        if current_bonus and any(target_item for target_item in target_items if target_item in current_bonus):
            self.scene_manager.currentScene.buttons["get"].click()
        else:
            self.scene_manager.currentScene.buttons["next"].click()