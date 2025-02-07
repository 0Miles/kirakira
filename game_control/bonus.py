from libs.scene_manager import SceneManager
from libs.constants import TEMPLATES_DIR

def check_bonus_info(scene_manager: SceneManager):
    screenshot = scene_manager.game.capture_screen()
    # 取得 gemexp 的位置
    matches = scene_manager.match_template(screenshot, "scenes/result/gemexp.png")
    if not matches:
        return None
    gemexp_x, gemexp_y, gemexp_w, gemexp_h = matches[0]
    y_start = gemexp_y - 730

    # 取得當前獎勵等級
    star_rank_region = (625, y_start, 100, 50)
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

    target_num_region = (650, y_start + 90, 180, 190)
    target_num_screenshot = screenshot[target_num_region[1]:target_num_region[1]+target_num_region[3], target_num_region[0]:target_num_region[0]+target_num_region[2]]
    target_num = scene_manager.find_first_matching_template_key(target_num_screenshot, target_num_template) or "12"

    # 取得當前獎勵
    current_bonus_template = {
        "gem": "scenes/result/bonus-highlow/current-gem.png",
        "green-tea": "scenes/result/bonus-highlow/current-green-tea.png"
    }
    current_bonus_region = (350, y_start + 380, 250, 350)
    current_bonus_screenshot = screenshot[current_bonus_region[1]:current_bonus_region[1]+current_bonus_region[3], current_bonus_region[0]:current_bonus_region[0]+current_bonus_region[2]]
    current_bonus = scene_manager.find_first_matching_template_key(current_bonus_screenshot, current_bonus_template) or "unknown"


    next_bonus_template = {
        "gem": "scenes/result/bonus-highlow/gem.png",
        "green-tea": "scenes/result/bonus-highlow/green-tea.png"
    }
    next_1_bonus_region = (603, y_start + 555, 114, 159)
    next_1_bonus_screenshot = screenshot[next_1_bonus_region[1]:next_1_bonus_region[1]+next_1_bonus_region[3], next_1_bonus_region[0]:next_1_bonus_region[0]+next_1_bonus_region[2]]
    next_1_bonus = scene_manager.find_first_matching_template_key(next_1_bonus_screenshot, next_bonus_template) or "unknown"

    next_2_bonus_region = (715, y_start + 555, 114, 159)
    next_2_bonus_screenshot = screenshot[next_2_bonus_region[1]:next_2_bonus_region[1]+next_2_bonus_region[3], next_2_bonus_region[0]:next_2_bonus_region[0]+next_2_bonus_region[2]]
    next_2_bonus = scene_manager.find_first_matching_template_key(next_2_bonus_screenshot, next_bonus_template) or "unknown"

    next_3_bonus_region = (828, y_start + 555, 114, 159)
    next_3_bonus_screenshot = screenshot[next_3_bonus_region[1]:next_3_bonus_region[1]+next_3_bonus_region[3], next_3_bonus_region[0]:next_3_bonus_region[0]+next_3_bonus_region[2]]
    next_3_bonus = scene_manager.find_first_matching_template_key(next_3_bonus_screenshot, next_bonus_template) or "unknown"
    
    return {
        "star_rank": int(star_rank),
        "target_num": int(target_num),
        "current_bonus": current_bonus,
        "next_1_bonus": next_1_bonus,
        "next_2_bonus": next_2_bonus,
        "next_3_bonus": next_3_bonus
    }