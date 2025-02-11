# 遊戲相關設定
GAME_NAME = ["UNLIGHT_Revive.exe", "nwjs"]  # 遊戲的進程名稱
GAME_WINDOW_TITLE = "unlight_revive"  # 遊戲視窗標題
GAME_EXECUTABLE_PATH = r"C:\\Program Files (x86)\\Steam\\steamapps\\common\\UNLIGHTRevive\\UNLIGHT_Revive.exe"  # 遊戲可執行文件路徑
STEAM_GAME_ID = "3247080"  # 遊戲的 Steam 應用 ID
TEMPLATE_ORIGIN_CLIENT_WIDTH = 950  # 製作 Template 時使用的遊戲原始畫面寬度
TEMPLATE_ORIGIN_CLIENT_HEIGHT = 888  # 製作 Template 時使用的遊戲原始畫面高度
TEMPLATE_ORIGIN_TITLE_BAR_HEIGHT = 40
TEMPLATE_ORIGIN_LEFT_BORDER_WIDTH = 1

# Steam 設定
STEAM_EXECUTABLE_PATH = r"C:\\Program Files (x86)\\Steam\\Steam.exe"  # Steam 執行檔路徑

# 模式
SCRIPT_MODE = "find_sandbag" # "being_a_sandbag"當沙包 or "find_sandbag"找沙包打

# 自動沙包設定
AUTO_SANDBAG_TARGET_USERNAME = ""
AUTO_SANDBAG_END = "close" # "close"關閉遊戲 "bonus"進入獎勵遊戲流程

# 自動找沙包設定
FIND_SANDBAG_USERNAME = ""
FIND_SANDBAG_ROOM_NAME = "徵投降包 感謝"
FIND_SANDBAG_FRIEND_ONLY = False

# Bonus Game 設定

# 基本模式設定範本
BONUS_GAME_TARGET = "basic" # 基本模式，不會使用道具與判斷星級
BONUS_GAME_TARGET_ITEMS = ["green-tea", "gem"]

# # 爬星模式設定範本
# BONUS_GAME_TARGET = "star_rank" # 爬星模式
#
# # 目標道具，可設定每個星級區間的目標道具
# BONUS_GAME_TARGET_ITEMS = {
#     100: ["里斯"], # 100星以上
#     115: ["死亡", 
#           "生命", 
#           "記",
#           "時間",
#           "靈","魂",
#           "里斯"], # 115星以上
# }
# # 失敗時使用的道具，留空則不使用
# BONUS_GAME_USE_ITEM_WHEN_FAILED = ["白色石楠1", "白色石楠3", "白色石楠5"]
# # 最高星級，超過此星級時若失敗不會使用道具繼續遊戲
# BONUS_GAME_MAX_GET_STAR_RANK = 130
# # 
# BONUS_GAME_WHEN_FAILED_END = "close" # "close"關閉遊戲 "exit"離開獎勵遊戲 "wait"不動作