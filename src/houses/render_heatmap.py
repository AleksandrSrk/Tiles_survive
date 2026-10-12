"""Картинка тепловой карты домиков на схеме штата v12: цвет блока = число домиков, плюс контуры земель.
Запуск: python src\\houses\\render_heatmap.py [--kinds blue,white] -> data\\720\\heat_720.png"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import map_schema as ms  # noqa: E402
import heatmap  # noqa: E402
import store  # noqa: E402

OUT = os.path.join(ms.BASE, "data", "720", "heat_720.png")


def heat_color(v, vmax):
    if v <= 0:
        return (232, 234, 238)
    t = min(1.0, (v / vmax) ** 0.5)
    return (255, int(235 - 190 * t), int(190 - 170 * t))   # светло-жёлтый -> красный


def font(sz):
    for f in ("arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kinds", default="", help="через запятую: blue,white,green,pink (пусто = все)")
    ap.add_argument("--db", default=store.DB)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    kinds = [k for k in a.kinds.split(",") if k] or None
    con = store.connect(a.db)
    houses = store.load_houses(con)
    grid = heatmap.block_counts(houses, kinds)
    vmax = max(1, int(grid.max()))

    W, H, sx, sy = 2300, 1700, 0.78, 0.55
    ox, oy = 1210, 1610

    def scr(X, Y):
        return ox + sx * (X - Y), oy - sy * ((X + Y) - 40)

    img = Image.new("RGB", (W, H), (247, 248, 250))
    d = ImageDraw.Draw(img)
    P, N = ms.PLATE, ms.N
    for bx in range(N):
        for by in range(N):
            if P[bx, by]:
                X0, Y0 = 20 + 20 * bx, 20 + 20 * by
                q = [scr(X0 - .5, Y0 - .5), scr(X0 + 19.5, Y0 - .5), scr(X0 + 19.5, Y0 + 19.5), scr(X0 - .5, Y0 + 19.5)]
                d.polygon(q, fill=heat_color(int(grid[bx, by]), vmax))
    for bx in range(N):
        for by in range(N):
            a_ = int(P[bx, by])
            for dx, dy in ((1, 0), (0, 1)):
                nx, ny = bx + dx, by + dy
                b_ = int(P[nx, ny]) if nx < N and ny < N else 0
                if a_ != b_:
                    if dx:
                        p, q = scr(19.5 + 20 * (bx + 1), 19.5 + 20 * by), scr(19.5 + 20 * (bx + 1), 39.5 + 20 * by)
                    else:
                        p, q = scr(19.5 + 20 * bx, 19.5 + 20 * (by + 1)), scr(39.5 + 20 * bx, 19.5 + 20 * (by + 1))
                    d.line([p, q], fill=(120, 120, 130), width=2)
    pc = heatmap.plate_counts(houses, kinds)
    for n, p_ in ms.PLATES.items():
        import numpy as np
        m = np.argwhere(P == n)
        if not len(m) or not pc.get(n):
            continue
        cx, cy = m.mean(0)
        k = np.argmin(((m - [cx, cy]) ** 2).sum(1))
        bx, by = m[k]
        p = scr(30 + 20 * bx, 30 + 20 * by)
        d.text(p, f"{pc[n]}", font=font(22), fill=(20, 22, 30), anchor="mm")
    d.text((40, 30), f"Тепловая карта домиков (всего {len(houses)}, макс. в блоке {vmax})", font=font(30), fill=(20, 22, 30))
    d.text((40, 72), "число = домиков на земле; серое = домиков не найдено/не снято", font=font(16), fill=(90, 90, 100))
    img.save(a.out)
    print("OK", a.out, "домиков:", len(houses))


if __name__ == "__main__":
    main()
