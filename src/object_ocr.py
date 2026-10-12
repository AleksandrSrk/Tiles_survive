"""Распознать всё на кадре дальнего зума: плашки объектов [TEG]Объект.
Рисуем рамки поверх скрина для визуальной проверки качества."""
import sys, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
import easyocr

SRC = Path(r"D:\PROJECT\TilesSurviveMap\data\720\screens\dalniy_raw.png")
ANNOT = Path(r"D:\PROJECT\TilesSurviveMap\data\720\screens\dalniy_annotated.png")

img = Image.open(SRC).convert("RGB")
print("Кадр:", img.size, flush=True)
reader = easyocr.Reader(["ru", "en"], gpu=False, verbose=False)
results = reader.readtext(np.array(img), detail=1)  # (bbox, text, conf)

TAG = re.compile(r"\[?\s*([A-Za-z]{2,4})\s*\]")  # [FNX], [ONE], [Zar], [HoD]...
draw = ImageDraw.Draw(img)
rows = []
for bbox, text, conf in results:
    xs = [p[0] for p in bbox]; ys = [p[1] for p in bbox]
    cx, cy = int(sum(xs) / 4), int(sum(ys) / 4)
    has_tag = bool(TAG.search(text))
    color = (0, 220, 0) if has_tag else (255, 60, 60)
    draw.rectangle([min(xs), min(ys), max(xs), max(ys)], outline=color, width=2)
    if has_tag:
        rows.append((text.strip(), round(float(conf), 2), cx, cy))

img.save(ANNOT)
print(f"\nВсего текстовых блоков: {len(results)} | из них с тегом [XXX]: {len(rows)}")
print("Аннотированный кадр:", ANNOT)
print("\n--- Объекты с тегом союза (text | conf | x,y) ---")
for text, conf, cx, cy in sorted(rows, key=lambda r: (r[3], r[2])):
    print(f"  {text:<28} conf={conf:<5} @({cx},{cy})")
