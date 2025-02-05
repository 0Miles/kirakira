import asyncio
from libs.puppeteer import Puppeteer
from libs.steam_control import SteamControl
from libs.app_control import AppControl
import config

async def main():
    steam = SteamControl(config.STEAM_GAME_ID)
    game = AppControl(config.GAME_NAME, config.GAME_WINDOW_TITLE)
    # 創建並初始化 Puppeteer
    puppeteer = Puppeteer(
        steam_control=steam,
        app_control=game
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
                if puppeteer.scene_manager.extra_info.get("green-tea-not-enough", False) and not puppeteer.scene_manager.extra_info.get("ap-not-enough", False):
                    game.close_app()
                    puppeteer.scene_manager.extra_info["green-tea-not-enough"] = False
                    puppeteer.scene_manager.extra_info["ap-not-enough"] = False
                    print("[INFO] 關閉遊戲，等待30分鐘後再開")
                    await asyncio.sleep(1800)
                else:
                    await puppeteer.start_action("BonusGame")
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