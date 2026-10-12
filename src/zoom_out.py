"""Шаг 1 обхода: максимальное отдаление (зум-аут колесом до упора).
Проверяет, что скролл-ввод доходит до игры. Снимает кадр максимального зума."""
import sys, time, ctypes
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import cv2
import window_manager as wm

SCR = r"D:\PROJECT\TilesSurviveMap\data\720\screens"
u = ctypes.windll.user32
MOUSEEVENTF_WHEEL = 0x0800


def wheel(cx, cy, clicks, delta=-120, pause=0.08):
    u.SetCursorPos(int(cx), int(cy)); time.sleep(0.3)
    for _ in range(clicks):
        u.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, delta, 0)
        time.sleep(pause)


def prep(img):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY).astype(np.float32)[150:878, 300:1474]


w = wm.ensure_window()
cx, cy = w.left + w.width // 2, w.top + w.height // 2
print("центр карты:", (cx, cy))

before, _ = wm.capture_window(SCR + r"\zoom_before.png", settle=1.0)
# отдаляем партиями, ловим момент, когда перестало меняться (упор)
prev = prep(before)
total = 0
for batch in range(8):
    wheel(cx, cy, 5, delta=-120)      # 5 кликов колеса "от себя" = зум-аут
    time.sleep(1.2)
    img, _ = wm.capture_window(SCR + r"\zoom_step.png", settle=0.8)
    cur = prep(img)
    win = cv2.createHanningWindow((cur.shape[1], cur.shape[0]), cv2.CV_32F)
    (dx, dy), resp = cv2.phaseCorrelate(prev, cur, win)
    change = (dx * dx + dy * dy) ** 0.5
    total += 5
    print(f"партия {batch+1}: всего кликов={total}, изменение кадра={change:.1f}px")
    prev = cur
    if change < 3:
        print("кадр перестал меняться -> достигнут максимум отдаления")
        break

img, bbox = wm.capture_window(SCR + r"\zoom_max.png", settle=1.2)
print("готово, кадр макс. зума:", img.size, bbox)
