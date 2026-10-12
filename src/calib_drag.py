"""Калибровка: один контролируемый драг карты -> измерить сдвиг контента.
Проверяет, что синтетический ввод доходит до игры, и даёт коэффициент драг->мир."""
import sys, time, ctypes
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import cv2
import window_manager as wm

SCR = r"D:\PROJECT\TilesSurviveMap\data\720\screens"
u = ctypes.windll.user32
MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP = 0x0002, 0x0004


def move(x, y):
    u.SetCursorPos(int(x), int(y))


def drag(x0, y0, x1, y1, steps=25, hold=0.15):
    move(x0, y0); time.sleep(0.25)
    u.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0); time.sleep(hold)
    for i in range(1, steps + 1):
        move(x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps)
        time.sleep(0.012)
    time.sleep(hold)
    u.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


w = wm.ensure_window()
L, T = w.left, w.top
print("окно:", (w.width, w.height), "позиция", (L, T))

before, _ = wm.capture_window(SCR + r"\calib_before.png", settle=1.2)

sx, sy = L + 1000, T + 520          # старт в области карты (центр)
ex, ey = sx - 400, sy               # тащим влево на 400 px
print("драг курсора:", (sx, sy), "->", (ex, ey), "(dx=-400)")
drag(sx, sy, ex, ey)
time.sleep(1.8)                     # прогрузка/рендер, не спешим

after, _ = wm.capture_window(SCR + r"\calib_after.png", settle=1.2)


def prep(img):
    g = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY).astype(np.float32)
    return g[150:878, 300:1474]     # чистая область карты, без UI

b, a = prep(before), prep(after)
win = cv2.createHanningWindow((a.shape[1], a.shape[0]), cv2.CV_32F)
(dx, dy), resp = cv2.phaseCorrelate(b, a, win)
print(f"сдвиг контента: dx={dx:.1f} dy={dy:.1f}  (уверенность resp={resp:.3f})")
k = dx / -400 if dx else 0
print(f"коэффициент: драг -400px -> контент dx={dx:.1f}  => k={k:.2f}")
