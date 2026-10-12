"""Тест: реальный сдвиг карты после драга + проверка инерции (кадр через 1.4 с и через +2.5 с).
Драги по +U (внутрь штата) 3 раза по 300 px, потом 1 раз по +V. Кадры -> data/720/screens/drag/"""
import sys, os, time, math
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import window_manager as wm
import driver as dv

OUT = r"D:\PROJECT\TilesSurviveMap\data\720\screens\drag"
os.makedirs(OUT, exist_ok=True)
TH = math.radians(35.2)
U = np.array([math.cos(TH), -math.sin(TH)])
V = np.array([math.cos(TH), math.sin(TH)])
K = 1.02

def shot(name):
    wm.capture_window(os.path.join(OUT, name + ".png"), settle=0.3)
    print("  кадр", name, flush=True)

def drag(d):
    w = dv.ensure_focus()
    cx, cy = w.left + w.width // 2, w.top + w.height // 2
    h = d / (2 * K)
    dv.safe_drag(cx + h[0], cy + h[1], cx - h[0], cy - h[1])

try:
    print("[старт]", dv.start_position(), flush=True)
    shot("f0")
    plan = [("u1", 300 * U), ("u2", 300 * U), ("u3", 300 * U), ("v1", 300 * V)]
    for name, d in plan:
        print("драг", name, d.round(0), flush=True)
        drag(d)
        time.sleep(1.4)
        shot(name + "_a")
        time.sleep(2.5)
        shot(name + "_b")
except (dv.Aborted, dv.FocusLost) as e:
    print("СТОП:", repr(e))
print("готово")
