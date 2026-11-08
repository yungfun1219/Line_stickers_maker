import os
from pathlib import Path
from PIL import Image
from rembg import remove


def process_line_stickers(input_dir='Data', output_dir='remove-OK'):
  # 3. 取得輸入資料夾路徑 (支援絕對路徑)
  input_path = Path(input_dir)
  if not input_path.exists():
    print(
        f'❌ 錯誤：找不到輸入資料夾「{input_path.absolute()}」，請確認路徑是否正確。',
        flush=True,
    )
    return

  # 1. 建立輸出資料夾（若不存在則自動建立，此處設定在與輸入同層級的 remove-OK）
  output_path = input_path.parent / output_dir
  os.makedirs(output_path, exist_ok=True)

  # 2. 定義支援的圖片副檔名
  valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')

  # 4. 尋找所有圖片檔案（並排序以確保順序固定）
  image_files = sorted(
      [f for f in input_path.iterdir() if f.suffix.lower() in valid_extensions]
  )

  if not image_files:
    print(
        f'⚠️ 提示：「{input_path.absolute()}」資料夾中找不到任何支援的圖片檔案。',
        flush=True,
    )
    return

  total_files = len(image_files)
  print(
      f'🔍 找到 {total_files} 張圖片，開始進行去背與 LINE 格式轉換...\n',
      flush=True,
  )

  success_count = 0

  for index, img_file in enumerate(image_files, 1):
    try:
      print(f'[{index}/{total_files}] ⏳ 正在處理: {img_file.name} ...', flush=True)

      # 開啟圖片並轉為 RGBA 格式（支援透明通道）
      input_image = Image.open(img_file).convert('RGBA')

      # 執行去背
      no_bg_image = remove(input_image)

      # --- 處理特別指定的主圖 (main.png) 與 標籤圖 (tab.png) ---
      if index == 1:
        # 1. 製作 main.png (240x240)
        main_img = no_bg_image.copy()
        main_img.thumbnail((240, 240), Image.Resampling.LANCZOS)
        main_canvas = Image.new('RGBA', (240, 240), (0, 0, 0, 0))
        mx = (240 - main_img.width) // 2
        my = (240 - main_img.height) // 2
        main_canvas.paste(main_img, (mx, my), main_img)
        main_file_path = output_path / 'main.png'
        main_canvas.save(main_file_path, 'PNG')
        print(f'   ✨ 已產生主圖: {main_file_path}', flush=True)

        # 2. 製作 tab.png (96x74)
        tab_img = no_bg_image.copy()
        tab_img.thumbnail((96, 74), Image.Resampling.LANCZOS)
        tab_canvas = Image.new('RGBA', (96, 74), (0, 0, 0, 0))
        tx = (96 - tab_img.width) // 2
        ty = (74 - tab_img.height) // 2
        tab_canvas.paste(tab_img, (tx, ty), tab_img)
        tab_file_path = output_path / 'tab.png'
        tab_canvas.save(tab_file_path, 'PNG')
        print(f'   ✨ 已產生標籤圖: {tab_file_path}', flush=True)

      # --- 處理貼圖本體 (01.png, 02.png ...) ---
      target_w, target_h = 370, 320

      sticker_img = no_bg_image.copy()
      sticker_img.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)

      sticker_canvas = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 0))
      sx = (target_w - sticker_img.width) // 2
      sy = (target_h - sticker_img.height) // 2
      sticker_canvas.paste(sticker_img, (sx, sy), sticker_img)

      # 依照順序命名為 01.png, 02.png ...
      output_filename = f'{index:02d}.png'
      output_filepath = output_path / output_filename

      sticker_canvas.save(output_filepath, 'PNG')
      success_count += 1
      print(
          f'[{index}/{total_files}] ✨ 成功儲存貼圖: {output_filepath}\n',
          flush=True,
      )

    except Exception as e:
      print(
          f'[{index}/{total_files}] ❌ 處理「{img_file.name}」時發生錯誤：{e}\n',
          flush=True,
      )

  print(
      f'🎉 全部處理完成！成功轉換 {success_count}/{total_files} 張圖片。',
      flush=True,
  )
  print(f'📁 所有符合 LINE 規範的檔案已存放在「{output_path}」資料夾中。')


if __name__ == '__main__':
  # 💡 這裡直接指定您的絕對完整路徑 (Windows 路徑前面建議加上 r 避免跳脫字元問題)
  absolute_input_dir = r'D:\github_repo\Line_image_cut\Data'

  process_line_stickers(input_dir=absolute_input_dir, output_dir='remove-OK')