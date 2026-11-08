import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
import batch_remove_resize  # 引入您原本的去背與轉檔程式

# 1. 自動載入 gemini_API.env 檔案中的環境變數
env_file = "gemini_API.env"
if os.path.exists(env_file):
    load_dotenv(env_file)
    print(f"🔑 成功載入設定檔：{env_file}")
else:
    print(f"⚠️ 警告：找不到「{env_file}」，將嘗試讀取系統預設的環境變數。")

def generate_stickers_from_prompt():
    print("========================================")
    print("🚀 第一階段：讀取 Gemini-prompt.txt 並透過 Imagen 生圖")
    print("========================================")
    
    prompt_file = "Gemini-prompt.txt"
    if not os.path.exists(prompt_file):
        print(f"❌ 錯誤：找不到「{prompt_file}」，請確認該檔案是否存在於同個資料夾中。")
        return False
        
    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_content = f.read()
        
    print(f"📖 成功讀取提示詞檔案，準備連線至 Google Imagen 模型...")

    # 初始化 Google GenAI Client (會自動讀取剛剛載入的 API 金鑰)
    try:
        client = genai.Client()
    except Exception as e:
        print(f"❌ 初始化 GenAI Client 失敗，請檢查 API 金鑰是否正確設定於 {env_file} 中。錯誤訊息：{e}")
        return False
    
    # 建立 Data 資料夾（若不存在）
    data_dir = "Data"
    os.makedirs(data_dir, exist_ok=True)

    try:
        print("⏳ 正在請求 AI 生成圖片，請稍候...")
        
        # 使用 Imagen 3 模型來根據提示詞生成圖片
        result = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt_content,
            config=types.GenerateImagesConfig(
                number_of_images=1, # 可根據需求調整張數
                output_mime_type="image/png",
                aspect_ratio="1:1",  # 貼圖建議使用 1:1 正方形
            )
        )

        # 將生成的圖片下載並存入 Data 資料夾
        for i, generated_image in enumerate(result.generated_images, 1):
            image_path = Path(data_dir) / f"{i:02d}.png"
            with open(image_path, "wb") as f:
                f.write(generated_image.image.image_bytes)
            print(f"✨ 成功下載圖片至: {image_path}")
            
        print("🎉 第一階段：圖片生成與下載至【Data】資料夾完成！\n")
        return True

    except Exception as e:
        print(f"❌ 生成圖片時發生錯誤：{e}")
        print("💡 提示：若 Imagen 服務暫時無法存取，您可以手動將圖片放入 Data 資料夾，程式會自動繼續執行後續步驟。")
        return False

def run_pipeline():
    # 步驟 1：讀取 Prompt 並嘗試自動生成圖檔到 Data 資料夾
    success = generate_stickers_from_prompt()
    
    # 若生成失敗（或您習慣手動放圖），只要 Data 裡面有圖，我們就直接進入去背與轉檔流程
    data_path = Path("Data")
    has_images = any(data_path.iterdir()) if data_path.exists() else False

    if not has_images:
        print("⚠️ 【Data】資料夾中沒有任何圖片，無法進行後續處理。")
        return

    print("========================================")
    print("🚀 第二階段：執行去背與 LINE 規格轉檔")
    print("========================================")
    
    # 步驟 2：呼叫您原本的 batch_remove_resize 程式邏輯處理 Data 裡的圖片
    batch_remove_resize.process_line_stickers(input_dir="Data", output_dir="remove-OK")
    
    print("\n🎊 全部流程一次搞定！產出的 LINE 貼圖已放在【remove-OK】資料夾中。")

if __name__ == "__main__":
    run_pipeline()