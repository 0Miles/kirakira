import os
import sys
import logging
from datetime import datetime
from typing import Optional

class Logger:
    _instance: Optional["Logger"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not Logger._initialized:
            self._setup_logger()
            Logger._initialized = True

    def _setup_logger(self):
        """設置記錄器"""
        self.logger = logging.getLogger("KiraKira")
        self.logger.propagate = False  
        self.logger.setLevel(logging.DEBUG)

        # 清除現有的處理器
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        # 建立日誌目錄 (使用執行入口檔所在目錄)
        entry_point_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        log_dir = os.path.join(entry_point_dir, "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 設置日誌格式
        formatter = logging.Formatter(
            "[%(asctime)s][%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # 控制台處理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        self.logger.addHandler(console_handler)

        # 檔案處理器
        current_time = datetime.now().strftime("%Y%m%d")
        file_handler = logging.FileHandler(
            os.path.join(log_dir, f"{current_time}.log"),
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

    def debug(self, message: str):
        """記錄除錯訊息"""
        self.logger.debug(message)

    def info(self, message: str):
        """記錄一般訊息"""
        self.logger.info(message)

    def warning(self, message: str):
        """記錄警告訊息"""
        self.logger.warning(message)

    def error(self, message: str):
        """記錄錯誤訊息"""
        self.logger.error(message)

    def critical(self, message: str):
        """記錄嚴重錯誤訊息"""
        self.logger.critical(message)

# 全域單例實例
logger = Logger()
