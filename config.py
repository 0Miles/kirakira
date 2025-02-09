# config.py

# 遊戲相關設定
GAME_NAME = ["UNLIGHT_Revive.exe", "nwjs"]  # 遊戲的進程名稱
GAME_WINDOW_TITLE = "unlight_revive"  # 遊戲視窗標題
GAME_EXECUTABLE_PATH = r"C:\\Program Files (x86)\\Steam\\steamapps\\common\\UNLIGHTRevive\\UNLIGHT_Revive.exe"  # 遊戲可執行文件路徑
STEAM_GAME_ID = "3247080"  # 遊戲的 Steam 應用 ID
TEMPLATE_ORIGIN_CLIENT_WIDTH = 950  # 製作 Template 時使用的遊戲原始畫面寬度
TEMPLATE_ORIGIN_CLIENT_HEIGHT = 888  # 製作 Template 時使用的遊戲原始畫面高度
TEMPLATE_ORIGIN_TITLE_BAR_HEIGHT = 40
TEMPLATE_ORIGIN_LEFT_BORDER_WIDTH = 1

# Bonus Game 設定
# BONUS_GAME_TARGET = "gem" # 洗GEM模式
# BONUS_GAME_TARGET_ITEMS = ["green-tea", "gem"]

BONUS_GAME_TARGET = "star_rank" # 爬星模式
# 爬星模式設定
BONUS_GAME_TARGET_ITEMS = {
    100: ["purple-chip", "red-chip", "里斯", "佛", "羅倫"], # 100星以上
    110: ["purple-chip", "red-chip", "yellow-chip", "green-chip", "blue-chip", "里斯", "佛", "羅倫"], # 110星以上
}
USE_ITEM_WHEN_FAILED = ["白色石楠1", "白色石楠3", "白色石楠5"]
MAX_GET_STAR_RANK = 130
FAILED_AND_NO_ITEM_OR_OVER_MAX_STAR_RANK = "close" # "close"關閉遊戲 "exit"離開獎勵遊戲 "wait"不動作


# Steam 設定
STEAM_EXECUTABLE_PATH = r"C:\\Program Files (x86)\\Steam\\Steam.exe"  # Steam 執行檔路徑

# 模式
SCRIPT_MODE = "find_sandbag"

# 自動沙包設定
AUTO_SANDBAG_TARGET_USERNAME = "燈心草"

# 自動找沙包設定
FIND_SANDBAG_USERNAME = "燈心草"
FIND_SANDBAG_ROOM_NAME = "徵投降包 感謝"
FIND_SANDBAG_FRIEND_ONLY = False