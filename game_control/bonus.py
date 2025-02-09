from libs.scene_manager import SceneManager
from libs.constants import TEMPLATES_DIR

def check_bonus_info(scene_manager: SceneManager):
    screenshot = scene_manager.game.capture_screen()

    # 使用 get_safe_client_region 處理所有區域
    # 取得當前獎勵等級
    rank_x, rank_y, rank_w, rank_h = scene_manager.get_safe_client_region(625, 0, 100, 50)
    star_rank_region = (rank_x, rank_y, rank_w, rank_h)
    star_rank_ocr_result = scene_manager.ocr_processor.process_screenshot(screenshot, star_rank_region)
    star_rank = star_rank_ocr_result[0]['text'] if star_rank_ocr_result else "77"

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
    num_x, num_y, num_w, num_h = scene_manager.get_safe_client_region(650, 90, 180, 190)
    target_num_region = (num_x, num_y, num_w, num_h)
    target_num_screenshot = screenshot[target_num_region[1]:target_num_region[1]+target_num_region[3], 
                                    target_num_region[0]:target_num_region[0]+target_num_region[2]]
    target_num = scene_manager.find_first_matching_template_key(target_num_screenshot, target_num_template) or "12"

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
    
    # 當前獎勵模板
    current_bonus_template = {item['name']: item['current_template'] for item in bonus_card_list}

    # 調整當前獎勵區域
    curr_x, curr_y, curr_w, curr_h = scene_manager.get_safe_client_region(350, 380, 250, 350)
    current_bonus_region = (curr_x, curr_y, curr_w, curr_h)
    current_bonus_screenshot = screenshot[current_bonus_region[1]:current_bonus_region[1]+current_bonus_region[3],
                                       current_bonus_region[0]:current_bonus_region[0]+current_bonus_region[2]]

    current_bonus = scene_manager.find_first_matching_template_key(current_bonus_screenshot, current_bonus_template) or "unknown"

    # 下一個獎勵模板
    next_bonus_template = {item['name']: item['next_template'] for item in bonus_card_list}
    # 調整三個下一個獎勵區域
    next_regions = []
    for x_start in [603, 715, 828]:
        x, y, w, h = scene_manager.get_safe_client_region(x_start, 555, 114, 159)
        next_regions.append((x, y, w, h))

    next_bonuses = []
    for region in next_regions:
        bonus_screenshot = screenshot[region[1]:region[1]+region[3], 
                                   region[0]:region[0]+region[2]]
        bonus = scene_manager.find_first_matching_template_key(bonus_screenshot, next_bonus_template) or "unknown"
        next_bonuses.append(bonus)

    return {
        "star_rank": int(star_rank),
        "target_num": int(target_num),
        "current_bonus": current_bonus,
        "next_1_bonus": next_bonuses[0],
        "next_2_bonus": next_bonuses[1],
        "next_3_bonus": next_bonuses[2]
    }