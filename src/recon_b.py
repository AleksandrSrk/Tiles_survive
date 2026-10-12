"""Разведка слоя Б: домики/ники на разных зумах. Свой штат -> макс. отдаление -> клик по миникарте
в 2 точки (центр, край) -> кадры на 8,12,16,20,25,30 щелчках приближения.
Кадры: data/720/screens/reconb/rb_<точка>_<щелчки>.png. Стоп: ScrollLock."""
import sys, os, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import window_manager as wm
import driver as dv
OUT = r"D:\PROJECT\TilesSurviveMap\data\720\screens\reconb"
os.makedirs(OUT, exist_ok=True)
LX, LY = 173, 101
try:
    if dv.abort_requested():
        print("ScrollLock включён"); sys.exit(2)
    print("[старт]", dv.start_position(), flush=True)
    for name, (dx, dy) in (("c", (71, 1)), ("r1", (117, 15))):
        dv.zoom_max()
        w = dv.ensure_focus()
        dv.safe_click(w.left + w.width - LX + dx, w.top + LY + dy)
        time.sleep(2.2)
        done = 0
        for target in (8, 12, 16, 20, 25, 30):
            cx, cy = w.left + w.width // 2, w.top + w.height // 2
            dv.safe_wheel(cx, cy, target - done, delta=+120, pause=0.3)
            done = target
            time.sleep(1.3)
            wm.capture_window(OUT + rf"\rb_{name}_{target:02d}.png", settle=0.5)
            print("кадр", name, target, flush=True)
    dv.zoom_max()
    print("готово", flush=True)
except dv.Aborted as e:
    print("ОСТАНОВЛЕНО:", e)
except dv.FocusLost as e:
    print("ФОКУС ПОТЕРЯН:", e)
