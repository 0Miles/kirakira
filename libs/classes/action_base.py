import asyncio
from typing import Optional, Dict, Callable, Any, List, Union, TypeVar, cast
from typing import TYPE_CHECKING
import inspect

if TYPE_CHECKING:
    from libs.scene_manager import SceneManager
    from libs.app_control import AppControl
    from libs.steam_control import SteamControl

T = TypeVar('T', bound=Callable)

def loop(scene_id: str):
    """裝飾器：註冊循環執行的場景處理器"""
    def decorator(func: T) -> T:
        async def wrapper(self, *args, **kwargs):
            if not isinstance(self, ActionBase):
                raise TypeError("This decorator can only be used with ActionBase subclasses")
            await func(self, *args, **kwargs)
            self._again()
        setattr(wrapper, '_scene_id', scene_id)
        setattr(wrapper, '_is_handler', True)
        return cast(T, wrapper)
    return decorator

def once(scene_id: str, wait_for: Union[str, List[str], None] = None, timeout: int = 60):
    """
    裝飾器：註冊只執行一次的場景處理器
    Args:
        scene_id: 處理器對應的場景ID
        wait_for: 執行後等待的場景
                 - str或List[str]: 等待指定的一個或多個場景
                 - "next": 等待序列中的下一個場景
                 - None: 等待任何場景變化
    """
    def decorator(func: T) -> T:
        async def wrapper(self, *args, **kwargs):
            if not isinstance(self, ActionBase):
                raise TypeError("This decorator can only be used with ActionBase subclasses")
            await func(self, *args, **kwargs)
            # 根據 wait_for 參數決定等待行為
            if wait_for == "next":
                self.set_idle_until_next(timeout)
            elif wait_for is not None:
                self.set_idle_until(wait_for, timeout)
            else:
                self.set_idle_until_change()
        setattr(wrapper, '_scene_id', scene_id)
        setattr(wrapper, '_is_handler', True)
        return cast(T, wrapper)
    return decorator

class ActionBase():
    def __init__(self, steam: 'SteamControl', game: 'AppControl', scene_manager: 'SceneManager'):
        self.steam = steam
        self.game = game
        self.scene_manager = scene_manager
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self.scene_handlers: Dict[str, Callable] = {}
        self._scene_ids: List[str] = []

        self._waiting_for: Optional[List[str]] = None
        self._waiting_timeout: int = 60
        self._waiting_start_timestamp: Optional[float] = None
        self._again_flag = False

        self._setup_scene_handlers()
        self._refresh_failed_count = 0

    def _setup_scene_handlers(self):
        """自動註冊場景處理器"""
        # 取得所有被標記為處理器的方法
        for name, method in inspect.getmembers(self):
            if hasattr(method, '_is_handler'):
                scene_id = getattr(method, '_scene_id')
                self.scene_handlers[scene_id] = method
                if scene_id not in self._scene_ids:
                    self._scene_ids.append(scene_id)

    async def process(self):
        if not await self.scene_manager.refresh():
            self._refresh_failed_count += 1
            if self._refresh_failed_count > 10:
                print("[Error] 無法更新場景，停止 Action")
                raise Exception("無法更新場景")
            return
        else:
            self._refresh_failed_count = 0

        if not self.scene_manager.currentScene:
            await self.on_unknown_scene()
            return
        
        if self._waiting_for and not self._again_flag:
            scene_id = self.scene_manager.currentScene.scene_id
            if scene_id in self._waiting_for:
                self._waiting_for = None
            elif asyncio.get_event_loop().time() - self._waiting_start_timestamp > self._waiting_timeout:
                self._waiting_for = None
                print(f"[WARNING] 等待超時: {self._waiting_timeout}s")
            else:
                await asyncio.sleep(.5)
                return

        scene_id = self.scene_manager.currentScene.scene_id
        handler = self.scene_handlers.get(scene_id)
        
        if handler:
            print(f"[INFO] 已找到 {scene_id} 對應的 Handler")
            self._again_flag = False
            await handler()
        else:
            print(f"[INFO] 出現未註冊的場景: {scene_id}")
            await self.on_unhandled_scene()

    async def on_start(self):
        """
        生命週期方法：腳本開始執行時調用
        """
        pass

    async def on_end(self):
        """
        生命週期方法：腳本結束執行時調用
        """
        pass
    
    async def on_unknown_scene(self):
        """
        生命週期方法：當無法識別當前場景時調用
        """
        await asyncio.sleep(.5)

    async def on_unhandled_scene(self):
        """
        生命週期方法：當前場景未註冊處理器時調用
        """
        self.stop()
        await asyncio.sleep(1)

    def check_game_available(self):
        """
        檢查遊戲是否可用
        """
        if not self.game.is_app_running():
            print("[WARNING] 遊戲未啟動或不在活動狀態")
            self.stop()
            return False

    async def run(self):
        """
        在非同步循環中執行腳本流程
        """
        if self._running:
            print(f"[WARNING] {self.__class__.__name__} 已在執行中")
            return

        self._running = True
        try:
            await self.on_start()
            # 初始化等待標誌
            self._waiting_for = None
            while self._running:
                await self.process()
                await asyncio.sleep(0.1)
                self.check_game_available()
        except Exception as e:
            print(f"[ERROR] 發生錯誤, Action:{self.__class__.__name__}, Scene:{self.scene_manager.currentScene.scene_id if self.scene_manager.currentScene else None}: {e}")
            self._running = False
            raise
        finally:
            await self.on_end()
            self._running = False

    def start(self):
        """
        啟動腳本的非同步執行
        """
        if self._task and not self._task.done():
            print(f"[WARNING] {self.__class__.__name__} 已啟動")
            return

        self._task = asyncio.create_task(self.run())

    def stop(self):
        """
        停止腳本執行
        """
        print(f"[INFO] 中止動作: {self.__class__.__name__}")
        self._running = False
        if self._task:
            self._task.cancel()
    
    def set_idle_until(self, scene_ids: Union[str, List[str]], timeout: int = 60):
        """
        等待直到指定的場景之一出現
        Args:
            scene_ids: 單一場景ID或場景ID列表
            timeout: 等待超時時間（秒）
        """
        if isinstance(scene_ids, str):
            scene_ids = [scene_ids]
        self._waiting_for = scene_ids
        self._waiting_timeout = timeout
        self._waiting_start_timestamp = asyncio.get_event_loop().time()

    def set_idle_until_next(self, timeout: int = 60):
        """
        等待直到下一個場景出現
        """
        current_scene_id = self.scene_manager.currentScene.scene_id
        current_index = self._scene_ids.index(current_scene_id)
        next_index = current_index + 1
        if next_index >= len(self._scene_ids):
            next_index = 0
        self.set_idle_until(self._scene_ids[next_index], timeout)
    
    def set_idle_until_change(self):
        """
        等待直到場景發生變化
        """
        self.set_idle_until([scene_id for scene_id in self.scene_manager.scenes if scene_id != self.scene_manager.currentScene.scene_id])
    
    def _again(self):
        """
        不進入閒置等待直到場景發生變化
        """
        self._again_flag = True
