"""Тест дальнего зума: DPI-корректный захват окна игры + OCR штата.
Окно НЕ ресайзим — снимаем как есть, чтобы проверить сам захват.
Пауза перед снимком — дать карте прогрузиться с сервера."""
import sys, time, ctypes, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
# DPI-awareness ДО любой работы с окнами: координаты в реальных пикселях
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

import pygetwindow as gw
from PIL import ImageGrab
import numpy as np
import easyocr

OUT = r"D:\PROJECT\TilesSurviveMap\data\720\screens\dalniy_raw.png"
TITLE = "TilesSurvive"

wins = [w for w in gw.getAllWindows() if TITLE.lower() in (w.title or "").lower()]
if not wins:
    print("Окно игры не найдено"); sys.exit(1)
w = wins[0]
try:
    w.activate()
except Exception as e:
    print("activate warn:", e)
time.sleep(1.5)  # дать окну выйти вперёд + прогрузка

bbox = (w.left, w.top, w.left + w.width, w.top + w.height)
print("bbox (реальные пиксели):", bbox)
img = ImageGrab.grab(bbox=bbox, all_screens=True)
img.save(OUT)
print("Сохранён скрин:", OUT, "размер:", img.size)

# --- OCR штата: верхне-левый угол, где плашка "Штат #720" ---
W, H = img.size
corner = img.crop((0, 0, int(W * 0.22), int(H * 0.14)))
corner = corner.resize((corner.width * 2, corner.height * 2))
print("\nЗагрузка OCR (ru+en, первый раз качает ru-модель)...", flush=True)
reader = easyocr.Reader(["ru", "en"], gpu=False, verbose=False)
res = reader.readtext(np.array(corner), detail=0)
joined = " ".join(res)
m = re.search(r"#\s*(\d{2,4})", joined)
print("Сырьё OCR (угол штата):", res)
print("Штат распознан:", int(m.group(1)) if m else "НЕ НАЙДЕН")
