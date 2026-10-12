"""Детерминированный старт: домой (Мое поселение) -> макс.зум -> проверка штата.
Тест клика по кнопке + гарантия, что мы в своём штате (720)."""
import sys, time, ctypes, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np, cv2, easyocr
import window_manager as wm

SCR = r"D:\PROJECT\TilesSurviveMap\data\720\screens"
TARGET_STATE = 720
u = ctypes.windll.user32


def click(x, y):
    u.SetCursorPos(int(x), int(y)); time.sleep(0.2)
    u.mouse_event(0x0002, 0, 0, 0, 0); time.sleep(0.06)
    u.mouse_event(0x0004, 0, 0, 0, 0)


def wheel_out(cx, cy, clicks=28):
    u.SetCursorPos(int(cx), int(cy)); time.sleep(0.2)
    for _ in range(clicks):
        u.mouse_event(0x0800, 0, 0, -120, 0); time.sleep(0.07)


w = wm.ensure_window()
L, T = w.left, w.top
# 1) кнопка "Мое поселение" (правая панель, верхняя строка)
print("клик 'Мое поселение' @", (L + 1665, T + 193))
click(L + 1665, T + 193)
time.sleep(2.2)                         # возврат к дому + прогрузка
# 2) максимальное отдаление
wheel_out(L + w.width // 2, T + w.height // 2, 28)
time.sleep(1.6)
# 3) снимок + OCR штата
img, _ = wm.capture_window(SCR + r"\home_verify.png", settle=1.2)
corner = img.crop((0, 0, int(img.width * 0.22), int(img.height * 0.14)))
corner = corner.resize((corner.width * 2, corner.height * 2))
reader = easyocr.Reader(["ru", "en"], gpu=False, verbose=False)
res = reader.readtext(np.array(corner), detail=0)
m = re.search(r"#\s*(\d{2,4})", " ".join(res))
state = int(m.group(1)) if m else None
print("штат OCR сырьё:", res)
print(f"штат: {state} | цель {TARGET_STATE} | в своём штате: {state == TARGET_STATE}")
