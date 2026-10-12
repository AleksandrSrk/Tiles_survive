"""Картинка штата 720 на ЗАФИКСИРОВАННОЙ схеме (v12): блоки 20x20, L-образные земли, владельцы из map_schema_720.sqlite.
Запуск: python src\render_schema.py   -> data\720\map_720_schema.png
Перед этим обновить владельцев: python src\map_schema_lock.py owners
Тег со значком ~ = слабая уверенность OCR (<0.7) в последнем скане layer_a; ? = владелец неизвестен."""
import os, sqlite3, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import map_schema as ms

BASE = ms.BASE
OUT = os.path.join(BASE, "data", "720", "map_720_schema.png")
LAYER_A = os.path.join(BASE, "data", "720", "layer_a.sqlite")

# у каждого союза свой заметный цвет (разные, чтобы не путать)
PALETTE = {
    "HoD": (120, 170, 255), "SUN": (255, 200, 60), "FNX": (255, 120, 40), "DEU": (40, 190, 190),
    "ONE": (30, 90, 200), "BDS": (230, 110, 190), "REZ": (80, 200, 110), "ZOV": (200, 60, 60),
    "EKT": (160, 110, 60), "ULT": (150, 80, 220), "Zar": (200, 200, 90), "Log": (140, 140, 140),
}
FALLBACK = [(255, 160, 160), (160, 255, 160), (160, 160, 255), (255, 255, 160), (160, 255, 255), (255, 160, 255)]
UNKNOWN = (225, 225, 230)


def color_for(tag):
    if not tag:
        return UNKNOWN
    if tag not in PALETTE:
        PALETTE[tag] = FALLBACK[len(PALETTE) % len(FALLBACK)]
    return PALETTE[tag]


def font(sz, bold=False):
    for f in (("arialbd.ttf" if bold else "arial.ttf"), "segoeui.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def main():
    con = sqlite3.connect("file:" + ms.DB.replace("\\", "/") + "?mode=ro", uri=True)
    rows = con.execute("SELECT num,code,title,owner_tag FROM plates ORDER BY num").fetchall()
    con.close()
    owner = {n: t for n, c, ti, t in rows}
    code = {n: c for n, c, ti, t in rows}
    weak = set()
    scan_id = None
    try:
        la = sqlite3.connect("file:" + LAYER_A.replace("\\", "/") + "?mode=ro", uri=True)
        scan_id = la.execute("SELECT MAX(id) FROM scans").fetchone()[0]
        c2n = {c: n for n, c in code.items()}
        for cid, conf in la.execute("SELECT cell_id,confidence FROM cell_owners WHERE scan_id=?", (scan_id,)):
            if conf is not None and conf < 0.7 and cid in c2n:
                weak.add(c2n[cid])
        la.close()
    except Exception:
        pass

    W, H = 2300, 1700
    sx, sy = 0.78, 0.55
    ox, oy = 1150 + 60, 1630 - 20

    def scr(X, Y):
        return (ox + sx * (X - Y), oy - sy * ((X + Y) - 40))

    img = Image.new("RGB", (W, H), (247, 248, 250))
    d = ImageDraw.Draw(img)
    P, N = ms.PLATE, ms.N

    def quad(bx, by):
        X0, Y0 = 20 + 20 * bx, 20 + 20 * by
        return [scr(X0 - .5, Y0 - .5), scr(X0 + 19.5, Y0 - .5), scr(X0 + 19.5, Y0 + 19.5), scr(X0 - .5, Y0 + 19.5)]

    for bx in range(N):
        for by in range(N):
            n = int(P[bx, by])
            if n:
                d.polygon(quad(bx, by), fill=color_for(owner.get(n)))
    # границы земель
    for bx in range(N):
        for by in range(N):
            a = int(P[bx, by])
            for dx, dy in ((1, 0), (0, 1)):
                nx, ny = bx + dx, by + dy
                b = int(P[nx, ny]) if nx < N and ny < N else 0
                if a != b:
                    if dx:
                        p, q = scr(19.5 + 20 * (bx + 1), 19.5 + 20 * by), scr(19.5 + 20 * (bx + 1), 39.5 + 20 * by)
                    else:
                        p, q = scr(19.5 + 20 * bx, 19.5 + 20 * (by + 1)), scr(39.5 + 20 * bx, 19.5 + 20 * (by + 1))
                    d.line([p, q], fill=(255, 255, 255), width=3)
    # подписи
    fb, fs, ff = font(22, True), font(15), font(30, True)
    for n, c, title, t in rows:
        m = np.argwhere(P == n)
        if not len(m):
            continue
        cx, cy = m.mean(0)
        k = np.argmin(((m - [cx, cy]) ** 2).sum(1))   # блок, ближайший к центру (для L-образных)
        bx, by = m[k]
        p = scr(30 + 20 * bx, 30 + 20 * by)
        lab = (t or "?") + ("~" if n in weak else "")
        dark = sum(color_for(t)) < 330
        fg = (255, 255, 255) if dark else (20, 22, 30)
        d.text((p[0], p[1] - 9), lab, font=fb, fill=fg, anchor="mm")
        d.text((p[0], p[1] + 12), title, font=fs, fill=fg, anchor="mm")
    # шапка + легенда
    d.text((40, 30), "Штат 720 · владельцы земель (схема v12)", font=ff, fill=(20, 22, 30))
    d.text((40, 72), f"layer_a scan {scan_id}   ~ слабая уверенность   ? неизвестен", font=font(16), fill=(90, 90, 100))
    cnt = {}
    for n in owner:
        if P.size and (P == n).any():
            cnt[owner[n] or "?"] = cnt.get(owner[n] or "?", 0) + 1
    y = 120
    for t, k in sorted(cnt.items(), key=lambda kv: -kv[1]):
        d.rectangle([40, y, 76, y + 24], fill=color_for(None if t == "?" else t))
        d.text((90, y + 12), f"{t}", font=font(20, True), fill=(20, 22, 30), anchor="lm")
        d.text((190, y + 12), f"{k}", font=font(20), fill=(90, 90, 100), anchor="lm")
        y += 34
    img.save(OUT)
    print("OK", OUT)
    for t, k in sorted(cnt.items(), key=lambda kv: -kv[1]):
        print(t, k, ", ".join(ti for n, c, ti, o in rows if (o or "?") == t))


if __name__ == "__main__":
    main()
