import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from libs.scene_manager import SceneManager

class Button:
    def __init__(self, button_id, scene_manager: 'SceneManager', template=None, position=None, region=None, color=False, threshold=0.9):
        self.button_id = button_id
        self.template = template if isinstance(template, list) or template is None else [template]
        self.scene_manager = scene_manager
        self.position = position
        self.region = region  # [x, y, width, height]
        self.prev_success_position = None
        self.color = color
        self.threshold = threshold

    def click(self):
        try:
            screenshot = self.scene_manager.game.capture_screen()
            
            target_match = None
            target_position = self.scene_manager.get_safe_client_position(*self.position) if self.position else None

            if self.template is not None and len(self.template) > 0:
                for template in self.template:
                    search_region = None
                    if self.region:
                        print(f"[INFO] 使用指定區域進行匹配: {self.region}")
                        search_region = self.scene_manager.get_safe_client_region(*self.region)
                    
                    # 先進行灰階匹配
                    gray_matches = self.scene_manager.match_template(
                        screenshot, 
                        template,
                        threshold=self.threshold,
                        region=search_region,
                        color=False
                    )
                    
                    if gray_matches and len(gray_matches) > 0:
                        # 如果需要彩色匹配，在每個灰階匹配位置嘗試彩色匹配
                        if self.color:
                            print(f"[INFO] 嘗試彩色匹配: {self.button_id}, 找到 {len(gray_matches)} 個灰階匹配")
                            found_color_match = False
                            for gray_match in gray_matches:
                                x, y, w, h = gray_match
                                # 使用灰階匹配位置建立局部搜尋區域
                                local_region = (x, y, w, h)
                                color_matches = self.scene_manager.match_template(
                                    screenshot,
                                    template,
                                    region=local_region,
                                    color=True,
                                    threshold=self.threshold
                                )
                                if color_matches and len(color_matches) > 0:
                                    target_match = gray_match
                                    found_color_match = True
                                    print(f"[INFO] 找到彩色匹配位置: {self.button_id} at {target_match}")
                                    break
                            
                            if not found_color_match:
                                print(f"[WARNING] 未找到符合的彩色匹配位置: {self.button_id}")
                                continue
                        else:
                            print(f"[INFO] 使用灰階匹配位置: {self.button_id} ({len(gray_matches)} 個匹配)")
                            target_match = gray_matches[0]
                            break
    
            if target_match is not None:
                # 計算點擊位置
                    x, y, w, h = target_match
                    click_x = x + w // 2
                    click_y = y + h // 2

                    target_position = (click_x, click_y)
            
            if target_position:
                try:
                    click_x, click_y = target_position
                    click_success = self.scene_manager.game.click(click_x, click_y)
                    
                    if click_success:
                        print(f"[INFO] 點擊按鈕: {self.button_id} at ({click_x}, {click_y})")
                        self.prev_success_position = (click_x, click_y)
                        return True
                    else:
                        print(f"[WARNING] 按鈕 {self.button_id} 點擊失敗")
                        return False
                except (IndexError, TypeError) as e:
                    print(f"[ERROR] 按鈕 {self.button_id} 計算點擊位置時發生錯誤: {e}")
                    return False

            print(f"[WARNING] 未找到按鈕 {self.button_id} 的匹配項")
            return False
        except Exception as e:
            print(f"[ERROR] 點擊按鈕 {self.button_id} 時發生錯誤: {e}")
            return False

    async def wait_click(self, max_retry=10, interval=1):
        start_scene_id = self.scene_manager.currentScene.scene_id if self.scene_manager.currentScene else None
        for i in range(max_retry):
            print(f"[INFO] 等待點擊按鈕 {self.button_id} {i}/{max_retry}")
            if self.click():
                print(f"[INFO] 點擊按鈕 {self.button_id} 成功")
                return True
            await asyncio.sleep(interval)
            check_scene = await self.scene_manager.check_current_screen()
            if not check_scene or check_scene.scene_id != start_scene_id:
                print(f"[INFO] 已轉場，停止等待按鈕 {self.button_id}")
                return True
        raise Exception(f"無法點擊按鈕 {self.button_id} (重試 {max_retry} 次)")
    
    
    async def try_wait_click(self, max_retry=10, interval=1):
        try:
            return await self.wait_click(max_retry, interval)
        except Exception as e:
            print(f"[WARNING] {e}")
            return False
    
    def click_prev_success_position(self):
        if self.prev_success_position:
            click_x, click_y = self.prev_success_position
            if self.scene_manager.game.click(click_x, click_y):
                print(f"[INFO] 點擊按鈕: {self.button_id} at ({click_x}, {click_y})")
                return True
        print(f"[WARNING] 無法點擊按鈕 {self.button_id} (未記錄上次成功的位置)")
        return False