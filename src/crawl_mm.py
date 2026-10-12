"""Обход штата (слой А) КЛИКАМИ ПО МИНИКАРТЕ. Абсолютное позиционирование, без дрейфа.
Миникарта (оффсеты от правого/верхнего края окна): левая вершина ромба (-173,+101),
полуширина 70.5 px, полувысота ~52 px. 1 px миникарты ~ 34 px экрана (замер test_mm).
Кадры -> data/720/screens/mm_grid/, журнал -> data/720/mm_grid_journal.json
Запуск: python crawl_mm.py [--test] [--dx 18] [--dy 12]   (--test: 12 точек в центре)
Каждый скан -> data/720/scans/scan_YYYYmmdd_HHMMSS/{frames,journal.json}
Досъёмка слабых плиток: --points data/720/recheck_XXX.json --into data/720/scans/scan_XXX (кадры добавляются в тот же журнал)
Обработка: python src/layer_a_process.py --journal <scan>/journal.json
Аварийный стоп: ScrollLock."""
import sys, os, time, json, datetime
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import window_manager as wm
import driver as dv

BASE = r"D:\PROJECT\TilesSurviveMap"
OUT = BASE + r"\data\720\screens\mm_grid"
JOURNAL = BASE + r"\data\720\mm_grid_journal.json"
LX, LY = 173, 101
HW, HH = 70.5, 52.0


def inside(dx, dy, margin=2.0):
    return abs(dy) <= HH * (1 - abs(dx - HW) / HW) - margin


def grid(step_x, step_y):
    pts = []
    xs = np.arange(2, 2 * HW - 1, step_x)
    for i, x in enumerate(xs):
        ys = [y for y in np.arange(-HH, HH + 1, step_y) if inside(x, y)]
        ys = ys if i % 2 == 0 else ys[::-1]
        pts += [(int(round(x)), int(round(y))) for y in ys]
    return pts


def main():
    step_x = int(sys.argv[sys.argv.index("--dx") + 1]) if "--dx" in sys.argv else 18
    step_y = int(sys.argv[sys.argv.index("--dy") + 1]) if "--dy" in sys.argv else 12
    if "--test" in sys.argv:
        pts = [(x, y) for x in (30, 60, 90, 115) for y in (-20, 0, 20) if inside(x, y)]
    else:
        pts = grid(step_x, step_y)
    zoom = int(sys.argv[sys.argv.index("--zoom") + 1]) if "--zoom" in sys.argv else 0
    out, journal, cells = OUT, JOURNAL, []
    into = sys.argv[sys.argv.index("--into") + 1] if "--into" in sys.argv else None
    if "--points" in sys.argv:
        pj = json.load(open(sys.argv[sys.argv.index("--points") + 1], encoding="utf-8"))
        pts = []
        for r in pj:
            p = (int(r["dx"]), int(r["dy"]))
            if inside(p[0], p[1]) and p not in pts: pts.append(p)
    if into or "--legacy" not in sys.argv:
        sd = into or (BASE + r"\data\720\scans\scan_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
        out, journal = sd + (r"\frames_zoom" if zoom else r"\frames"), sd + (r"\journal_zoom.json" if zoom else r"\journal.json")
        if into and os.path.exists(journal): cells = json.load(open(journal, encoding="utf-8"))["cells"]
    os.makedirs(out, exist_ok=True)
    print(f"точек: {len(pts)}, папка: {out}", flush=True)
    print("[старт]", dv.start_position(), flush=True)
    try:
        for i, (dx, dy) in enumerate(pts):
            w = dv.ensure_focus()
            dv.safe_click(w.left + w.width - LX + dx, w.top + LY + dy)
            time.sleep(2.2)
            if zoom:
                dv.safe_wheel(w.left + w.width // 2, w.top + w.height // 2, zoom, delta=+120, pause=0.3)
                time.sleep(1.2)
            fn = out + rf"\g_x{dx:03d}_y{dy:+04d}.png"
            img, _ = wm.capture_window(fn, settle=0.5)
            own = dv.is_own_state(np.array(img))
            cells.append({"i": len(cells), "dx": dx, "dy": dy, "file": fn, "own": own})
            print(f"  [{i+1}/{len(pts)}] dx={dx} dy={dy} own={own}", flush=True)
            if zoom: dv.zoom_max()
            with open(journal, "w", encoding="utf-8") as f:
                json.dump({"lx": LX, "ly": LY, "cells": cells}, f, ensure_ascii=False, indent=1)
    except dv.Aborted as e:
        print("ОСТАНОВЛЕНО:", e)
    except dv.FocusLost as e:
        print("ФОКУС ПОТЕРЯН:", e)
    print("готово")


if __name__ == "__main__":
    if dv.abort_requested():
        print("ScrollLock включён"); sys.exit(2)
    main()
