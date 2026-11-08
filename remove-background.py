import os
from pathlib import Path
from PIL import Image
from rembg import remove

def batch_remove_and_resize(input_dir="Data", output_dir="remove-OK", target_size=300):
    # 1. 建立輸出資料夾（若不存在則自動建立）
    os.makedirs(output_dir, exist_ok=True)
    
    # 2. 定義支援的圖片副檔名
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
    
    # 3. 取得輸入資料夾路徑
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ 錯誤：找不到輸入資料夾「{input_dir}」，請確認路徑是否正確。")
        return

    # 4. 尋找所有圖片檔案
    image_files = [f for f in input_path.iterdir() if f.suffix.lower() in valid_extensions]
    
    if not image_files:
        print(f"⚠️ 提示：在「{input_dir}」資料夾中找不到任何支援的圖片檔案。")
        return

    print(f"🔍 找到 {len(image_files)} 張圖片，開始進行去背與縮放至 {target_size}x{target_size} 像素...\n")

    # 5. 逐一讀取、去背、縮放並置中儲存
    success_count = 0
    for img_file in image_files:
        try:
            print(f"處理中: {img_file.name} ...")
            
            # 開啟圖片並轉為 RGBA 格式（支援透明通道）
            input_image = Image.open(img_file).convert("RGBA")
            
            # 執行去背
            no_bg_image = remove(input_image)
            
            # --- 調整尺寸與置中處理 ---
            # 保持原始長寬比例，縮放主體使其能放入 target_size x target_size 內
            no_bg_image.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
            
            # 建立一個 300x300 的全透明畫布
            new_image = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
            
            # 計算貼上的座標，使縮放後的圖片置於畫布正中央
            paste_x = (target_size - no_bg_image.width) // 2
            paste_y = (target_size - no_bg_image.height) // 2
            
            # 將去背後的圖片貼到新畫布上
            new_image.paste(no_bg_image, (paste_x, paste_y), no_bg_image)
            
            # 設定輸出檔名與路徑（統一儲存為 .png）
            output_filename = f"{img_file.stem}.png"
            output_filepath = Path(output_dir) / output_filename
            
            # 儲存圖片
            new_image.save(output_filepath, "PNG")
            success_count += 1
            print(f"✨ 成功！已儲存至: {output_filepath}")
            
        except Exception as e:
            print(f"❌ 處理「{img_file.name}」時發生錯誤：{e}")

    print(f"\n🎉 全部處理完成！成功處理 {success_count}/{len(image_files)} 張圖片。")
    print(f"📁 統一尺寸為 {target_size}x{target_size} 的 PNG 檔案已存放在「{output_dir}」資料夾中。")

if __name__ == "__main__":
    # 執行批次去背與縮放函式
    batch_remove_and_resize(input_dir="Data", output_dir="remove-OK", target_size=300)