# LINE 創意貼圖自動化製作與處理專案報告

本專案旨在打造一套完整的自動化工作流程，從 **AI 提示詞設計、圖像生成、自動去背、尺寸正規化** 到符合 **LINE Creators Market 官方規範** 的貼圖打包，實現「一條龍」的程式化生產。

---

## 一、 專案核心目標與規格

### 1. 視覺設計主題與 16 格文字清單
角色維持一致的可愛社畜男性搭配胖貓造型，透過俏皮的漫畫符號（速度線、汗滴、愛心、星星等）強化幽默感。16 格文字內容各自獨立且準確：
1. `收到！馬上去辦（靈魂已出竅）`
2. `好的，小的這就去肝`
3. `收到，老大說得都對`
4. `好的，我醒了（但心死）`
5. `謝謝老闆，老闆一生平安發大財`
6. `小的明白，馬上奉上`
7. `恩恩、收到、好低（極度敷衍）`
8. `啊對對對`
9. `確實、完全認同（眼神死）`
10. `水喔（不知道發生什麼事但先附議）`
11. `收到了，但不想動`
12. `好的，但這超出我的薪水範圍了`
13. `我對這間破公司無話可說`
14. `今天又是元氣的一天（眼神死）`
15. `我的熱情好像在週一早上就燒光了`
16. `腦子空空，月薪三萬五的容貌`

### 2. LINE 官方審核尺寸規範
* **Main (主要圖片)**：$240 \times 240\text{ px}$（1張，透明背景，命名為 `main.png`）
* **Tab (聊天室標籤圖)**：$96 \times 74\text{ px}$（1張，透明背景，命名為 `tab.png`）
* **貼圖本體 (Stickers)**：最大 $370 \times 320\text{ px}$ 等比例置中（16張，透明背景，依序命名為 `01.png` 到 `16.png`）

---

## 二、 專案資料夾結構

專案運行所需的檔案與目錄結構如下：
```text
📂 Line圖裁切/
│
├── gemini_API.env             # 存放 Gemini API 金鑰設定檔
├── Gemini-prompt.txt          # 生成圖片的完整 AI 提示詞
├── batch_remove_resize.py     # 去背、縮放與 LINE 格式轉檔模組
├── run_generate_and_process.py # 整合 API 生圖與自動化處理的總控程式
│
├── 📂 Data/                   # 原始圖片放置資料夾（自動下載或手動放入）
└── 📂 remove-OK/              # 最終符合 LINE 規範的 PNG 輸出資料夾
```

---

## 三、 核心程式碼實作

### 1. 設定檔：`gemini_API.env`
用於安全存放 API 金鑰：
```env
GEMINI_API_KEY=您的實際API金鑰字串
```

### 2. 影像處理與去背模組：`batch_remove_resize.py`
負責讀取 `Data` 資料夾中的圖片，透過 `rembg` 進行深度學習去背，並依據 LINE 官方規格產生 `main.png`、`tab.png` 與依序編號的貼圖本體。

```python
import os
from pathlib import Path
from PIL import Image
from rembg import remove

def process_line_stickers(input_dir="Data", output_dir="remove-OK"):
    os.makedirs(output_dir, exist_ok=True)
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
    
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ 錯誤：找不到輸入資料夾「{input_dir}」", flush=True)
        return

    image_files = sorted([f for f in input_path.iterdir() if f.suffix.lower() in valid_extensions])
    if not image_files:
        print(f"⚠️ 提示：在「{input_dir}」中找不到支援的圖片。", flush=True)
        return

    total_files = len(image_files)
    print(f"🔍 找到 {total_files} 張圖片，開始進行去背與 LINE 格式轉換...\n", flush=True)

    success_count = 0
    for index, img_file in enumerate(image_files, 1):
        try:
            print(f"[{index}/{total_files}] ⏳ 正在處理: {img_file.name} ...", flush=True)
            input_image = Image.open(img_file).convert("RGBA")
            no_bg_image = remove(input_image)
            
            # 處理 main.png 與 tab.png (僅第一張圖)
            if index == 1:
                # Main: 240x240
                main_img = no_bg_image.copy()
                main_img.thumbnail((240, 240), Image.Resampling.LANCZOS)
                main_canvas = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
                main_canvas.paste(main_img, ((240 - main_img.width) // 2, (240 - main_img.height) // 2), main_img)
                main_canvas.save(Path(output_dir) / "main.png", "PNG")
                
                # Tab: 96x74
                tab_img = no_bg_image.copy()
                tab_img.thumbnail((96, 74), Image.Resampling.LANCZOS)
                tab_canvas = Image.new("RGBA", (96, 74), (0, 0, 0, 0))
                tab_canvas.paste(tab_img, ((96 - tab_img.width) // 2, (74 - tab_img.height) // 2), tab_img)
                tab_canvas.save(Path(output_dir) / "tab.png", "PNG")

            # 處理貼圖本體 (370x320)
            target_w, target_h = 370, 320
            sticker_img = no_bg_image.copy()
            sticker_img.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
            
            sticker_canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
            sticker_canvas.paste(sticker_img, ((target_w - sticker_img.width) // 2, (target_h - sticker_img.height) // 2), sticker_img)
            
            output_filepath = Path(output_dir) / f"{index:02d}.png"
            sticker_canvas.save(output_filepath, "PNG")
            success_count += 1
            print(f"[{index}/{total_files}] ✨ 成功儲存: {output_filepath}\n", flush=True)
            
        except Exception as e:
            print(f"❌ 處理 {img_file.name} 失敗: {e}\n", flush=True)

    print(f"🎉 處理完成！成功轉換 {success_count}/{total_files} 張圖片至「{output_dir}」。", flush=True)
```

### 3. 總控與 API 整合主程式：`run_generate_and_process.py`
負責讀取 `.env` 與 `Gemini-prompt.txt`，透過 Google Imagen 模型生成圖片並下載至 `Data`，隨後無縫銜接去背與轉檔流程。

```python
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
import batch_remove_resize

# 載入 API 金鑰設定
load_dotenv("gemini_API.env")

def generate_stickers_from_prompt():
    print("========================================")
    print("🚀 第一階段：讀取提示詞並透過 Imagen 生圖")
    print("========================================")
    
    if not os.path.exists("Gemini-prompt.txt"):
        print("❌ 錯誤：找不到 Gemini-prompt.txt")
        return False
        
    with open("Gemini-prompt.txt", "r", encoding="utf-8") as f:
        prompt_content = f.read()

    try:
        client = genai.Client()
    except Exception as e:
        print(f"❌ 初始化 GenAI Client 失敗: {e}")
        return False
    
    os.makedirs("Data", exist_ok=True)

    try:
        print("⏳ 正在請求 AI 生成圖片...")
        result = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt_content,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/png",
                aspect_ratio="1:1",
            )
        )

        for i, img in enumerate(result.generated_images, 1):
            image_path = Path("Data") / f"{i:02d}.png"
            with open(image_path, "wb") as f:
                f.write(img.image.image_bytes)
            print(f"✨ 成功下載圖片至: {image_path}")
            
        return True
    except Exception as e:
        print(f"❌ 生圖失敗: {e}（若 API 尚未開通，可手動將圖片放入 Data 資料夾）")
        return False

def run_pipeline():
    generate_stickers_from_prompt()
    
    if not any(Path("Data").iterdir()) if Path("Data").exists() else False:
        print("⚠️ 【Data】資料夾無圖片，終止處理。")
        return

    print("========================================")
    print("🚀 第二階段：執行去背與 LINE 規格轉檔")
    print("========================================")
    batch_remove_resize.process_line_stickers(input_dir="Data", output_dir="remove-OK")
    print("\n🎊 全部流程執行完畢！")

if __name__ == "__main__":
    run_pipeline()
```

---

## 四、 執行步驟總結

1. **環境套件安裝**：
   ```bash
   pip install google-genai pillow rembg python-dotenv
   ```
2. **放置必要檔案**：確保 `gemini_API.env`、`Gemini-prompt.txt`、`batch_remove_resize.py` 與 `run_generate_and_process.py` 位於同一個工作目錄。
3. **執行主程式**：
   ```bash
   python run_generate_and_process.py
   ```
4. **取得成果**：前往 `remove-OK` 資料夾，即可直接取得符合 LINE 上傳審核標準的 `main.png`、`tab.png` 以及 `01.png` ~ `16.png`。