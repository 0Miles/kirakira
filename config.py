# config.py

# 遊戲相關設定
GAME_NAME = ["UNLIGHT_Revive.exe", "nwjs"]  # 遊戲的進程名稱
GAME_WINDOW_TITLE = "unlight_revive"  # 遊戲視窗標題
GAME_EXECUTABLE_PATH = r"C:\\Program Files (x86)\\Steam\\steamapps\\common\\UNLIGHTRevive\\UNLIGHT_Revive.exe"  # 遊戲可執行文件路徑
STEAM_GAME_ID = "3247080"  # 遊戲的 Steam 應用 ID

# Steam 設定
STEAM_EXECUTABLE_PATH = r"C:\\Program Files (x86)\\Steam\\Steam.exe"  # Steam 執行檔路徑

# 影像處理相關設定
TEMPLATE_MATCH_THRESHOLD = 0.8  # 範本匹配閾值 (0-1)
IMAGE_RESIZE_WIDTH = 1280  # 圖像處理時的標準寬度
IMAGE_RESIZE_HEIGHT = 720  # 圖像處理時的標準高度

# OCR 設定
OCR_LANGUAGE = "en"  # PaddleOCR 識別語言
USE_ANGLE_CLS = False  # 是否啟用文字方向分類

# 日誌設定
LOG_DIR = "logs"  # 日誌存放目錄
LOG_LEVEL = "INFO"  # 日誌等級 (DEBUG, INFO, WARNING, ERROR)

# 其他設定
CHECK_INTERVAL = 5  # 檢查遊戲狀態的時間間隔 (秒)
