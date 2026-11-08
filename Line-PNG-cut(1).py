import os
import cv2
import numpy as np
from PIL import Image

# 取得目前執行程式所在的絕對目錄
current_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_dir, 'IMG_8842.JPG')

if not os.path.exists(image_path):
  raise FileNotFoundError(f'找不到圖片檔案: {image_path}')

# 讀取圖片 (支援中文路徑)
img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
if img is None:
  raise FileNotFoundError(f'無法成功解析圖片: {image_path}')

img_h, img_w, _ = img.shape

# 建立輸出資料夾
output_dir = os.path.join(current_dir, 'smart_line_stickers')
os.makedirs(output_dir, exist_ok=True)

# 16方格為 4欄 x 4列
cols = 4
rows = 4

cell_w = img_w / cols
cell_h = img_h / rows

sticker_count = 0

# 迴圈切出每一格
for r in range(rows):
  for c in range(cols):
    sticker_count += 1

    # 計算每一格的精確座標
    x_start = int(c * cell_w)
    y_start = int(r * cell_h)
    x_end = int((c + 1) * cell_w)
    y_end = int((r + 1) * cell_h)

    # 裁切格子
    sticker = img[y_start:y_end, x_start:x_end]

    # 色彩轉換並用 Pillow 調整為 LINE 貼圖標準尺寸 (最大 370x320)
    sticker_rgb = cv2.cvtColor(sticker, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(sticker_rgb)
    pil_img.thumbnail((370, 320), Image.Resampling.LANCZOS)

    # 儲存圖片
    output_path = os.path.join(
        output_dir, f'smart_sticker_{sticker_count:02d}.png'
    )
    pil_img.save(output_path, 'PNG')
    print(f'已裁切第 {sticker_count} 張貼圖並儲存: {output_path}')

print('16 方格貼圖全部裁切完成！')