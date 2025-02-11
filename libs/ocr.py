import cv2
from paddleocr import PaddleOCR

from paddleocr.ppocr.utils.logging import get_logger
import logging
logger = get_logger()
logger.setLevel(logging.ERROR)

class OCRProcessor:
    def __init__(self, use_angle_cls=False, lang="ch"):
        """
        初始化 OCR 處理器。
        :param use_angle_cls: 是否使用文字方向分類
        :param lang: 文字識別語言 (默認為中文)
        """
        self.ocr = PaddleOCR(use_angle_cls=use_angle_cls, lang=lang)
    
    def process_image(self, image_path):
        """
        從圖片提取文字。
        :param image_path: 圖片路徑
        :return: 解析後的文字結果
        """
        result = self.ocr.ocr(image_path, cls=True)
        return self._parse_result(result)
    
    def process_screenshot(self, screenshot, region=None):
        """
        從截圖（numpy array）提取文字，若提供區域則裁剪該區域後再提取。
        :param screenshot: OpenCV 截圖
        :param region: (x, y, width, height) 指定區域，可選
        :return: 解析後的文字結果，包含文字與其位置（如果有提供區域）
        """
        offset_x, offset_y = 0, 0
        
        if region:
            x, y, w, h = region
            screenshot = screenshot[y:y+h, x:x+w]  # 裁剪區域
            offset_x, offset_y = x, y
        
        result = self.ocr.ocr(screenshot, cls=True)
        return self._parse_result_with_position(result, offset_x, offset_y) if region else self._parse_result(result)
    
    
    def _parse_result(self, result):
        """
        解析 OCR 輸出結果。
        :param result: OCR 原始輸出
        :return: 識別到的文字列表
        """
        if not result:
            print("[WARNING] OCR 未能識別任何內容")
            return []  # 確保返回可迭代的空列表
        
        parsed_text = []
        for line in result:
            for word_info in line:
                text = word_info[1][0]  # 文字內容
                position = word_info[0]  # 文字的邊界框座標
                x_min, y_min, x_max, y_max = int(position[0][0]), int(position[0][1]), int(position[2][0]), int(position[2][1])
                parsed_text.append({"text": text, "position": (x_min, y_min, x_max, y_max)})
        return parsed_text
    def _parse_result_with_position(self, result, offset_x, offset_y):
        """
        解析 OCR 輸出結果，包含文字與其位置。
        :param result: OCR 原始輸出
        :param offset_x: 區域左上角 X 偏移量
        :param offset_y: 區域左上角 Y 偏移量
        :return: 包含文字與其座標的列表
        """
        parsed_text = []
        for line in result:
            if not line:
                continue
            for word_info in line:
                text = word_info[1][0]  # 文字內容
                position = word_info[0]  # 文字的邊界框座標
                x_min, y_min, x_max, y_max = int(position[0][0] + offset_x), int(position[0][1] + offset_y), int(position[2][0] + offset_x), int(position[2][1] + offset_y)
                parsed_text.append({"text": text, "position": (x_min, y_min, x_max, y_max)})
        return parsed_text

if __name__ == "__main__":
    ocr_processor = OCRProcessor()
    image_path = "test_image.png"  # 測試圖片
    extracted_text = ocr_processor.process_image(image_path)
    print("Extracted Text:", extracted_text)
    
    # 測試擷取指定區域
    screenshot = cv2.imread(image_path)
    region = (50, 50, 300, 100)  # 指定區域 (x, y, width, height)
    extracted_text_region = ocr_processor.process_region(screenshot, region)
    print("Extracted Text from Region:", extracted_text_region)
