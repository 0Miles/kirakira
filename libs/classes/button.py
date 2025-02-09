import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from libs.scene_manager import SceneManager

class Button:
    def __init__(self, button_id, template, scene_manager: 'SceneManager', region=None):
        self.button_id = button_id
        self.template = template if isinstance(template, list) else [template]
        self.scene_manager = scene_manager
        self.region = region  # [x, y, width, height]
        self.prev_success_position = None

    def click(self):
        try:
            screenshot = self.scene_manager.game.capture_screen()
            
            for template in self.template:
                # 如果有指定區域，則進行區域縮放
                search_region = None
                if self.region:
                    print(f"[INFO] 使用指定區域進行匹配: {self.region}")
                    search_region = self.scene_manager.get_safe_client_region(*self.region)
                
                matches = self.scene_manager.match_template(
                    screenshot, 
                    template,
                    region=search_region
                )
                
                if matches:
                    # 計算相對於視窗的點擊位置
                    x, y, w, h = matches[0]  # 取第一個匹配結果
                    click_x = x + w // 2
                    click_y = y + h // 2
                    
                    # 使用 AppControl 的 click 方法，並儲存點擊結果
                    click_success = self.scene_manager.game.click(click_x, click_y)
                    
                    if click_success:
                        print(f"[INFO] 點擊按鈕: {self.button_id} at ({click_x}, {click_y})")
                        self.prev_success_position = (click_x, click_y)
                        return True
                    else:
                        print(f"[WARNING] 按鈕 {self.button_id} 點擊失敗")
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