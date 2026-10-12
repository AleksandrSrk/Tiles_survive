"""Тест позиционирования кликом по миникарте (слой А, макс-отдаление).
Миникарта: левая вершина ромба ~ (right-173, top+101), правая ~ (right-32), центр ~ (right-103).
Клики: c0 лев.вершина, +7 вправо, +7 вправо +7 вниз, +14/+7, обратно c0 (повторяемость), центр.
Кадры -> data/720/screens/mm/"""
import sys, os, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import window_manager as wm
import driver as dv

OUT = r"D:\PROJECT\TilesSurviveMap\data\720\screens\mm"
os.makedirs(OUT, exist_ok=True)
LX, LY = 173, 101          # от правого/верхнего края окна до левой вершины ромба

def shot(name):
    wm.capture_window(os.path.join(OUT, name + ".png"), settle=0.5)
    print("  кадр", name, flush=True)

def click_mm(dx, dy, name):
    w = dv.ensure_focus()
    x = w.left + w.width - LX + dx
    y = w.top + LY + dy
    dv.safe_click(x, y)
    time.sleep(2.2)
    shot(name)

try:
    print("[старт]", dv.start_position(), flush=True)
    shot("s0")
    pts = [("c0", 0, 0), ("c1", 7, 0), ("c2", 7, 7), ("c3", 14, 7), ("c0b", 0, 0), ("c4", 70, 0), ("c5", 70, -30), ("c6", 70, 40)]
    for name, dx, dy in pts:
        print("клик миникарты", name, dx, dy, flush=True)
        click_mm(dx, dy, name)
except (dv.Aborted, dv.FocusLost) as e:
    print("СТОП:", repr(e))
print("готово")
