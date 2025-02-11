import asyncio
from typing import TYPE_CHECKING
from libs.puppeteer import Puppeteer
from libs.scene_manager import SceneManager
from libs.steam_control import SteamControl
from libs.app_control import AppControl
import config

if TYPE_CHECKING:
    from actions.find_sandbag import FindSandbag

async def main():
    steam = SteamControl(config.STEAM_GAME_ID)
    game = AppControl(config.GAME_NAME, config.GAME_WINDOW_TITLE)
    scene_manager = SceneManager(game, (config.TEMPLATE_ORIGIN_CLIENT_WIDTH, config.TEMPLATE_ORIGIN_CLIENT_HEIGHT), config.TEMPLATE_ORIGIN_TITLE_BAR_HEIGHT, config.TEMPLATE_ORIGIN_LEFT_BORDER_WIDTH)
    # 創建並初始化 Puppeteer
    puppeteer = Puppeteer(
        steam_control=steam,
        app_control=game,
        scene_manager=scene_manager
    )
    await puppeteer.initialize()
    
    # 列出所有可用的動作
    available_actions = puppeteer.list_available_actions()
    print("可用的動作：")
    for action in available_actions:
        print(f"- {action}")

    # 開始執行動作
    while True:
        if not game.is_app_running():
            # 透過 Steam 啟動遊戲
            print(f"[INFO] 正在透過 Steam 啟動遊戲: {config.GAME_NAME}...")
            steam.start_game()

            # 檢測遊戲是否已開啟完畢
            while not game.is_app_running():
                print("[INFO] 遊戲尚未啟動，等待 5 秒後再次檢查...")
                await asyncio.sleep(5)
            print("[INFO] 遊戲啟動完成。")

        try:
            await puppeteer.start_action("GoToDiethelm")
            if (config.SCRIPT_MODE == "being_a_sandbag"):
                await puppeteer.start_action("BeingASandbag")
            elif (config.SCRIPT_MODE == "find_sandbag"):
                await puppeteer.start_action("FindSandbag")
                find_sandbag: 'FindSandbag' = puppeteer.get_action("FindSandbag")
                if find_sandbag.green_tea_not_enough and find_sandbag.ap_not_enough:
                    game.close_app()
                    find_sandbag.green_tea_not_enough = False
                    find_sandbag.ap_not_enough = False
                    print("[INFO] 關閉遊戲，等待30分鐘後再開")
                    await asyncio.sleep(1800)
                else:
                    if config.BONUS_GAME_TARGET == "gem":
                        await puppeteer.start_action("BonusGameGemCollectMode")
                    elif config.BONUS_GAME_TARGET == "star_rank":
                        await puppeteer.start_action("BonusGameStarRankMode")
        except Exception as e:
            print(f"[ERROR] 發生錯誤: {e}")
            puppeteer.logger.error(f"發生錯誤: {e}")
            # 關閉遊戲等待重啟，避免腳本卡住
            try:
                game.close_app()
            except:
                pass
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())