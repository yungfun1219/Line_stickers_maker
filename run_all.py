import os
from pathlib import Path
import batch_remove_resize  # 引入您原本的去背與轉檔程式

def run_pipeline():
    print("========================================")
    print("🚀 第一階段：讀取 Gemini-prompt.txt 提示詞")
    print("========================================")
    
    prompt_file = "Gemini-prompt.txt"
    if not os.path.exists(prompt_file):
        print(f"❌ 錯誤：找不到「{prompt_file}」，請確認該檔案是否存在於同個資料夾中。")
        return
        
    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_content = f.read()
        
    print(f"📖 成功讀取「{prompt_file}」，內容字數：{len(prompt_content)} 字元。")
    print("💡 提示：若您已將 16 張圖片準備好並放入【Data】資料夾，程式將直接進入下一步驟。\n")
    
    # 檢查 Data 資料夾是否存在
    data_dir = "Data"
    if not os.path.exists(data_dir):
        print(f"⚠️ 提示：找不到「{data_dir}」資料夾。系統已自動幫您建立。")
        os.makedirs(data_dir, exist_ok=True)
        print(f"📁 請將圖檔放入【{data_dir}】資料夾後，再次執行此程式！")
        return

    print("========================================")
    print("🚀 第二階段：執行圖片去背與 LINE 規格轉檔")
    print("========================================")
    
    # 直接呼叫 batch_remove_resize.py 裡的處理函式
    batch_remove_resize.process_line_stickers(input_dir="Data", output_dir="remove-OK")
    
    print("\n🎉 全部流程執行完畢！")

if __name__ == "__main__":
    run_pipeline()