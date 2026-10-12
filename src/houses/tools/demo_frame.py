"""Демо на ОДНОМ скриншоте: найти домики, нарисовать кружки, при желании откалибровать геометрию и посчитать по землям.
  python src\\houses\\tools\\demo_frame.py shot.png
  python src\\houses\\tools\\demo_frame.py shot.png --calib "475,455:123,1218 1225,580:136,1197 805,190:140,1220 868,880:119,1196"
Калибровка: пиксель_на_экране:игровые_X,Y (берётся ближайшая найденная находка в радиусе 30 px).
Результат: data/720/demo_<имя>.png (кружки: blue синий, white жёлтый, green зелёный, pink розовый)."""
import argparse
import math
import os
import sys
from collections import Counter

import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, SRC)
sys.path.insert(0, os.path.dirname(HERE))
import detect  # noqa: E402
import geo as geomod  # noqa: E402
import heatmap  # noqa: E402
import store  # noqa: E402

COL = {"blue": (255, 80, 0), "white": (0, 200, 255), "green": (0, 220, 0), "pink": (255, 0, 255)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shot")
    ap.add_argument("--calib", default="")
    ap.add_argument("--save-db", action="store_true", help="сохранить находки кадра в houses.sqlite (нужна --calib)")
    a = ap.parse_args()
    img = cv2.imread(a.shot)
    dets = detect.detect(img)
    print("найдено:", len(dets), dict(Counter(d.kind for d in dets)))
    out = img.copy()
    for d in dets:
        cv2.circle(out, (d.x, d.y), 22, COL.get(d.kind, (0, 0, 255)), 2)
    name = os.path.splitext(os.path.basename(a.shot))[0]
    path = os.path.join(SRC, "..", "data", "720", f"demo_{name}.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cv2.imwrite(path, out)
    print("картинка:", os.path.normpath(path))
    if a.calib:
        pts = []
        for item in a.calib.split():
            p, g = item.split(":")
            px, py = map(float, p.split(","))
            X, Y = map(float, g.split(","))
            near = min(dets, key=lambda d: math.hypot(d.x - px, d.y - py))
            if math.hypot(near.x - px, near.y - py) > 30:
                print("нет находки рядом с", p)
                continue
            pts.append(((near.x, near.y), (X, Y)))
        geo, err = geomod.fit(pts)
        print(f"масштаб: {geo.a:.2f} px на u, {geo.b:.2f} px на v; p0={geo.p0:.1f} q0={geo.q0:.1f}; макс. невязка {err:.1f} px")
        houses = [(*geo.to_game(d.x, d.y), d.kind) for d in dets]
        pc = heatmap.plate_counts(houses)
        print("домиков по землям (номер: сколько):", dict(sorted(pc.items())))
        if a.save_db:
            con = store.connect()
            print("сохранено детекций:", store.add_frame(con, name, geo, dets), "домиков после слияния:", store.rebuild_houses(con))


if __name__ == "__main__":
    main()
