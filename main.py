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
        if not steam.is_steam_running():
            await puppeteer.start_action("BootSteam")

        if not game.is_app_running():
            await puppeteer.start_action("BootGame")
        
        game.focus_window()
        
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

if __name__ == "__main__":
    asyncio.run(main())