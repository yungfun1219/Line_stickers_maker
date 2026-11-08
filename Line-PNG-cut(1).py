import cv2
import numpy as np
import os
from PIL import Image

# 1. 讀取圖片
image_path = '2026-11-08.png'  # 請替換為你的圖片檔案名稱
img = cv2.imread(image_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 2. 影像二值化與形態學處理（找出貼圖主體與背景的界線）
# 假設背景是淺色系，利用反轉閾值抓出深色的貼圖主體
_, thresh = cv2.threshold(gray, 235, 255, cv2.THRESH_BINARY_INV)

# 進行閉運算（Closing），將貼圖內部的碎塊與周圍裝飾字連成一個完整的區塊
kernel = np.ones((15, 15), np.uint8)
closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

# 3. 尋找所有獨立的貼圖輪廓
contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

output_dir = 'smart_line_stickers'
os.makedirs(output_dir, exist_ok=True)

bounding_boxes = []
for c in contours:
    x, y, w, h = cv2.boundingRect(c)
    # 過濾掉太小的雜訊或佔滿全圖的大框
    if w > 80 and h > 80 and w < img.shape[1] * 0.95 and h < img.shape[0] * 0.95:
        bounding_boxes.append((x, y, w, h))

# 4. 依照排版位置排序（先由上到下分行，再由左到右排序）
# 這裡以大約的行高分群
bounding_boxes = sorted(bounding_boxes, key=lambda b: (b[1] // 120, b[0]))

# 5. 進行智慧裁切與邊距微調
for i, (x, y, w, h) in enumerate(bounding_boxes):
    # 設定安全邊距 (Padding)，避免切到外框或特效字
    padding = 10
    x_start = max(0, x - padding)
    y_start = max(0, y - padding)
    x_end = min(img.shape[1], x + w + padding)
    y_end = min(img.shape[0], y + h + padding)

    # 裁切區域
    sticker = img[y_start:y_end, x_start:x_end]

    # 轉換色彩並用 Pillow 調整為 LINE 貼圖標準尺寸 (最大 370x320)
    sticker_rgb = cv2.cvtColor(sticker, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(sticker_rgb)
    pil_img.thumbnail((370, 320), Image.Resampling.LANCZOS)

    # 儲存圖片
    output_path = os.path.join(output_dir, f'smart_sticker_{i+1:02d}.png')
    pil_img.save(output_path, 'PNG')
    print(f'已智慧裁切並儲存: {output_path}')

print('所有貼圖智慧裁切完成！')