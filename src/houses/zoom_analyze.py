"""Решает по кадрам zoom_capture, сколько щелчков от макс. отдаления нужно, чтобы появился БЕЛЫЙ домик (и не ближе).
Запуск (обычный процесс, игра не нужна): python src\\houses\\zoom_analyze.py [папка с кадрами]
Для каждого кадра: мультимасштабный поиск домиков (шаблоны сняты на целевом зуме, scale=1.0 = целевой зум).
Домик принимаем, только если на кадре найдено >=3 домиков (любых) и масштаб белого в пределах 15% от медианного (отсев ложняков).
Пишет data/720/house_zoom.json {clicks_from_max_out, scale_vs_template, blue_first, white_first, table}."""
import glob
import json
import os
import re
import sys
from collections import Counter

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import detect  # noqa: E402

BASE = os.path.dirname(os.path.dirname(HERE))
FRAMES = os.path.join(BASE, "data", "720", "screens", "zoom_house")
OUT = os.path.join(BASE, "data", "720", "house_zoom.json")


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else FRAMES
    files = sorted(glob.glob(os.path.join(folder, "c_*.png")))
    if not files:
        print("нет кадров в", folder)
        return
    tpls = detect.load_templates()
    table = []
    for f in files:
        k = int(re.search(r"c_(\d+)", f).group(1))
        res = detect.detect_multiscale(cv2.imread(f), tpls, min_score=0.6)
        blues = [(s, d) for s, d in res if d.kind == "blue"]
        whites = [(s, d) for s, d in res if d.kind == "white"]
        allsc = [s for s, _ in blues + whites]
        sb = float(np.median(allsc)) if len(allsc) >= 3 else None      # опорный масштаб кадра: все найденные домики
        wh_ok = [s for s, _ in whites if sb and abs(s - sb) / sb <= 0.15]
        row = dict(clicks=k, blue=len(blues), white_raw=len(whites), white_ok=len(wh_ok), scale=round(sb, 2) if sb else None)
        table.append(row)
        print(row, flush=True)
    blue_first = next((r["clicks"] for r in table if r["blue"] >= 3), None)
    white_first = next((r["clicks"] for i, r in enumerate(table) if r["white_ok"] >= 1 and
                        any(t["white_ok"] >= 1 for t in table[i + 1:i + 2])), None)   # два кадра подряд
    rec = next((r for r in table if r["clicks"] == white_first), None)
    result = dict(clicks_from_max_out=white_first, blue_first=blue_first, white_first=white_first,
                  scale_vs_template=rec["scale"] if rec else None, table=table)
    json.dump(result, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nсиние домики впервые на щелчке:", blue_first)
    print("белый домик впервые (стабильно) на щелчке:", white_first,
          "| масштаб относительно шаблонов (1.0 = зум с твоей калибровкой 22 px на u):", result["scale_vs_template"])
    print("записано:", OUT)


if __name__ == "__main__":
    main()
