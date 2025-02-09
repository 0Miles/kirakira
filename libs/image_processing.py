import cv2
import numpy as np
import os

class ImageProcessor:
    def load_image(self, image_path):
        """
        加載圖像。
        :param image_path: 圖像文件路徑
        :return: 加載的 OpenCV 圖像
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"無法找到圖像: {image_path}")
        
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"無法讀取圖像: {image_path}")
        
        return image
    
    def resize_image(self, image, width=None, height=None):
        """
        調整圖像大小。
        :param image: OpenCV 圖像數據
        :param width: 目標寬度
        :param height: 目標高度
        :return: 調整大小後的圖像
        """
        if width is None and height is None:
            return image
        
        dimensions = (width, height) if width and height else None
        return cv2.resize(image, dimensions) if dimensions else image
    
    def convert_to_grayscale(self, image):
        """
        轉換為灰度圖像。
        :param image: OpenCV 圖像數據
        :return: 灰度圖像
        """
        if image is None:
            raise ValueError("輸入圖像為 None，無法轉換為灰度。")
        
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def apply_threshold(self, image, threshold=127):
        """
        應用二值化處理。
        :param image: OpenCV 圖像數據
        :param threshold: 閾值
        :return: 二值化圖像
        """
        if image is None:
            raise ValueError("輸入圖像為 None，無法應用閾值處理。")
        
        _, binary_image = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
        return binary_image
    
    def match_template(self, source_image, template_path, threshold=0.8, scale_ratio=1.0):
        """
        使用模板匹配查找圖像中的目標區域。
        Args:
            source_image: 原始圖像 (numpy array)
            template_path: 模板圖像的檔案路徑
            threshold: 匹配閾值 (0~1)
            scale_ratio: 模板縮放比例
        Returns:
            匹配到的區域列表 [(x, y, w, h)]
        """
        template_image = self.load_image(template_path)
        
        if scale_ratio != 1.0:
            new_width = int(template_image.shape[1] * scale_ratio)
            new_height = int(template_image.shape[0] * scale_ratio)
            template_image = cv2.resize(template_image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        source_gray = self.convert_to_grayscale(source_image)
        template_gray = self.convert_to_grayscale(template_image)

        result = cv2.matchTemplate(source_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        matches = [(pt[0], pt[1], template_gray.shape[1], template_gray.shape[0]) 
                  for pt in zip(*locations[::-1])]

        return matches
    
    def save_screenshot(self, image, filename="screenshot.png"):
        """ 儲存 OpenCV 圖像 """
        cv2.imwrite(filename, image)
        print(f"已儲存截圖: {filename}")
