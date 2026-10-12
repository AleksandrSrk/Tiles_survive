"""БОЕВОЙ режим: сразу встать на зум «домики» (без пошагового обучения).
  from houses import zoom_set; zoom_set.set_house_zoom()
Берёт число щелчков из data/720/house_zoom.json (его создаёт zoom_analyze.py), отдаляется до упора и
приближает ровно на столько щелчков. Нужна игра (driver, window_manager), ScrollLock = стоп."""
import json
import os
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CFG = os.path.join(BASE, "data", "720", "house_zoom.json")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def house_zoom_clicks():
    n = json.load(open(CFG, encoding="utf-8")).get("clicks_from_max_out")
    if not n:
        raise RuntimeError("в house_zoom.json нет clicks_from_max_out: сначала zoom_capture.py и zoom_analyze.py")
    return int(n)


def set_house_zoom(settle=1.0):
    import driver as dv
    n = house_zoom_clicks()
    w = dv.ensure_focus()
    dv.zoom_max()
    cx, cy = w.left + w.width // 2, w.top + w.height // 2
    dv.safe_wheel(cx, cy, n, delta=+120, pause=0.15)
    time.sleep(settle)          # домики подгружаются
    return n
