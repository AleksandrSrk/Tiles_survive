"""Тест: видны ли бейджи плиток при приближении. Свой штат -> макс. отдаление -> клик по миникарте
на плитки с плохим OCR (R4-02 dx102,dy-3 / R6-01 dx83,dy0) -> кадры на 0,2,3,4,6 щелчков приближения.
Кадры: data/720/screens/zoombadge/zb_<точка>_<щелчки>.png. Стоп: ScrollLock."""
import sys, os, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import window_manager as wm
import driver as dv
OUT = r"D:\PROJECT\TilesSurviveMap\data\720\screens\zoombadge"
os.makedirs(OUT, exist_ok=True)
LX, LY = 173, 101
try:
    if dv.abort_requested():
        print("ScrollLock включён"); sys.exit(2)
    print("[старт]", dv.start_position(), flush=True)
    for name, (dx, dy) in (("r4_02", (102, -3)), ("r6_01", (83, 0))):
        dv.zoom_max()
        w = dv.ensure_focus()
        dv.safe_click(w.left + w.width - LX + dx, w.top + LY + dy)
        time.sleep(2.2)
        done = 0
        for target in (0, 2, 3, 4, 6):
            if target > done:
                cx, cy = w.left + w.width // 2, w.top + w.height // 2
                dv.safe_wheel(cx, cy, target - done, delta=+120, pause=0.3)
                done = target
                time.sleep(1.2)
            img, _ = wm.capture_window(OUT + rf"\zb_{name}_{target}.png", settle=0.5)
            print("кадр", name, target, flush=True)
    dv.zoom_max()
    print("готово", flush=True)
except dv.Aborted as e:
    print("ОСТАНОВЛЕНО:", e)
except dv.FocusLost as e:
    print("ФОКУС ПОТЕРЯН:", e)
