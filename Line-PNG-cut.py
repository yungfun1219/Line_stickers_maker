import os
import cv2
import numpy as np
from PIL import Image

# 1. 讀取圖片（請確認檔名是否正確）
image_path = '2026-11-08.png'  # 請替換為您的 4x4 圖片檔名
if not os.path.exists(image_path):
  # 試著找尋當前資料夾下的圖檔
  for file in os.listdir('.'):
    if file.endswith(('.png', '.jpg', '.jpeg')):
      image_path = file
      break

print(f'正在讀取圖片: {image_path}')
img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

if img is None:
  raise FileNotFoundError(
      f'找不到圖片 {image_path}，請確認檔案名稱與路徑是否正確！'
  )

# 如果圖片帶有透明通道，先轉為 BGR
if img.shape[2] == 4:
  # 備份 alpha 通道，若無則轉純 BGR
  bgr_img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
else:
  bgr_img = img

h_img, w_img, _ = bgr_img.shape

# 2. 建立輸出資料夾
output_dir = 'line_stickers_output'
os.makedirs(output_dir, exist_ok=True)

# 3. 4x4 網格切割參數設定
rows, cols = 4, 4
cell_h = h_img // rows
cell_h_rem = h_img % rows
cell_w = w_img // cols
cell_w_rem = w_img % cols

sticker_count = 0

print('開始進行 4x4 圖貼切割與去背...')

for r in range(rows):
  for c in range(cols):
    sticker_count += 1

    # 計算每個格子的起點與終點（處理像素除不盡的問題）
    y1 = r * cell_h + min(r, cell_h_rem)
    y2 = (r + 1) * cell_h + min(r + 1, cell_h_rem)
    x1 = c * cell_w + min(c, cell_w_rem)
    x2 = (c + 1) * cell_w + min(c + 1, cell_w_rem)

    # 擷取該格子的子畫面
    cell_img = bgr_img[y1:y2, x1:x2]

    # 4. 自動去背處理（將淺色/透明背景轉為透明）
    gray_cell = cv2.cvtColor(cell_img, cv2.COLOR_BGR2GRAY)

    # 假設背景是白色或淺灰色（大於 235 視為背景）
    # 建立遮罩：背景為 0，主體為 255
    _, mask = cv2.threshold(gray_cell, 230, 255, cv2.THRESH_BINARY_INV)

    # 形態學清理雜訊
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

    # 尋找該格子內主體的邊界，去除多餘留白
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if contours:
      # 找出最大輪廓或合併所有輪廓範圍
      all_pts = np.concatenate(contours)
      bx, by, bw, bh = cv2.boundingRect(all_pts)

      # 加上一點安全邊距 (Padding) 避免貼圖邊緣被切太緊
      padding = 12
      bx = max(0, bx - padding)
      by = max(0, by - padding)
      bw = min(cell_img.shape[1] - bx, bw + padding * 2)
      bh = min(cell_img.shape[0] - by, bh + padding * 2)

      # 裁切出精準的主體
      final_crop = cell_img[by : by + bh, bx : bx + bw]
      final_mask = mask[by : by + bh, bx : bx + bw]
    else:
      final_crop = cell_img
      final_mask = np.ones(cell_img.shape[:2], dtype=np.uint8) * 255

    # 5. 轉成 RGBA (加入透明通道)
    b, g, r_ch = cv2.split(final_crop)
    rgba = cv2.merge([b, g, r_ch, final_mask])

    # 6. 使用 Pillow 縮放為 LINE 貼圖標準大小 (最大 370x320，保持比例)
    pil_img = Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA))
    pil_img.thumbnail((370, 320), Image.Resampling.LANCZOS)

    # 7. 儲存結果
    output_path = os.path.join(output_dir, f'sticker_{sticker_count:03d}.png')
    pil_img.save(output_path, 'PNG')
    print(f'已成功切割並去背: {output_path}')

print(f'\n所有 16 張貼圖已處理完成！檔案儲存在資料夾: "{output_dir}"')