"""Тест линейности: драги по +U/-U с разной длиной КУРСОРА (px), без всякого k. Кадры -> data/720/screens/drag2/"""
import sys, os, time, math
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import window_manager as wm
import driver as dv

OUT = r"D:\PROJECT\TilesSurviveMap\data\720\screens\drag2"
os.makedirs(OUT, exist_ok=True)
TH = math.radians(35.2)
U = np.array([math.cos(TH), -math.sin(TH)])

def shot(name):
    wm.capture_window(os.path.join(OUT, name + ".png"), settle=0.4)

def drag_cursor(L, sign):
    """Курсор тянем на L px: контент уйдёт за курсором (sign=+1: курсор вдоль -U, вид вдоль +U)."""
    w = dv.ensure_focus()
    cx, cy = w.left + w.width // 2, w.top + w.height // 2
    h = sign * L * U / 2
    dv.safe_drag(cx + h[0], cy + h[1], cx - h[0], cy - h[1])
    time.sleep(1.6)

try:
    print("[старт]", dv.start_position(), flush=True)
    shot("f0")
    i = 0
    for L in (150, 250, 350, 450, 300, 300):
        i += 1
        print("драг курсор", L, "вперёд", flush=True)
        drag_cursor(L, +1)
        shot(f"d{i}_L{L}_fwd")
        drag_cursor(L, -1)
        shot(f"d{i}_L{L}_back")
except (dv.Aborted, dv.FocusLost) as e:
    print("СТОП:", repr(e))
print("готово")
