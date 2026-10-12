"""Калибровка миникарта -> игровые X:Y. Свой штат, зум ~28 щелчков (один раз), дальше только клики по миникарте
(миникарта работает на любом зуме). По каждой точке 2 кадра (через 3 и 6 с) - плашка с X:Y читается офлайн.
Кадры: data/720/screens/calib/cc_<i>_<dx>_<dy>_<a|b>.png, журнал calib_journal.json. Стоп: ScrollLock."""
import sys, os, time, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import window_manager as wm
import driver as dv
OUT = r"D:\PROJECT\TilesSurviveMap\data\720\screens\calib"
os.makedirs(OUT, exist_ok=True)
LX, LY = 173, 101
PTS = [(71, 0), (30, 0), (110, 0), (71, -30), (71, 30), (50, -15), (92, -15), (50, 15), (92, 15), (20, 0), (125, 0), (71, -45), (71, 45)]
J = []
try:
    if dv.abort_requested():
        print("ScrollLock включён"); sys.exit(2)
    w = dv.ensure_focus()
    img, _ = wm.capture_window(OUT + r"\_probe.png", settle=0.5)
    if not dv.is_own_state(np.array(img)):
        print("[не свой штат -> start_position]", dv.start_position(), flush=True)
    dv.zoom_max()
    w = dv.ensure_focus()
    dv.safe_click(w.left + w.width - LX + PTS[0][0], w.top + LY + PTS[0][1]); time.sleep(2.2)
    cx, cy = w.left + w.width // 2, w.top + w.height // 2
    dv.safe_wheel(cx, cy, 28, delta=+120, pause=0.3); time.sleep(3.0)
    for i, (dx, dy) in enumerate(PTS):
        w = dv.ensure_focus()
        if i > 0:
            dv.safe_click(w.left + w.width - LX + dx, w.top + LY + dy)
            time.sleep(2.2)
            dv.safe_wheel(cx, cy, 30, delta=+120, pause=0.25)
        time.sleep(3.0)
        fa = OUT + rf"\cc_{i:02d}_{dx:03d}_{dy:+03d}_a.png"; wm.capture_window(fa, settle=0.3)
        time.sleep(3.0)
        fb = OUT + rf"\cc_{i:02d}_{dx:03d}_{dy:+03d}_b.png"; wm.capture_window(fb, settle=0.3)
        J.append({"i": i, "dx": dx, "dy": dy, "a": fa, "b": fb})
        json.dump(J, open(OUT + r"\calib_journal.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("точка", i, dx, dy, flush=True)
    dv.zoom_max()
    print("готово", flush=True)
except dv.Aborted as e:
    print("ОСТАНОВЛЕНО:", e)
except dv.FocusLost as e:
    print("ФОКУС ПОТЕРЯН:", e)
