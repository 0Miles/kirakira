import logging
import os
from datetime import datetime

class Logger:
    def __init__(self, log_dir="logs", log_level=logging.INFO):
        """
        初始化日誌記錄器。
        :param log_dir: 日誌存放目錄
        :param log_level: 記錄等級
        """
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
        log_filepath = os.path.join(log_dir, log_filename)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filepath, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("GameBotLogger")
    
    def info(self, message):
        """ 記錄 INFO 級別的日誌 """
        self.logger.info(message)
    
    def warning(self, message):
        """ 記錄 WARNING 級別的日誌 """
        self.logger.warning(message)
    
    def error(self, message):
        """ 記錄 ERROR 級別的日誌 """
        self.logger.error(message)
    
    def debug(self, message):
        """ 記錄 DEBUG 級別的日誌 """
        self.logger.debug(message)

if __name__ == "__main__":
    logger = Logger()
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.debug("This is a debug message.")