# KiraKira

## 安裝說明

### 系統需求
- Python 3.8 或更新版本
- pip（Python 套件安裝工具）
- Windows 作業系統（目前僅支援 Windows）

### 安裝相依套件
1. 建立虛擬環境（建議使用）：
```bash
python -m venv .venv
source .venv/bin/activate  # Windows 系統請使用：.venv\Scripts\activate
```

2. 安裝必要套件：
```bash
pip install -r requirements.txt
```

## 核心功能

### Scene
Scene 系統是一套用於自動化腳本的畫面狀態管理框架。每個 Scene 代表一個特定的畫面狀態，主要負責：
- 透過圖像識別判斷當前是否處於該狀態
- 管理畫面上的互動元件（按鈕、輸入框等）
- 處理畫面互動邏輯
- 處理不同狀態間的轉換

#### 1. 畫面狀態識別
每個 Scene 都必須提供識別用的圖片（identification_images），系統會透過這些圖片來判斷當前是否處於該狀態。識別圖片必須是該畫面中獨特且穩定的視覺元素。

#### 2. 互動元件管理
Scene 可以管理兩種主要的互動元件：
- **按鈕（Button）**：可點擊的介面元素
- **輸入框（Input）**：包含文字輸入框、下拉式選單、核取方塊等

#### 3. 狀態轉換
Scene 透過 SceneManager 來管理狀態轉換，確保腳本能在不同畫面間正確切換。

## Scene 設定說明

### 基礎設定
```json
{
    "scene_id": "your-scene-id",                    // 場景識別碼
    "identification_images": [                      // 用於識別場景的圖片
        "scenes/your-scene/identifier1.png",        // 可設定多個識別圖片
        "scenes/your-scene/identifier2.png"         // 所有圖片都必須能被找到才算符合
    ],
    "button_configs": [                            // 按鈕設定（選用）
        {
            "id": "confirm",                        // 按鈕識別碼
            "template": "path/to/button.png"        // 按鈕圖片範本
        },
        {
            "id": "menu",
            "template": [                           // 可使用多個範本圖片
                "path/to/menu1.png",                // 符合任一圖片即視為找到按鈕
                "path/to/menu2.png"
            ]
        }
    ],
    "input_configs": [                             // 輸入框設定（選用）
        {
            "id": "username",                       // 輸入框識別碼
            "type": "text",                         // 輸入框類型：text/select/checkbox
            "label_template": "path/to/label.png",  // 輸入框標籤圖片
            "input_template": "path/to/input.png",  // 輸入框圖片
            "position": "right",                    // 輸入框相對於標籤的位置
            "offset": [0, 0]                        // 輸入框相對於標籤的位移量 [x, y]
        }
    ]
}
```

### Scene ID 命名規則

Scene ID 使用底線（_）來表示場景的階層關係，例如：

```
matching                    # 配對主畫面
matching_diethelm          # 配對主畫面下的 diethelm 子畫面
matching_diethelm_dialog   # diethelm 子畫面下的對話框
```

## Scene 使用方式

### 1. 初始化
```python
from your_scene import YourScene
from core.scene_manager import SceneManager

scene_manager = SceneManager()
your_scene = YourScene(scene_manager)
```

### 2. 狀態檢查
```python
# 檢查是否在特定場景
if scene_manager.is_current_scene("your-scene-id"):
    # 執行相關操作
    pass
```

### 3. 互動操作
```python
# 按鈕點擊
your_scene.buttons["confirm"].click()

# 輸入框操作
your_scene.inputs["username"].input("輸入文字")      # 文字輸入
your_scene.inputs["option"].select("選項")          # 下拉選單選擇
your_scene.inputs["agree"].check()                 # 核取方塊勾選