"""Нарезать шаблоны домиков из скриншота: центры домиков в пикселях кадра.
  python src\\houses\\tools\\make_templates.py shot.png blue:476,453 green:850,500 white:872,870 pink:694,578
Сохраняет assets/houses/<вид>.png размером 36x50. Центр точный не нужен, но чем ближе к центру «горшка», тем лучше."""
import os
import sys

import cv2

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
W, H = 36, 50


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    img = cv2.imread(sys.argv[1])
    out = os.path.join(BASE, "assets", "houses")
    os.makedirs(out, exist_ok=True)
    for arg in sys.argv[2:]:
        kind, xy = arg.split(":")
        x, y = map(int, xy.split(","))
        cv2.imwrite(os.path.join(out, kind + ".png"), img[y - H // 2:y + H // 2, x - W // 2:x + W // 2])
        print("шаблон", kind, "->", os.path.join(out, kind + ".png"))


if __name__ == "__main__":
    main()
